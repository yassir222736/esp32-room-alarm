#pragma once
// ===== Persoonlijke instellingen – NIET delen =====

// Wi-Fi (alleen 2,4 GHz netwerken werken met de ESP32)
#define WIFI_SSID     "VUL_HIER_JE_WIFI_NAAM_IN"
#define WIFI_PASSWORD "VUL_HIER_JE_WIFI_WACHTWOORD_IN"

// Lukt Wi-Fi niet, dan maakt de ESP32 zijn eigen netwerk:
#define AP_SSID       "Kameralarm"
#define AP_PASSWORD   "VERANDER-MIJ-123"   // minstens 8 tekens, kies een eigen wachtwoord

// Pincode om het alarm via de webpagina te bedienen
#define WEB_PIN       "1234"

// Gsm-melding via de gratis ntfy-app (https://ntfy.sh)
// Abonneer je in de app op exact deze naam. Hou ze geheim: wie de naam kent, ziet je meldingen.
#define NTFY_TOPIC    "kameralarm-VERANDER-MIJ"
