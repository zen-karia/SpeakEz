#include "glove_cnn.h"
#include "MicroTFLite.h"


constexpr int tensorArenaSize = 60 * 1024;
alignas(16) byte tensorArena[tensorArenaSize];

const int thumb   = 39;  
const int pointer = 34; 
const int middle  = 35;  
const int ring    = 32;  
const int pinky   = 33;

float raw [5];
const char letters[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H','I','K', 'L', 'M', 'O', 'Q', 'W', 'Y'}; 
int letter;
float maxConfidence = 0.0;

int runInference(float* flex) {

    for (int i = 0; i < 5; i++) {
    if (!ModelSetInput(flex[i], i)) {
      Serial.println("Failed to set input!");
    }
    }

    if (!ModelRunInference()) {
      Serial.println("inference failed");
        return -1;
    }


  for(int i = 0; i < 16; i++){

    float val = ModelGetOutput(i);
    if (ModelGetOutput(i) > maxConfidence){
      maxConfidence = val;
      letter = i;
    }
  }
  return (letter);
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
  raw[0] = 9.0;
  raw[1] = 81.0;
  raw[2] = 64.0;
  raw[3] = 6.0;
  raw[4] = 0.0;

  letter = runInference(raw);

  Serial.print("Letter: ");
  Serial.println(letters[letter]);

  delay(10000);

}


 

