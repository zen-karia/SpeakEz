const int sensor1 = 15;
const int sensor2 = 13;
const int sensor3 = 4;
const int sensor4 = 14;
const int sensor5 = 25;

void setup() {
  // put your setup code here, to run once:
  pinMode(5, INPUT);
  Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly:


  if (digitalRead(5) == LOW){
  unsigned long start = millis();

    while (millis() - start <= 2000){

      Serial.print("1: ");
      Serial.print(analogRead(sensor1));
      Serial.print(" || 2: ");
      Serial.print(analogRead(sensor2));
      Serial.print(" || 3: ");
      Serial.print(analogRead(sensor3));
      Serial.print(" || 4: ");
      Serial.print(analogRead(sensor4));
      Serial.print(" || 5: ");
      Serial.print(analogRead(sensor5));
      delay (50);
    }
      Serial.println("Done");

  }





}
