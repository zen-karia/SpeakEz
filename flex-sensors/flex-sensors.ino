const int thumb = 15;
const int pointer = 13;
const int middle = 4;
const int ring = 14;
const int pinky = 25;
char currentLetter = 'A'; 

void setup() {

  pinMode(5, INPUT);
  Serial.begin(115200);

}

void loop() {

  if (digitalRead(5) == LOW) {
    delay(50);  // debounce
    unsigned long start = millis();
    while (millis() - start < 2000) { // 2 seconds
      static unsigned long lastSent = 0;
      if (millis() - lastSent >= 50) { // 20Hz
        lastSent = millis();
        Serial.print(analogRead(thumb)); Serial.print(",");
        Serial.print(analogRead(pointer)); Serial.print(",");
        Serial.print(analogRead(middle)); Serial.print(",");
        Serial.print(analogRead(ring)); Serial.print(",");
        Serial.println(analogRead(pinky));
      }
    }

    Serial.println("DONE");
    delay(300);  
  }

}
