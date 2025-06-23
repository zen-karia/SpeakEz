#!/usr/bin/env python3
"""
Test script for ESP32 integration with Flask backend
Simulates ESP32 sensor data to test the prediction endpoint
"""

import requests
import json
import time
import random

# Flask backend URL
BASE_URL = "http://localhost:5000"

def test_esp32_status():
    """Test the ESP32 status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/esp32/status")
        print("✅ ESP32 Status Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ESP32 Status Test Failed: {e}")
        return False

def test_esp32_prediction(sensor_data):
    """Test the ESP32 prediction endpoint with sample data"""
    try:
        url = f"{BASE_URL}/esp32/predict"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "sensor_values": sensor_data
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"✅ ESP32 Prediction Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Sent Data: {sensor_data}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ESP32 Prediction Test Failed: {e}")
        return False

def generate_test_data():
    """Generate various test sensor data patterns"""
    test_cases = [
        # Letter A pattern (thumb bent, others straight)
        [850, 150, 120, 100, 80],
        
        # Letter B pattern (all straight)
        [120, 100, 80, 90, 70],
        
        # Letter C pattern (all curved)
        [650, 620, 580, 600, 590],
        
        # Letter D pattern (thumb and index bent, others straight)
        [750, 720, 150, 120, 100],
        
        # Letter E pattern (all bent)
        [820, 810, 800, 790, 780],
        
        # Random data
        [random.randint(0, 1023) for _ in range(5)],
        
        # Invalid data (wrong length)
        [100, 200, 300, 400],
    ]
    
    return test_cases

def main():
    """Main test function"""
    print("🧪 Testing ESP32 Integration with Flask Backend")
    print("=" * 50)
    
    # Test 1: Check if Flask backend is running
    print("\n1. Testing Flask Backend Status...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Flask backend is running")
        else:
            print("❌ Flask backend is not responding correctly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Flask backend: {e}")
        print("Make sure to run: python app.py")
        return
    
    # Test 2: Check ESP32 status endpoint
    print("\n2. Testing ESP32 Status Endpoint...")
    if not test_esp32_status():
        print("❌ ESP32 status endpoint failed")
        return
    
    # Test 3: Test prediction with various data patterns
    print("\n3. Testing ESP32 Prediction Endpoint...")
    test_cases = generate_test_data()
    
    for i, sensor_data in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        success = test_esp32_prediction(sensor_data)
        
        if success:
            print("✅ Test case passed")
        else:
            print("❌ Test case failed")
        
        time.sleep(1)  # Wait between requests
    
    print("\n" + "=" * 50)
    print("🎉 ESP32 Integration Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Upload esp32_example.ino to your ESP32")
    print("2. Update WiFi credentials and server IP in Arduino code")
    print("3. Connect your flex sensors to analog pins A0-A4")
    print("4. Test with real sensor data")

if __name__ == "__main__":
    main() 