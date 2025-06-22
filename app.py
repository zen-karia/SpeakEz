# app.py

import cv2
import numpy as np
import pickle
import tensorflow as tf
import mediapipe as mp
from math import acos, degrees

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

# --- Main inference loop ---------------------------------------------------

def main():
    # Load main landmark-based model + preprocessor
    main_model = tf.keras.models.load_model("asl_letter_model_v3.keras")
    scaler     = pickle.load(open("scaler_v3.pkl", "rb"))
    le         = pickle.load(open("label_encoder_v3.pkl", "rb"))

    # Load closed-fist refiner
    closed_cnn = tf.keras.models.load_model("closed_fist_refiner.keras")
    closed_le  = pickle.load(open("closed_fist_le.pkl", "rb"))

    # Load B-vs-W refiner
    bw_cnn = tf.keras.models.load_model("bw_refiner.keras")
    bw_le  = pickle.load(open("bw_le.pkl", "rb"))

    # Ambiguous sets
    ambig_closed = {'A','E','O','S','M','N','T'}
    ambig_bw     = {'B','W'}

    # Mediapipe hands (world landmarks)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        model_complexity=1,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h_img, w_img = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if res.multi_hand_world_landmarks:
            world_lms = res.multi_hand_world_landmarks[0].landmark
            # Build feature vector
            coords = np.array([[p.x,p.y,p.z] for p in world_lms], dtype=np.float32).flatten()
            angs   = landmark_angles(world_lms)
            dists  = tip_distances(world_lms)
            img_lms = res.multi_hand_landmarks[0].landmark
            area   = hull_area(img_lms, w_img, h_img)
            feat   = np.concatenate([coords, angs, dists, [area]]).reshape(1, -1)

            # Main prediction
            feat_s = scaler.transform(feat)
            probs  = main_model.predict(feat_s, verbose=0)[0]
            pred   = le.inverse_transform([np.argmax(probs)])[0]
            conf   = np.max(probs)

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

            # Draw results
            mp.solutions.drawing_utils.draw_landmarks(
                frame, res.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS
            )
            cv2.putText(
                frame, pred, (10,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3
            )

        cv2.imshow("ASL Letter Recognition", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()
