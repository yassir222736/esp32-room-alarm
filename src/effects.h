#pragma once
#include <Arduino.h>

enum class Effect {
  Off,        // alles uit
  Arming,     // blauw knippert traag (vertrektijd)
  Watching,   // RGB groen "ademt" zacht
  PreAlarm,   // rood/blauw rustig om en om, RGB oranje, kort piepje per seconde
  Alarm,      // politie: snel rood/blauw, RGB kleurenwiel, zoemer
};

void effectsBegin();
void effectsSet(Effect e);
void effectsLoop();

// Rechtstreekse aansturing (voor de testmodus)
void setRgb(uint8_t r, uint8_t g, uint8_t b);
void setBuzzer(bool on);
