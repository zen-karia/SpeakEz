#include "glove_cnn.h"
#include "MicroTFLite.h"


constexpr int tensorArenaSize = 60 * 1024;
alignas(16) byte tensorArena[tensorArenaSize];

const int thumb   = 39;  
const int pointer = 34; 
const int middle  = 35;  
const int ring    = 32;  
const int pinky   = 33;

uint8_t flex [5];
float raw [5];

void runInference(uint8_t* flex) {

    for (int i = 0; i < 5; i++) {
       Serial.println("in input");
    if (!ModelSetInput(flex[i], i)) {
      Serial.println("Failed to set input!");
    }
    }

    if (!ModelRunInference()) {
      Serial.println("inference failed");
        return;
    }


  for(int i = 0; i < 16; i++){
    Serial.print("Output "); Serial.print(i); Serial.print(": ");
    Serial.println(ModelGetOutput(i));
  }

}



void setup() {

  Serial.begin(115200);

  delay(1000);

  if (!ModelInit(glove_cnn_int8_tflite, tensorArena, tensorArenaSize)) {
    Serial.println("Model initialization failed!");
    while (true) {;}
  }

}

void loop() {

  // raw[0] = analogRead(thumb);
  // raw[1] = analogRead(pointer);
  // raw[2] = analogRead(middle);
  // raw[3] = analogRead(ring);
  // raw[4] = analogRead(pinky);
  raw[0] = 0;
  raw[1] = 0;
  raw[2] = 0;
  raw[3] = 0;
  raw[4] = 0;

  for (int i = 0; i < 5; i++){
    float norm = map(raw[i], 0, 4095, 0, 255);
    flex[i] = static_cast<int8_t>(norm);
    Serial.print("flex: ");
    Serial.println(flex[i]);
  }
  runInference(flex);
  Serial.println("done!");
  delay(10000);

}


 

