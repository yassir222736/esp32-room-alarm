#include "effects.h"
#include "config.h"

static Effect current = Effect::Off;
static uint32_t effectStart = 0;

static constexpr uint8_t CH_R = 0, CH_G = 1, CH_B = 2;

void effectsBegin() {
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_LED_BLUE, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
  ledcSetup(CH_R, 5000, 8);
  ledcSetup(CH_G, 5000, 8);
  ledcSetup(CH_B, 5000, 8);
  ledcAttachPin(PIN_RGB_R, CH_R);
  ledcAttachPin(PIN_RGB_G, CH_G);
  ledcAttachPin(PIN_RGB_B, CH_B);
  effectsSet(Effect::Off);
}

void setRgb(uint8_t r, uint8_t g, uint8_t b) {
  if (RGB_COMMON_ANODE) { r = 255 - r; g = 255 - g; b = 255 - b; }
  ledcWrite(CH_R, r);
  ledcWrite(CH_G, g);
  ledcWrite(CH_B, b);
}

void setBuzzer(bool on) { digitalWrite(PIN_BUZZER, on && settings.buzzerEnabled); }

static void setRedBlue(bool red, bool blue) {
  digitalWrite(PIN_LED_RED, red);
  digitalWrite(PIN_LED_BLUE, blue);
}

// Kleurenwiel: positie 0..255 -> RGB
static void wheel(uint8_t pos) {
  if (pos < 85) setRgb(255 - pos * 3, pos * 3, 0);
  else if (pos < 170) { pos -= 85; setRgb(0, 255 - pos * 3, pos * 3); }
  else { pos -= 170; setRgb(pos * 3, 0, 255 - pos * 3); }
}

void effectsSet(Effect e) {
  current = e;
  effectStart = millis();
  setRedBlue(false, false);
  setRgb(0, 0, 0);
  setBuzzer(false);
}

void effectsLoop() {
  uint32_t t = millis() - effectStart;
  switch (current) {
    case Effect::Off:
      break;

    case Effect::Arming: {
      bool on = (t % 1000) < 150;
      setRedBlue(false, on);
      setRgb(0, 0, on ? 60 : 0);
      break;
    }

    case Effect::Watching: {
      // zacht ademend groen, periode 4 s
      float phase = (t % 4000) / 4000.0f;
      float level = 0.5f - 0.5f * cosf(phase * 2 * PI);
      setRgb(0, (uint8_t)(3 + level * 25), 0);
      break;
    }

    case Effect::PreAlarm: {
      bool half = (t % 1000) < 500;  // 1 Hz om en om
      setRedBlue(half, !half);
      setRgb(255, 80, 0);
      setBuzzer((t % 1000) < 60);    // kort piepje per seconde
      break;
    }

    case Effect::Alarm: {
      // politiepatroon: 3 flitsen rood, 3 flitsen blauw (cyclus 600 ms)
      uint32_t c = t % 600;
      bool redPhase = c < 300;
      bool flash = (c % 100) < 50;
      setRedBlue(redPhase && flash, !redPhase && flash);
      wheel((t / 8) % 256);
      // zoemer: 400 ms aan, 200 ms uit
      setBuzzer((t % 600) < 400);
      break;
    }
  }
}
