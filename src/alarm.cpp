#include "alarm.h"
#include "config.h"
#include "effects.h"
#include "logbook.h"
#include "notify.h"
#include "sensors.h"
#include <algorithm>
#include <vector>

static AlarmState state = AlarmState::Off;
static uint32_t stateStartMs = 0;
static uint32_t stateDurationMs = 0;  // 0 = geen aftelling

static float baseline = NAN;
static std::vector<float> calSamples;
static AlarmState afterCalibration = AlarmState::Watching;

static uint8_t breakStreak = 0;
static uint32_t tripMs = 0;
static float tripDistance = 0;

// Verzoeken vanuit andere taken (webserver)
enum class Request : uint8_t { None, Arm, Disarm, Toggle, Calibrate };
static volatile Request pending = Request::None;
static const char *volatile pendingSource = "";

static void enter(AlarmState s, uint32_t durationS = 0) {
  state = s;
  stateStartMs = millis();
  stateDurationMs = durationS * 1000UL;
  breakStreak = 0;
  switch (s) {
    case AlarmState::Off:         effectsSet(Effect::Off); break;
    case AlarmState::Arming:      effectsSet(Effect::Arming); break;
    case AlarmState::Calibrating: break;  // effect blijft zoals het was
    case AlarmState::Watching:    effectsSet(Effect::Watching); break;
    case AlarmState::TripPending: break;
    case AlarmState::PreAlarm:    effectsSet(Effect::PreAlarm); break;
    case AlarmState::Alarm:       effectsSet(Effect::Alarm); break;
  }
  Serial.printf("[alarm] -> %s\n", alarmStateName());
}

static bool timeUp() { return stateDurationMs && millis() - stateStartMs >= stateDurationMs; }

static void startCalibration(AlarmState then) {
  calSamples.clear();
  afterCalibration = then;
  enter(AlarmState::Calibrating);
}

static void finishCalibration() {
  int noEcho = std::count_if(calSamples.begin(), calSamples.end(), [](float v) { return v < 0; });
  std::vector<float> valid;
  for (float v : calSamples) if (v > 0) valid.push_back(v);
  if (noEcho > (int)calSamples.size() / 2 || valid.empty()) {
    baseline = -1;
  } else {
    std::sort(valid.begin(), valid.end());
    baseline = valid[valid.size() / 2];
  }
  Serial.printf("[alarm] basisafstand: %.1f cm (%d x geen echo)\n", baseline, noEcho);
  enter(afterCalibration);
}

static bool beamBroken(float d) {
  if (isnan(baseline)) return false;
  if (baseline < 0) return d > 0;  // er verschijnt plots iets in een "lege" straal
  if (d < 0) return true;          // echo verdwenen (bv. deur onder een hoek)
  return fabsf(d - baseline) > settings.thresholdCm;
}

static String distanceText(float d) {
  return d < 0 ? String("geen echo") : String(d, 0) + " cm";
}

static void startPreAlarm() {
  String detail = "afstand " + distanceText(tripDistance) + " (basis " + distanceText(baseline) + ")";
  if (settings.pirConfirm) detail += ", PIR bevestigd";
  logbookAdd(LogType::Entry, detail);
  enter(AlarmState::PreAlarm, settings.entryDelayS);
}

static void disarm(const char *source) {
  if (state == AlarmState::Off) return;
  bool wasAlarming = state == AlarmState::PreAlarm || state == AlarmState::Alarm;
  logbookAdd(LogType::Disarmed, String("via ") + source);
  if (wasAlarming) notifySend("Kameralarm uitgeschakeld", String("Uitgeschakeld via ") + source, false);
  enter(AlarmState::Off);
}

static void arm(const char *source) {
  if (state != AlarmState::Off) return;
  logbookAdd(LogType::Armed, String("via ") + source);
  enter(AlarmState::Arming, settings.exitDelayS);
}

static void handleRequest() {
  Request r = pending;
  if (r == Request::None) return;
  pending = Request::None;
  const char *src = pendingSource;
  switch (r) {
    case Request::Arm: arm(src); break;
    case Request::Disarm: disarm(src); break;
    case Request::Toggle: state == AlarmState::Off ? arm(src) : disarm(src); break;
    case Request::Calibrate:
      if (state == AlarmState::Off || state == AlarmState::Watching) startCalibration(state);
      break;
    default: break;
  }
}

void alarmBegin() { enter(AlarmState::Off); }

void alarmLoop(bool newSample) {
  handleRequest();
  float d = sonarDistance();

  switch (state) {
    case AlarmState::Off:
      break;

    case AlarmState::Arming:
      if (timeUp()) startCalibration(AlarmState::Watching);
      break;

    case AlarmState::Calibrating:
      if (newSample) calSamples.push_back(d);
      if ((int)calSamples.size() >= CALIBRATION_SAMPLES) finishCalibration();
      break;

    case AlarmState::Watching:
      if (!newSample) break;
      breakStreak = beamBroken(d) ? breakStreak + 1 : 0;
      if (breakStreak >= settings.confirmCount) {
        tripMs = millis();
        tripDistance = d;
        uint32_t lastPir = pirLastMotionMs();
        bool pirRecent = lastPir > stateStartMs && tripMs - lastPir <= settings.pirWindowS * 1000UL;
        if (!settings.pirConfirm || pirRecent) startPreAlarm();
        else enter(AlarmState::TripPending, settings.pirWindowS);
      }
      break;

    case AlarmState::TripPending:
      if (pirLastMotionMs() >= tripMs) {
        startPreAlarm();
      } else if (timeUp()) {
        logbookAdd(LogType::NoPir, "afstand " + distanceText(tripDistance) + " – opnieuw gekalibreerd");
        startCalibration(AlarmState::Watching);
      }
      break;

    case AlarmState::PreAlarm:
      if (timeUp()) {
        logbookAdd(LogType::Alarm);
        char when[16] = "onbekend uur";
        time_t now = time(nullptr);
        if (now > 1700000000) strftime(when, sizeof(when), "%H:%M:%S", localtime(&now));
        notifySend("ALARM in je kamer!", String("Iemand kwam binnen om ") + when + ". Tik om de pagina te openen.", true);
        enter(AlarmState::Alarm, settings.alarmDurationS);
      }
      break;

    case AlarmState::Alarm:
      if (timeUp()) {
        logbookAdd(LogType::AlarmEnd, "na " + String(settings.alarmDurationS) + " s, bewaakt verder");
        effectsSet(Effect::Watching);
        startCalibration(AlarmState::Watching);  // nieuwe basis (deur staat misschien open)
      }
      break;
  }
}

void alarmRequestArm(const char *source) { pendingSource = source; pending = Request::Arm; }
void alarmRequestDisarm(const char *source) { pendingSource = source; pending = Request::Disarm; }
void alarmRequestToggle(const char *source) { pendingSource = source; pending = Request::Toggle; }
void alarmRequestCalibrate() { pending = Request::Calibrate; }

AlarmState alarmState() { return state; }

const char *alarmStateName() {
  switch (state) {
    case AlarmState::Off:         return "uit";
    case AlarmState::Arming:      return "inschakelen";
    case AlarmState::Calibrating: return "kalibreren";
    case AlarmState::Watching:    return "bewaken";
    case AlarmState::TripPending: return "controle";
    case AlarmState::PreAlarm:    return "vooralarm";
    case AlarmState::Alarm:       return "alarm";
  }
  return "?";
}

uint32_t alarmSecondsLeft() {
  if (!stateDurationMs) return 0;
  uint32_t elapsed = millis() - stateStartMs;
  return elapsed >= stateDurationMs ? 0 : (stateDurationMs - elapsed + 999) / 1000;
}

float alarmBaseline() { return baseline; }
