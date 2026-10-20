#include "config.h"
#include <ArduinoJson.h>
#include <LittleFS.h>

Settings settings;

static const char *SETTINGS_FILE = "/settings.json";

void settingsLoad() {
  File f = LittleFS.open(SETTINGS_FILE, "r");
  if (!f) return;  // eerste start: standaardwaarden
  JsonDocument doc;
  if (deserializeJson(doc, f) == DeserializationError::Ok) {
    Settings d;
    settings.thresholdCm    = doc["thresholdCm"]    | d.thresholdCm;
    settings.confirmCount   = doc["confirmCount"]   | d.confirmCount;
    settings.pirConfirm     = doc["pirConfirm"]     | d.pirConfirm;
    settings.pirWindowS     = doc["pirWindowS"]     | d.pirWindowS;
    settings.exitDelayS     = doc["exitDelayS"]     | d.exitDelayS;
    settings.entryDelayS    = doc["entryDelayS"]    | d.entryDelayS;
    settings.alarmDurationS = doc["alarmDurationS"] | d.alarmDurationS;
    settings.buzzerEnabled  = doc["buzzerEnabled"]  | d.buzzerEnabled;
    settings.irToggleCode   = doc["irToggleCode"]   | d.irToggleCode;
  }
  f.close();
}

void settingsSave() {
  JsonDocument doc;
  doc["thresholdCm"]    = settings.thresholdCm;
  doc["confirmCount"]   = settings.confirmCount;
  doc["pirConfirm"]     = settings.pirConfirm;
  doc["pirWindowS"]     = settings.pirWindowS;
  doc["exitDelayS"]     = settings.exitDelayS;
  doc["entryDelayS"]    = settings.entryDelayS;
  doc["alarmDurationS"] = settings.alarmDurationS;
  doc["buzzerEnabled"]  = settings.buzzerEnabled;
  doc["irToggleCode"]   = settings.irToggleCode;
  File f = LittleFS.open(SETTINGS_FILE, "w");
  if (!f) return;
  serializeJson(doc, f);
  f.close();
}
