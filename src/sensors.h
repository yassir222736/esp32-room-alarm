#pragma once
#include <Arduino.h>

void sensorsBegin();
// Doet om de SONAR_INTERVAL_MS een meting; geeft true terug als er een nieuwe meting is.
bool sensorsLoop();

// Laatste gefilterde afstand in cm, of -1 bij "geen echo".
float sonarDistance();
// Eén losse meting (blokkeert max ~25 ms). -1 = geen echo.
float sonarMeasureOnce();

bool pirActive();
uint32_t pirLastMotionMs();  // millis() van de laatste beweging (0 = nooit)
