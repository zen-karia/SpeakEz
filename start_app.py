#!/usr/bin/env python3
"""
Helper script to start the Flask backend server for ASL recognition (v3 with refiners)
"""

import subprocess
import sys
import os

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

def start_backend():
    """Start the Flask backend server"""
    print("Starting Flask backend server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    print("🚀 Starting ASL Recognition Backend (v3 with refiners)")
    print("=" * 50)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        sys.exit(1)
    
    # Check model files
    if not check_model_files():
        print("\n❌ Please ensure all model files are present before starting the server.")
        sys.exit(1)
    
    # Install requirements
    if install_requirements():
        # Start the server
        start_backend()
    else:
        sys.exit(1) 