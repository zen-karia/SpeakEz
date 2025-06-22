# SpeakEz ASL Learning App - Setup Instructions

## Overview
SpeakEz is an interactive ASL (American Sign Language) learning application that uses machine learning to recognize hand signs in real-time. The app features a Python Flask backend with TensorFlow models and a React frontend with webcam integration.

## Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Webcam for real-time sign recognition
- Good lighting for accurate hand detection

## Installation Steps

### 1. Clone and Navigate to Project
```bash
cd SpeakEz
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- TensorFlow 2.19.0 (matches model version)
- OpenCV 4.8.1.78
- MediaPipe 0.10.7
- Flask 2.3.3
- Flask-CORS 4.0.0

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Verify Model Files
Ensure these files are present in the root directory:
- `asl_letter_model_v3.keras` - Main ASL recognition model
- `scaler_v3.pkl` - Feature scaler
- `label_encoder_v3.pkl` - Label encoder
- `closed_fist_refiner.keras` - Refiner for closed-fist letters
- `closed_fist_le.pkl` - Closed-fist label encoder
- `bw_refiner.keras` - Refiner for B/W distinction
- `bw_le.pkl` - B/W label encoder

## Testing the Installation

### 1. Test TensorFlow Installation
```bash
python test_tensorflow.py
```
This should show:
- ✅ TensorFlow 2.19.0 loaded successfully
- ✅ All models loaded without errors
- ✅ All dependencies working

### 2. Test Model Performance
```bash
python test_model.py
```
This opens a webcam window where you can test ASL recognition in real-time.

### 3. Test Backend API
```bash
python start_app.py
```
The Flask server should start on `http://localhost:5000`

## Running the Application

### 1. Start the Backend Server
```bash
python start_app.py
```
**Expected Output:**
```
🚀 Starting ASL Recognition API (v3 with refiners)
✅ Models loaded:
   - Main model: asl_letter_model_v3.keras
   - Closed fist refiner: closed_fist_refiner.keras
   - B/W refiner: bw_refiner.keras
 * Running on http://0.0.0.0:5000
```

### 2. Start the Frontend (New Terminal)
```bash
cd frontend
npm run dev
```
**Expected Output:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. Access the Application
Open your browser and go to: `http://localhost:5173`

## Using the Application

### Interactive Learning Flow
1. **Grant Camera Permission**: Allow webcam access when prompted
2. **Practice Mode**: The app will randomly select letters from your practice set
3. **Make the Sign**: Show the requested ASL letter to your webcam
4. **Get Feedback**: 
   - ✅ "Correct!" - Move to next letter
   - ❌ "Try again" - Keep practicing the same letter
5. **Progress**: Successfully recognized signs advance to the next letter

### Customizing Practice Letters
Edit `frontend/src/assets/components/Learn/LearnMain.jsx`:
```javascript
// Change this array to practice different letters
const practiceLetters = ['B', 'W']; // Example: only B and W
```

### Confidence Threshold
The app uses a 70% confidence threshold. You can adjust this in the frontend code if needed.

## Model Features

### Enhanced v3 Model
- **Main Model**: Uses MediaPipe hand landmarks and geometric features
- **Closed-fist Refiner**: Improves accuracy for A, E, O, S, M, N, T
- **B/W Refiner**: Distinguishes between B and W signs
- **Real-time Processing**: Optimized for interactive learning

### Supported Letters
The model recognizes all 26 ASL alphabet letters (A-Z) with enhanced accuracy for commonly confused signs.

## Troubleshooting

### Common Issues

#### 1. TensorFlow Import Errors
```bash
# If you get TensorFlow errors, ensure you have the correct version:
pip uninstall tensorflow
pip install tensorflow==2.19.0
```

#### 2. Model Loading Errors
```bash
# Test model loading:
python test_tensorflow.py
```
Ensure all model files are present and TensorFlow version matches.

#### 3. Webcam Not Working
- Check browser permissions
- Ensure no other applications are using the webcam
- Try refreshing the page

#### 4. Poor Recognition Accuracy
- Ensure good lighting
- Keep hand centered in frame
- Use plain background
- Make clear, deliberate signs

#### 5. Backend Connection Issues
```bash
# Check if backend is running:
curl http://localhost:5000/health
```
Should return: `{"status": "healthy", "model": "v3_with_refiners"}`

### Performance Tips
- **Lighting**: Bright, even lighting works best
- **Background**: Plain, uncluttered backgrounds
- **Hand Position**: Keep hand centered and fully visible
- **Sign Clarity**: Make deliberate, clear hand shapes
- **Distance**: Maintain consistent distance from camera

## Development

### Backend Structure
- `app.py` - Main Flask API with prediction endpoint
- `test_model.py` - Model testing and validation
- `test_tensorflow.py` - TensorFlow installation verification

### Frontend Structure
- `frontend/src/App.jsx` - Main application component
- `frontend/src/assets/components/Learn/LearnMain.jsx` - Learning interface
- `frontend/src/assets/components/Hero/HeroMain.jsx` - Landing page

### API Endpoints
- `POST /predict` - Submit image for ASL recognition
- `GET /health` - Health check endpoint

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure model files are present
4. Test with the provided test scripts

The application is designed to work with TensorFlow 2.19.0 and includes comprehensive error handling and testing utilities. 