#pragma once
#include <Arduino.h>

// Soorten gebeurtenissen in het logboek
namespace LogType {
constexpr const char *Boot      = "opstart";
constexpr const char *Armed     = "ingeschakeld";
constexpr const char *Disarmed  = "uitgeschakeld";
constexpr const char *Entry     = "binnenkomst";       // tripwire (+PIR) -> vooralarm
constexpr const char *Alarm     = "alarm";
constexpr const char *NoPir     = "tripwire zonder PIR";
constexpr const char *AlarmEnd  = "alarm gestopt";
}

void logbookBegin();
void logbookAdd(const char *type, const String &detail = "");
uint32_t logbookEntryCount();  // totaal aantal binnenkomsten
String logbookJson();
void logbookClear();
