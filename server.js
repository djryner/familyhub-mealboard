import 'dotenv/config';
import express from 'express';
import session from 'express-session';
import path from 'path';
import { fileURLToPath } from 'url';
import { initDatabase } from './src/db/init.js';
import { routes } from './src/routes/index.js';
import { healthRoutes } from './src/routes/health.js';
import { logger } from './src/utils/logger.js';
import { getTheme } from './src/utils/theme.js';
import { config } from './src/config/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8000;
const HOST = process.env.HOST || '0.0.0.0';

// Initialize database
initDatabase();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET || 'dev-secret-change-me',
  resave: false,
  saveUninitialized: false,
  cookie: { 
    secure: process.env.NODE_ENV === 'production',
    maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
  }
}));

// View engine setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Flash messages middleware
app.use((req, res, next) => {
  res.locals.messages = req.session.messages || [];
  req.session.messages = [];
  next();
});

// Helper to add flash messages
app.use((req, res, next) => {
  req.flash = (type, message) => {
    req.session.messages = req.session.messages || [];
    req.session.messages.push({ type, message });
  };
  next();
});

// Theme middleware
app.use((req, res, next) => {
  res.locals.theme = config.seasonalThemesEnabled ? getTheme() : '';
  next();
});

// Routes
app.use('/health', healthRoutes);
app.use('/', routes);

// Admin routes
const { adminRouter } = await import('./src/routes/admin.js');
app.use('/admin', adminRouter);

// Rewards routes (only if points enabled)
if (process.env.POINTS_ENABLED !== 'false') {
  const { rewardsRouter } = await import('./src/routes/rewards.js');
  app.use('/rewards', rewardsRouter);
}

// Error handling
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).send('Internal Server Error');
});

// Start server
app.listen(PORT, HOST, () => {
  logger.info(`FamilyHub server running on http://${HOST}:${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
