#!/usr/bin/env python3
"""
Complete SpeakEz System Startup Script
Runs Flask backend with ESP32 integration
"""

import subprocess
import sys
import os
import time
import socket
from pathlib import Path

def get_local_ip():
    """Get the local IP address for ESP32 connection"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def install_requirements():
    """Install required Python packages"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements. Please install manually:")
        print("pip install -r requirements.txt")
        return False
    return True

def check_model_files():
    """Check if all required model files are present"""
    required_files = [
        "asl_letter_model_v3.keras",
        "scaler_v3.pkl", 
        "label_encoder_v3.pkl",
        "closed_fist_refiner.keras",
        "closed_fist_le.pkl",
        "bw_refiner.keras",
        "bw_le.pkl"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing model files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All model files found:")
    for file in required_files:
        print(f"   - {file}")
    return True

def start_flask_backend():
    """Start the Flask backend server"""
    print("🌐 Starting Flask backend server...")
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Flask server stopped")
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")

def main():
    print("🚀 Starting Complete SpeakEz System with ESP32 Integration")
    print("=" * 60)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        sys.exit(1)
    
    # Check model files
    if not check_model_files():
        print("\n❌ Please ensure all model files are present before starting the server.")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Get local IP for ESP32 connection
    local_ip = get_local_ip()
    print(f"\n📡 Your local IP address: {local_ip}")
    print("   Update this in your ESP32 code: serverUrl = \"http://" + local_ip + ":5000/esp32/predict\"")
    
    print("\n🔧 Starting Flask Backend...")
    print("   Flask Backend: http://localhost:5000")
    print("   ESP32 Endpoint: http://localhost:5000/esp32/predict")
    print("   Status Check: http://localhost:5000/esp32/status")
    
    print("\n📋 Complete Setup Instructions:")
    print("   1. ✅ Flask backend will start automatically")
    print("   2. 🔌 Upload esp32_example.ino to your ESP32")
    print("   3. 📡 Update WiFi credentials and IP address in ESP32 code")
    print("   4. 🔗 Connect 5 flex sensors to analog pins A0-A4")
    print("   5. 🌐 Start frontend: cd frontend && npm run dev")
    print("   6. 🎯 Click 'Enter Pairing Mode' in the web interface")
    print("   7. 🎉 Test with real ESP32 data or use 'Simulate ESP32 Data' button")
    print("   8. 🤖 Your glove_cnn_model.keras will be loaded automatically")
    
    print("\n🧪 Testing Options:")
    print("   • Run: python test_esp32_integration.py (test backend endpoints)")
    print("   • Use 'Simulate ESP32 Data' button in pairing mode (test frontend)")
    print("   • Connect real ESP32 for live testing")
    
    print("\n🎵 Audio Files:")
    print("   • Place .mp3 files in: frontend/public/audio/")
    print("   • Files should be named: A.mp3, B.mp3, C.mp3, etc.")
    
    print("\n🤖 CNN Model:")
    print("   • Your glove_cnn_model.keras will be loaded automatically")
    print("   • Check console for model loading confirmation")
    print("   • Monitor prediction output in real-time")
    
    print("\nPress Ctrl+C to stop the Flask backend")
    print("=" * 60)
    
    try:
        start_flask_backend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down SpeakEz system...")
        sys.exit(0)

if __name__ == "__main__":
    main() 