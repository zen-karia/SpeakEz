int sensor1;
int sensor2;
int sensor3;
int sensor4;
int sensor5;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly:

  sensor1 = analogRead(4);
  sensor2 = analogRead(2);
  // sensor3 = analogRead(4);
  // sensor4 = analogRead(4);
  // sensor5 = analogRead(4);

  Serial.print("1: ");
  Serial.print(sensor1);
  Serial.print(" || 2: ");
  Serial.println(sensor2);
// + " || 3: " + sensor3 + " || 4: " + sensor4 + " || 5: " + sensor5


}
