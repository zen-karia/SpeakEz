import React, { useState, useEffect } from 'react';
import { FaStar } from 'react-icons/fa';

const StarRating = ({ rating, setRating }) => {
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
    { id: 1, rating: 5, comment: "This is the best ASL learning tool I've ever used! So intuitive.", timestamp: "2024-01-01T00:00:00.000Z" },
    { id: 2, rating: 4, comment: "Really helpful for practice. The word recognition is a great feature.", timestamp: "2024-01-01T00:00:00.000Z" },
    { id: 3, rating: 5, comment: "A fantastic project. Made learning fun and interactive.", timestamp: "2024-01-01T00:00:00.000Z" },
    { id: 4, rating: 3, comment: "Good start, but sometimes the letter recognition is a bit slow.", timestamp: "2024-01-01T00:00:00.000Z" },
    { id: 5, rating: 4, comment: "I love the clean interface and the instant feedback. Highly recommend!", timestamp: "2024-01-01T00:00:00.000Z" },
    { id: 6, rating: 5, comment: "Finally, a modern way to learn sign language. Thank you!", timestamp: "2024-01-01T00:00:00.000Z" },
];

const Reviews = () => {
  const [reviews, setReviews] = useState([]);
  const [newReview, setNewReview] = useState({ rating: null, comment: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [isInitialized, setIsInitialized] = useState(false);

  // Load reviews from localStorage on component mount
  useEffect(() => {
    try {
      const savedReviews = localStorage.getItem('speakez_reviews');
      if (savedReviews) {
        const parsedReviews = JSON.parse(savedReviews);
        setReviews(parsedReviews);
      } else {
        // If no saved reviews, use sample reviews
        setReviews(sampleReviews);
        localStorage.setItem('speakez_reviews', JSON.stringify(sampleReviews));
      }
    } catch (error) {
      console.error('Error loading reviews from localStorage:', error);
      setReviews(sampleReviews);
    } finally {
      setIsInitialized(true);
    }
  }, []);

  // Save reviews to localStorage whenever reviews change (but only after initialization)
  useEffect(() => {
    if (isInitialized && reviews.length > 0) {
      try {
        localStorage.setItem('speakez_reviews', JSON.stringify(reviews));
      } catch (error) {
        console.error('Error saving reviews to localStorage:', error);
      }
    }
  }, [reviews, isInitialized]);

  const handleSubmitReview = async () => {
    // Validate form
    if (!newReview.rating) {
      setSubmitMessage('Please select a rating');
      return;
    }
    if (!newReview.comment.trim()) {
      setSubmitMessage('Please enter a comment');
      return;
    }

    setIsSubmitting(true);
    setSubmitMessage('');

    try {
      // Create new review object
      const reviewToAdd = {
        id: Date.now(), // Simple ID generation
        rating: newReview.rating,
        comment: newReview.comment.trim(),
        timestamp: new Date().toISOString()
      };

      // Add to reviews list
      setReviews(prevReviews => [reviewToAdd, ...prevReviews]);

      // Reset form
      setNewReview({ rating: null, comment: '' });
      setSubmitMessage('Thank you for your review! 🎉');

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSubmitMessage('');
      }, 3000);

    } catch (error) {
      console.error('Error submitting review:', error);
      setSubmitMessage('Error submitting review. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCommentChange = (e) => {
    setNewReview(prev => ({ ...prev, comment: e.target.value }));
  };

  const handleRatingChange = (rating) => {
    setNewReview(prev => ({ ...prev, rating }));
  };

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
              value={newReview.comment}
              onChange={handleCommentChange}
            ></textarea>
          </div>
          <div className="mb-8">
            <label className="block mb-2 font-medium">Your Rating</label>
            <StarRating rating={newReview.rating} setRating={handleRatingChange} />
          </div>
          
          {submitMessage && (
            <div className={`mb-4 p-3 rounded-lg text-center ${
              submitMessage.includes('Thank you') 
                ? 'bg-green-600 text-white' 
                : 'bg-red-600 text-white'
            }`}>
              {submitMessage}
            </div>
          )}
          
          <button 
            className={`w-full py-3 rounded-lg font-bold transition-colors ${
              isSubmitting 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-cyan-600 hover:bg-cyan-700'
            }`}
            onClick={handleSubmitReview}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </div>

        <div className="flex flex-col">
          <h3 className="text-2xl font-semibold mb-6">Hall of Reviews</h3>
          <div className="bg-gray-800 p-6 rounded-lg h-96 overflow-y-auto border border-gray-700">
            {reviews.length === 0 ? (
              <p className="text-gray-400 text-center">No reviews yet. Be the first to share your experience!</p>
            ) : (
              reviews.map((review, index) => (
                <div key={review.id} className="border-b border-gray-700 pb-4 mb-4 last:border-b-0">
                  <div className="flex items-center mb-1">
                    {[...Array(review.rating)].map((_, i) => (
                      <FaStar key={i} color="#ffc107" size={16} />
                    ))}
                  </div>
                  <p className="text-gray-300 italic">"{review.comment}"</p>
                  <p className="text-right text-xs text-gray-500 mt-2">
                    - Anonymous • {new Date(review.timestamp).toLocaleDateString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reviews;