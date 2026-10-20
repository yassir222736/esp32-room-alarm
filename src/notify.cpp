#include "notify.h"
#include "secrets.h"
#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>

struct NotifyJob {
  String title;
  String message;
  bool urgent;
};

static void notifyTask(void *arg) {
  NotifyJob *job = static_cast<NotifyJob *>(arg);
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure();  // geen certificaat bundelen; inhoud is niet geheim
    HTTPClient http;
    if (http.begin(client, "https://ntfy.sh/" NTFY_TOPIC)) {
      http.addHeader("Title", job->title);
      http.addHeader("Priority", job->urgent ? "urgent" : "default");
      http.addHeader("Tags", job->urgent ? "rotating_light" : "information_source");
      http.addHeader("Click", "http://" + WiFi.localIP().toString() + "/");
      int code = http.POST(job->message);
      Serial.printf("[ntfy] melding verstuurd, HTTP %d\n", code);
      http.end();
    }
  } else {
    Serial.println("[ntfy] geen Wi-Fi, melding niet verstuurd");
  }
  delete job;
  vTaskDelete(nullptr);
}

void notifySend(const String &title, const String &message, bool urgent) {
  auto *job = new NotifyJob{title, message, urgent};
  xTaskCreate(notifyTask, "ntfy", 8192, job, 1, nullptr);
}
