import Database from 'better-sqlite3';
import { config } from '../config/index.js';
import { logger } from '../utils/logger.js';

let db = null;

export function getDb() {
  if (!db) {
    db = new Database(config.databasePath);
    db.pragma('journal_mode = WAL');
    db.pragma('foreign_keys = ON');
  }
  return db;
}

export function initDatabase() {
  const database = getDb();
  
  logger.info('Initializing database...');
  
  // Create tables
  database.exec(`
    -- Chore Templates
    CREATE TABLE IF NOT EXISTS chore_templates (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      is_active INTEGER DEFAULT 1
    );

    -- Chore Metadata (recurring chore definitions)
    CREATE TABLE IF NOT EXISTS chore_metadata (
      task_id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      assigned_to TEXT,
      recurrence TEXT,
      points INTEGER NOT NULL DEFAULT 1
    );

    -- Chore Occurrences (individual instances)
    CREATE TABLE IF NOT EXISTS chores (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      task_id TEXT NOT NULL,
      due_date TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      completed_at TEXT,
      ignored_at TEXT,
      FOREIGN KEY (task_id) REFERENCES chore_metadata(task_id)
    );

    -- Users
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      color TEXT,
      avatar TEXT,
      is_parent INTEGER DEFAULT 0,
      image_url TEXT
    );

    -- Points Ledger
    CREATE TABLE IF NOT EXISTS points_ledger (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_name TEXT NOT NULL,
      points INTEGER NOT NULL,
      reason TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- Rewards
    CREATE TABLE IF NOT EXISTS rewards (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      cost_points INTEGER NOT NULL,
      emoji TEXT,
      active INTEGER DEFAULT 1
    );

    -- Reward Redemptions
    CREATE TABLE IF NOT EXISTS reward_redemptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_name TEXT NOT NULL,
      reward_id INTEGER NOT NULL,
      reward_title TEXT NOT NULL,
      points_spent INTEGER NOT NULL,
      redeemed_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (reward_id) REFERENCES rewards(id)
    );

    -- Meals
    CREATE TABLE IF NOT EXISTS meals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      date TEXT NOT NULL,
      meal_type TEXT DEFAULT 'dinner',
      description TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_chores_due_date ON chores(due_date);
    CREATE INDEX IF NOT EXISTS idx_chores_status ON chores(status);
    CREATE INDEX IF NOT EXISTS idx_points_ledger_user ON points_ledger(user_name);
    CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date);
  `);

  logger.info('Database initialized successfully');
  
  return database;
}

export function closeDb() {
  if (db) {
    db.close();
    db = null;
  }
}
