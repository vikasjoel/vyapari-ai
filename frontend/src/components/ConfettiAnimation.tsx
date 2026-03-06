/**
 * Confetti animation for "Go Live" celebration
 */

import confetti from 'canvas-confetti';

export function celebrateGoLive() {
  const duration = 3000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

  function randomInRange(min: number, max: number) {
    return Math.random() * (max - min) + min;
  }

  // Burst of confetti
  const interval = setInterval(function () {
    const timeLeft = animationEnd - Date.now();

    if (timeLeft <= 0) {
      clearInterval(interval);
      return;
    }

    const particleCount = 50 * (timeLeft / duration);

    // Indian flag colors: saffron, white, green, gold
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      colors: ['#f97316', '#ea580c', '#ffffff', '#10b981', '#ffd700'],
    });
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      colors: ['#f97316', '#ea580c', '#ffffff', '#10b981', '#ffd700'],
    });
  }, 250);
}

// Quick burst for smaller celebrations
export function quickBurst() {
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#f97316', '#ea580c', '#ffd700'],
  });
}
