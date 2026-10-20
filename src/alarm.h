#pragma once
#include <Arduino.h>

enum class AlarmState {
  Off,          // uitgeschakeld
  Arming,       // vertrektijd loopt
  Calibrating,  // basisafstand meten
  Watching,     // bewaken
  TripPending,  // tripwire onderbroken, wachten op PIR-bevestiging
  PreAlarm,     // voorwaarschuwing, nog uit te schakelen
  Alarm,        // alarm loeit
};

void alarmBegin();
// newSample = er is net een nieuwe afstandsmeting
void alarmLoop(bool newSample);

// Veilig aan te roepen vanuit de webserver-taak; uitvoering gebeurt in alarmLoop().
void alarmRequestArm(const char *source);
void alarmRequestDisarm(const char *source);
void alarmRequestToggle(const char *source);
void alarmRequestCalibrate();

AlarmState alarmState();
const char *alarmStateName();
uint32_t alarmSecondsLeft();  // aftelling in de huidige toestand (0 = geen)
float alarmBaseline();        // basisafstand in cm, -1 = geen echo, NAN = nog niet gemeten
