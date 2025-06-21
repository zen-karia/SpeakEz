import cv2
import threading
import tkinter as tk
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pickle

# Paths to your saved model and preprocessing objects
MODEL_PATH = "asl_letter_model.keras"
SCALER_PATH = "scaler.pkl"
LE_PATH    = "label_encoder.pkl"

class HandTrackerApp:
    def __init__(self, window, window_title, camera_index=0):
        self.window = window
        self.window.title(window_title)
        self.cap = cv2.VideoCapture(camera_index)

        # Load model, scaler, and label encoder
        self.model = tf.keras.models.load_model(MODEL_PATH)
        with open(SCALER_PATH, 'rb') as f:
            self.scaler = pickle.load(f)
        with open(LE_PATH, 'rb') as f:
            self.le = pickle.load(f)

        # MediaPipe Hands setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

        # Tkinter UI: a label to display the video frames
        self.video_label = tk.Label(window)
        self.video_label.pack()

        # Start the video loop in a separate thread
        self.running = True
        threading.Thread(target=self.video_loop, daemon=True).start()

        # On closing the window, stop the loop
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    def video_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Mirror and convert to RGB
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process with MediaPipe
            results = self.hands.process(rgb)

            # Draw landmarks and predict
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, handLms, self.mp_hands.HAND_CONNECTIONS)
                    # Extract features for prediction
                    lm = handLms.landmark
                    feat = [val for p in lm for val in (p.x, p.y, p.z)]
                    feat_arr = np.array([feat], dtype=np.float32)
                    feat_scaled = self.scaler.transform(feat_arr)
                    probs = self.model.predict(feat_scaled, verbose=0)
                    pred = self.le.inverse_transform([np.argmax(probs)])[0]
                    # Overlay prediction
                    cv2.putText(frame, f"{pred}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            # Convert to ImageTk
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Cleanup when loop ends
        self.cap.release()

    def on_close(self):
        self.running = False
        self.window.destroy()

if __name__ == "__main__":
    # Make sure you’ve installed: opencv-python mediapipe pillow tensorflow scikit-learn
    HandTrackerApp(tk.Tk(), "ASL Letter Recognition App")
