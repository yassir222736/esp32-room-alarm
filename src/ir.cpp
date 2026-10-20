#include "ir.h"
#include "config.h"
#include <IRrecv.h>
#include <IRutils.h>

static IRrecv irrecv(PIN_IR_RECV);
static decode_results results;
static volatile bool learning = false;
static bool verbose = false;
static uint32_t lastToggleMs = 0;

void irBegin() { irrecv.enableIRIn(); }
void irStartLearning() { learning = true; }
bool irIsLearning() { return learning; }
void irSetVerbose(bool on) { verbose = on; }

bool irLoop() {
  if (!irrecv.decode(&results)) return false;
  bool toggle = false;
  uint64_t code = results.value;
  bool isRepeat = results.repeat || code == kRepeat;

  if (verbose && !isRepeat) {
    Serial.printf("[ir] %s code 0x%llX\n", typeToString(results.decode_type).c_str(), code);
  }

  if (!isRepeat && results.decode_type != UNKNOWN) {
    if (learning) {
      settings.irToggleCode = code;
      settingsSave();
      learning = false;
      Serial.printf("[ir] nieuwe aan/uit-knop opgeslagen: 0x%llX\n", code);
    } else if (code == settings.irToggleCode && millis() - lastToggleMs > 1500) {
      lastToggleMs = millis();
      toggle = true;
    }
  }
  irrecv.resume();
  return toggle;
}
