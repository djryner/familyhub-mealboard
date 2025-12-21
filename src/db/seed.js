import { getDb, initDatabase } from './init.js';
import { logger } from '../utils/logger.js';

// Initialize database first
initDatabase();

// Seed default data
const db = getDb();

logger.info('🌱 Seeding database...');

// Seed users
const users = [
  { id: 'alice', name: 'Alice', color: '#3498db', avatar: '👧' },
  { id: 'bob', name: 'Bob', color: '#2ecc71', avatar: '👦' },
  { id: 'charlie', name: 'Charlie', color: '#f39c12', avatar: '👶' },
];

const insertUser = db.prepare('INSERT OR IGNORE INTO users (id, name, color, avatar) VALUES (?, ?, ?, ?)');
users.forEach(user => {
  insertUser.run(user.id, user.name, user.color, user.avatar);
});

logger.info(`✅ Seeded ${users.length} users`);

// Seed rewards
const rewards = [
  { title: '🍦 Ice Cream', cost_points: 10, emoji: '🍦' },
  { title: '🎮 Extra Gaming Time (30min)', cost_points: 20, emoji: '🎮' },
  { title: '🍕 Pizza Night', cost_points: 30, emoji: '🍕' },
  { title: '🎬 Movie Night Choice', cost_points: 25, emoji: '🎬' },
  { title: '🏰 Trip to Fun Zone', cost_points: 100, emoji: '🏰' },
];

const insertReward = db.prepare('INSERT OR IGNORE INTO rewards (title, cost_points, emoji, active) VALUES (?, ?, ?, 1)');
rewards.forEach(reward => {
  insertReward.run(reward.title, reward.cost_points, reward.emoji);
});

logger.info(`✅ Seeded ${rewards.length} rewards`);

// Seed chore templates
const templates = [
  { name: 'Feed the dog', category: 'Pet Care' },
  { name: 'Walk the dog', category: 'Pet Care' },
  { name: 'Clean room', category: 'Bedroom' },
  { name: 'Make bed', category: 'Bedroom' },
  { name: 'Take out trash', category: 'Kitchen' },
  { name: 'Load dishwasher', category: 'Kitchen' },
  { name: 'Vacuum living room', category: 'Living Room' },
];

const insertTemplate = db.prepare('INSERT OR IGNORE INTO chore_templates (name, category, is_active) VALUES (?, ?, 1)');
templates.forEach(template => {
  insertTemplate.run(template.name, template.category);
});

logger.info(`✅ Seeded ${templates.length} chore templates`);

// Seed meals
const today = new Date();
const meals = [
  { title: 'Spaghetti Bolognese', date: new Date(today.getTime() + 0 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], mealType: 'dinner', description: 'Classic Italian pasta with meat sauce' },
  { title: 'Chicken Tacos', date: new Date(today.getTime() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], mealType: 'dinner', description: 'Grilled chicken with taco toppings' },
  { title: 'Pizza Night', date: new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], mealType: 'dinner', description: 'Homemade or delivery pizza' },
  { title: 'Grilled Salmon', date: new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], mealType: 'dinner', description: 'Salmon with roasted vegetables' },
  { title: 'Stir Fry', date: new Date(today.getTime() + 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], mealType: 'dinner', description: 'Vegetable and chicken stir fry' },
];

const insertMeal = db.prepare('INSERT OR IGNORE INTO meals (title, date, meal_type, description) VALUES (?, ?, ?, ?)');
meals.forEach(meal => {
  insertMeal.run(meal.title, meal.date, meal.mealType, meal.description);
});

logger.info(`✅ Seeded ${meals.length} meals`);

logger.info('🎉 Database seeding complete!');
