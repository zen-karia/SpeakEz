#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi credentials
const char* ssid = "Ishaan";

const char* password = "14165563809";

// Flask server URL (change IP if needed)
const char* serverURL = "http://192.168.68.107:5000/esp32/predict";

// ADC1-compatible GPIO pins
const int thumb   = 39;  // ADC1_CH3
const int pointer = 34;  // ADC1_CH6
const int middle  = 35;  // ADC1_CH7
const int ring    = 32;  // ADC1_CH4
const int pinky   = 33;  // ADC1_CH5

// Timing variables
unsigned long previousMillis = 0;                                             
const long interval = 500; // 2 times per second (200 ms)

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Read sensor values
    int thumbVal   = analogRead(thumb);
    int pointerVal = analogRead(pointer);
    int middleVal  = analogRead(middle);
    int ringVal    = analogRead(ring);
    int pinkyVal   = analogRead(pinky);

    // Print to Serial (for debugging)
    Serial.print("Sending: ");
    Serial.print(thumbVal); Serial.print(", ");
    Serial.print(pointerVal); Serial.print(", ");
    Serial.print(middleVal); Serial.print(", ");
    Serial.print(ringVal); Serial.print(", ");
    Serial.println(pinkyVal);

    // Send data via HTTP POST
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverURL);
      http.addHeader("Content-Type", "application/json");


           String json = "{";
      json += "\"pinky\":" + String(pinkyVal) + ",";
      json += "\"ring\":" + String(ringVal) + ",";
      json += "\"middle\":" + String(middleVal) + ",";
      json += "\"pointer\":" + String(pointerVal) + ",";
      json += "\"thumb\":" + String(thumbVal);  
      json += "}";
      int httpResponseCode = http.POST(json);

      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Server Response: " + response);
      } else {
        Serial.println("Error sending POST: " + String(httpResponseCode));
      }

      http.end();
    } else {
      Serial.println("WiFi Disconnected");
    }
  }
}
