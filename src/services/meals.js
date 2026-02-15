import { getDb } from '../db/init.js';
import { logger } from '../utils/logger.js';
import { DateTime } from 'luxon';

export class MealsService {
  
  /**
   * Fetch meals for a date range
   */
  static fetchMeals(startDate, endDate) {
    try {
      const db = getDb();
      const stmt = db.prepare(`
        SELECT id, title, date, meal_type, description, created_at
        FROM meals
        WHERE date >= ? AND date <= ?
        ORDER BY date ASC
      `);
      
      const rows = stmt.all(startDate, endDate);
      
      return rows.map(row => ({
        id: row.id,
        title: row.title,
        date: row.date,
        mealType: row.meal_type,
        description: row.description || '',
        createdAt: row.created_at,
      }));
      
    } catch (error) {
      logger.error('Error in fetchMeals:', error);
      return [];
    }
  }
  
  /**
   * Get a single meal by ID
   */
  static getMeal(mealId) {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM meals WHERE id = ?');
    return stmt.get(mealId);
  }
  
  /**
   * Create a new meal
   */
  static createMeal({ title, date, mealType = 'dinner', description = '' }) {
    const db = getDb();
    const stmt = db.prepare(`
      INSERT INTO meals (title, date, meal_type, description)
      VALUES (?, ?, ?, ?)
    `);
    
    const result = stmt.run(title, date, mealType, description);
    logger.info(`Created meal: ${title} for ${date}`);
    
    return result.lastInsertRowid;
  }
  
  /**
   * Update an existing meal
   */
  static updateMeal(mealId, { title, date, mealType, description }) {
    const db = getDb();
    const stmt = db.prepare(`
      UPDATE meals
      SET title = ?, date = ?, meal_type = ?, description = ?
      WHERE id = ?
    `);
    
    const result = stmt.run(title, date, mealType, description, mealId);
    logger.info(`Updated meal ${mealId}`);
    
    return result.changes > 0;
  }
  
  /**
   * Delete a meal
   */
  static deleteMeal(mealId) {
    const db = getDb();
    const stmt = db.prepare('DELETE FROM meals WHERE id = ?');
    const result = stmt.run(mealId);
    
    logger.info(`Deleted meal ${mealId}`);
    return result.changes > 0;
  }
  
  /**
   * Get all meals (with optional limit)
   */
  static getAllMeals(limit = 100) {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM meals ORDER BY date DESC LIMIT ?');
    return stmt.all(limit);
  }

  /**
   * Get upcoming meals
   */
  static getUpcomingMeals(limit = 100) {
    const db = getDb();
    const stmt = db.prepare("SELECT * FROM meals WHERE date >= date('now') ORDER BY date ASC LIMIT ?");
    return stmt.all(limit);
  }

  /**
   * Get past meals (history)
   */
  static getPastMeals(limit = 100) {
    const db = getDb();
    const stmt = db.prepare("SELECT * FROM meals WHERE date < date('now') ORDER BY date DESC LIMIT ?");
    return stmt.all(limit);
  }

  /**
   * Create recurring meals
   * @param {Object} params
   * @param {string} params.title
   * @param {string} params.startDate - ISO date string
   * @param {number} params.dayOfWeek - 1 (Monday) to 7 (Sunday)
   * @param {number} params.weeks - Number of weeks to repeat
   * @param {string} params.mealType
   * @param {string} params.description
   */
  static createRecurringMeals({ title, startDate, dayOfWeek, weeks, mealType, description }) {
    let date = DateTime.fromISO(startDate);

    // Find the first occurrence of dayOfWeek on or after startDate
    // dayOfWeek should be 1-7 (Mon-Sun)
    while (date.weekday !== dayOfWeek) {
      date = date.plus({ days: 1 });
    }

    let count = 0;
    for (let i = 0; i < weeks; i++) {
      this.createMeal({
        title,
        date: date.toISODate(),
        mealType,
        description
      });
      date = date.plus({ weeks: 1 });
      count++;
    }

    return count;
  }
}
