# CNN Integration Guide for ESP32 System

This guide will help you integrate your trained CNN model into the ESP32 system for automatic ASL letter recognition.

## 🎯 **Automatic Data Flow**

```
ESP32 → JSON → CNN → Letter → Frontend → Audio
```

## 📋 **Step-by-Step Integration**

### 1. **Prepare Your CNN Model**

Save your trained model and preprocessing files:
- **Model**: `esp32_asl_model.keras`
- **Scaler**: `esp32_scaler.pkl`
- **Label Encoder**: `esp32_label_encoder.pkl`

### 2. **Place Files in SpeakEz Directory**

Put your files in the main SpeakEz folder:
```
SpeakEz/
├── esp32_asl_model.keras
├── esp32_scaler.pkl
├── esp32_label_encoder.pkl
├── app.py
└── ...
```

### 3. **Update the Code**

Open `app.py` and find the `load_esp32_models()` function. Uncomment these lines:

```python
def load_esp32_models():
    """Load CNN model for ESP32 sensor data"""
    global esp32_cnn_model, esp32_scaler, esp32_label_encoder
    
    try:
        # Load your ESP32 CNN model here
        esp32_cnn_model = tf.keras.models.load_model("esp32_asl_model.keras")
        esp32_scaler = pickle.load(open("esp32_scaler.pkl", "rb"))
        esp32_label_encoder = pickle.load(open("esp32_label_encoder.pkl", "rb"))
        print("✅ ESP32 CNN model loaded successfully!")
    except Exception as e:
        print(f"⚠️  ESP32 model loading failed: {e}")
        print("Using placeholder prediction function")
```

### 4. **Test the Integration**

1. **Start the system:**
   ```bash
   python start_complete_system.py
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Click "Enter Pairing Mode"**

4. **Test with real ESP32 data** or use "Simulate ESP32 Data" button

## 🔍 **What Happens Automatically**

### **When ESP32 Sends Data:**
1. **ESP32** sends JSON: `{"sensor_values": [512, 256, 128, 64, 32]}`
2. **Flask** receives data at `/esp32/predict` endpoint
3. **CNN** processes the 5 sensor values
4. **CNN** outputs letter prediction (e.g., "A")
5. **Flask** returns: `{"prediction": "A", "audio_file": "/audio/A.mp3"}`
6. **Frontend** receives prediction and plays audio automatically

### **Console Output:**
```
🔍 Using CNN model for prediction with sensor data: [512, 256, 128, 64, 32]
🎯 CNN Prediction: A (confidence: 0.856)
ESP32 Prediction: {'prediction': 'A', 'confidence': 0.856, 'audio_file': '/audio/A.mp3'}
```

## 🎵 **Audio Integration**

Your audio files should be in:
```
SpeakEz/frontend/public/audio/
├── A.mp3
├── B.mp3
├── C.mp3
...
└── Z.mp3
```

## 🧪 **Testing Your CNN**

### **Test with Simulated Data:**
1. Click "Simulate ESP32 Data" in pairing mode
2. Watch console for CNN processing
3. Verify letter detection and audio playback

### **Test with Real ESP32:**
1. Upload `esp32_example.ino` to your ESP32
2. Connect flex sensors to analog pins A0-A4
3. Make ASL signs and watch real-time detection

## 🔧 **Troubleshooting**

### **Model Loading Issues:**
- Check file paths and names
- Ensure model is compatible with TensorFlow version
- Verify scaler and label encoder match your training data

### **Prediction Issues:**
- Check sensor data format (exactly 5 values)
- Verify CNN input shape matches your model
- Monitor console output for debugging

### **Audio Issues:**
- Ensure audio files exist in correct location
- Check browser audio permissions
- Verify audio file format (MP3 recommended)

## 📊 **Expected Data Format**

### **ESP32 Input:**
```json
{
  "sensor_values": [value1, value2, value3, value4, value5]
}
```

### **CNN Output:**
```json
{
  "prediction": "A",
  "confidence": 0.856,
  "audio_file": "/audio/A.mp3"
}
```

## 🎉 **Success Indicators**

You'll know it's working when:
- ✅ Console shows "ESP32 CNN model loaded successfully!"
- ✅ "Simulate ESP32 Data" button produces predictions
- ✅ Letter detection displays in pairing mode
- ✅ Audio plays automatically for detected letters
- ✅ Real ESP32 data produces accurate predictions

## 🚀 **Next Steps**

1. **Train your CNN** with ESP32 sensor data
2. **Save the model** and preprocessing files
3. **Follow the integration steps** above
4. **Test thoroughly** with simulated and real data
5. **Deploy with your ESP32 glove**

The system is now ready for your CNN model! Just add your trained model files and uncomment the loading lines. 