import { getDb } from '../db/init.js';
import { config } from '../config/index.js';

export class PointsService {
  
  /**
   * Get user balance
   */
  static getUserBalance(userName) {
    const db = getDb();
    const stmt = db.prepare('SELECT COALESCE(SUM(points), 0) as balance FROM points_ledger WHERE user_name = ?');
    const result = stmt.get(userName);
    return result?.balance || 0;
  }
  
  /**
   * Award points to a user
   */
  static awardPoints(userName, points, reason = '') {
    if (!config.pointsEnabled) return;
    
    const db = getDb();
    const stmt = db.prepare(`
      INSERT INTO points_ledger (user_name, points, reason, created_at)
      VALUES (?, ?, ?, datetime('now'))
    `);
    
    stmt.run(userName, points, reason);
  }
  
  /**
   * Deduct points from a user
   */
  static deductPoints(userName, points, reason = '') {
    return this.awardPoints(userName, -points, reason);
  }
  
  /**
   * Get points history for a user
   */
  static getPointsHistory(userName, limit = 50) {
    const db = getDb();
    const stmt = db.prepare(`
      SELECT * FROM points_ledger 
      WHERE user_name = ? 
      ORDER BY created_at DESC 
      LIMIT ?
    `);
    
    return stmt.all(userName, limit);
  }
  
  /**
   * List all users
   */
  static listUsers() {
    const db = getDb();
    const stmt = db.prepare('SELECT id, name, color, avatar, image_url, is_parent FROM users ORDER BY name');
    return stmt.all();
  }
  
  /**
   * Get leaderboard (all users with balances)
   */
  static getLeaderboard() {
    const db = getDb();
    const stmt = db.prepare(`
      SELECT 
        u.id,
        u.name,
        u.color,
        u.avatar,
        u.image_url,
        u.is_parent,
        COALESCE(SUM(p.points), 0) as balance
      FROM users u
      LEFT JOIN points_ledger p ON u.name = p.user_name
      GROUP BY u.id, u.name, u.color, u.avatar, u.image_url, u.is_parent
      ORDER BY balance DESC, u.name
    `);
    
    return stmt.all();
  }
  
  /**
   * List rewards
   */
  static listRewards(activeOnly = true) {
    const db = getDb();
    let query = 'SELECT * FROM rewards';
    
    if (activeOnly) {
      query += ' WHERE active = 1';
    }
    
    query += ' ORDER BY cost_points, title';
    
    return db.prepare(query).all();
  }
  
  /**
   * Redeem a reward
   */
  static redeemReward(userName, rewardId) {
    const db = getDb();
    
    // Get reward details
    const reward = db.prepare('SELECT * FROM rewards WHERE id = ?').get(rewardId);
    if (!reward) {
      throw new Error('Reward not found');
    }
    
    // Check user balance
    const balance = this.getUserBalance(userName);
    if (balance < reward.cost_points) {
      throw new Error('Insufficient points');
    }
    
    // Deduct points
    this.deductPoints(userName, reward.cost_points, `Redeemed: ${reward.title}`);
    
    // Record redemption
    const stmt = db.prepare(`
      INSERT INTO reward_redemptions (user_name, reward_id, reward_title, points_spent, redeemed_at)
      VALUES (?, ?, ?, ?, datetime('now'))
    `);
    
    stmt.run(userName, rewardId, reward.title, reward.cost_points);
    
    return { reward, newBalance: balance - reward.cost_points };
  }
  
  /**
   * Get redemption history
   */
  static getRedemptionHistory(userName = null, limit = 50) {
    const db = getDb();
    let query = 'SELECT * FROM reward_redemptions';
    const params = [];
    
    if (userName) {
      query += ' WHERE user_name = ?';
      params.push(userName);
    }
    
    query += ' ORDER BY redeemed_at DESC LIMIT ?';
    params.push(limit);
    
    return db.prepare(query).all(...params);
  }
}
