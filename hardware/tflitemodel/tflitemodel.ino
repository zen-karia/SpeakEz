#include "glove_cnn.h"
#include "MicroTFLite.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1331.h>
#include <SPI.h>

#define sclk 18
#define mosi 23
#define cs   17
#define rst  5
#define dc   16

#define	GREEN           0x07E0
#define WHITE           0xFFFF

Adafruit_SSD1331 display = Adafruit_SSD1331(&SPI, cs, dc, rst);

constexpr int tensorArenaSize = 60 * 1024;
alignas(16) byte tensorArena[tensorArenaSize];

const int thumb   = 39;  
const int pointer = 34; 
const int middle  = 35;  
const int ring    = 32;  
const int pinky   = 33;

float raw [5];
const char letters[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H','I','K', 'L', 'M', 'O', 'Q', 'W', 'Y'}; 

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

  delay(1000);

  display.begin();

  if (!ModelInit(glove_cnn_int8_tflite, tensorArena, tensorArenaSize)) {
    Serial.println("Model initialization failed!");
    while (true) {;}
  }

}

void loop() {

  raw[0] = analogRead(thumb);
  raw[1] = analogRead(pointer);
  raw[2] = analogRead(middle);
  raw[3] = analogRead(ring);
  raw[4] = analogRead(pinky);

  
  int letter = runInference(raw);

  Serial.print("Letter: ");
  Serial.println(letters[letter]);

  display.fillScreen(WHITE);

  display.setTextColor(GREEN);
  display.setTextSize(1);
  display.setCursor(6, 15);
  display.print(letters[letter]);

  delay(2000);

}


 

