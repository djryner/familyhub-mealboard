import express from 'express';
import { ChoreService } from '../services/chores.js';
import { MealsService } from '../services/meals.js';
import { PointsService } from '../services/points.js';
import { config } from '../config/index.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

/**
 * Home page - Dashboard
 */
router.get('/', (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const endDate = new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    // Fetch chores due today
    const choresToday = ChoreService.fetchChores({
      start: today,
      end: today,
      includeCompleted: true,
    });
    
    // Fetch meals for next 7 days
    const meals = MealsService.fetchMeals(today, endDate);
    
    // Get leaderboard if points enabled
    const leaderboard = config.pointsEnabled ? PointsService.getLeaderboard() : [];
    
    res.render('index', {
      choresToday,
      meals: meals.slice(0, 7),
      leaderboard,
      pointsEnabled: config.pointsEnabled,
    });
    
  } catch (error) {
    logger.error('Error rendering index:', error);
    res.status(500).send('Internal Server Error');
  }
});

/**
 * Chores page
 */
router.get('/chores', (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const endDate = new Date(Date.now() + 13 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    const chores = ChoreService.fetchChores({
      start: today,
      end: endDate,
      includeCompleted: false,
    });
    
    res.render('chores', { chores });
    
  } catch (error) {
    logger.error('Error rendering chores:', error);
    res.status(500).send('Internal Server Error');
  }
});

/**
 * Meal plans page
 */
router.get('/meal-plans', (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const endDate = new Date(Date.now() + 13 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    const meals = MealsService.fetchMeals(today, endDate);
    
    res.render('meal_plans', { meals });
    
  } catch (error) {
    logger.error('Error rendering meal plans:', error);
    res.status(500).send('Internal Server Error');
  }
});

/**
 * Complete a chore (POST)
 */
router.post('/chores/:choreId/complete', (req, res) => {
  try {
    const { choreId } = req.params;
    const success = ChoreService.completeChore(choreId);
    
    if (success && config.pointsEnabled) {
      // Get chore info to award points
      const chores = ChoreService.fetchChores({ includeCompleted: true });
      const chore = chores.find(c => c.id == choreId);
      
      if (chore && chore.assignedTo) {
        PointsService.awardPoints(chore.assignedTo, chore.points, `Completed: ${chore.title}`);
        req.flash('success', `Chore completed! ${chore.points} points awarded to ${chore.assignedTo}.`);
      } else {
        req.flash('success', 'Chore completed!');
      }
    } else {
      req.flash('success', 'Chore completed!');
    }
    
    res.redirect(req.headers.referer || '/');
    
  } catch (error) {
    logger.error('Error completing chore:', error);
    req.flash('error', 'Error completing chore.');
    res.redirect(req.headers.referer || '/');
  }
});

/**
 * Ignore a chore (POST)
 */
router.post('/chores/:choreId/ignore', (req, res) => {
  try {
    const { choreId } = req.params;
    ChoreService.ignoreChore(choreId);
    
    req.flash('warning', 'Chore ignored (no points awarded).');
    res.redirect(req.headers.referer || '/');
    
  } catch (error) {
    logger.error('Error ignoring chore:', error);
    req.flash('error', 'Error ignoring chore.');
    res.redirect(req.headers.referer || '/');
  }
});

/**
 * API: Chore categories
 */
router.get('/api/chore-categories', (req, res) => {
  try {
    const categories = ChoreService.getChoreCategories();
    res.json(categories);
  } catch (error) {
    logger.error('Error fetching chore categories:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

/**
 * API: Chore templates
 */
router.get('/api/chore-templates', (req, res) => {
  try {
    const { category } = req.query;
    const templates = ChoreService.getChoreTemplates(true);
    
    const filtered = category 
      ? templates.filter(t => t.category === category)
      : templates;
    
    res.json(filtered);
  } catch (error) {
    logger.error('Error fetching chore templates:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

/**
 * API: Meals (legacy endpoint)
 */
router.get('/api/meals', (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const endDate = new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    const meals = MealsService.fetchMeals(today, endDate);
    res.json(meals);
  } catch (error) {
    logger.error('Error fetching meals API:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

/**
 * Create meal page
 */
router.get('/meals/create', (req, res) => {
  res.render('create_meal');
});

/**
 * Create meal (POST)
 */
router.post('/meals/create', (req, res) => {
  try {
    const { title, date, mealType, description } = req.body;
    
    if (!title || !date) {
      req.flash('error', 'Title and date are required.');
      return res.redirect('/meals/create');
    }
    
    MealsService.createMeal({ title, date, mealType: mealType || 'dinner', description });
    req.flash('success', 'Meal created successfully!');
    res.redirect('/meal-plans');
    
  } catch (error) {
    logger.error('Error creating meal:', error);
    req.flash('error', 'Error creating meal.');
    res.redirect('/meals/create');
  }
});

/**
 * Delete meal (POST)
 */
router.post('/meals/:mealId/delete', (req, res) => {
  try {
    const { mealId } = req.params;
    MealsService.deleteMeal(mealId);
    req.flash('success', 'Meal deleted successfully!');
    res.redirect(req.headers.referer || '/meal-plans');
  } catch (error) {
    logger.error('Error deleting meal:', error);
    req.flash('error', 'Error deleting meal.');
    res.redirect(req.headers.referer || '/meal-plans');
  }
});

export { router as routes };
