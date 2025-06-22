import React, { useState } from 'react'
import LearnMain from '../Learn/LearnMain'
import PairingMain from '../Pairing/PairingMain'

const HeroMain = () => {
  const [showModal, setShowModal] = useState(false);
  const [showModal2, setShowModal2] = useState(false);

  return (
    <div className='flex flex-col items-center justify-center h-screen px-4'>
      <h1 className='text-4xl sm:text-6xl font-bold text-white mb-5 text-center'>
        Welcome to <span className="animated-gradient-text text-4xl sm:text-6xl font-bold">SpeakEz</span>
      </h1>
      <h3 className='text-lg sm:text-2xl text-white font-bold text-center'>Your hands have a voice!!!</h3>
      <button
        className='bg-black-500 text-2xl sm:text-3xl font-bold mt-4 px-4 py-2 rounded-lg underline'
        onClick={() => setShowModal(true)}
      >
        <span className='animated-gradient-text underline decoration-cyan-400 hover:opacity-50'>Try It Yourself</span>
      </button>
      <button
        className='bg-black-500 text-2xl sm:text-3xl font-bold mt-4 px-4 py-2 rounded-lg underline'
        onClick={() => setShowModal2(true)}
      >
        <span className='animated-gradient-text underline decoration-cyan-400 hover:opacity-50'>Enter Pairing Mode</span>
      </button>
      <div
        className={`
          fixed left-0 bottom-0 w-full h-full z-50
          transition-transform duration-500 ease-in-out bg-white
          ${showModal ? "translate-y-0" : "translate-y-full"}
          flex flex-col items-center justify-center overflow-y-auto
        `}
        style={{ pointerEvents: showModal ? "auto" : "none" }}
      >
        <div className="absolute inset-0 bg-white bg-opacity-100 z-0"></div>
        <div className="relative z-10 flex flex-col w-full h-full">
          <button
            className="absolute top-4 right-4 text-4xl text-black font-bold mr-5"
            onClick={() => setShowModal(false)}
          >
            ×
          </button>
          <h2 className="text-3xl font-bold mb-4 text-cyan-700"><LearnMain /></h2>
        </div>
      </div>
      <div
        className={`
          fixed left-0 bottom-0 w-full h-full z-50
          transition-transform duration-500 ease-in-out bg-white
          ${showModal2 ? "translate-y-0" : "translate-y-full"}
          flex flex-col items-center justify-center overflow-y-auto
        `}
        style={{ pointerEvents: showModal2 ? "auto" : "none" }}
      >
        <div className="absolute inset-0 bg-white bg-opacity-100 z-0"></div>
        <div className="relative z-10 flex flex-col w-full h-full">
          <button
            className="absolute top-4 right-4 text-4xl text-black font-bold mr-5"
            onClick={() => setShowModal2(false)}
          >
            ×
          </button>
          <h2 className="text-3xl font-bold mb-4 text-cyan-700"><PairingMain /></h2>
        </div>
      </div>
    </div>
  )
}

export default HeroMain