# Admin Interface Guide

## Overview
The FamilyHub Admin Interface provides a mobile-friendly way to manage your family's hub without needing to use the kiosk screen. Any device on the same network can access the admin interface.

## Accessing the Admin Interface

1. **From the same network**: Navigate to `http://<raspberry-pi-ip>:8000/admin`
2. **On the Pi itself**: Navigate to `http://localhost:8000/admin`
3. **Via navigation**: Click "⚙️ Admin" in the main navigation menu
4. **QR Code (Desktop)**: When viewing the admin page on a desktop/laptop, scan the QR code at the top with your phone to quickly open the admin on your mobile device

## Features

### Dashboard
- **Quick Stats**: View counts of users, pending chores, upcoming meals, and active rewards
- **QR Code (Desktop Only)**: Scan with your phone to open admin on mobile
- **Quick Links**: Direct access to manage users, meals, chores, and rewards
- **Recent Activity**: See recently added meals and redemptions

### Manage Users
- **View Users**: See all family members with their current points balance
- **Add User**: Create new family members (with optional parent status)
- **Delete User**: Remove users from the system

### Manage Meals
- **View Meals**: See all planned meals sorted by date
- **Add Meal**: Create new meal plans with:
  - Title
  - Date
  - Meal type (Breakfast, Lunch, Dinner, Snack)
  - Description (optional)
- **Edit Meal**: Update existing meal details
- **Delete Meal**: Remove meal plans

### Manage Chores
- **View Chore Templates**: See all available chore templates
- **Add Template**: Create new chore templates with:
  - Title
  - Description
  - Category (Cleaning, Kitchen, Outdoor, Pet Care, Organizing, Other)
  - Points value
- **Delete Template**: Remove chore templates

### Manage Rewards
- **View Rewards**: See all rewards with their point costs
- **Add Reward**: Create new rewards with:
  - Title
  - Description (optional)
  - Point cost
  - Active status
- **Toggle Active/Inactive**: Enable or disable rewards
- **Delete Reward**: Remove rewards from the catalog

## Mobile Experience

The admin interface is designed with mobile devices in mind:

- **Touch-Friendly Buttons**: Large tap targets (minimum 48px height)
- **Responsive Forms**: Full-width inputs on mobile devices
- **Card-Based Layout**: Easy-to-scan information cards
- **Simplified Navigation**: Clean, straightforward menu structure
- **No Pinch/Zoom**: Properly scaled for mobile viewports

## Tips

1. **Add Meals in Advance**: Plan your week's meals at once for easier management
2. **Use Categories**: Organize chores by category for better clarity
3. **Set Appropriate Points**: Balance reward costs with chore point values
4. **Toggle Inactive**: Instead of deleting rewards, toggle them inactive for seasonal availability
5. **Check Dashboard**: The dashboard gives you a quick overview of system activity

## Technical Details

- **Port**: 8000 (default)
- **Database**: Local SQLite file (`familyhub.db`)
- **Session Management**: Uses express-session for flash messages
- **No External APIs**: Everything runs locally

## Troubleshooting

**Can't access admin interface:**
- Ensure the server is running: `systemctl status familyhub` (on Pi)
- Check your network connection
- Verify you're using the correct IP address

**Changes not showing:**
- Refresh your browser (the kiosk screen auto-refreshes every 60 seconds)
- Check for error messages at the top of the page

**Database errors:**
- Check server logs: `journalctl -u familyhub -f` (on Pi)
- Verify database file permissions
