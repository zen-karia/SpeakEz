#include "MicroTFLite.h"
#include "LittleFS.h"

constexpr int tensorArenaSize = 20 * 1024;
alignas(16) byte tensorArena[tensorArenaSize];

const int thumb   = 39;  
const int pointer = 34; 
const int middle  = 35;  
const int ring    = 32;  
const int pinky   = 33;

float raw [5];
const char letters[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H','I','K', 'L', 'M', 'O', 'Q', 'W', 'Y'}; 

uint8_t *loadedModel;
size_t modelSize;

void loadModel(void);

int runInference(float* flex) {

  int letter = 0;
  float maxConfidence = 0.0;

  for (int i = 0; i < 5; i++) {
    if (!ModelSetInput(flex[i], i)) {
      Serial.println("Failed to set input!");
    }
  }

  if (!ModelRunInference()) {
    Serial.println("inference failed");
    return -1;
  }


  for(int j = 0; j < 16; j++){

    float val = ModelGetOutput(j);
    if (ModelGetOutput(j) > maxConfidence){
      maxConfidence = val;
      letter = j;
    }
  }
  return (letter);
}


void setup() {

  Serial.begin(115200);

  delay(6000);
  Serial.println("setup before");


  if (!LittleFS.begin()){
    Serial.println("Error mounting LittleFs");
    return;
  }
  Serial.println("setup");

  loadModel();


  if (!ModelInit(loadedModel, tensorArena, tensorArenaSize)) {
    Serial.println("Model initialization failed!");
    while (true) {;}
  }

}

void loop() {

  raw[0] = 259.0;
  raw[1] = 0.0;
  raw[2] = 4095.0;
  raw[3] = 1937.0;
  raw[4] = 4095.0;

 int letter = runInference(raw);
  Serial.print("Letter: ");
  Serial.println(letters[letter]);

  delay(2000);

}

void loadModel(){

  Serial.println("In read");
  File file = LittleFS.open("/glove_cnn.tflite", "r");

  if(!file){
    Serial.println("Failed to open file for reading");
    return;
  }

  if (file.size() == 0){
    Serial.println("file size 0");
      file.close();
    return;
  }


  modelSize = file.size();
  Serial.print("Model Size: ");
  Serial.println(modelSize);

  loadedModel = (uint8_t*) malloc(modelSize);
  if (!loadedModel) {
    Serial.println("Failed to allocate memory for model");
      file.close();
    return;
  }
  Serial.println("before byte");
  file.readBytes((char*)loadedModel, modelSize);
  Serial.println("Finished read");

  file.close();
}


 

