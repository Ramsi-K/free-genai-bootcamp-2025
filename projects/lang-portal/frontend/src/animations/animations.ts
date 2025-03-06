// src/animations/animations.ts
// Animation utility functions

/**
 * Generate a random pulse animation delay
 */
export function randomPulseDelay(): string {
    const delay = Math.random() * 2; // Random delay between 0 and 2 seconds
    return `${delay}s`;
  }
  
  /**
   * Generate CSS for a glowing effect
   */
  export function getGlowingEffect(color: string, intensity: number = 10): string {
    return `0 0 ${intensity}px ${color}, 0 0 ${intensity * 2}px ${color}`;
  }
  
  /**
   * Get scanning animation style
   */
  export function getScanningAnimation(duration: number = 2): React.CSSProperties {
    return {
      position: 'relative',
      overflow: 'hidden',
      animation: `scanning ${duration}s linear infinite`,
    };
  }
  
  /**
   * Create a typing animation effect
   */
  export function typeText(element: HTMLElement, text: string, speed: number = 50): Promise<void> {
    return new Promise((resolve) => {
      let i = 0;
      element.textContent = '';
      
      function typing() {
        if (i < text.length) {
          element.textContent += text.charAt(i);
          i++;
          setTimeout(typing, speed);
        } else {
          resolve();
        }
      }
      
      typing();
    });
  }
  