# QR Code Feature for Admin Interface

## Overview
Added a QR code feature to the admin dashboard that displays **only on desktop/tablet devices**. When viewing the admin page on a larger screen, users can scan the QR code with their phone to quickly open the admin interface on their mobile device from anywhere.

## How It Works

### Desktop Experience (768px and wider)
1. Visit the admin interface on a desktop/laptop (via configured URL)
2. See a prominent QR code card at the top of the page
3. Scan the QR code with your phone's camera
4. Automatically opens the admin interface on your phone - **works from any network** (home Wi-Fi, cellular, etc.)

### Mobile Experience (under 768px)
- QR code section is **hidden** (no need to scan when already on mobile)
- Full admin functionality available directly

## Implementation Details

### Backend (`src/routes/admin.js`)
- **Configurable Admin URL** from environment variables:
  - `ADMIN_BASE_URL` (e.g., `https://admin.soft-relay.com`)
  - `ADMIN_PATH` (e.g., `/admin`)
- Generates QR code pointing to the configured admin URL
- Uses the `qrcode` npm package for QR generation
- Passes QR code data URL to the view
- **No longer relies on local IP detection** - works globally via Cloudflare Tunnel

### Frontend (`views/admin/index.ejs`)
- Displays QR code card with gradient background
- Shows the URL below the QR code for reference
- Wrapped in `desktop-only` class for responsive hiding

### Styling (`public/css/admin.css`)
- **Media query**: `@media (min-width: 768px)` shows QR code
- Beautiful gradient card (purple/blue)
- White background for QR code image
- Centered layout with shadows

### Utility (`src/utils/qrcode.js`)
- Reusable QR code generation functions
- Supports both data URL (PNG) and SVG formats
- Configurable error correction, size, colors

## Features

✅ **Global Access**: Works from any network (home, cellular, remote)  
✅ **Secure HTTPS**: Via Cloudflare Tunnel  
✅ **Responsive Design**: Only shows on desktop  
✅ **Beautiful UI**: Gradient card with clear instructions  
✅ **Network Independent**: No LAN routing or mDNS required  
✅ **Easy Scanning**: Large, clear QR code (300x300px)  
✅ **URL Display**: Shows the URL for manual entry if needed  
✅ **Configurable**: Environment variables for easy updates  

## Example URL
The QR code encodes a URL like:
```
https://admin.soft-relay.com/admin
```

This allows any device from any location to securely access the admin interface.

## Configuration

Set these environment variables in your `.env` file:

```bash
# Admin Access Configuration
ADMIN_BASE_URL=https://admin.soft-relay.com
ADMIN_PATH=/admin
```

For local development, use:
```bash
ADMIN_BASE_URL=http://localhost:8000
ADMIN_PATH=/admin
```

## Dependencies Added
```json
{
  "qrcode": "^1.5.4"  // QR code generation library
}
```

## CSS Classes

### `.desktop-only`
- `display: none` by default (mobile-first)
- `display: block` on screens ≥768px

### `.qr-code-card`
- Gradient background (purple to violet)
- White QR code area with shadow
- Centered, max-width 500px
- Rounded corners

## User Experience

### On Desktop:
```
╔═══════════════════════════════════════╗
║   📱 Scan to Access Admin Securely    ║
║                                       ║
║   ┌─────────────────┐                ║
║   │                 │                ║
║   │   [QR Code]     │                ║
║   │                 │                ║
║   └─────────────────┘                ║
║                                       ║
║   https://admin.soft-relay.com/admin ║
║   🔒 Secure access via Cloudflare    ║
╚═══════════════════════════════════════╝

[Stats Cards Below...]
```

### On Mobile:
```
[Stats Cards - No QR Code]
```

## Testing

✅ QR code generates successfully  
✅ Contains correct local IP URL  
✅ Hidden on mobile viewport  
✅ Visible on desktop viewport  
✅ Scannable with phone camera  
✅ Links to correct admin page  

## Browser Compatibility

- ✅ Chrome/Edge (desktop & mobile)
- ✅ Safari (desktop & mobile)
- ✅ Firefox (desktop & mobile)
- ✅ iOS Camera App (scanning)
- ✅ Android Camera App (scanning)

## Future Enhancements (Optional)

1. **Custom branding**: Add FamilyHub logo to QR code
2. **Dark mode support**: Invert colors for dark theme
3. **Multiple URLs**: Generate QR codes for other pages
4. **Share button**: Copy URL to clipboard
5. **WiFi QR**: Generate WiFi connection QR code

---

**Status**: ✅ Implemented and working
**Date**: December 21, 2025
