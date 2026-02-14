
/**
 * Get the current seasonal theme class based on the month.
 * @returns {string} The CSS class for the theme ('theme-valentine', 'theme-thanksgiving', 'theme-christmas', or '')
 */
export function getTheme() {
  const month = new Date().getMonth(); // 0-11

  switch (month) {
    case 1: // February
      return 'theme-valentine';
    case 10: // November
      return 'theme-thanksgiving';
    case 11: // December
      return 'theme-christmas';
    default:
      return '';
  }
}
