#!/usr/bin/env python3
"""
Simple test script to verify TensorFlow 2.19.0 installation
"""

def test_tensorflow():
    """Test TensorFlow installation and basic functionality"""
    print("🧪 Testing TensorFlow 2.19.0 Installation")
    print("=" * 40)
    
    try:
        import tensorflow as tf
        print("✅ TensorFlow imported successfully")
        
        # Try different ways to get version
        try:
            version = tf.version.VERSION
            print(f"✅ TensorFlow version: {version}")
        except:
            try:
                version = tf.__version__
                print(f"✅ TensorFlow version: {version}")
            except:
                print("⚠️  Could not determine TensorFlow version")
        
        # Test Keras availability with more detailed info
        print("\n🔍 Checking Keras availability...")
        if hasattr(tf, 'keras'):
            print("✅ Keras is available in TensorFlow")
            print(f"   Keras version: {tf.keras.__version__}")
        else:
            print("❌ Keras not found in TensorFlow")
            print("   This might indicate an incomplete TensorFlow installation")
            print("   Try reinstalling TensorFlow: pip install tensorflow==2.19.0")
            return False
        
        # Test basic model loading
        print("\n🧪 Testing model loading...")
        try:
            model = tf.keras.models.load_model("asl_letter_model_v3.keras")
            print("✅ Main model loaded successfully")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return False
        
        # Test other dependencies
        print("\n🔍 Checking other dependencies...")
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
        
        import numpy as np
        print(f"✅ NumPy version: {np.__version__}")
        
        import pickle
        print("✅ Pickle imported successfully")
        
        from PIL import Image
        print("✅ PIL imported successfully")
        
        print("\n🎉 All tests passed! TensorFlow 2.19.0 is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   This suggests TensorFlow is not properly installed")
        print("   Try: pip install tensorflow==2.19.0")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tensorflow()
    if success:
        print("\n🚀 Ready to run the ASL application!")
        print("Next steps:")
        print("1. python start_app.py")
        print("2. cd frontend && npm run dev")
    else:
        print("\n❌ Please fix the issues above before running the application.")
        print("\n💡 Troubleshooting tips:")
        print("1. Try: pip uninstall tensorflow tensorflow-intel -y")
        print("2. Then: pip install tensorflow==2.19.0")
        print("3. Run this test again") 