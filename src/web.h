#pragma once
#include <Arduino.h>

void webBegin();
// Stuurt periodiek de live status naar alle open webpagina's.
void webLoop();
String statusJson();
