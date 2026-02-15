import { test, beforeEach, afterEach, describe } from 'node:test';
import assert from 'node:assert';
import { MealsService } from './meals.js';
import { closeDb, initDatabase } from '../db/init.js';
import { config } from '../config/index.js';
import { DateTime } from 'luxon';

// Use in-memory database for testing
config.databasePath = ':memory:';

describe('MealsService', () => {
  beforeEach(() => {
    closeDb();
    initDatabase();
  });

  afterEach(() => {
    closeDb();
  });

  test('getUpcomingMeals returns only future meals', () => {
    const today = DateTime.now().toISODate();
    const futureDate = DateTime.now().plus({ days: 2 }).toISODate();
    const pastDate = DateTime.now().minus({ days: 2 }).toISODate();

    MealsService.createMeal({ title: 'Future Meal', date: futureDate });
    MealsService.createMeal({ title: 'Today Meal', date: today });
    MealsService.createMeal({ title: 'Past Meal', date: pastDate });

    const upcoming = MealsService.getUpcomingMeals();
    assert.strictEqual(upcoming.length, 2); // Today + Future
    // upcoming is ordered by ASC date
    // if today < futureDate (which it is), then index 0 is Today
    assert.strictEqual(upcoming[0].title, 'Today Meal');
    assert.strictEqual(upcoming[1].title, 'Future Meal');
  });

  test('getPastMeals returns only past meals', () => {
    const futureDate = DateTime.now().plus({ days: 2 }).toISODate();
    const pastDate = DateTime.now().minus({ days: 2 }).toISODate();
    const pastDateOlder = DateTime.now().minus({ days: 4 }).toISODate();

    MealsService.createMeal({ title: 'Future Meal', date: futureDate });
    MealsService.createMeal({ title: 'Past Meal', date: pastDate });
    MealsService.createMeal({ title: 'Older Past Meal', date: pastDateOlder });

    const history = MealsService.getPastMeals();
    assert.strictEqual(history.length, 2);
    // past meals is ordered by DESC date (most recent first)
    // pastDate > pastDateOlder
    assert.strictEqual(history[0].title, 'Past Meal');
    assert.strictEqual(history[1].title, 'Older Past Meal');
  });

  test('createRecurringMeals creates correct number of meals', () => {
    const start = DateTime.now().toISODate();
    // Use a Monday (1)
    const dayOfWeek = 1;
    const weeks = 4;

    const count = MealsService.createRecurringMeals({
        title: 'Recurring Lunch',
        startDate: start,
        dayOfWeek: dayOfWeek,
        weeks: weeks,
        mealType: 'lunch'
    });

    assert.strictEqual(count, 4);

    const allMeals = MealsService.getAllMeals();
    assert.strictEqual(allMeals.length, 4);

    // Sort ascending for easier check
    const sorted = allMeals.sort((a, b) => a.date.localeCompare(b.date));

    for (let i = 0; i < sorted.length - 1; i++) {
        const d1 = DateTime.fromISO(sorted[i].date);
        const d2 = DateTime.fromISO(sorted[i+1].date);
        const diff = d2.diff(d1, 'days').toObject().days;
        assert.ok(Math.abs(diff - 7) < 0.1, `Dates should be 7 days apart, got ${diff}`);
        assert.strictEqual(d1.weekday, 1, 'Should be Monday');
    }
    // Check last one too
    const last = DateTime.fromISO(sorted[sorted.length-1].date);
    assert.strictEqual(last.weekday, 1, 'Should be Monday');
  });
});
