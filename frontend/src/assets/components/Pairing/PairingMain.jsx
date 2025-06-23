import React, { useState, useEffect, useRef } from 'react';

const PairingMain = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [currentLetter, setCurrentLetter] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [lastReceived, setLastReceived] = useState(null);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [connectionMessage, setConnectionMessage] = useState('');
  const [lastESP32DataTime, setLastESP32DataTime] = useState(null);
  
  const audioRef = useRef(null);
  const intervalRef = useRef(null);

  // Audio file mapping
  const letterAudioMap = {
    'A': '/audio/A.mp3', 'B': '/audio/B.mp3', 'C': '/audio/C.mp3',
    'D': '/audio/D.mp3', 'E': '/audio/E.mp3', 'F': '/audio/F.mp3',
    'G': '/audio/G.mp3', 'H': '/audio/H.mp3', 'I': '/audio/I.mp3',
    'K': '/audio/K.mp3', 'L': '/audio/L.mp3', 'M': '/audio/M.mp3', 
    'N': '/audio/N.mp3', 'O': '/audio/O.mp3', 'P': '/audio/P.mp3',
    'Q': '/audio/Q.mp3', 'R': '/audio/R.mp3', 'S': '/audio/S.mp3',
    'T': '/audio/T.mp3', 'U': '/audio/U.mp3', 'V': '/audio/V.mp3',
    'W': '/audio/W.mp3', 'X': '/audio/X.mp3', 'Y': '/audio/Y.mp3',
    'Z': 'None'
  };

  // Start ESP32 connection monitoring
  const startPairingMode = async () => {
    setIsConnecting(true);
    setConnectionStatus('Connecting to ESP32...');
    setConnectionMessage('Initializing connection...');

    try {
      // First, check if Flask backend is running
      const healthResponse = await fetch('http://localhost:5000/health');
      if (!healthResponse.ok) {
        throw new Error('Flask backend not running');
      }

      // Check ESP32 status
      const statusResponse = await fetch('http://localhost:5000/esp32/status');
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        console.log('ESP32 Status:', statusData);
      }

      setIsConnected(true);
      setConnectionStatus('Connected to ESP32');
      setConnectionMessage('Connection Successful! 🎉');
      
      // Start monitoring for ESP32 data
      startDataMonitoring();

    } catch (error) {
      console.error('Connection failed:', error);
      setIsConnected(false);
      setConnectionStatus('Connection Failed');
      setConnectionMessage('Failed to connect. Please check your ESP32 and Flask backend.');
    } finally {
      setIsConnecting(false);
    }
  };

  // Stop pairing mode
  const stopPairingMode = () => {
    setIsConnected(false);
    setConnectionStatus('Disconnected');
    setConnectionMessage('');
    setCurrentLetter(null);
    setConfidence(0);
    setLastReceived(null);
    
    // Clear any ongoing monitoring
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    // Stop any playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  };

  // Monitor ESP32 data in real-time
  const startDataMonitoring = () => {
    // Poll for ESP32 data every 2 seconds
    intervalRef.current = setInterval(async () => {
      try {
        // Check ESP32 status and look for recent predictions
        const statusResponse = await fetch('http://localhost:5000/esp32/status');
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          // Do not update connectionMessage here anymore
          // if (statusData.esp32_model_loaded) {
          //   setConnectionMessage('ESP32 CNN Model Loaded - Ready for ASL Recognition');
          // } else {
          //   setConnectionMessage('ESP32 Connected - Using Placeholder Model');
          // }
        }
      } catch (error) {
        console.error('Data monitoring error:', error);
        setConnectionMessage('Connection lost. Trying to reconnect...');
      }
    }, 2000);
  };

  // Play audio for detected letter
  const playLetterAudio = (letter) => {
    try {
      const audioUrl = letterAudioMap[letter];
      if (audioUrl && audioEnabled) {
        console.log(`🔊 Playing audio for letter: ${letter} (${audioUrl})`);
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        audio.play().catch(error => {
          console.error('Error playing audio:', error);
        });
      }
    } catch (error) {
      console.error('Error creating audio:', error);
    }
  };

  // Process ESP32 prediction response
  const processESP32Prediction = (result) => {
    console.log('📊 Processing ESP32 prediction:', result);
    setLastReceived(JSON.stringify(result, null, 2));
    
    if (result.detected && result.prediction) {
      console.log(`🎯 Letter detected: ${result.prediction} (confidence: ${result.confidence})`);
      setCurrentLetter(result.prediction);
      setConfidence(result.confidence);
      
      // Automatically play audio for the detected letter
      playLetterAudio(result.prediction);
      
      // Update connection message to show successful detection
      setConnectionMessage(`Letter ${result.prediction} detected! Audio played.`);
      setLastESP32DataTime(Date.now());
    } else {
      console.log('❌ No letter detected in this data');
      setCurrentLetter(null);
      setConfidence(0);
    }
  };

  // Simulate ESP32 data reception (for testing)
  const simulateESP32Data = async () => {
    if (!isConnected) return;

    try {
      console.log('🧪 Simulating ESP32 sensor data...');
      
      // Simulate sensor data for testing
      const testSensorData = [
        Math.floor(Math.random() * 1024), // Thumb
        Math.floor(Math.random() * 1024), // Index
        Math.floor(Math.random() * 1024), // Middle
        Math.floor(Math.random() * 1024), // Ring
        Math.floor(Math.random() * 1024)  // Pinky
      ];

      console.log('📡 Sending sensor data to Flask backend:', testSensorData);

      const response = await fetch('http://localhost:5000/esp32/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sensor_values: testSensorData }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Received prediction from Flask backend:', result);
        processESP32Prediction(result);
      } else {
        console.error('❌ Error from Flask backend:', response.status);
      }
    } catch (error) {
      console.error('Error simulating ESP32 data:', error);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  // Auto-start pairing mode when component mounts
  useEffect(() => {
    startPairingMode();
    
    // Cleanup on unmount
    return () => {
      stopPairingMode();
    };
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      if (isConnected) {
        if (lastESP32DataTime && Date.now() - lastESP32DataTime < 10000) {
          setConnectionStatus('Connected to ESP32');
          setConnectionMessage('Connection Successful! 🎉');
        } else {
          setConnectionStatus('Waiting for ESP32 data...');
          setConnectionMessage('No recent data from ESP32. Please check your device.');
        }
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [isConnected, lastESP32DataTime]);

  useEffect(() => {
    if (!isConnected) return;
    const poll = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:5000/esp32/latest');
        if (res.ok) {
          const data = await res.json();
          processESP32Prediction(data);
        }
      } catch (e) {
        // Optionally handle error
      }
    }, 2000);
    return () => clearInterval(poll);
  }, [isConnected]);

  return (
    <div className="p-8 flex flex-col items-center">
      <div className="flex flex-col items-center mb-8">
        <span className="text-2xl font-bold mb-2">ESP32 Glove Pairing Mode</span>
        <p className="text-gray-600 text-center max-w-md">
          Real-time ASL letter recognition with audio output using ESP32 flex sensors.
        </p>
      </div>

      <div className="flex flex-col items-center w-full max-w-2xl space-y-6">
        {/* Connection Status */}
        <div className="w-full p-4 bg-gray-100 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold">Connection Status:</span>
            <span className={`px-2 py-1 rounded text-sm ${
              isConnected ? 'bg-green-100 text-green-800' : 
              isConnecting ? 'bg-yellow-100 text-yellow-800' : 
              'bg-red-100 text-red-800'
            }`}>
              {connectionStatus}
            </span>
          </div>
          
          {connectionMessage && (
            <div className={`p-3 rounded-lg text-center ${
              connectionMessage.includes('Successful') 
                ? 'bg-green-100 text-green-800' 
                : connectionMessage.includes('Failed') 
                ? 'bg-red-100 text-red-800'
                : 'bg-blue-100 text-blue-800'
            }`}>
              {connectionMessage}
            </div>
          )}
        </div>

        {/* Audio Controls */}
        <div className="w-full p-4 bg-gray-100 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="font-semibold">Audio Output:</span>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={audioEnabled}
                onChange={(e) => setAudioEnabled(e.target.checked)}
                className="mr-2"
              />
              <span>Enable Audio</span>
            </label>
          </div>
        </div>

        {/* Current Letter Display */}
        {currentLetter && (
          <div className="w-full p-6 bg-cyan-100 rounded-lg text-center">
            <h3 className="text-lg font-semibold mb-2">Detected Letter:</h3>
            <div className="text-6xl font-bold text-cyan-700">{currentLetter}</div>
            <p className="text-sm text-gray-600 mt-2">
              Confidence: {(confidence * 100).toFixed(1)}%
            </p>
            {audioEnabled && (
              <p className="text-sm text-gray-600">Audio played automatically</p>
            )}
          </div>
        )}

        {/* Test Button */}
        <div className="w-full p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold mb-2">Test ESP32 Integration:</h3>
          <button
            onClick={simulateESP32Data}
            disabled={!isConnected}
            className={`px-4 py-2 rounded-lg font-bold transition-colors ${
              isConnected 
                ? 'bg-blue-500 hover:bg-blue-600 text-white' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Simulate ESP32 Data
          </button>
          <p className="text-xs text-gray-600 mt-2">
            Click to test the ESP32 prediction endpoint with random sensor data
          </p>
        </div>

        {/* Last Received Data */}
        {lastReceived && (
          <div className="w-full p-4 bg-gray-100 rounded-lg">
            <h3 className="font-semibold mb-2">Last Received Data:</h3>
            <pre className="bg-gray-800 text-green-400 p-3 rounded text-xs overflow-x-auto max-h-40">
              {lastReceived}
            </pre>
          </div>
        )}

        {/* Instructions */}
        <div className="w-full p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold mb-2">Setup Instructions:</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
            <li>Ensure your ESP32 is powered on and connected to WiFi</li>
            <li>Upload esp32_example.ino to your ESP32</li>
            <li>Connect 5 flex sensors to analog pins A0-A4</li>
            <li>Start Flask backend: python app.py</li>
            <li>Make ASL signs with your glove - letters will be detected in real-time</li>
            <li>Audio will play automatically for each detected letter (if enabled)</li>
          </ol>
        </div>

        {/* Connection Info */}
        <div className="w-full p-4 bg-gray-100 rounded-lg">
          <h3 className="font-semibold mb-2">Connection Information:</h3>
          <div className="text-sm space-y-1">
            <p><strong>Flask Backend:</strong> http://localhost:5000</p>
            <p><strong>ESP32 Endpoint:</strong> /esp32/predict</p>
            <p><strong>Data Format:</strong> JSON with 5 sensor values</p>
            <p><strong>Update Frequency:</strong> 1 per second</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PairingMain; 