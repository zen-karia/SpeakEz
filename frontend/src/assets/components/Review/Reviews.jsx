import React, { useState } from 'react';
import { FaStar } from 'react-icons/fa';

const StarRating = () => {
  const [rating, setRating] = useState(null);
  const [hover, setHover] = useState(null);

  return (
    <div className="flex">
      {[...Array(5)].map((star, index) => {
        const ratingValue = index + 1;
        return (
          <label key={index}>
            <input
              type="radio"
              name="rating"
              className="hidden"
              value={ratingValue}
              onClick={() => setRating(ratingValue)}
            />
            <FaStar
              className="cursor-pointer"
              color={ratingValue <= (hover || rating) ? '#ffc107' : '#e4e5e9'}
              size={30}
              onMouseEnter={() => setHover(ratingValue)}
              onMouseLeave={() => setHover(null)}
            />
          </label>
        );
      })}
    </div>
  );
};

const sampleReviews = [
    { rating: 5, comment: "This is the best ASL learning tool I've ever used! So intuitive." },
    { rating: 4, comment: "Really helpful for practice. The word recognition is a great feature." },
    { rating: 5, comment: "A fantastic project. Made learning fun and interactive." },
    { rating: 3, comment: "Good start, but sometimes the letter recognition is a bit slow." },
    { rating: 4, comment: "I love the clean interface and the instant feedback. Highly recommend!" },
    { rating: 5, comment: "Finally, a modern way to learn sign language. Thank you!" },
];

const Reviews = () => {
  return (
    <div className="relative z-10 p-10 min-h-screen text-white bg-black bg-opacity-20">
      <h2 className="text-center text-4xl font-bold mb-16">Reviews</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-16 max-w-6xl mx-auto">
        <div className="flex flex-col">
          <h3 className="text-2xl font-semibold mb-6">Share Your Feedback</h3>
          <div className="mb-6">
            <label htmlFor="experience" className="block mb-2 font-medium">
              Your Experience
            </label>
            <textarea
              id="experience"
              rows="5"
              className="w-full p-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              placeholder="Tell us about your experience..."
            ></textarea>
          </div>
          <div className="mb-8">
            <label className="block mb-2 font-medium">Your Rating</label>
            <StarRating />
          </div>
          <button className="w-full py-3 bg-cyan-600 rounded-lg font-bold hover:bg-cyan-700 transition-colors">
            Submit Feedback
          </button>
        </div>

        <div className="flex flex-col">
          <h3 className="text-2xl font-semibold mb-6">Hall of Reviews</h3>
          <div className="bg-gray-800 p-6 rounded-lg h-96 overflow-y-auto border border-gray-700">
            {sampleReviews.map((review, index) => (
              <div key={index} className="border-b border-gray-700 pb-4 mb-4">
                <div className="flex items-center mb-1">
                  {[...Array(review.rating)].map((_, i) => (
                    <FaStar key={i} color="#ffc107" />
                  ))}
                </div>
                <p className="text-gray-300 italic">"{review.comment}"</p>
                <p className="text-right text-xs text-gray-500 mt-2">- Anonymous</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reviews;