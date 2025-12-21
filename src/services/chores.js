import { getDb } from '../db/init.js';
import { logger } from '../utils/logger.js';

export class ChoreService {
  
  /**
   * Fetch chore occurrences with optional filters
   */
  static fetchChores({ start, end, includeCompleted = true, limit } = {}) {
    const db = getDb();
    
    let query = `
      SELECT 
        c.id,
        c.task_id,
        c.due_date,
        c.status,
        c.completed_at,
        c.ignored_at,
        m.title,
        m.assigned_to,
        m.points
      FROM chores c
      LEFT JOIN chore_metadata m ON c.task_id = m.task_id
      WHERE 1=1
    `;
    
    const params = [];
    
    if (!includeCompleted) {
      query += ' AND c.status = ?';
      params.push('pending');
    }
    
    if (start) {
      query += ' AND c.due_date >= ?';
      params.push(start);
    }
    
    if (end) {
      query += ' AND c.due_date <= ?';
      params.push(end);
    }
    
    query += ' ORDER BY c.due_date ASC';
    
    if (limit) {
      query += ' LIMIT ?';
      params.push(limit);
    }
    
    const stmt = db.prepare(query);
    const rows = stmt.all(...params);
    
    return rows.map(row => ({
      id: row.id,
      taskId: row.task_id,
      title: row.title,
      assignedTo: row.assigned_to,
      dueDate: row.due_date,
      status: row.status,
      completed: row.status === 'completed',
      points: row.points,
      completedAt: row.completed_at,
      ignoredAt: row.ignored_at,
    }));
  }
  
  /**
   * Complete a chore occurrence
   */
  static completeChore(choreId) {
    const db = getDb();
    const now = new Date().toISOString();
    
    const stmt = db.prepare(`
      UPDATE chores 
      SET status = 'completed', completed_at = ?
      WHERE id = ?
    `);
    
    const result = stmt.run(now, choreId);
    logger.info(`Chore ${choreId} marked as completed`);
    
    return result.changes > 0;
  }
  
  /**
   * Ignore a chore occurrence (no points)
   */
  static ignoreChore(choreId) {
    const db = getDb();
    const now = new Date().toISOString();
    
    const stmt = db.prepare(`
      UPDATE chores 
      SET status = 'ignored', ignored_at = ?
      WHERE id = ?
    `);
    
    const result = stmt.run(now, choreId);
    logger.info(`Chore ${choreId} marked as ignored`);
    
    return result.changes > 0;
  }
  
  /**
   * Auto-ignore chores due before today
   */
  static ignoreUncompletedChoresBeforeToday() {
    const db = getDb();
    const today = new Date().toISOString().split('T')[0];
    const now = new Date().toISOString();
    
    const stmt = db.prepare(`
      UPDATE chores 
      SET status = 'ignored', ignored_at = ?
      WHERE due_date < ? AND status = 'pending'
    `);
    
    const result = stmt.run(now, today);
    if (result.changes > 0) {
      logger.info(`Auto-ignored ${result.changes} chores due before today`);
    }
    
    return result.changes;
  }
  
  /**
   * Get chore metadata by task_id
   */
  static getChoreMetadata(taskId) {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM chore_metadata WHERE task_id = ?');
    return stmt.get(taskId);
  }
  
  /**
   * Create or update chore metadata
   */
  static upsertChoreMetadata(taskId, { title, assignedTo, recurrence, points }) {
    const db = getDb();
    const stmt = db.prepare(`
      INSERT INTO chore_metadata (task_id, title, assigned_to, recurrence, points)
      VALUES (?, ?, ?, ?, ?)
      ON CONFLICT(task_id) DO UPDATE SET
        title = excluded.title,
        assigned_to = excluded.assigned_to,
        recurrence = excluded.recurrence,
        points = excluded.points
    `);
    
    return stmt.run(taskId, title, assignedTo || null, recurrence || null, points || 1);
  }
  
  /**
   * Get chore templates
   */
  static getChoreTemplates(activeOnly = true) {
    const db = getDb();
    let query = 'SELECT * FROM chore_templates';
    
    if (activeOnly) {
      query += ' WHERE is_active = 1';
    }
    
    query += ' ORDER BY category, name';
    
    return db.prepare(query).all();
  }
  
  /**
   * Get unique chore categories
   */
  static getChoreCategories() {
    const db = getDb();
    const rows = db.prepare('SELECT DISTINCT category FROM chore_templates WHERE is_active = 1 ORDER BY category').all();
    return rows.map(r => r.category);
  }
}
