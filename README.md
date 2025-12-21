# FamilyHub Meal Board - Node.js Edition

A family management web application built with Node.js, Express, and SQLite. Manage chores, meal plans, points, and rewards all in one place.

## Features

- 📋 **Chores Management**: Track recurring chores with point values
- 🍽️ **Meal Planning**: Local meal planning with date and meal type support
- ⭐ **Points System**: Award points for completed chores
- 🎁 **Rewards Catalog**: Redeem points for rewards
- 🏆 **Leaderboard**: Track family member progress
- 🖥️ **Kiosk Mode**: Run in fullscreen on Raspberry Pi
- 📱 **Mobile Admin Interface**: Manage everything from your phone without using the kiosk screen

## Tech Stack

- **Backend**: Node.js + Express.js
- **Database**: SQLite (better-sqlite3)
- **Views**: EJS templates
- **No External APIs**: 100% local operation
- **Deployment**: Systemd service on Raspberry Pi

## Quick Start

### Prerequisites

- Node.js 18+ (automatically installed by install script on Pi)
- Raspberry Pi (recommended) or any Linux system
- No external API dependencies - fully local operation!

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd familyhub-mealboard
   ```

2. **Run the install script:**
   ```bash
   chmod +x install-node.sh
   sudo ./install-node.sh
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env
   ```

   Update these values:
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google service account JSON
   - `FAMILYHUB_CALENDAR_ID`: Your Google Calendar ID
   - `SESSION_SECRET`: Random secret for sessions
   - `FAMILYHUB_TZ`: Your timezone

4. **Seed the database:**
   ```bash
   npm run seed
   ```

5. **Start the service:**
   ```bash
   sudo systemctl start familyhub
   sudo systemctl status familyhub
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run in development mode:**
   ```bash
   npm run dev
   ```

4. **Access the app:**
   ```
   http://localhost:8000
   ```

## Project Structure

```
familyhub-mealboard/
├── server.js                 # Main application entry point
├── package.json              # Dependencies and scripts
├── .env.example              # Environment variables template
├── install-node.sh           # Installation script for Pi
├── src/
│   ├── config/
│   │   └── index.js          # Configuration management
│   ├── db/
│   │   ├── init.js           # Database initialization
│   │   └── seed.js           # Database seeding
│   ├── services/
│   │   ├── chores.js         # Chores business logic
│   │   ├── points.js         # Points/rewards logic
│   │   ├── meals.js          # Meals service
│   │   └── google.js         # Google API integration
│   ├── routes/
│   │   ├── index.js          # Main routes
│   │   ├── rewards.js        # Rewards routes
│   │   └── health.js         # Health check endpoints
│   └── utils/
│       └── logger.js         # Logging utility
├── views/                    # EJS templates
│   ├── index.ejs
│   ├── chores.ejs
│   ├── meal_plans.ejs
│   └── partials/
└── public/                   # Static assets
    └── css/
        └── style.css
```

## API Endpoints

### Health Checks
- `GET /health/healthz` - Liveness probe
- `GET /health/readyz` - Readiness probe
- `GET /health/status` - Detailed status

### Main Routes
- `GET /` - Dashboard
- `GET /chores` - Chores list
- `GET /meal-plans` - Meal plans
- `GET /rewards` - Rewards catalog

### API Endpoints
- `GET /api/meals` - Get meals (JSON)
- `GET /api/chore-categories` - Get chore categories
- `GET /api/chore-templates` - Get chore templates
- `POST /chores/:id/complete` - Complete a chore
- `POST /chores/:id/ignore` - Ignore a chore (no points)
- `POST /rewards/redeem` - Redeem a reward

## Mobile Admin Interface

Access the admin interface to manage your FamilyHub from any device on your network:

**URL**: `http://<raspberry-pi-ip>:8000/admin`

### Admin Features

- **Dashboard**: View stats and recent activity at a glance
- **Manage Users**: Add or remove family members
- **Manage Meals**: Create, edit, and delete meal plans
- **Manage Chores**: Create and manage chore templates
- **Manage Rewards**: Add rewards and toggle availability

The admin interface is fully mobile-optimized with:
- Touch-friendly buttons (48px+ tap targets)
- Responsive card-based layouts
- Full-width forms on mobile devices
- No pinch-to-zoom needed

See [ADMIN-GUIDE.md](./ADMIN-GUIDE.md) for detailed documentation.

## Database Schema

The app uses SQLite with the following tables:

- `chore_templates` - Chore template definitions
- `chore_metadata` - Recurring chore metadata
- `chores` - Individual chore occurrences
- `users` - Family members
- `points_ledger` - Points transactions
- `rewards` - Available rewards
- `reward_redemptions` - Redemption history

## Configuration

All configuration is done through environment variables in `.env`:

```bash
# Server
NODE_ENV=production
HOST=0.0.0.0
PORT=8000

# Session
SESSION_SECRET=your-secret-here

# Database
DATABASE_PATH=./familyhub.db

# Google Integration
GOOGLE_APPLICATION_CREDENTIALS=./secrets/service-account.json
FAMILYHUB_CALENDAR_ID=your-calendar@group.calendar.google.com
FAMILYHUB_TZ=America/Chicago

# Features
FAMILYHUB_HEALTH_ENABLED=true
POINTS_ENABLED=true
POINTS_DEFAULT=1
```

## Systemd Service

The app runs as a systemd service on Raspberry Pi:

```bash
# Check status
sudo systemctl status familyhub

# View logs
sudo journalctl -u familyhub -f

# Restart
sudo systemctl restart familyhub
```

## Kiosk Mode

The install script automatically sets up Chromium to launch in kiosk mode on boot for the `familyhub` user.

## Migration from Python Version

This is a complete rewrite of the original Python/Flask app. Key changes:

- **Runtime**: Python → Node.js
- **Framework**: Flask → Express
- **ORM**: SQLAlchemy → better-sqlite3 (native)
- **Templates**: Jinja2 → EJS
- **Database**: Same SQLite schema (mostly compatible)

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u familyhub -n 50
```

### Database errors
Delete and reinitialize:
```bash
rm familyhub.db
npm run seed
sudo systemctl restart familyhub
```

### Google API errors
- Verify service account JSON path
- Check calendar sharing permissions
- Ensure Calendar/Tasks APIs are enabled

## Development

### Run tests
```bash
npm test
```

### Watch mode
```bash
npm run dev
```

### Database operations
```bash
# Seed data
npm run seed

# Run migrations
npm run migrate
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
