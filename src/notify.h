#pragma once
#include <Arduino.h>

// Stuurt een pushmelding naar de ntfy-app op je gsm (op de achtergrond, blokkeert niet).
void notifySend(const String &title, const String &message, bool urgent);
