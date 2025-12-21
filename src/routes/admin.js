import express from 'express';
import { ChoreService } from '../services/chores.js';
import { MealsService } from '../services/meals.js';
import { PointsService } from '../services/points.js';
import { getDb } from '../db/init.js';
import { logger } from '../utils/logger.js';
import { generateQRCode } from '../utils/qrcode.js';
import { uploadUserImage, getUserImagePath, deleteUserImage } from '../utils/upload.js';
import os from 'os';

const router = express.Router();

/**
 * Get the server's local IP address
 */
function getLocalIpAddress() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Skip internal (loopback) and non-IPv4 addresses
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost';
}

/**
 * Admin Dashboard
 */
router.get('/', async (req, res) => {
  try {
    const db = getDb();
    
    // Get the admin URL
    const protocol = req.protocol;
    const host = req.get('host');
    const adminUrl = `${protocol}://${host}/admin`;
    
    // For local network access, also provide IP-based URL
    const localIp = getLocalIpAddress();
    const port = process.env.PORT || 8000;
    const localAdminUrl = `http://${localIp}:${port}/admin`;
    
    // Generate QR code for the admin URL
    let qrCodeDataUrl = null;
    try {
      qrCodeDataUrl = await generateQRCode(localAdminUrl, { width: 300 });
    } catch (error) {
      logger.warn('Could not generate QR code:', error);
    }
    
    // Get counts
    const stats = {
      users: db.prepare('SELECT COUNT(*) as count FROM users').get().count,
      chores: db.prepare("SELECT COUNT(*) as count FROM chores WHERE status = 'pending'").get().count,
      meals: db.prepare("SELECT COUNT(*) as count FROM meals WHERE date >= date('now')").get().count,
      rewards: db.prepare('SELECT COUNT(*) as count FROM rewards WHERE active = 1').get().count,
    };
    
    // Recent activity
    const recentMeals = MealsService.getAllMeals(5);
    const recentChores = ChoreService.fetchChores({ limit: 5, includeCompleted: true });
    const recentRedemptions = PointsService.getRedemptionHistory(null, 5);
    
    res.render('admin/index', {
      stats,
      recentMeals,
      recentChores,
      recentRedemptions,
      qrCodeDataUrl,
      localAdminUrl,
    });
  } catch (error) {
    logger.error('Error rendering admin dashboard:', error);
    console.error('Full error:', error);
    res.status(500).send('Internal Server Error: ' + error.message);
  }
});

/**
 * Users Management
 */
router.get('/users', (req, res) => {
  try {
    const users = PointsService.listUsers();
    const leaderboard = PointsService.getLeaderboard();
    res.render('admin/users', { users, leaderboard });
  } catch (error) {
    logger.error('Error rendering users:', error);
    res.status(500).send('Internal Server Error');
  }
});

router.get('/users/create', (req, res) => {
  res.render('admin/create_user');
});

router.post('/users/create', uploadUserImage.single('userImage'), (req, res) => {
  try {
    const { name, isParent } = req.body;
    
    if (!name) {
      req.flash('error', 'Name is required.');
      return res.redirect('/admin/users/create');
    }
    
    // Generate a unique ID from the name
    const baseId = name.toLowerCase().replace(/[^a-z0-9]/g, '');
    let id = baseId;
    let counter = 1;
    
    const db = getDb();
    
    // Ensure ID is unique
    while (db.prepare('SELECT id FROM users WHERE id = ?').get(id)) {
      id = `${baseId}${counter}`;
      counter++;
    }
    
    // Get image URL if uploaded
    let imageUrl = null;
    if (req.file) {
      imageUrl = getUserImagePath(req.file.filename);
      logger.info(`User image uploaded: ${imageUrl}`);
    }
    
    // Insert the user
    const stmt = db.prepare('INSERT INTO users (id, name, color, avatar, image_url) VALUES (?, ?, ?, ?, ?)');
    stmt.run(id, name, '#3498db', '👤', imageUrl);
    
    // Set is_parent flag if checked (need to check if column exists)
    if (isParent) {
      try {
        db.prepare('UPDATE users SET is_parent = 1 WHERE id = ?').run(id);
      } catch (e) {
        // Column might not exist, ignore
        logger.warn('is_parent column not found');
      }
    }
    
    req.flash('success', `User ${name} created successfully!`);
    res.redirect('/admin/users');
  } catch (error) {
    logger.error('Error creating user:', error);
    console.error('Full user creation error:', error);
    req.flash('error', error.message || 'Error creating user.');
    res.redirect('/admin/users/create');
  }
});

router.get('/users/:userId/delete-confirm', (req, res) => {
  try {
    const { userId } = req.params;
    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
    
    if (!user) {
      req.flash('error', 'User not found.');
      return res.redirect('/admin/users');
    }
    
    res.render('admin/delete_user_confirm', { user });
  } catch (error) {
    logger.error('Error loading user for deletion:', error);
    req.flash('error', 'Error loading user.');
    res.redirect('/admin/users');
  }
});

router.post('/users/:userId/delete', (req, res) => {
  try {
    const { userId } = req.params;
    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
    
    // Delete user's image if it exists
    if (user && user.image_url) {
      deleteUserImage(user.image_url);
    }
    
    db.prepare('DELETE FROM users WHERE id = ?').run(userId);
    
    req.flash('success', 'User deleted successfully!');
    res.redirect('/admin/users');
  } catch (error) {
    logger.error('Error deleting user:', error);
    req.flash('error', 'Error deleting user.');
    res.redirect('/admin/users');
  }
});

router.get('/users/:userId/edit', (req, res) => {
  try {
    const { userId } = req.params;
    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
    
    if (!user) {
      req.flash('error', 'User not found.');
      return res.redirect('/admin/users');
    }
    
    res.render('admin/edit_user', { user });
  } catch (error) {
    logger.error('Error loading user for editing:', error);
    req.flash('error', 'Error loading user.');
    res.redirect('/admin/users');
  }
});

router.post('/users/:userId/edit', uploadUserImage.single('userImage'), (req, res) => {
  try {
    const { userId } = req.params;
    const { name, isParent, removeImage } = req.body;
    
    if (!name) {
      req.flash('error', 'Name is required.');
      return res.redirect(`/admin/users/${userId}/edit`);
    }
    
    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
    
    if (!user) {
      req.flash('error', 'User not found.');
      return res.redirect('/admin/users');
    }
    
    let imageUrl = user.image_url;
    
    // Handle image removal
    if (removeImage === '1') {
      if (user.image_url) {
        deleteUserImage(user.image_url);
      }
      imageUrl = null;
    }
    
    // Handle new image upload
    if (req.file) {
      // Delete old image if it exists
      if (user.image_url) {
        deleteUserImage(user.image_url);
      }
      imageUrl = getUserImagePath(req.file.filename);
      logger.info(`User image updated: ${imageUrl}`);
    }
    
    // Update user
    db.prepare('UPDATE users SET name = ?, image_url = ?, is_parent = ? WHERE id = ?')
      .run(name, imageUrl, isParent ? 1 : 0, userId);
    
    req.flash('success', `User ${name} updated successfully!`);
    res.redirect('/admin/users');
  } catch (error) {
    logger.error('Error updating user:', error);
    console.error('Full user update error:', error);
    req.flash('error', error.message || 'Error updating user.');
    res.redirect(`/admin/users/${req.params.userId}/edit`);
  }
});

/**
 * Chores Management
 */
router.get('/chores', (req, res) => {
  try {
    const templates = ChoreService.getChoreTemplates(false);
    const metadata = getDb().prepare('SELECT * FROM chore_metadata ORDER BY title').all();
    res.render('admin/chores', { templates, metadata });
  } catch (error) {
    logger.error('Error rendering chores:', error);
    res.status(500).send('Internal Server Error');
  }
});

router.get('/chores/template/create', (req, res) => {
  const categories = ChoreService.getChoreCategories();
  res.render('admin/create_chore_template', { categories });
});

router.post('/chores/template/create', (req, res) => {
  try {
    const { name, category } = req.body;
    
    if (!name || !category) {
      req.flash('error', 'Name and category are required.');
      return res.redirect('/admin/chores/template/create');
    }
    
    const db = getDb();
    const stmt = db.prepare('INSERT INTO chore_templates (name, category, is_active) VALUES (?, ?, 1)');
    stmt.run(name, category);
    
    req.flash('success', 'Chore template created successfully!');
    res.redirect('/admin/chores');
  } catch (error) {
    logger.error('Error creating chore template:', error);
    req.flash('error', 'Error creating chore template.');
    res.redirect('/admin/chores/template/create');
  }
});

router.get('/chores/:id/delete-confirm', (req, res) => {
  try {
    const { id } = req.params;
    const db = getDb();
    const template = db.prepare('SELECT * FROM chore_templates WHERE id = ?').get(id);
    
    if (!template) {
      req.flash('error', 'Chore template not found.');
      return res.redirect('/admin/chores');
    }
    
    res.render('admin/delete_chore_confirm', { template });
  } catch (error) {
    logger.error('Error loading chore template for deletion:', error);
    req.flash('error', 'Error loading chore template.');
    res.redirect('/admin/chores');
  }
});

router.post('/chores/template/:id/delete', (req, res) => {
  try {
    const { id } = req.params;
    const db = getDb();
    db.prepare('DELETE FROM chore_templates WHERE id = ?').run(id);
    
    req.flash('success', 'Chore template deleted successfully!');
    res.redirect('/admin/chores');
  } catch (error) {
    logger.error('Error deleting chore template:', error);
    req.flash('error', 'Error deleting chore template.');
    res.redirect('/admin/chores');
  }
});

router.post('/chores/:id/delete', (req, res) => {
  try {
    const { id } = req.params;
    const db = getDb();
    db.prepare('DELETE FROM chore_templates WHERE id = ?').run(id);
    
    req.flash('success', 'Chore template deleted successfully!');
    res.redirect('/admin/chores');
  } catch (error) {
    logger.error('Error deleting chore template:', error);
    req.flash('error', 'Error deleting chore template.');
    res.redirect('/admin/chores');
  }
});

/**
 * Meals Management
 */
router.get('/meals', (req, res) => {
  try {
    const meals = MealsService.getAllMeals(50);
    res.render('admin/meals', { meals });
  } catch (error) {
    logger.error('Error rendering meals:', error);
    res.status(500).send('Internal Server Error');
  }
});

router.get('/meals/create', (req, res) => {
  res.render('admin/create_meal');
});

router.post('/meals/create', (req, res) => {
  try {
    const { title, date, mealType, description } = req.body;
    
    if (!title || !date) {
      req.flash('error', 'Title and date are required.');
      return res.redirect('/admin/meals/create');
    }
    
    MealsService.createMeal({ title, date, mealType: mealType || 'dinner', description });
    req.flash('success', 'Meal created successfully!');
    res.redirect('/admin/meals');
  } catch (error) {
    logger.error('Error creating meal:', error);
    req.flash('error', 'Error creating meal.');
    res.redirect('/admin/meals/create');
  }
});

router.get('/meals/:id/edit', (req, res) => {
  try {
    const { id } = req.params;
    const meal = MealsService.getMeal(id);
    
    if (!meal) {
      req.flash('error', 'Meal not found.');
      return res.redirect('/admin/meals');
    }
    
    res.render('admin/edit_meal', { meal });
  } catch (error) {
    logger.error('Error loading meal:', error);
    req.flash('error', 'Error loading meal.');
    res.redirect('/admin/meals');
  }
});

router.post('/meals/:id/edit', (req, res) => {
  try {
    const { id } = req.params;
    const { title, date, mealType, description } = req.body;
    
    if (!title || !date) {
      req.flash('error', 'Title and date are required.');
      return res.redirect(`/admin/meals/${id}/edit`);
    }
    
    MealsService.updateMeal(id, { title, date, mealType, description });
    req.flash('success', 'Meal updated successfully!');
    res.redirect('/admin/meals');
  } catch (error) {
    logger.error('Error updating meal:', error);
    req.flash('error', 'Error updating meal.');
    res.redirect(`/admin/meals/${id}/edit`);
  }
});

router.get('/meals/:id/delete-confirm', (req, res) => {
  try {
    const { id } = req.params;
    const meal = MealsService.getMeal(id);
    
    if (!meal) {
      req.flash('error', 'Meal not found.');
      return res.redirect('/admin/meals');
    }
    
    res.render('admin/delete_meal_confirm', { meal });
  } catch (error) {
    logger.error('Error loading meal for deletion:', error);
    req.flash('error', 'Error loading meal.');
    res.redirect('/admin/meals');
  }
});

router.post('/meals/:id/delete', (req, res) => {
  try {
    const { id } = req.params;
    logger.info(`Attempting to delete meal ${id}`);
    
    const meal = MealsService.getMeal(id);
    if (!meal) {
      logger.warn(`Meal ${id} not found for deletion`);
      req.flash('error', 'Meal not found.');
      return res.redirect('/admin/meals');
    }
    
    MealsService.deleteMeal(id);
    logger.info(`Successfully deleted meal ${id}: ${meal.title}`);
    req.flash('success', `Meal "${meal.title}" deleted successfully!`);
    res.redirect('/admin/meals');
  } catch (error) {
    logger.error('Error deleting meal:', error);
    console.error('Full delete error:', error);
    req.flash('error', 'Error deleting meal: ' + error.message);
    res.redirect('/admin/meals');
  }
});

/**
 * Rewards Management
 */
router.get('/rewards', (req, res) => {
  try {
    const rewards = PointsService.listRewards(false);
    res.render('admin/rewards', { rewards });
  } catch (error) {
    logger.error('Error rendering rewards:', error);
    res.status(500).send('Internal Server Error');
  }
});

router.get('/rewards/create', (req, res) => {
  res.render('admin/create_reward');
});

router.post('/rewards/create', (req, res) => {
  try {
    const { title, cost_points, emoji, active } = req.body;
    
    if (!title || !cost_points) {
      req.flash('error', 'Title and cost are required.');
      return res.redirect('/admin/rewards/create');
    }
    
    const db = getDb();
    const stmt = db.prepare('INSERT INTO rewards (title, cost_points, emoji, active) VALUES (?, ?, ?, ?)');
    stmt.run(title, parseInt(cost_points, 10), emoji || '🎁', active === 'on' ? 1 : 1);
    
    req.flash('success', 'Reward created successfully!');
    res.redirect('/admin/rewards');
  } catch (error) {
    logger.error('Error creating reward:', error);
    req.flash('error', 'Error creating reward.');
    res.redirect('/admin/rewards/create');
  }
});

router.get('/rewards/:id/delete-confirm', (req, res) => {
  try {
    const { id } = req.params;
    const db = getDb();
    const reward = db.prepare('SELECT * FROM rewards WHERE id = ?').get(id);
    
    if (!reward) {
      req.flash('error', 'Reward not found.');
      return res.redirect('/admin/rewards');
    }
    
    res.render('admin/delete_reward_confirm', { reward });
  } catch (error) {
    logger.error('Error loading reward for deletion:', error);
    req.flash('error', 'Error loading reward.');
    res.redirect('/admin/rewards');
  }
});

router.post('/rewards/:id/delete', (req, res) => {
  try {
    const { id } = req.params;
    const db = getDb();
    db.prepare('DELETE FROM rewards WHERE id = ?').run(id);
    
    req.flash('success', 'Reward deleted successfully!');
    res.redirect('/admin/rewards');
  } catch (error) {
    logger.error('Error deleting reward:', error);
    req.flash('error', 'Error deleting reward.');
    res.redirect('/admin/rewards');
  }
});

router.post('/rewards/:id/toggle', (req, res) => {
  try {
    const { id } = req.params;
    const db = getDb();
    db.prepare('UPDATE rewards SET active = NOT active WHERE id = ?').run(id);
    
    req.flash('success', 'Reward status updated!');
    res.redirect('/admin/rewards');
  } catch (error) {
    logger.error('Error toggling reward:', error);
    req.flash('error', 'Error updating reward.');
    res.redirect('/admin/rewards');
  }
});

export { router as adminRouter };
