#include <WiFi.h>
#include <WebServer.h>
#include "MicroTFLite.h"
#include "LittleFS.h"


const char* ssid = "wifi";
const char* password = "pass";

WebServer server(80);

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

void handleModelUpload() {
  HTTPUpload& upload = server.upload();

  static File uploadFile;

  if (upload.status == UPLOAD_FILE_START) {

    Serial.println("OTA model upload started");
    uploadFile = LittleFS.open("/glove_cnn.tflite", "w");

  }
  else if (upload.status == UPLOAD_FILE_WRITE) {
    if (uploadFile) {
      uploadFile.write(upload.buf, upload.currentSize);
    }
  }

  else if (upload.status == UPLOAD_FILE_END) {
    if (uploadFile) {
      uploadFile.close();
      Serial.println("OTA model upload finished");
      server.send(200, "text/plain", "Model uploaded. Rebooting...");
      delay(1000);
      ESP.restart();
    }
  }
}

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

  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.on(
    "/upload",
    HTTP_POST,
    []() {},
    handleModelUpload
  );
  server.begin();
  Serial.println("OTA server started");

  loadModel();


  if (!ModelInit(loadedModel, tensorArena, tensorArenaSize)) {
    Serial.println("Model initialization failed!");
    while (true) {;}
  }

}

void loop() {

  server.handleClient();

  raw[0] = analogRead(thumb);
  raw[1] = analogRead(pointer);
  raw[2] = analogRead(middle);
  raw[3] = analogRead(ring);
  raw[4] = analogRead(pinky);

 int letter = runInference(raw);
  Serial.print("Letter: ");
  Serial.println(letters[letter]);

  delay(2000);

}

void loadModel(){

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
  
  file.readBytes((char*)loadedModel, modelSize);

  file.close();
}


 

