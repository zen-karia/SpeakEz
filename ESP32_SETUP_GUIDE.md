# ESP32 Integration Setup Guide for SpeakEz

This guide will help you integrate your ESP32 glove with the SpeakEz Flask backend for real-time ASL letter recognition with audio output.

## 🎯 **System Overview**

```
ESP32 → HTTP POST → Flask Backend → CNN Model → Letter → Audio File → Frontend
```

**Data Flow:**
- ESP32 sends 5 sensor values every 1 second
- Flask backend processes data with CNN model
- Returns letter prediction and audio file path
- Frontend plays corresponding audio file

## 🔧 **Hardware Requirements**

### ESP32 Setup
- **ESP32 Development Board**
- **5 Flex Sensors** (one for each finger)
- **5 x 10kΩ Resistors** (for voltage dividers)
- **Breadboard and Wires**

### Connections
```
Flex Sensor 1 (Thumb)   → A0
Flex Sensor 2 (Index)   → A1  
Flex Sensor 3 (Middle)  → A2
Flex Sensor 4 (Ring)    → A3
Flex Sensor 5 (Pinky)   → A4

Each flex sensor needs a voltage divider:
VCC → Flex Sensor → ESP32 Pin
     ↓
   10kΩ Resistor → GND
```

## 📋 **Step-by-Step Setup**

### 1. Install Arduino Libraries

In Arduino IDE, install these libraries:
- **ArduinoJson** (by Benoit Blanchon)
- **WiFi** (built-in for ESP32)
- **HTTPClient** (built-in for ESP32)

### 2. Configure ESP32 Code

1. Open `esp32_example.ino` in Arduino IDE
2. Update WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Update Flask backend IP address:
   ```cpp
   const char* serverUrl = "http://<your-ip>:5000/esp32/predict";
   ```
4. Upload to your ESP32

### 3. Start Flask Backend

```bash
# Start the Flask backend
python app.py
```

The backend will be available at:
- **Main API**: http://localhost:5000
- **ESP32 Endpoint**: http://localhost:5000/esp32/predict
- **Status Check**: http://localhost:5000/esp32/status

### 4. Test the Integration

```bash
# Run the test script
python test_esp32_integration.py
```

This will test:
- Flask backend connectivity
- ESP32 endpoints
- Prediction functionality
- Data validation

### 5. Start Frontend (Optional)

```bash
cd frontend
npm run dev
```

## 📊 **Data Format**

### ESP32 → Flask (Request)
```json
{
  "sensor_values": [512, 256, 128, 64, 32],
  "timestamp": 1234567890
}
```

### Flask → ESP32 (Response)
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "sensor_data": [512, 256, 128, 64, 32],
  "detected": true,
  "prediction": "A",
  "confidence": 0.85,
  "audio_file": "/audio/A.mp3"
}
```

## 🎵 **Audio Files Setup**

Your audio files should be stored in:
```
SpeakEz/frontend/public/audio/
├── A.mp3
├── B.mp3
├── C.mp3
...
└── Z.mp3
```

## 🔍 **Troubleshooting**

### ESP32 Connection Issues
- **WiFi not connecting**: Check SSID and password
- **HTTP request failed**: Verify Flask backend IP and port
- **No response**: Check serial monitor for debug output

### Flask Backend Issues
- **Port already in use**: Change port in `app.py`
- **Model loading failed**: Check if model files exist
- **Prediction errors**: Check sensor data format

### Data Format Issues
- **Wrong number of sensors**: Ensure exactly 5 values
- **Invalid JSON**: Check ESP32 JSON formatting
- **Missing fields**: Verify required fields in request

## 🎯 **Customization**

### Adding Your CNN Model

1. **Train your CNN model** with ESP32 sensor data
2. **Save the model** as `esp32_asl_model.keras`
3. **Update the model loading** in `app.py`:
   ```python
   esp32_cnn_model = tf.keras.models.load_model("esp32_asl_model.keras")
   esp32_scaler = pickle.load(open("esp32_scaler.pkl", "rb"))
   esp32_label_encoder = pickle.load(open("esp32_label_encoder.pkl", "rb"))
   ```

### Sensor Calibration

1. **Run calibration function** in ESP32:
   ```cpp
   calibrateSensors();
   ```
2. **Observe sensor values** for different finger positions
3. **Update thresholds** in `placeholder_esp32_prediction()` function

### Audio Customization

1. **Replace audio files** in `frontend/public/audio/`
2. **Update audio mapping** in `get_audio_file_path()` function
3. **Test audio playback** in browser

## 📱 **API Endpoints**

### ESP32 Prediction
- **URL**: `POST /esp32/predict`
- **Purpose**: Process sensor data and return prediction
- **Input**: JSON with sensor_values array
- **Output**: JSON with prediction and audio file

### ESP32 Status
- **URL**: `GET /esp32/status`
- **Purpose**: Check ESP32 integration status
- **Output**: JSON with system status

### Health Check
- **URL**: `GET /health`
- **Purpose**: Check Flask backend health
- **Output**: JSON with backend status

## 🚀 **Performance Optimization**

### Reduce Latency
- **Increase update frequency** (change `SEND_INTERVAL` in ESP32)
- **Optimize CNN model** for faster inference
- **Use WebSocket** instead of HTTP for real-time communication

### Improve Accuracy
- **Calibrate sensors** properly
- **Train CNN model** with more data
- **Add data preprocessing** and filtering

## 🔒 **Security Considerations**

- **Local network only**: This setup is for development
- **Add authentication**: For production use
- **Validate input data**: Prevent malicious requests
- **Rate limiting**: Prevent spam requests

## 📞 **Support**

If you encounter issues:

1. **Check serial monitor** for ESP32 debug output
2. **Check Flask console** for backend errors
3. **Run test script** to verify integration
4. **Verify network connectivity** between ESP32 and computer
5. **Check sensor connections** and calibration

## 🎉 **Success Indicators**

You'll know it's working when:
- ✅ ESP32 connects to WiFi
- ✅ Flask backend receives sensor data
- ✅ CNN model makes predictions
- ✅ Audio files play correctly
- ✅ Real-time letter detection works
- ✅ Response times are under 1 second 