import React, { useRef, useState, useCallback, useEffect } from 'react';
import Webcam from "react-webcam";

const videoConstraints = {
  width: 400,
  height: 240,
  facingMode: "user"
};

// AVAILABLE LETTERS SET - CHANGE THIS TO CUSTOMIZE WHICH LETTERS TO PRACTICE
const AVAILABLE_LETTERS = ['B', 'W', 'A', 'R', 'K', 'J'];

// You can customize this set to practice specific letters:
// Examples:
// const AVAILABLE_LETTERS = ['A', 'B', 'C']; // Only practice A, B, C
// const AVAILABLE_LETTERS = ['A', 'E', 'O', 'S', 'M', 'N', 'T']; // Only closed-fist letters
// const AVAILABLE_LETTERS = ['B', 'W']; // Only B and W
// const AVAILABLE_LETTERS = ['A', 'B', 'C', 'D', 'E']; // Only first 5 letters

const LearnMain = () => {
  const webcamRef = useRef(null);
  const [webcamActive, setWebcamActive] = useState(false);
  const [currentLetter, setCurrentLetter] = useState('');
  const [isLearning, setIsLearning] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [lettersCompleted, setLettersCompleted] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  // Function to get a random letter from the available set
  const getRandomLetter = () => {
    const randomIndex = Math.floor(Math.random() * AVAILABLE_LETTERS.length);
    return AVAILABLE_LETTERS[randomIndex];
  };

  // Function to capture and send frame to backend
  const captureAndPredict = useCallback(async () => {
    if (!webcamRef.current || !isLearning || isProcessing) return;

    setIsProcessing(true);
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageSrc }),
      });

      const result = await response.json();
      
      if (result.detected && result.prediction) {
        setPrediction(result.prediction);
        setConfidence(result.confidence);
        
        // Check if prediction matches current letter
        if (result.prediction === currentLetter && result.confidence > 0.5) {
          setFeedback('Correct! 🎉');
          setLettersCompleted(prev => prev + 1);
          
          // Get next random letter after a short delay
          setTimeout(() => {
            const nextLetter = getRandomLetter();
            setCurrentLetter(nextLetter);
            setFeedback('');
            setPrediction(null);
          }, 1500);
        } else {
          setFeedback(`Try again! You showed: ${result.prediction}`);
        }
      } else {
        setFeedback('No hand detected. Please show your hand clearly.');
      }
    } catch (error) {
      console.error('Error predicting:', error);
      setFeedback('Error connecting to server. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  }, [isLearning, currentLetter, isProcessing]);

  // Continuous prediction when learning is active
  useEffect(() => {
    let interval;
    if (isLearning && webcamActive) {
      interval = setInterval(captureAndPredict, 1000); // Predict every second
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLearning, webcamActive, captureAndPredict]);

  const startLearning = () => {
    setWebcamActive(true);
    setIsLearning(true);
    setCurrentLetter(getRandomLetter()); // Start with a random letter
    setLettersCompleted(0);
    setFeedback('');
    setPrediction(null);
  };

  const stopLearning = () => {
    setWebcamActive(false);
    setIsLearning(false);
    setFeedback('');
    setPrediction(null);
  };

  const resetLearning = () => {
    setCurrentLetter(getRandomLetter());
    setLettersCompleted(0);
    setFeedback('');
    setPrediction(null);
  };

  return (
    <div className="p-8 flex flex-col items-center">
      <div className="flex flex-col items-center mb-8">
        <span className="text-2xl font-bold mb-2">Take a look at the ASL Alphabet</span>
        <img
          src="asl.jpg"
          alt="ASL Alphabet"
          className="w-[400px] h-[300px] mt-2"
        />
      </div>

      {/* Learning Interface */}
      <div className="flex flex-col items-center w-full max-w-2xl">
        {!isLearning ? (
          <div className="text-center">
            <p className="mb-4 text-gray-600">
              Interactive ASL Learning
            </p>
            <button
              onClick={startLearning}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              Start Learning
            </button>
          </div>
        ) : (
          <div className="w-full">
            {/* Progress and Stats */}
            <div className="flex justify-center items-center mb-4 p-4 bg-gray-100 rounded-lg">
              <div>
                <span className="font-semibold">Letters Completed: </span>
                <span>{lettersCompleted}</span>
              </div>
            </div>

            {/* Current Letter Prompt */}
            <div className="text-center mb-6">
              <h3 className="text-3xl font-bold text-blue-600 mb-2">
                Show the letter: <span className="text-4xl">{currentLetter}</span>
              </h3>
              <p className="text-gray-600">Make the ASL sign for "{currentLetter}"</p>
            </div>

            {/* Webcam */}
            <div className="flex justify-center mb-4">
              {webcamActive && (
                <div className="relative">
                  <Webcam
                    audio={false}
                    height={240}
                    width={400}
                    videoConstraints={videoConstraints}
                    ref={webcamRef}
                    className="rounded-lg border-2 border-cyan-400"
                    screenshotFormat="image/jpeg"
                  />
                  <button
                    className="absolute top-2 right-2 text-black rounded-full w-8 h-8 flex items-center justify-center font-bold"
                    onClick={stopLearning}
                    title="Stop Learning"
                  >
                    ×
                  </button>
                </div>
              )}
            </div>

            {/* Feedback and Prediction */}
            <div className="text-center space-y-2">
              {feedback && (
                <div className={`p-3 rounded-lg font-semibold ${
                  feedback.includes('Correct') 
                    ? 'bg-green-100 text-green-800' 
                    : feedback.includes('Error') 
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {feedback}
                </div>
              )}
              
              {prediction && (
                <div className="p-2 bg-gray-100 rounded">
                  <span className="font-semibold">Detected: </span>
                  <span className="text-lg">{prediction}</span>
                  <span className="ml-2 text-sm text-gray-600">
                    (Confidence: {(confidence * 100).toFixed(1)}%)
                  </span>
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="flex justify-center gap-4 mt-6">
              <button
                onClick={resetLearning}
                className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                Reset Progress
              </button>
              <button
                onClick={stopLearning}
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                Stop Learning
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LearnMain;