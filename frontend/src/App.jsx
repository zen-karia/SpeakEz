import { useEffect, useRef } from 'react'
import './index.css'
import HeroMain from './assets/components/Hero/HeroMain'

function getRandom(min, max) {
  return Math.random() * (max - min) + min;
}

function Stars({ count = 20 }) {
  const ref = useRef();
  const stars = useRef([]);

  useEffect(() => {
    stars.current = Array.from({ length: count }).map(() => {
      const angle = getRandom(0, 2 * Math.PI);
      return {
        x: getRandom(0, 100),
        y: getRandom(0, 100),
        dx: Math.cos(angle) * getRandom(0.02, 0.08), 
        dy: Math.sin(angle) * getRandom(0.02, 0.08),
      };
    });

    const container = ref.current;
    container.innerHTML = "";
    const starDivs = stars.current.map((star, i) => {
      const div = document.createElement("div");
      div.className = "star";
      div.style.position = "absolute";
      div.style.width = "4px";
      div.style.height = "4px";
      div.style.background = "#6fffe9";
      div.style.borderRadius = "50%";
      div.style.boxShadow = "0 0 8px 2px #6fffe9, 0 0 2px 1px #fff";
      div.style.opacity = "0.8";
      container.appendChild(div);
      return div;
    });

    function animate() {
      stars.current.forEach((star, i) => {
        // Update position
        star.x += star.dx;
        star.y += star.dy;

        // Wrap around
        if (star.x < 0) star.x += 100;
        if (star.x > 100) star.x -= 100;
        if (star.y < 0) star.y += 100;
        if (star.y > 100) star.y -= 100;

        // Update DOM
        starDivs[i].style.left = `${star.x}%`;
        starDivs[i].style.top = `${star.y}%`;
      });
      requestAnimationFrame(animate);
    }

    animate();

    // Cleanup on unmount
    return () => {
      container.innerHTML = "";
    };
  }, [count]);

  return <div ref={ref} className="stars-overlay" />;
}

function App() {
  return (
    <div className="min-h-screen w-full bg-star-gradient bg-star-grid relative overflow-hidden">
      <div className="grid-overlay"></div>
      <Stars count={30} />
      <div>
        <HeroMain />
      </div>
    </div>
  );
}

export default App
