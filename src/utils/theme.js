import { DateTime } from 'luxon';

/**
 * Returns the theme based on the current month.
 * @param {Date} [dateOverride] - Optional date object to override current date.
 * @returns {string} The theme name ('valentines', 'thanksgiving', 'christmas', or 'default').
 */
export function getTheme(dateOverride = null) {
  const now = dateOverride ? DateTime.fromJSDate(dateOverride) : DateTime.now();
  const month = now.month;

  if (month === 2) return 'valentines';
  if (month === 11) return 'thanksgiving';
  if (month === 12) return 'christmas';

  return 'default';
}
