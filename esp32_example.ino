/*
 * ESP32 Arduino Code for SpeakEz ASL Recognition
 * Sends flex sensor data to Flask backend for CNN prediction
 * 
 * Hardware: ESP32 with 5 flex sensors connected to analog pins
 * Data Format: JSON with 5 sensor values
 * Frequency: 1 per second
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "SPUR";
const char* password = "Collaborate!";

// Flask Backend Configuration
const char* serverUrl = "http://10.200.14.43:5000/esp32/predict";  // Update with your computer's IP
const int serverPort = 5000;

// Pin Configuration
const int FLEX_SENSORS[] = {A0, A1, A2, A3, A4};  // Flex sensor pins
const int NUM_SENSORS = 5;

// Timing
const unsigned long SEND_INTERVAL = 1000;  // Send data every 1 second
unsigned long lastSendTime = 0;

// HTTP client
HTTPClient http;

void setup() {
  Serial.begin(115200);
  
  // Initialize sensors
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(FLEX_SENSORS[i], INPUT);
  }
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("ESP32 ready to send sensor data!");
}

void loop() {
  // Send data at regular intervals
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    sendSensorData();
    lastSendTime = millis();
  }
}

void sendSensorData() {
  // Read sensor values
  int sensorValues[NUM_SENSORS];
  for (int i = 0; i < NUM_SENSORS; i++) {
    sensorValues[i] = analogRead(FLEX_SENSORS[i]);
  }
  
  // Create JSON data
  StaticJsonDocument<512> doc;
  
  // Add sensor data
  JsonArray sensors = doc.createNestedArray("sensor_values");
  for (int i = 0; i < NUM_SENSORS; i++) {
    sensors.add(sensorValues[i]);
  }
  
  // Add timestamp
  doc["timestamp"] = millis();
  
  // Convert to string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send HTTP POST request
  if (WiFi.status() == WL_CONNECTED) {
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
      
      // Parse response to get prediction
      parsePredictionResponse(response);
    } else {
      Serial.println("Error on sending POST: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
  
  // Debug output
  Serial.println("Sent: " + jsonString);
  Serial.println("Sensor values: [" + 
    String(sensorValues[0]) + ", " + 
    String(sensorValues[1]) + ", " + 
    String(sensorValues[2]) + ", " + 
    String(sensorValues[3]) + ", " + 
    String(sensorValues[4]) + "]");
}

void parsePredictionResponse(String response) {
  // Parse the JSON response from Flask backend
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, response);
  
  if (error) {
    Serial.println("Failed to parse response JSON");
    return;
  }
  
  // Extract prediction data
  if (doc["detected"] == true) {
    const char* prediction = doc["prediction"];
    float confidence = doc["confidence"];
    const char* audioFile = doc["audio_file"];
    
    Serial.println("=== PREDICTION ===");
    Serial.println("Letter: " + String(prediction));
    Serial.println("Confidence: " + String(confidence));
    Serial.println("Audio File: " + String(audioFile));
    Serial.println("==================");
  } else {
    Serial.println("No letter detected");
  }
}

// Function to test the connection
void testConnection() {
  Serial.println("Testing connection to Flask backend...");
  
  if (WiFi.status() == WL_CONNECTED) {
    http.begin("http://<your-ip>:5000/esp32/status");  // Update IP
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Status Response: " + response);
    } else {
      Serial.println("Error getting status: " + String(httpResponseCode));
    }
    
    http.end();
  }
}

// Function to calibrate sensors
void calibrateSensors() {
  Serial.println("Calibration mode - move your fingers and observe values:");
  
  for (int i = 0; i < 10; i++) {
    Serial.print("Reading ");
    Serial.print(i + 1);
    Serial.print("/10: ");
    
    for (int j = 0; j < NUM_SENSORS; j++) {
      int value = analogRead(FLEX_SENSORS[j]);
      Serial.print("S");
      Serial.print(j);
      Serial.print(":");
      Serial.print(value);
      Serial.print(" ");
    }
    Serial.println();
    delay(1000);
  }
  
  Serial.println("Calibration complete!");
} 