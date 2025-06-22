#!/usr/bin/env python3
"""
Test script for ASL letter recognition model v3 with refiners
"""

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pickle
from math import acos, degrees
import time
import json

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

# --- Model loading --------------------------------------------------------

print("🚀 Loading ASL Recognition Models...")

try:
    # Load main landmark-based model + preprocessor
    main_model = tf.keras.models.load_model("asl_letter_model_v3.keras")
    print("✅ Main model loaded successfully")
    
    scaler = pickle.load(open("scaler_v3.pkl", "rb"))
    print("✅ Scaler loaded successfully")
    
    le = pickle.load(open("label_encoder_v3.pkl", "rb"))
    print("✅ Label encoder loaded successfully")

    # Load closed-fist refiner
    closed_cnn = tf.keras.models.load_model("closed_fist_refiner.keras")
    print("✅ Closed-fist refiner loaded successfully")
    
    closed_le = pickle.load(open("closed_fist_le.pkl", "rb"))
    print("✅ Closed-fist label encoder loaded successfully")

    # Load B-vs-W refiner
    bw_cnn = tf.keras.models.load_model("bw_refiner.keras")
    print("✅ B/W refiner loaded successfully")
    
    bw_le = pickle.load(open("bw_le.pkl", "rb"))
    print("✅ B/W label encoder loaded successfully")

except Exception as e:
    print(f"❌ Error loading models: {e}")
    print("Please ensure all model files are present in the current directory")
    exit(1)

# Ambiguous sets
ambig_closed = {'A','E','O','S','M','N','T'}
ambig_bw = {'B','W'}

# Mediapipe hands (world landmarks)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    model_complexity=1,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

print("✅ All models loaded successfully!")

def predict_asl_letter(frame):
    """Predict ASL letter from frame using enhanced model with refiners"""
    try:
        # Mirror the frame
        frame = cv2.flip(frame, 1)
        h_img, w_img = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        res = hands.process(rgb)
        
        if res.multi_hand_world_landmarks:
            world_lms = res.multi_hand_world_landmarks[0].landmark
            img_lms = res.multi_hand_landmarks[0].landmark
            
            # Build feature vector
            coords = np.array([[p.x,p.y,p.z] for p in world_lms], dtype=np.float32).flatten()
            angs = landmark_angles(world_lms)
            dists = tip_distances(world_lms)
            area = hull_area(img_lms, w_img, h_img)
            feat = np.concatenate([coords, angs, dists, [area]]).reshape(1, -1)
            
            # Main prediction
            feat_s = scaler.transform(feat)
            probs = main_model.predict(feat_s, verbose=0)[0]
            pred = le.inverse_transform([np.argmax(probs)])[0]
            conf = float(np.max(probs))
            
            # Cascade to refiners if needed
            if pred in ambig_closed and conf < 0.9:
                x1, y1, x2, y2 = get_hand_bbox(img_lms, frame.shape)
                crop = frame[y1:y2, x1:x2]
                if crop.size:
                    crop = cv2.resize(crop, (128, 128)) / 255.0
                    subp = closed_cnn.predict(crop[np.newaxis, ...], verbose=0)[0]
                    pred = closed_le.inverse_transform([np.argmax(subp)])[0]
            
            elif pred in ambig_bw and conf < 0.9:
                x1, y1, x2, y2 = get_hand_bbox(img_lms, frame.shape)
                crop = frame[y1:y2, x1:x2]
                if crop.size:
                    crop = cv2.resize(crop, (128, 128)) / 255.0
                    subp = bw_cnn.predict(crop[np.newaxis, ...], verbose=0)[0][0]
                    pred = 'W' if subp > 0.5 else 'B'
            
            return pred, conf, True
        
        return None, 0.0, False
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None, 0.0, False

def main():
    """Main test function with webcam"""
    print("🎥 Starting webcam test...")
    print("Press 'q' to quit")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("📹 Webcam started successfully")
    print("🤚 Show your hand to the camera to test ASL recognition")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
        
        # Get prediction
        prediction, confidence, detected = predict_asl_letter(frame)
        
        # Draw results
        if detected:
            # Draw prediction text
            text = f"{prediction} ({confidence:.2f})"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 255, 0), 2)
            
            # Draw confidence bar
            bar_width = int(200 * confidence)
            cv2.rectangle(frame, (10, 50), (210, 70), (255, 255, 255), 2)
            cv2.rectangle(frame, (10, 50), (10 + bar_width, 70), (0, 255, 0), -1)
            
            # Draw status
            cv2.putText(frame, "Hand Detected", (10, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No Hand Detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Show frame
        cv2.imshow('ASL Recognition Test', frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Test completed")

if __name__ == "__main__":
    main()

MODEL_PATH   = "glove_cnn_model.keras"
CLASSES_PATH = "classes.json"

# the five flex sensors, in order
FINGER_NAMES = ["thumb", "pointer", "middle", "ring", "pinky"]
N_SENSORS    = len(FINGER_NAMES)

def load_resources():
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASSES_PATH, "r") as f:
        classes = json.load(f)
    return model, classes

def predict_from_input(model, classes, vals):
    """
    vals: list of 5 floats, in the same order as FINGER_NAMES
    """
    # shape (1, 5, 1)
    arr = np.array(vals, dtype=np.float32)[np.newaxis, ..., np.newaxis]
    probs = model.predict(arr, verbose=0)[0]
    idx   = np.argmax(probs)
    return classes[idx], probs[idx]

def main():
    print("🔎 Speakez Glove Predictor")
    model, classes = load_resources()

    print(f"Expecting {N_SENSORS} comma-separated flex readings in this order:")
    print("  " + ", ".join(FINGER_NAMES))
    print("Type 'quit' to exit.\n")

    while True:
        line = input("Enter sensors: ").strip()
        if line.lower() in ("quit", "exit"):
            break

        parts = [p.strip() for p in line.split(",")]
        if len(parts) != N_SENSORS:
            print(f"⚠️  Got {len(parts)} values; need {N_SENSORS}. Try again.\n")
            continue

        try:
            vals = [float(p) for p in parts]
        except ValueError:
            print("⚠️  Could not parse all inputs as floats. Re-enter.\n")
            continue

        letter, conf = predict_from_input(model, classes, vals)
        print(f"→ Prediction: {letter}  (confidence {conf:.2%})\n")

if __name__ == "__main__":
    main() 