import React, { useRef, useState, useCallback } from 'react';
import Webcam from "react-webcam";

const videoConstraints = {
    width: 400,
    height: 240,
    facingMode: "user"
  };

const LearnMain = () => {
  const webcamRef1 = useRef(null);
  const webcamRef2 = useRef(null);
  const [webcamActive1, setWebcamActive1] = useState(false);
  const [webcamActive2, setWebcamActive2] = useState(false);

  // Example: Capture a frame when capturing is true
  const captureFrame = useCallback(() => {
    if (webcamActive1 && webcamRef1.current) {
      const imageSrc = webcamRef1.current.getScreenshot();
      // Do something with imageSrc (send to backend, process, etc.)
      // You can repeat this at intervals if you want continuous capture
    }
  }, [webcamActive1]);

  // Optionally, use useEffect to capture frames at intervals when capturing is true
  // (not shown here for brevity)

  return (
    <div className="p-8 flex flex-col items-center">
      <div className="flex flex-col items-center mb-8">
        <span className="text-2xl font-bold mb-2">Take a look at The ASL Alphabet</span>
        <img
          src="asl.jpg"
          alt="ASL Alphabet"
          className="w-[400px] h-[300px] mt-2"
        />
      </div>
      <div className="flex flex-row gap-8 justify-center w-full gap-40">
        <div className="flex flex-col items-center relative">
          <span className="font-semibold mb-2">Letter Recognition</span>
          {!webcamActive1 ? (
            <button
              className="animated-gradient-text underline decoration-cyan-400 hover:opacity-50"
              onClick={() => setWebcamActive1(true)}
            >
              Start
            </button>
          ) : (
            <>
              <Webcam
                audio={false}
                height={240}
                width={400}
                videoConstraints={videoConstraints}
                ref={webcamRef1}
                className="rounded-lg border-2 border-cyan-400"
                screenshotFormat="image/jpeg"
              />
              <button
                className="absolute right-[4px] bg-white-500 text-black rounded-full w-8 h-8 flex items-center justify-center font-bold"
                onClick={() => setWebcamActive1(false)}
                title="Close"
              >
                ×
              </button>
            </>
          )}
        </div>
        <div className="flex flex-col items-center relative">
          <span className="font-semibold mb-2">Word Recognition</span>
          {!webcamActive2 ? (
            <button
              className="animated-gradient-text underline decoration-cyan-400 hover:opacity-50"
              onClick={() => setWebcamActive2(true)}
            >
              Start
            </button>
          ) : (
            <>
              <Webcam
                audio={false}
                height={240}
                width={400}
                videoConstraints={videoConstraints}
                ref={webcamRef2}
                className="rounded-lg border-2 border-cyan-400"
                screenshotFormat="image/jpeg"
              />
              <button
                className="absolute right-[4px] bg-white-500 text-black rounded-full w-8 h-8 flex items-center justify-center font-bold"
                onClick={() => setWebcamActive2(false)}
                title="Close"
              >
                ×
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default LearnMain