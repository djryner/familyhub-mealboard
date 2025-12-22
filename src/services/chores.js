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

  /**
   * Get all chore metadata (definitions) for a specific user
   */
  static getChoresByUser(userId) {
    const db = getDb();
    const stmt = db.prepare(`
      SELECT * FROM chore_metadata 
      WHERE LOWER(assigned_to) = LOWER(?)
      ORDER BY title
    `);
    return stmt.all(userId);
  }

  /**
   * Create a new chore definition
   */
  static createChore({ title, assignedTo, frequency, points }) {
    const db = getDb();
    const taskId = `chore_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const stmt = db.prepare(`
      INSERT INTO chore_metadata (task_id, title, assigned_to, recurrence, points)
      VALUES (?, ?, ?, ?, ?)
    `);
    
    stmt.run(taskId, title, assignedTo, frequency, points);
    
    // Create initial occurrences based on frequency
    this.generateChoreOccurrences(taskId, frequency);
    
    return { taskId, title, assignedTo, frequency, points };
  }

  /**
   * Generate chore occurrences based on frequency
   */
  static generateChoreOccurrences(taskId, frequency) {
    const db = getDb();
    const today = new Date();
    const occurrences = [];
    
    // For ad-hoc chores, create one occurrence for today
    if (frequency === 'adhoc') {
      occurrences.push([taskId, today.toISOString().split('T')[0]]);
    } else {
      // Generate occurrences for the next 30 days for recurring chores
      for (let i = 0; i < 30; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
        
        let shouldCreate = false;
        
        switch (frequency) {
          case 'daily':
            shouldCreate = true;
            break;
          case 'weekends':
            shouldCreate = dayOfWeek === 0 || dayOfWeek === 6;
            break;
          case 'weekdays':
            shouldCreate = dayOfWeek >= 1 && dayOfWeek <= 5;
            break;
          case 'school-week':
            // Sunday, Monday, Tuesday, Wednesday, Thursday
            shouldCreate = dayOfWeek === 0 || (dayOfWeek >= 1 && dayOfWeek <= 4);
            break;
        }
        
        if (shouldCreate) {
          occurrences.push([taskId, date.toISOString().split('T')[0]]);
        }
      }
    }
    
    if (occurrences.length > 0) {
      const stmt = db.prepare(`
        INSERT INTO chores (task_id, due_date, status)
        VALUES (?, ?, 'pending')
      `);
      
      const insertMany = db.transaction((items) => {
        for (const [taskId, dueDate] of items) {
          stmt.run(taskId, dueDate);
        }
      });
      
      insertMany(occurrences);
      logger.info(`Generated ${occurrences.length} occurrences for chore ${taskId}`);
    }
  }

  /**
   * Update a chore definition
   */
  static updateChore(taskId, { title, frequency, points }) {
    const db = getDb();
    
    const stmt = db.prepare(`
      UPDATE chore_metadata
      SET title = ?, recurrence = ?, points = ?
      WHERE task_id = ?
    `);
    
    stmt.run(title, frequency, points, taskId);
    
    // Remove future occurrences and regenerate
    const deleteStmt = db.prepare(`
      DELETE FROM chores
      WHERE task_id = ? AND due_date >= date('now') AND status = 'pending'
    `);
    deleteStmt.run(taskId);
    
    // Regenerate occurrences
    this.generateChoreOccurrences(taskId, frequency);
    
    return { taskId, title, frequency, points };
  }

  /**
   * Delete a chore definition and all its occurrences
   */
  static deleteChore(taskId) {
    const db = getDb();
    
    // Delete occurrences first
    const deleteOccurrences = db.prepare('DELETE FROM chores WHERE task_id = ?');
    deleteOccurrences.run(taskId);
    
    // Delete metadata
    const deleteMetadata = db.prepare('DELETE FROM chore_metadata WHERE task_id = ?');
    deleteMetadata.run(taskId);
    
    logger.info(`Deleted chore ${taskId} and all its occurrences`);
    return true;
  }

  /**
   * Get available (unassigned) chores for claiming
   */
  static getAvailableChores({ start, end } = {}) {
    const db = getDb();
    
    let query = `
      SELECT 
        c.id,
        c.task_id,
        c.due_date,
        c.status,
        m.title,
        m.points
      FROM chores c
      LEFT JOIN chore_metadata m ON c.task_id = m.task_id
      WHERE c.status = 'pending' AND (m.assigned_to IS NULL OR m.assigned_to = '')
    `;
    
    const params = [];
    
    if (start) {
      query += ' AND c.due_date >= ?';
      params.push(start);
    }
    
    if (end) {
      query += ' AND c.due_date <= ?';
      params.push(end);
    }
    
    query += ' ORDER BY c.due_date ASC';
    
    const stmt = db.prepare(query);
    const rows = stmt.all(...params);
    
    return rows.map(row => ({
      id: row.id,
      taskId: row.task_id,
      title: row.title,
      dueDate: row.due_date,
      status: row.status,
      points: row.points,
    }));
  }

  /**
   * Get all ad-hoc chore definitions (unassigned)
   */
  static getAdHocChores() {
    const db = getDb();
    const stmt = db.prepare(`
      SELECT * FROM chore_metadata 
      WHERE assigned_to IS NULL OR assigned_to = ''
      ORDER BY title
    `);
    return stmt.all();
  }

  /**
   * Claim an available chore for a user
   */
  static claimChore(choreId, userName) {
    const db = getDb();
    
    // First get the chore to find its task_id
    const chore = db.prepare('SELECT task_id FROM chores WHERE id = ?').get(choreId);
    if (!chore) {
      throw new Error('Chore not found');
    }
    
    // Check if it's actually an available chore
    const metadata = db.prepare('SELECT assigned_to FROM chore_metadata WHERE task_id = ?').get(chore.task_id);
    if (metadata && metadata.assigned_to && metadata.assigned_to !== '') {
      throw new Error('This chore is already assigned');
    }
    
    // Update this specific occurrence to be assigned
    const stmt = db.prepare(`
      UPDATE chores 
      SET status = 'pending'
      WHERE id = ?
    `);
    
    stmt.run(choreId);
    
    // Note: We don't update the metadata assigned_to because this is a one-time claim
    // The chore remains available for future occurrences
    
    logger.info(`Chore ${choreId} claimed by ${userName}`);
    return true;
  }
}
