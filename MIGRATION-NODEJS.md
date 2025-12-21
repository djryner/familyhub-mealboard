# Migration Guide: Python → Node.js

This guide helps you migrate from the Python/Flask version to the Node.js/Express version of FamilyHub.

## Overview

The Node.js version is a complete rewrite with the same features but different technology stack:

| Component | Python Version | Node.js Version |
|-----------|---------------|-----------------|
| Runtime | Python 3.12+ | Node.js 18+ |
| Web Framework | Flask | Express.js |
| Database Driver | SQLAlchemy | better-sqlite3 |
| Templates | Jinja2 | EJS |
| Package Manager | pip/uv | npm |
| Process Manager | systemd | systemd |

## Database Compatibility

The Node.js version uses the **same SQLite schema** as the Python version, with minor differences:

### Compatible Tables
✅ These tables are fully compatible:
- `chore_templates`
- `chore_metadata`
- `chores`
- `users`
- `points_ledger`
- `rewards`
- `reward_redemptions`

### Migration Steps

#### Option 1: Keep Existing Database
If you want to keep your existing data:

```bash
# Backup your Python database
cp familyhub.db familyhub-python-backup.db

# The Node.js app will use the existing database
# No changes needed!
```

#### Option 2: Fresh Start
If you want to start fresh:

```bash
# Remove old database
rm familyhub.db

# Seed new database
npm run seed
```

## Configuration Migration

### Python (.env or config)
```python
# Python version
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
FAMILYHUB_CALENDAR_ID=calendar@group.calendar.google.com
FAMILYHUB_TZ=America/Chicago
DATABASE_URL=sqlite:///familyhub.db
SESSION_SECRET=secret
HOST=0.0.0.0
PORT=5000
```

### Node.js (.env)
```bash
# Node.js version (same variables, slightly different format)
GOOGLE_APPLICATION_CREDENTIALS=./secrets/familyhub-467020-b04ae183c477.json
FAMILYHUB_CALENDAR_ID=calendar@group.calendar.google.com
FAMILYHUB_TZ=America/Chicago
DATABASE_PATH=./familyhub.db
SESSION_SECRET=secret
HOST=0.0.0.0
PORT=8000

# Additional Node.js settings
NODE_ENV=production
FAMILYHUB_HEALTH_ENABLED=true
POINTS_ENABLED=true
POINTS_DEFAULT=1
```

## Deployment Migration

### Stop Python Service
```bash
sudo systemctl stop familyhub
sudo systemctl disable familyhub
```

### Install Node.js Version
```bash
# Run the Node.js install script
chmod +x install-node.sh
sudo ./install-node.sh
```

### Update Service Configuration
The Node.js install script creates a new systemd service at `/etc/systemd/system/familyhub.service`.

Key differences:
- `ExecStart` now points to Node.js instead of Python
- Working directory should point to Node.js project
- User remains `familyhub`

```ini
[Service]
Type=simple
User=familyhub
WorkingDirectory=/path/to/familyhub-mealboard
Environment="NODE_ENV=production"
EnvironmentFile=/path/to/familyhub-mealboard/.env
ExecStart=/usr/bin/node /path/to/familyhub-mealboard/server.js
```

## Feature Parity Checklist

✅ **Implemented:**
- Dashboard with chores and meals
- Chores management (complete/ignore)
- Points system
- Rewards catalog & redemption
- Google Calendar integration (meals)
- Google Tasks integration (chores)
- Health check endpoints
- Kiosk mode support
- SQLite database
- Session management
- Flash messages

⚠️ **May Need Customization:**
- Custom chore recurrence logic (simplified in Node.js version)
- Admin dashboard (not yet implemented)
- User authentication (Replit Auth removed)

## API Endpoint Mapping

All endpoints remain the same:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard |
| `/chores` | GET | Chores list |
| `/meal-plans` | GET | Meal plans |
| `/rewards` | GET | Rewards catalog |
| `/chores/:id/complete` | POST | Complete chore |
| `/chores/:id/ignore` | POST | Ignore chore |
| `/api/meals` | GET | Meals JSON |
| `/api/chore-categories` | GET | Categories JSON |
| `/api/chore-templates` | GET | Templates JSON |
| `/health/healthz` | GET | Liveness |
| `/health/readyz` | GET | Readiness |
| `/health/status` | GET | Status |

## Testing the Migration

### 1. Verify Database
```bash
sqlite3 familyhub.db ".tables"
# Should show: chore_metadata, chore_templates, chores, points_ledger, rewards, reward_redemptions, users
```

### 2. Check Service Status
```bash
sudo systemctl status familyhub
sudo journalctl -u familyhub -f
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health/healthz

# Dashboard (should return HTML)
curl http://localhost:8000/

# API endpoint
curl http://localhost:8000/api/chore-categories
```

### 4. Test in Browser
Open `http://your-pi-ip:8000` in a browser and verify:
- Dashboard loads with chores/meals
- Leaderboard shows users with points
- Chores can be completed/ignored
- Rewards catalog is accessible

## Rollback Plan

If you need to rollback to Python:

```bash
# Stop Node.js service
sudo systemctl stop familyhub
sudo systemctl disable familyhub

# Restore Python service
sudo systemctl enable familyhub-python  # If you backed it up
sudo systemctl start familyhub-python

# Restore database backup (if needed)
cp familyhub-python-backup.db familyhub.db
```

## Performance Notes

The Node.js version is expected to have:
- **Similar memory usage** (~50-100MB)
- **Faster startup time** (Node.js vs Python interpreter)
- **Better SQLite performance** (better-sqlite3 is synchronous and faster)
- **Lower CPU usage** for typical family workloads

## Troubleshooting

### Google API Errors
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` path is absolute
- Check service account has Calendar & Tasks API access
- Verify calendar is shared with service account email

### Database Errors
```bash
# Check database integrity
sqlite3 familyhub.db "PRAGMA integrity_check;"

# View tables
sqlite3 familyhub.db ".schema"
```

### Service Won't Start
```bash
# Check logs
sudo journalctl -u familyhub -n 100 --no-pager

# Test manually
cd /path/to/familyhub-mealboard
node server.js
```

### Port Conflicts
If port 8000 is in use:
```bash
# Change in .env
PORT=8080

# Update kiosk URL in autostart file
# Edit /home/familyhub/.config/autostart/familyhub-kiosk.desktop
```

## Support

For issues specific to the Node.js version:
1. Check logs: `journalctl -u familyhub -f`
2. Verify `.env` configuration
3. Test endpoints with `curl`
4. Check database with `sqlite3`

The Node.js version maintains feature parity with the Python version while offering improved performance and simpler deployment.
