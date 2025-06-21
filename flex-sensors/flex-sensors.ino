const int sensor1 = 15;
const int sensor2 = 13;
const int sensor3 = 4;
const int sensor4 = 14;
const int sensor5 = 25;
char currentLetter = 'A'; 

void setup() {

  pinMode(5, INPUT);
  Serial.begin(115200);

}

void loop() {
if (digitalRead(BUTTON_PIN) == LOW) {
    delay(50);  // debounce
    unsigned long start = millis();
    while (millis() - start < 2000) { // 2 seconds
      static unsigned long lastSent = 0;
      if (millis() - lastSent >= 50) { // 20Hz
        lastSent = millis();
        Serial.print(analogRead(A0)); Serial.print(",");
        Serial.print(analogRead(A1)); Serial.print(",");
        Serial.print(analogRead(A2)); Serial.print(",");
        Serial.print(analogRead(A3)); Serial.print(",");
        Serial.println(analogRead(A4));
      }
    }

-    Serial.println("DONE");
    delay(300);  -


}
