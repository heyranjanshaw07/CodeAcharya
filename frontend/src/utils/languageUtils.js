/**
 * Language utilities for CodeAcharya
 */

/**
 * Returns human-readable language label for display in the UI and confirmation modals.
 */
export const getLanguageDisplayName = (lang) => {
  if (!lang) return '';
  switch (lang.toLowerCase()) {
    case 'python':
      return 'Python';
    case 'c':
      return 'C';
    case 'cpp':
      return 'C++';
    case 'java':
      return 'Java';
    default:
      return lang.charAt(0).toUpperCase() + lang.slice(1);
  }
};

