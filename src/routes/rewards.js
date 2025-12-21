import express from 'express';
import { PointsService } from '../services/points.js';
import { config } from '../config/index.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

/**
 * Rewards catalog page
 */
router.get('/', (req, res) => {
  try {
    if (!config.pointsEnabled) {
      return res.status(403).render('403', { message: 'Rewards are not enabled' });
    }
    
    const rewards = PointsService.listRewards(true);
    const users = PointsService.listUsers();
    const leaderboard = PointsService.getLeaderboard();
    
    res.render('rewards/index', { rewards, users, leaderboard });
    
  } catch (error) {
    logger.error('Error rendering rewards:', error);
    res.status(500).send('Internal Server Error');
  }
});

/**
 * Redeem a reward (POST)
 */
router.post('/redeem', (req, res) => {
  try {
    const { userName, rewardId } = req.body;
    
    if (!userName || !rewardId) {
      req.flash('error', 'Missing required fields');
      return res.redirect('/rewards');
    }
    
    const result = PointsService.redeemReward(userName, parseInt(rewardId, 10));
    
    req.flash('success', `${userName} redeemed ${result.reward.title}! New balance: ${result.newBalance} points.`);
    res.redirect('/rewards');
    
  } catch (error) {
    logger.error('Error redeeming reward:', error);
    req.flash('error', error.message || 'Error redeeming reward');
    res.redirect('/rewards');
  }
});

/**
 * Redemption history page
 */
router.get('/history', (req, res) => {
  try {
    const history = PointsService.getRedemptionHistory(null, 100);
    res.render('rewards/history', { history });
    
  } catch (error) {
    logger.error('Error rendering redemption history:', error);
    res.status(500).send('Internal Server Error');
  }
});

export { router as rewardsRouter };
