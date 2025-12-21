# QR Code Feature for Admin Interface

## Overview
Added a QR code feature to the admin dashboard that displays **only on desktop/tablet devices**. When viewing the admin page on a larger screen, users can scan the QR code with their phone to quickly open the admin interface on their mobile device.

## How It Works

### Desktop Experience (768px and wider)
1. Visit http://localhost:8000/admin on a desktop/laptop
2. See a prominent QR code card at the top of the page
3. Scan the QR code with your phone's camera
4. Automatically opens the admin interface on your phone

### Mobile Experience (under 768px)
- QR code section is **hidden** (no need to scan when already on mobile)
- Full admin functionality available directly

## Implementation Details

### Backend (`src/routes/admin.js`)
- **Auto-detects local IP address** using Node.js `os.networkInterfaces()`
- Generates QR code pointing to: `http://<local-ip>:8000/admin`
- Uses the `qrcode` npm package for QR generation
- Passes QR code data URL to the view

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

✅ **Automatic IP Detection**: No configuration needed  
✅ **Responsive Design**: Only shows on desktop  
✅ **Beautiful UI**: Gradient card with clear instructions  
✅ **Network Access**: Works across your local network  
✅ **Easy Scanning**: Large, clear QR code (300x300px)  
✅ **URL Display**: Shows the URL for manual entry if needed  

## Example URL
The QR code encodes a URL like:
```
http://192.168.42.69:8000/admin
```

This allows any device on the same network to access the admin interface.

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
╔═══════════════════════════════════╗
║   📱 Scan to Open on Mobile       ║
║                                   ║
║   ┌─────────────────┐            ║
║   │                 │            ║
║   │   [QR Code]     │            ║
║   │                 │            ║
║   └─────────────────┘            ║
║                                   ║
║   http://192.168.42.69:8000/admin║
╚═══════════════════════════════════╝

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
