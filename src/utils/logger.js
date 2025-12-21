const logLevels = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3,
};

const currentLevel = logLevels[process.env.LOG_LEVEL?.toUpperCase() || 'INFO'] || logLevels.INFO;

const formatMessage = (level, ...args) => {
  const timestamp = new Date().toISOString();
  return `[${timestamp}] ${level}: ${args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' ')}`;
};

export const logger = {
  error: (...args) => {
    if (currentLevel >= logLevels.ERROR) console.error(formatMessage('ERROR', ...args));
  },
  warn: (...args) => {
    if (currentLevel >= logLevels.WARN) console.warn(formatMessage('WARN', ...args));
  },
  info: (...args) => {
    if (currentLevel >= logLevels.INFO) console.log(formatMessage('INFO', ...args));
  },
  debug: (...args) => {
    if (currentLevel >= logLevels.DEBUG) console.log(formatMessage('DEBUG', ...args));
  },
};
