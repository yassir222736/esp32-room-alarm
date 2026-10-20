#include "sensors.h"
#include "config.h"

static float history[3] = {-1, -1, -1};
static uint8_t histIdx = 0;
static float filtered = -1;
static uint32_t lastSonarMs = 0;
static uint32_t lastPirMs = 0;

void sensorsBegin() {
  pinMode(PIN_SONAR_TRIG, OUTPUT);
  digitalWrite(PIN_SONAR_TRIG, LOW);
  pinMode(PIN_SONAR_ECHO, INPUT);
  pinMode(PIN_PIR, INPUT);
}

float sonarMeasureOnce() {
  digitalWrite(PIN_SONAR_TRIG, LOW);
  delayMicroseconds(3);
  digitalWrite(PIN_SONAR_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_SONAR_TRIG, LOW);
  unsigned long us = pulseIn(PIN_SONAR_ECHO, HIGH, SONAR_TIMEOUT_US);
  if (us == 0) return -1;
  float cm = us / 58.0f;
  if (cm < 2 || cm > SONAR_MAX_CM) return -1;
  return cm;
}

// Mediaan van 3: één uitschieter wordt genegeerd. "Geen echo" (-1) telt als grootste waarde.
static float median3(float a, float b, float c) {
  auto key = [](float v) { return v < 0 ? 1e9f : v; };
  float x = key(a), y = key(b), z = key(c);
  float m = max(min(x, y), min(max(x, y), z));
  return m >= 1e9f ? -1 : m;
}

bool sensorsLoop() {
  if (digitalRead(PIN_PIR)) lastPirMs = millis();

  if (millis() - lastSonarMs < SONAR_INTERVAL_MS) return false;
  lastSonarMs = millis();
  history[histIdx] = sonarMeasureOnce();
  histIdx = (histIdx + 1) % 3;
  filtered = median3(history[0], history[1], history[2]);
  return true;
}

float sonarDistance() { return filtered; }
bool pirActive() { return digitalRead(PIN_PIR); }
uint32_t pirLastMotionMs() { return lastPirMs; }
