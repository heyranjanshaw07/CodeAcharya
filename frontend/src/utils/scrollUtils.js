import { useRef, useCallback } from 'react';

/**
 * Universal Action Response Auto-Scroll Utility
 * 
 * Provides smooth, reliable scrolling to action result sections while:
 * 1. Accounting for sticky navigation header offsets.
 * 2. Avoiding unnecessary scrolling if the target element is already comfortably visible.
 * 3. Handling both React refs and direct DOM elements.
 * 4. Waiting for DOM updates (via requestAnimationFrame).
 */

const DEFAULT_HEADER_OFFSET = 85;

/**
 * Smoothly scrolls the window to bring the target element into view below the sticky header.
 * 
 * @param {HTMLElement|React.RefObject} target - The DOM element or React ref.
 * @param {Object} [options]
 * @param {number} [options.offset=85] - Header offset in pixels.
 * @param {string} [options.behavior='smooth'] - Scroll behavior ('smooth' | 'auto').
 * @param {boolean} [options.force=false] - Force scroll even if partially visible.
 * @returns {boolean} Whether scrolling occurred.
 */
export function autoScrollTo(target, options = {}) {
  const element = target && typeof target === 'object' && 'current' in target 
    ? target.current 
    : target;

  if (!element || typeof window === 'undefined') return false;

  const offset = options.offset ?? DEFAULT_HEADER_OFFSET;
  const behavior = options.behavior || 'smooth';
  const rect = element.getBoundingClientRect();
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

  // Check if the top of the section is already comfortably in view below the header
  const isAlreadyVisible = (
    rect.top >= offset - 15 &&
    rect.top <= viewportHeight * 0.65 &&
    rect.bottom > offset
  );

  if (isAlreadyVisible && !options.force) {
    return false; // Skip redundant scrolling
  }

  const elementTop = rect.top + window.pageYOffset;
  const targetY = Math.max(0, elementTop - offset);

  try {
    window.scrollTo({
      top: targetY,
      behavior: behavior
    });
  } catch (err) {
    // Fallback for browsers that don't support window.scrollTo with options
    element.scrollIntoView({ behavior: behavior, block: 'start' });
  }

  return true;
}

/**
 * Scrolls an internal container (such as inside a modal) to reveal a target child element.
 * 
 * @param {HTMLElement|React.RefObject} containerTarget - The scrollable parent container.
 * @param {HTMLElement|React.RefObject} childTarget - The child element to reveal.
 * @param {Object} [options]
 */
export function scrollContainerToChild(containerTarget, childTarget, options = {}) {
  const container = containerTarget && 'current' in containerTarget 
    ? containerTarget.current 
    : containerTarget;
  const child = childTarget && 'current' in childTarget 
    ? childTarget.current 
    : childTarget;

  if (!container || !child) return;

  const behavior = options.behavior || 'smooth';
  const containerRect = container.getBoundingClientRect();
  const childRect = child.getBoundingClientRect();

  const isChildVisible = (
    childRect.top >= containerRect.top &&
    childRect.bottom <= containerRect.bottom
  );

  if (isChildVisible && !options.force) {
    return;
  }

  const targetScrollTop = child.offsetTop - (options.offsetTop || 16);
  try {
    container.scrollTo({
      top: Math.max(0, targetScrollTop),
      behavior: behavior
    });
  } catch (err) {
    child.scrollIntoView({ behavior: behavior, block: 'nearest' });
  }
}

/**
 * Reusable React Hook for action result auto-scrolling.
 * 
 * @param {Object} [defaultOptions] - Default options passed to autoScrollTo.
 * @returns {[React.RefObject, (customOptions?: Object) => void]} [targetRef, scrollToTarget]
 */
export function useAutoScroll(defaultOptions = {}) {
  const targetRef = useRef(null);

  const scrollToTarget = useCallback((customOptions = {}) => {
    // requestAnimationFrame ensures the DOM has re-rendered the loading or result state
    requestAnimationFrame(() => {
      autoScrollTo(targetRef, { ...defaultOptions, ...customOptions });
    });
  }, [defaultOptions]);

  return [targetRef, scrollToTarget];
}
