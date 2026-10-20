#include "logbook.h"
#include <ArduinoJson.h>
#include <LittleFS.h>
#include <deque>

struct LogEntry {
  time_t t;          // Unix-tijd, 0 = klok nog niet gelijkgezet
  uint32_t uptimeS;  // seconden sinds opstart (reserve als de klok onbekend is)
  String type;
  String detail;
};

static const char *LOG_FILE = "/log.json";
static constexpr size_t MAX_ENTRIES = 200;

static std::deque<LogEntry> entries;
static uint32_t entryCount = 0;
static SemaphoreHandle_t mutex;

static time_t nowOrZero() {
  time_t now = time(nullptr);
  return now > 1700000000 ? now : 0;  // vóór 2023 = nog geen NTP-tijd
}

static void buildJson(JsonDocument &doc) {
  doc["count"] = entryCount;
  JsonArray arr = doc["entries"].to<JsonArray>();
  for (const auto &e : entries) {
    JsonObject o = arr.add<JsonObject>();
    o["t"] = (uint32_t)e.t;
    o["up"] = e.uptimeS;
    o["type"] = e.type;
    o["detail"] = e.detail;
  }
}

static void save() {
  JsonDocument doc;
  buildJson(doc);
  File f = LittleFS.open(LOG_FILE, "w");
  if (!f) return;
  serializeJson(doc, f);
  f.close();
}

void logbookBegin() {
  mutex = xSemaphoreCreateMutex();
  File f = LittleFS.open(LOG_FILE, "r");
  if (!f) return;
  JsonDocument doc;
  if (deserializeJson(doc, f) == DeserializationError::Ok) {
    entryCount = doc["count"] | 0;
    for (JsonObject o : doc["entries"].as<JsonArray>()) {
      entries.push_back({(time_t)(o["t"] | 0u), o["up"] | 0u,
                         o["type"] | "", o["detail"] | ""});
    }
  }
  f.close();
}

void logbookAdd(const char *type, const String &detail) {
  xSemaphoreTake(mutex, portMAX_DELAY);
  entries.push_back({nowOrZero(), millis() / 1000, type, detail});
  while (entries.size() > MAX_ENTRIES) entries.pop_front();
  if (strcmp(type, LogType::Entry) == 0) entryCount++;
  save();
  xSemaphoreGive(mutex);
  Serial.printf("[log] %s %s\n", type, detail.c_str());
}

uint32_t logbookEntryCount() { return entryCount; }

String logbookJson() {
  xSemaphoreTake(mutex, portMAX_DELAY);
  JsonDocument doc;
  buildJson(doc);
  String out;
  serializeJson(doc, out);
  xSemaphoreGive(mutex);
  return out;
}

void logbookClear() {
  xSemaphoreTake(mutex, portMAX_DELAY);
  entries.clear();
  entryCount = 0;
  save();
  xSemaphoreGive(mutex);
}
