#pragma once
#include <Arduino.h>

void irBegin();
// Geeft true terug als de aan/uit-knop van de afstandsbediening is ingedrukt.
bool irLoop();
// Volgende ingedrukte knop wordt de nieuwe aan/uit-knop.
void irStartLearning();
bool irIsLearning();
// Testmodus: druk elke ontvangen code af.
void irSetVerbose(bool on);
