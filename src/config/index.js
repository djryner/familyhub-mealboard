import 'dotenv/config';

export const config = {
  // Server
  host: process.env.HOST || '0.0.0.0',
  port: parseInt(process.env.PORT || '8000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // Session
  sessionSecret: process.env.SESSION_SECRET || 'dev-secret-change-me',
  
  // Database
  databasePath: process.env.DATABASE_PATH || './familyhub.db',
  
  // Timezone
  timezone: process.env.FAMILYHUB_TZ || 'America/Chicago',
  
  // Features
  healthEnabled: process.env.FAMILYHUB_HEALTH_ENABLED === 'true',
  pointsEnabled: process.env.POINTS_ENABLED !== 'false',
  pointsDefault: parseInt(process.env.POINTS_DEFAULT || '1', 10),
};
