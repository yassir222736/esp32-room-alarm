#include "web.h"
#include "alarm.h"
#include "config.h"
#include "ir.h"
#include "logbook.h"
#include "notify.h"
#include "secrets.h"
#include "sensors.h"
#include <ArduinoJson.h>
#include <ESPAsyncWebServer.h>
#include <LittleFS.h>
#include <WiFi.h>

static AsyncWebServer server(80);
static AsyncWebSocket ws("/ws");
static const char *SOUND_FILE = "/alarm.mp3";
static File uploadFile;
static bool uploadOk = false;

// Bescherming tegen raden: na MAX_PIN_FAILS foute pogingen blijft alles PIN_LOCK_MS geblokkeerd.
static constexpr uint8_t MAX_PIN_FAILS = 5;
static constexpr uint32_t PIN_LOCK_MS = 60000;
static uint8_t pinFails = 0;
static uint32_t pinLockedSince = 0;
static bool pinLocked = false;

static bool isLocked() {
  if (pinLocked && millis() - pinLockedSince >= PIN_LOCK_MS) pinLocked = false;
  return pinLocked;
}

static bool pinOk(AsyncWebServerRequest *req) {
  if (isLocked()) return false;
  const AsyncWebParameter *p = req->getParam("pin", true);
  if (!p) p = req->getParam("pin");
  if (p && p->value() == WEB_PIN) {
    pinFails = 0;
    return true;
  }
  if (++pinFails >= MAX_PIN_FAILS) {
    pinFails = 0;
    pinLocked = true;
    pinLockedSince = millis();
    Serial.println("[web] te veel foute pincodes, 1 minuut geblokkeerd");
  }
  return false;
}

static void denied(AsyncWebServerRequest *req) {
  if (isLocked()) req->send(429, "text/plain", "Te veel foute pogingen, wacht 1 minuut");
  else req->send(403, "text/plain", "Verkeerde pincode");
}

String statusJson() {
  JsonDocument doc;
  doc["state"] = alarmStateName();
  doc["left"] = alarmSecondsLeft();
  float d = sonarDistance();
  doc["distance"] = d < 0 ? -1 : roundf(d);
  float b = alarmBaseline();
  if (isnan(b)) doc["baseline"] = nullptr;
  else doc["baseline"] = b < 0 ? -1 : roundf(b);
  doc["pir"] = pirActive();
  doc["entries"] = logbookEntryCount();
  doc["sound"] = LittleFS.exists(SOUND_FILE);
  doc["irLearning"] = irIsLearning();
  JsonObject s = doc["settings"].to<JsonObject>();
  s["thresholdCm"] = settings.thresholdCm;
  s["confirmCount"] = settings.confirmCount;
  s["pirConfirm"] = settings.pirConfirm;
  s["pirWindowS"] = settings.pirWindowS;
  s["exitDelayS"] = settings.exitDelayS;
  s["entryDelayS"] = settings.entryDelayS;
  s["alarmDurationS"] = settings.alarmDurationS;
  s["buzzerEnabled"] = settings.buzzerEnabled;
  char ir[20];
  snprintf(ir, sizeof(ir), "0x%llX", settings.irToggleCode);
  s["irToggleCode"] = ir;
  String out;
  serializeJson(doc, out);
  return out;
}

template <typename T>
static void readParam(AsyncWebServerRequest *req, const char *name, T &target, long lo, long hi) {
  const AsyncWebParameter *p = req->getParam(name, true);
  if (!p) return;
  long v = p->value().toInt();
  target = (T)constrain(v, lo, hi);
}

static void readBool(AsyncWebServerRequest *req, const char *name, bool &target) {
  const AsyncWebParameter *p = req->getParam(name, true);
  if (p) target = p->value() == "1" || p->value() == "true";
}

void webBegin() {
  server.addHandler(&ws);

  server.on("/api/state", HTTP_GET, [](AsyncWebServerRequest *req) {
    req->send(200, "application/json", statusJson());
  });

  server.on("/api/log", HTTP_GET, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);  // logboek verraadt wanneer je weg bent
    req->send(200, "application/json", logbookJson());
  });

  server.on("/api/checkpin", HTTP_POST, [](AsyncWebServerRequest *req) {
    pinOk(req) ? req->send(200, "text/plain", "ok") : denied(req);
  });

  server.on("/api/arm", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    alarmRequestArm("webpagina");
    req->send(200, "text/plain", "ok");
  });

  server.on("/api/disarm", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    alarmRequestDisarm("webpagina");
    req->send(200, "text/plain", "ok");
  });

  server.on("/api/calibrate", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    alarmRequestCalibrate();
    req->send(200, "text/plain", "ok");
  });

  server.on("/api/irlearn", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    irStartLearning();
    req->send(200, "text/plain", "Druk nu op een knop van de afstandsbediening");
  });

  server.on("/api/testnotify", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    notifySend("Kameralarm test", "Als je dit ziet, werken de meldingen!", false);
    req->send(200, "text/plain", "ok");
  });

  server.on("/api/log/clear", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    logbookClear();
    req->send(200, "text/plain", "ok");
  });

  server.on("/api/settings", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    readParam(req, "thresholdCm", settings.thresholdCm, 5, 200);
    readParam(req, "confirmCount", settings.confirmCount, 1, 10);
    readParam(req, "pirWindowS", settings.pirWindowS, 2, 60);
    readParam(req, "exitDelayS", settings.exitDelayS, 5, 300);
    readParam(req, "entryDelayS", settings.entryDelayS, 0, 120);
    readParam(req, "alarmDurationS", settings.alarmDurationS, 10, 900);
    readBool(req, "pirConfirm", settings.pirConfirm);
    readBool(req, "buzzerEnabled", settings.buzzerEnabled);
    settingsSave();
    req->send(200, "text/plain", "ok");
  });

  server.on("/api/sound/delete", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!pinOk(req)) return denied(req);
    LittleFS.remove(SOUND_FILE);
    req->send(200, "text/plain", "ok");
  });

  // mp3 uploaden: POST /upload?pin=xxxx (multipart, veld "file")
  server.on(
      "/upload", HTTP_POST,
      [](AsyncWebServerRequest *req) {
        if (!pinOk(req)) return denied(req);
        uploadOk ? req->send(200, "text/plain", "ok")
                 : req->send(400, "text/plain", "Upload mislukt (te groot of geen mp3?)");
      },
      [](AsyncWebServerRequest *req, const String &filename, size_t index, uint8_t *data, size_t len, bool final) {
        if (index == 0) {
          uploadOk = false;
          if (!pinOk(req)) return;
          LittleFS.remove(SOUND_FILE);
          uploadFile = LittleFS.open(SOUND_FILE, "w");
          uploadOk = (bool)uploadFile;
        }
        if (!uploadOk) return;
        if (uploadFile.write(data, len) != len) {  // schijf vol
          uploadFile.close();
          LittleFS.remove(SOUND_FILE);
          uploadOk = false;
          return;
        }
        if (final) {
          uploadFile.close();
          Serial.printf("[web] mp3 opgeslagen (%u bytes)\n", (unsigned)(index + len));
        }
      });

  server.serveStatic(SOUND_FILE, LittleFS, SOUND_FILE).setCacheControl("no-cache");
  server.serveStatic("/", LittleFS, "/www/").setDefaultFile("index.html");
  server.onNotFound([](AsyncWebServerRequest *req) { req->send(404, "text/plain", "Niet gevonden"); });
  server.begin();
}

void webLoop() {
  static uint32_t lastPush = 0;
  if (millis() - lastPush < 300) return;
  lastPush = millis();
  ws.cleanupClients();
  if (ws.count()) ws.textAll(statusJson());
}
