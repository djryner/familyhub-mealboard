# FamilyHub Node.js Quick Start

## Local Development (macOS)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Seed database:**
   ```bash
   npm run seed
   ```

4. **Run server:**
   ```bash
   npm start
   # or for development with auto-reload:
   npm run dev
   ```

5. **Open in browser:**
   ```
   http://localhost:8000
   ```

## Deploy to Raspberry Pi

1. **Clone/copy files to Pi:**
   ```bash
   git clone <repo-url>
   cd familyhub-mealboard
   ```

2. **Run install script:**
   ```bash
   chmod +x install-node.sh
   sudo ./install-node.sh
   ```

3. **Configure environment:**
   ```bash
   nano .env
   # Update GOOGLE_APPLICATION_CREDENTIALS and FAMILYHUB_CALENDAR_ID
   ```

4. **Restart service:**
   ```bash
   sudo systemctl restart familyhub
   ```

5. **Check status:**
   ```bash
   sudo systemctl status familyhub
   sudo journalctl -u familyhub -f
   ```

## Key Endpoints

- Dashboard: `http://localhost:8000/`
- Chores: `http://localhost:8000/chores`
- Meals: `http://localhost:8000/meal-plans`
- Rewards: `http://localhost:8000/rewards`
- Health: `http://localhost:8000/health/healthz`

## Common Commands

```bash
# Start server
npm start

# Development mode (auto-reload)
npm run dev

# Seed database
npm run seed

# Service management (Pi only)
sudo systemctl status familyhub
sudo systemctl restart familyhub
sudo journalctl -u familyhub -f
```

## File Structure

```
├── server.js                 # Main entry point
├── package.json              # Dependencies
├── .env                      # Configuration
├── src/
│   ├── config/              # Config management
│   ├── db/                  # Database
│   ├── services/            # Business logic
│   ├── routes/              # HTTP routes
│   └── utils/               # Utilities
├── views/                   # EJS templates
└── public/                  # Static files
```

## Troubleshooting

**Can't connect to Google APIs:**
- Check `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`
- Ensure service account has Calendar/Tasks API access

**Database errors:**
- Delete `familyhub.db` and run `npm run seed`

**Service won't start:**
- Check logs: `sudo journalctl -u familyhub -n 50`
- Test manually: `node server.js`

For detailed migration from Python version, see `MIGRATION-NODEJS.md`.
