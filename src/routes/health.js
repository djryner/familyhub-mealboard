import express from 'express';
import { config } from '../config/index.js';

const router = express.Router();

let startupTime = Date.now();
let isHealthy = true;

/**
 * Liveness probe - is the server running?
 */
router.get('/healthz', (req, res) => {
  if (isHealthy) {
    res.status(200).send('OK');
  } else {
    res.status(503).send('Service Unavailable');
  }
});

/**
 * Readiness probe - is the server ready to serve traffic?
 */
router.get('/readyz', (req, res) => {
  const uptime = Math.floor((Date.now() - startupTime) / 1000);
  
  // Wait 60 seconds after startup before reporting ready
  if (uptime < 60) {
    return res.status(503).json({
      status: 'starting',
      uptime,
      message: 'Server is starting up',
    });
  }
  
  res.status(200).json({
    status: 'ready',
    uptime,
  });
});

/**
 * Detailed health status
 */
router.get('/status', (req, res) => {
  const uptime = Math.floor((Date.now() - startupTime) / 1000);
  
  res.json({
    status: isHealthy ? 'healthy' : 'unhealthy',
    uptime,
    environment: config.nodeEnv,
    timestamp: new Date().toISOString(),
  });
});

export { router as healthRoutes };
