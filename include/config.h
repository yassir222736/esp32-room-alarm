#pragma once
#include <Arduino.h>

// ===== Pinnen (zie docs/bedrading.md) =====
constexpr uint8_t PIN_SONAR_TRIG = 26;
constexpr uint8_t PIN_SONAR_ECHO = 27;  // via spanningsdeler 1k/2k!
constexpr uint8_t PIN_PIR        = 34;  // input-only pin
constexpr uint8_t PIN_IR_RECV    = 35;  // input-only pin; IR-module op 5V via 1k in serie (GEEN pulldown: zwakke uitgang)
constexpr uint8_t PIN_LED_RED    = 25;
constexpr uint8_t PIN_LED_BLUE   = 33;
// Alle pinnen zitten in de rechterrij van het 30-pins bord (VIN … EN),
// want de linkerrij heeft op het breadboard geen vrij gaatje.
constexpr uint8_t PIN_RGB_R      = 13;
constexpr uint8_t PIN_RGB_G      = 14;
constexpr uint8_t PIN_RGB_B      = 32;
constexpr uint8_t PIN_BUZZER     = 12;  // via PN2222-transistor (GPIO12 moet laag zijn bij opstart: ok via 1k + B-E)

// Zet op true als de RGB-led een gemeenschappelijke ANODE heeft (lange poot naar 3V3).
constexpr bool RGB_COMMON_ANODE = false;

// ===== Ultrasone sensor =====
constexpr uint32_t SONAR_INTERVAL_MS = 50;     // 20 metingen per seconde
constexpr uint32_t SONAR_TIMEOUT_US  = 25000;  // ~4 m; daarna "geen echo"
constexpr float    SONAR_MAX_CM      = 400.0f;
constexpr int      CALIBRATION_SAMPLES = 30;

// ===== Standaardinstellingen (aanpasbaar via de webpagina) =====
struct Settings {
  uint16_t thresholdCm   = 20;   // afwijking van de basisafstand
  uint8_t  confirmCount  = 2;    // aantal metingen op rij
  bool     pirConfirm    = true; // PIR moet de tripwire bevestigen
  uint16_t pirWindowS    = 10;   // tijdvenster tripwire <-> PIR
  uint16_t exitDelayS    = 30;   // tijd om de kamer te verlaten
  uint16_t entryDelayS   = 10;   // vooralarm (tijd om uit te schakelen)
  uint16_t alarmDurationS = 180; // hoe lang het alarm loeit
  bool     buzzerEnabled = true;
  uint64_t irToggleCode  = 0xFFA25D; // POWER-knop ELEGOO-afstandsbediening (NEC)
};

extern Settings settings;
void settingsLoad();
void settingsSave();

constexpr const char *HOSTNAME = "kameralarm";
constexpr const char *TZ_BRUSSELS = "CET-1CEST,M3.5.0,M10.5.0/3";
