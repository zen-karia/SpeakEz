# SpeakEZ: Giving Your Hands a Voice 🎤🤟

# Inspiration 💡
“Imagine a world where every hand gesture finds its voice.”
Our goal was to bridge silence and sound, empowering every signer to be heard, whether ordering coffee ☕ or joining a conversation 🗣️.

# What it does 🚀
SpeakEZ is a lightweight glove that reads finger-bend data and instantly speaks your ASL signs, no cameras or bulky apps required. It turns each gesture into clear, spoken words so communication flows naturally 🌊.

# How we built it 🛠️
Browser-Based Classifier 🖥️: Trained a CNN on hand-shape images for initial ASL letter recognition—a teaching tool for ASL learners.

Flex-Sensor Glove Prototype 🤖: Integrated bend sensors into a glove to capture live finger positions.

ML Model for Glove Data 🧠: Developed a time-series classifier to map sensor streams to ASL letters and words.

Real-Time Translation 🌐: Streamed sensor data over Wi-Fi, classified on the fly, and synthesized speech 🔊.

# Challenges we ran into ⚠️
Calibrating sensor drift across different hand sizes 🤏🖐️

Reducing classification latency ⏱️

Building a robust training dataset for dynamic gestures 🔄

# Accomplishments that we’re proud of 🏆
Achieved 95% accuracy on flex-sensor letter classification 🎯

Demoed “I ❤️ YOU” and letter translation in under 2 seconds ⏲️

Created an intuitive web quiz for ASL learners 📝

# What we learned 📚
User-centric design is critical: simplicity beat complexity every time ✨

Sensor fusion and data augmentation improve robustness 🔧

Real-time ML demands careful optimization of both model and hardware ⚡

#What’s next for SpeakEZ 🔭
Expand vocabulary to include whole words and phrases 🗨️

Add multilingual support for international sign systems 🌍

Refine glove ergonomics and battery life for all-day wear 🔋
