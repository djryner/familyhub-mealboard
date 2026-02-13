# Cloudflare Tunnel Deployment - Quick Start

## ⚡ Quick Summary

Admin access is now global via `https://admin.soft-relay.com/admin` instead of LAN-only.

## 🚀 Deployment Steps (Raspberry Pi)

### 1. Update Environment Variables

Edit `/path/to/familyhub/.env` and add:

```bash
# Admin Access Configuration
ADMIN_BASE_URL=https://admin.soft-relay.com
ADMIN_PATH=/admin
```

### 2. Restart the Application

```bash
sudo systemctl restart familyhub
```

### 3. Verify QR Code

1. Visit `https://admin.soft-relay.com/admin` on a desktop
2. Check that the QR code displays the HTTPS URL (not local IP)
3. Scan QR code with mobile device on cellular
4. Verify it opens the admin page

## ✅ Verification Checklist

- [ ] `.env` file updated with `ADMIN_BASE_URL` and `ADMIN_PATH`
- [ ] Application restarted
- [ ] Admin accessible at `https://admin.soft-relay.com/admin`
- [ ] QR code displays HTTPS URL
- [ ] QR code works from mobile device on cellular network
- [ ] Cloudflare Tunnel is running: `systemctl status cloudflared`

## 🔧 Cloudflare Tunnel Status

Check if the tunnel is running:

```bash
# Check service status
sudo systemctl status cloudflared

# View tunnel info
cloudflared tunnel info familyhub-admin

# View logs
sudo journalctl -u cloudflared -f
```

## 🔙 Rollback (if needed)

If you need to revert to local-only access:

1. **Remove or comment out** the new env variables:
   ```bash
   # ADMIN_BASE_URL=https://admin.soft-relay.com
   # ADMIN_PATH=/admin
   ```

2. **Restart**:
   ```bash
   sudo systemctl restart familyhub
   ```

3. QR code will fall back to `http://localhost:8000/admin`

## 📝 Code Changes Summary

**Modified Files:**
- `src/routes/admin.js` - Uses environment-based admin URL
- `views/admin/index.ejs` - Updated UI text for global access
- `.env.example` - Added new configuration variables

**Removed:**
- Local IP address detection logic
- LAN-specific QR code generation

## 🔐 Security Notes

- Admin is now globally accessible
- **Ensure Cloudflare Access is enabled** (if not already)
- Application-level authentication should be enforced
- Consider rate limiting on admin endpoints

## 📚 Full Documentation

See `CLOUDFLARE-TUNNEL-MIGRATION.md` for complete details.

## 🆘 Support

**Common Issues:**

1. **404 on admin URL**
   - Check Cloudflare DNS: `admin.soft-relay.com` should point to tunnel
   - Verify tunnel config: `cat ~/.cloudflared/config.yml`

2. **QR code shows old URL**
   - Check `.env` file has correct values
   - Restart application: `sudo systemctl restart familyhub`
   - Clear browser cache

3. **Tunnel not running**
   - Start tunnel: `sudo systemctl start cloudflared`
   - Enable on boot: `sudo systemctl enable cloudflared`

## 🎯 Next Steps

After deployment:

1. Test admin access from multiple networks (home, cellular, remote)
2. Verify authentication is working properly
3. Consider enabling Cloudflare Access for additional security
4. Update any documentation or training materials with new URL
5. Inform family members about new access method

---

**Deployment Date:** _[Fill in when deployed]_  
**Deployed By:** _[Fill in]_  
**Cloudflare Tunnel Status:** _[Fill in: Active/Inactive]_  
**Authentication Method:** _[Fill in: Cloudflare Access / App-level / Both]_
