// Kameralarm – ELEGOO ESP32 starterset
// Ultrasone "tripwire" + PIR-bevestiging, politieleds, webpagina met eigen mp3,
// logboek en gsm-meldingen via ntfy.

#include "alarm.h"
#include "config.h"
#include "effects.h"
#include "ir.h"
#include "logbook.h"
#include "secrets.h"
#include "sensors.h"
#include "web.h"
#include <ESPmDNS.h>
#include <LittleFS.h>
#include <WiFi.h>

// ===== Wi-Fi =====
static void wifiBegin() {
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(HOSTNAME);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.printf("Verbinden met Wi-Fi \"%s\"", WIFI_SSID);
  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print('.');
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    WiFi.setAutoReconnect(true);
    Serial.printf("Verbonden! Open http://%s/ of http://%s.local/\n",
                  WiFi.localIP().toString().c_str(), HOSTNAME);
  } else {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD);
    Serial.printf("Geen Wi-Fi. Eigen netwerk \"%s\" gestart, open http://%s/\n",
                  AP_SSID, WiFi.softAPIP().toString().c_str());
  }
  MDNS.begin(HOSTNAME);
  MDNS.addService("http", "tcp", 80);
  configTzTime(TZ_BRUSSELS, "be.pool.ntp.org", "pool.ntp.org");
}

// ===== Testmodus via de seriële monitor =====
static bool stopRequested() {
  if (!Serial.available()) return false;
  while (Serial.available()) Serial.read();
  return true;
}

static void printHelp() {
  Serial.println(F(
      "\n=== Kameralarm – commando's (typ en druk Enter) ===\n"
      "  help         dit overzicht\n"
      "  status       huidige toestand\n"
      "  arm / disarm alarm aan / uit\n"
      "  cal          basisafstand opnieuw meten\n"
      "  --- testen (alarm moet uit staan, Enter = stoppen) ---\n"
      "  t sonar      afstand live tonen\n"
      "  t pir        bewegingssensor live tonen\n"
      "  t ir         codes van de afstandsbediening tonen\n"
      "  t leds       rode en blauwe led\n"
      "  t rgb        RGB-led: rood, groen, blauw, kleurenwiel\n"
      "  t buzzer     zoemer\n"
      "  t alarm      alarmeffect 5 seconden\n"));
}

static void testSonar() {
  Serial.println("Afstand (Enter = stop):");
  while (!stopRequested()) {
    float d = sonarMeasureOnce();
    if (d < 0) Serial.println("  geen echo");
    else Serial.printf("  %.1f cm\n", d);
    delay(200);
  }
}

static void testPir() {
  Serial.println("PIR (opwarmen duurt ~60 s na inschakelen). Enter = stop:");
  int last = -1;
  while (!stopRequested()) {
    int v = digitalRead(PIN_PIR);
    if (v != last) Serial.println(v ? "  BEWEGING" : "  rust");
    last = v;
    delay(50);
  }
}

static void testIr() {
  Serial.println("Druk op knoppen van de afstandsbediening. Enter = stop:");
  irSetVerbose(true);
  while (!stopRequested()) { irLoop(); delay(10); }
  irSetVerbose(false);
}

// Ruwe meting van de IR-pin: niveau in rust en aantal wisselingen per seconde.
static void testIrPin() {
  Serial.println("IR-pin (D35) ruw. Enter = stop:");
  while (!stopRequested()) {
    int edges = 0, last = digitalRead(PIN_IR_RECV), highs = 0, samples = 0;
    uint32_t s = millis();
    while (millis() - s < 1000) {
      int v = digitalRead(PIN_IR_RECV);
      if (v != last) edges++;
      last = v;
      highs += v;
      samples++;
      delayMicroseconds(20);
    }
    Serial.printf("  rust-niveau %s (%d%% hoog), %d wisselingen\n",
                  highs * 2 > samples ? "HOOG" : "LAAG", highs * 100 / samples, edges);
  }
}

static void testLeds() {
  Serial.println("Rood en blauw om en om. Enter = stop");
  bool r = true;
  while (!stopRequested()) {
    digitalWrite(PIN_LED_RED, r);
    digitalWrite(PIN_LED_BLUE, !r);
    r = !r;
    delay(400);
  }
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_LED_BLUE, LOW);
}

static void testRgb() {
  Serial.println("RGB: rood, groen, blauw (elk 1 s), daarna kleurenwiel. Enter = stop");
  setRgb(255, 0, 0); delay(1000);
  setRgb(0, 255, 0); delay(1000);
  setRgb(0, 0, 255); delay(1000);
  effectsSet(Effect::Alarm);
  bool buzz = settings.buzzerEnabled;
  settings.buzzerEnabled = false;
  while (!stopRequested()) { effectsLoop(); delay(5); }
  settings.buzzerEnabled = buzz;
  effectsSet(Effect::Off);
}

static void testBuzzer() {
  Serial.println("Zoemer: 3 piepjes");
  bool buzz = settings.buzzerEnabled;
  settings.buzzerEnabled = true;
  for (int i = 0; i < 3; i++) { setBuzzer(true); delay(200); setBuzzer(false); delay(300); }
  settings.buzzerEnabled = buzz;
}

static void testAlarm() {
  Serial.println("Alarmeffect 5 s");
  effectsSet(Effect::Alarm);
  uint32_t s = millis();
  while (millis() - s < 5000) { effectsLoop(); delay(5); }
  effectsSet(Effect::Off);
}

static void handleSerial() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  cmd.toLowerCase();
  if (cmd.isEmpty()) return;

  bool isTest = cmd.startsWith("t ");
  if (isTest && alarmState() != AlarmState::Off) {
    Serial.println("Zet eerst het alarm uit (disarm).");
    return;
  }

  if (cmd == "help") printHelp();
  else if (cmd == "status") Serial.println(statusJson());
  else if (cmd == "arm") alarmRequestArm("seriële monitor");
  else if (cmd == "disarm") alarmRequestDisarm("seriële monitor");
  else if (cmd == "cal") alarmRequestCalibrate();
  else if (cmd == "t sonar") testSonar();
  else if (cmd == "t pir") testPir();
  else if (cmd == "t ir") testIr();
  else if (cmd == "t irpin") testIrPin();
  else if (cmd == "t leds") testLeds();
  else if (cmd == "t rgb") testRgb();
  else if (cmd == "t buzzer") testBuzzer();
  else if (cmd == "t alarm") testAlarm();
  else Serial.println("Onbekend commando, typ 'help'.");
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println("\n\n=== Kameralarm start ===");

  if (!LittleFS.begin(true)) Serial.println("LittleFS kon niet starten!");
  settingsLoad();
  effectsBegin();
  sensorsBegin();
  irBegin();
  logbookBegin();
  alarmBegin();

  // korte opstartgroet: rood, blauw, groen
  digitalWrite(PIN_LED_RED, HIGH); delay(150); digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_LED_BLUE, HIGH); delay(150); digitalWrite(PIN_LED_BLUE, LOW);
  setRgb(0, 80, 0); delay(150); setRgb(0, 0, 0);

  wifiBegin();
  webBegin();
  // even wachten op de juiste tijd, zodat ook de opstart een tijdstip krijgt in het logboek
  for (int i = 0; i < 50 && WiFi.status() == WL_CONNECTED && time(nullptr) < 1700000000; i++) delay(100);
  logbookAdd(LogType::Boot);
  printHelp();
}

void loop() {
  bool newSample = sensorsLoop();
  if (irLoop()) alarmRequestToggle("afstandsbediening");
  alarmLoop(newSample);
  effectsLoop();
  webLoop();
  handleSerial();
  delay(2);
}
