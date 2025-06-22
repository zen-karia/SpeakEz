# app.py - Flask backend for ASL recognition

import cv2
import numpy as np
import pickle
import tensorflow as tf
import mediapipe as mp
from math import acos, degrees
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# --- ESP32 CNN Model for Sensor Data ---------------------------------------------------

# Global variable for ESP32 CNN model
esp32_cnn_model = None
esp32_scaler = None
esp32_label_encoder = None

def load_esp32_models():
    """Load CNN model for ESP32 sensor data"""
    global esp32_cnn_model, esp32_scaler, esp32_label_encoder
    
    try:
        # Load your ESP32 CNN model here
        esp32_cnn_model = tf.keras.models.load_model("glove_cnn_model.keras")
        # esp32_scaler = pickle.load(open("esp32_scaler.pkl", "rb"))
        # esp32_label_encoder = pickle.load(open("esp32_label_encoder.pkl", "rb"))
        print("✅ ESP32 CNN model (glove_cnn_model.keras) loaded successfully!")
        print("⚠️  Note: Using default preprocessing (no scaler/label encoder)")
        print("📝 If you have scaler and label encoder files, uncomment the lines above")
    except Exception as e:
        print(f"⚠️  ESP32 model loading failed: {e}")
        print("Using placeholder prediction function")

def predict_esp32_letter(sensor_data):
    """
    Predict ASL letter from ESP32 sensor data using CNN
    sensor_data: list of 5 sensor values
    Returns: (prediction, confidence, detected)
    """
    try:
        # Ensure we have exactly 5 sensor values
        if len(sensor_data) != 5:
            print(f"Expected 5 sensor values, got {len(sensor_data)}")
            return None, 0.0, False
        
        # Convert to numpy array and reshape for CNN
        sensor_array = np.array(sensor_data, dtype=np.float32).reshape(1, -1)
        
        # If you have a trained CNN model, use it here
        if esp32_cnn_model is not None:
            print(f"🔍 Using glove_cnn_model.keras for prediction with sensor data: {sensor_data}")
            
            # Normalize the data (if scaler is available)
            if esp32_scaler is not None:
                sensor_scaled = esp32_scaler.transform(sensor_array)
                print(f"📊 Data normalized using scaler")
            else:
                # Use raw data or basic normalization
                sensor_scaled = sensor_array / 1024.0  # Normalize to 0-1 range
                print(f"📊 Data normalized to 0-1 range (no scaler)")
            
            # Make prediction
            prediction = esp32_cnn_model.predict(sensor_scaled, verbose=0)
            print(f"🎯 Raw CNN output: {prediction}")
            
            # Get letter and confidence
            if esp32_label_encoder is not None:
                letter = esp32_label_encoder.inverse_transform([np.argmax(prediction)])[0]
                confidence = np.max(prediction)
                print(f"🎯 Using label encoder for letter mapping")
            else:
                # Map prediction index to letter (assuming 0-25 for A-Z)
                predicted_index = np.argmax(prediction)
                if predicted_index < 26:
                    letter = chr(65 + predicted_index)  # Convert 0-25 to A-Z
                else:
                    letter = 'X'  # Unknown letter
                confidence = np.max(prediction)
                print(f"🎯 Direct index mapping: {predicted_index} -> {letter}")
            
            print(f"🎯 Final Prediction: {letter} (confidence: {confidence:.3f})")
            return letter, confidence, True
        else:
            # Placeholder prediction function - replace with your actual logic
            print(f"🔍 Using placeholder prediction with sensor data: {sensor_data}")
            letter, confidence = placeholder_esp32_prediction(sensor_data)
            print(f"🎯 Placeholder Prediction: {letter} (confidence: {confidence:.3f})")
            return letter, confidence, True
        
    except Exception as e:
        print(f"Error in ESP32 prediction: {e}")
        return None, 0.0, False

def placeholder_esp32_prediction(sensor_data):
    """
    Placeholder function for ESP32 prediction
    Replace this with your actual CNN model logic
    """
    # This is a simple example - replace with your trained model
    # Example logic based on sensor patterns
    thumb, index, middle, ring, pinky = sensor_data
    
    # Simple threshold-based detection (replace with your CNN)
    if thumb > 800 and index < 200 and middle < 200 and ring < 200 and pinky < 200:
        return 'A', 0.85
    elif thumb < 200 and index < 200 and middle < 200 and ring < 200 and pinky < 200:
        return 'B', 0.90
    elif thumb > 600 and index > 600 and middle > 600 and ring > 600 and pinky > 600:
        return 'C', 0.80
    elif thumb > 700 and index > 700 and middle < 200 and ring < 200 and pinky < 200:
        return 'D', 0.75
    elif thumb > 800 and index > 800 and middle > 800 and ring > 800 and pinky > 800:
        return 'E', 0.85
    else:
        return 'X', 0.50  # Unknown/No detection

# --- Audio File Mapping ---------------------------------------------------

def get_audio_file_path(letter):
    """Get the audio file path for a given letter"""
    if letter and len(letter) == 1 and letter.isalpha():
        return f"/audio/{letter.upper()}.mp3"
    return None

# --- Feature helpers --------------------------------------------------------

def landmark_angles(landmarks):
    """
    Compute 2 joint angles per finger from world landmarks.
    Returns a (10,) array of angles in degrees.
    """
    fingers = {
        'thumb':   [(1,2,3),(2,3,4)],
        'index':   [(5,6,7),(6,7,8)],
        'middle':  [(9,10,11),(10,11,12)],
        'ring':    [(13,14,15),(14,15,16)],
        'pinky':   [(17,18,19),(18,19,20)],
    }
    coords = np.array([[p.x, p.y, p.z] for p in landmarks], dtype=np.float32)
    angles = []
    for joints in fingers.values():
        for a, b, c in joints:
            v1 = coords[a] - coords[b]
            v2 = coords[c] - coords[b]
            cosang = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2) + 1e-6)
            angles.append(degrees(acos(np.clip(cosang, -1, 1))))
    return np.array(angles, dtype=np.float32)

def tip_distances(landmarks):
    """
    Compute Euclidean distance from each fingertip to the wrist.
    Returns a (5,) array of distances.
    """
    pts = np.array([[p.x, p.y, p.z] for p in landmarks], dtype=np.float32)
    wrist = pts[0]
    tips  = pts[[4, 8, 12, 16, 20]]
    return np.linalg.norm(tips - wrist, axis=1)

def hull_area(landmarks, w, h):
    """
    Compute 2D convex-hull area of the hand projection.
    landmarks: normalized image-space landmarks
    w,h: frame width & height in pixels
    """
    pts = np.array([[int(p.x*w), int(p.y*h)] for p in landmarks], dtype=np.int32)
    hull = cv2.convexHull(pts)
    return cv2.contourArea(hull)

def get_hand_bbox(landmarks, frame_shape, pad=0.2):
    """
    Return a padded bounding box (x1,y1,x2,y2) in pixel coords
    around the hand landmarks.
    """
    h, w = frame_shape[:2]
    xs = [p.x for p in landmarks]
    ys = [p.y for p in landmarks]
    x1 = int(max(0, (min(xs) - pad) * w))
    x2 = int(min(w, (max(xs) + pad) * w))
    y1 = int(max(0, (min(ys) - pad) * h))
    y2 = int(min(h, (max(ys) + pad) * h))
    return x1, y1, x2, y2

# --- Global variables for models ---------------------------------------------------

# Load models once when the app starts
main_model = None
scaler = None
le = None
closed_cnn = None
closed_le = None
bw_cnn = None
bw_le = None
hands = None

def load_models():
    """Load all models and preprocessors"""
    global main_model, scaler, le, closed_cnn, closed_le, bw_cnn, bw_le, hands
    
    print("Loading ASL recognition models...")
    
    # Load main landmark-based model + preprocessor
    main_model = tf.keras.models.load_model("asl_letter_model_v3.keras")
    scaler = pickle.load(open("scaler_v3.pkl", "rb"))
    le = pickle.load(open("label_encoder_v3.pkl", "rb"))

    # Load closed-fist refiner
    closed_cnn = tf.keras.models.load_model("closed_fist_refiner.keras")
    closed_le = pickle.load(open("closed_fist_le.pkl", "rb"))

    # Load B-vs-W refiner
    bw_cnn = tf.keras.models.load_model("bw_refiner.keras")
    bw_le = pickle.load(open("bw_le.pkl", "rb"))

    # Mediapipe hands (world landmarks)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,  # Use static mode for single images
        model_complexity=1,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Load ESP32 models
    load_esp32_models()
    
    print("✅ All models loaded successfully!")

def predict_asl_letter(image_data):
    """
    Predict ASL letter from image data
    image_data: base64 encoded image string
    Returns: (prediction, confidence, detected)
    """
    try:
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        frame = cv2.flip(frame, 1)  # Mirror the image
        
        h_img, w_img = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if not res.multi_hand_world_landmarks:
            return None, 0.0, False

        world_lms = res.multi_hand_world_landmarks[0].landmark
        
        # Build feature vector
        coords = np.array([[p.x,p.y,p.z] for p in world_lms], dtype=np.float32).flatten()
        angs = landmark_angles(world_lms)
        dists = tip_distances(world_lms)
        img_lms = res.multi_hand_landmarks[0].landmark
        area = hull_area(img_lms, w_img, h_img)
        feat = np.concatenate([coords, angs, dists, [area]]).reshape(1, -1)

        # Main prediction
        feat_s = scaler.transform(feat)
        probs = main_model.predict(feat_s, verbose=0)[0]
        pred = le.inverse_transform([np.argmax(probs)])[0]
        conf = np.max(probs)

        # Ambiguous sets
        ambig_closed = {'A','E','O','S','M','N','T'}
        ambig_bw = {'B','W'}

        # Cascade to refiners if needed
        if pred in ambig_closed and conf < 0.9:
            x1,y1,x2,y2 = get_hand_bbox(img_lms, frame.shape)
            crop = frame[y1:y2, x1:x2]
            if crop.size:
                crop = cv2.resize(crop, (128,128)) / 255.0
                subp = closed_cnn.predict(crop[np.newaxis,...], verbose=0)[0]
                pred = closed_le.inverse_transform([np.argmax(subp)])[0]

        elif pred in ambig_bw and conf < 0.9:
            x1,y1,x2,y2 = get_hand_bbox(img_lms, frame.shape)
            crop = frame[y1:y2, x1:x2]
            if crop.size:
                crop = cv2.resize(crop, (128,128)) / 255.0
                subp = bw_cnn.predict(crop[np.newaxis,...], verbose=0)[0][0]
                pred = 'W' if subp > 0.5 else 'B'

        return pred, conf, True
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None, 0.0, False

# --- Flask routes ---------------------------------------------------

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint for ASL letter prediction from webcam"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        prediction, confidence, detected = predict_asl_letter(image_data)
        
        if detected:
            audio_file = get_audio_file_path(prediction)
            return jsonify({
                'detected': True,
                'prediction': prediction,
                'confidence': float(confidence),
                'audio_file': audio_file
            })
        else:
            return jsonify({
                'detected': False,
                'prediction': None,
                'confidence': 0.0,
                'audio_file': None
            })
            
    except Exception as e:
        print(f"Error in /predict endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/esp32/predict', methods=['POST'])
def esp32_predict():
    """Endpoint for ESP32 sensor data prediction"""
    try:
        data = request.get_json()
        
        # Validate input data
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract sensor data
        sensor_data = None
        if 'sensor_values' in data:
            sensor_data = data['sensor_values']
        elif 'sensors' in data:
            sensor_data = data['sensors']
        elif 'data' in data:
            sensor_data = data['data']
        else:
            return jsonify({'error': 'No sensor data found. Expected: sensor_values, sensors, or data'}), 400
        
        # Validate sensor data
        if not isinstance(sensor_data, list) or len(sensor_data) != 5:
            return jsonify({'error': f'Expected 5 sensor values, got {len(sensor_data) if isinstance(sensor_data, list) else "non-list"}'}), 400
        
        # Make prediction
        prediction, confidence, detected = predict_esp32_letter(sensor_data)
        
        # Prepare response
        response = {
            'timestamp': datetime.now().isoformat(),
            'sensor_data': sensor_data,
            'detected': detected
        }
        
        if detected:
            audio_file = get_audio_file_path(prediction)
            response.update({
                'prediction': prediction,
                'confidence': float(confidence),
                'audio_file': audio_file
            })
        else:
            response.update({
                'prediction': None,
                'confidence': 0.0,
                'audio_file': None
            })
        
        print(f"ESP32 Prediction: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in /esp32/predict endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/esp32/status', methods=['GET'])
def esp32_status():
    """Endpoint to check ESP32 integration status"""
    return jsonify({
        'status': 'active',
        'esp32_model_loaded': esp32_cnn_model is not None,
        'endpoints': {
            'predict': '/esp32/predict',
            'status': '/esp32/status'
        },
        'data_format': {
            'sensor_values': '[value1, value2, value3, value4, value5]',
            'frequency': '1 per second'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'ASL Recognition API is running'})

if __name__ == "__main__":
    # Load models before starting the server
    load_models()
    
    print("🚀 Starting Flask backend server...")
    print("Server will be available at: http://localhost:5000")
    print("ESP32 endpoint: http://localhost:5000/esp32/predict")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
