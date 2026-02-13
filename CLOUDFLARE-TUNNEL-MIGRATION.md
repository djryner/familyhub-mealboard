# Cloudflare Tunnel Migration - Admin Access

## Summary

FamilyHub Admin access has been migrated from LAN-only access (using local IP/hostname) to globally accessible, secure access via Cloudflare Tunnel. Admin is now reachable from anywhere using a stable HTTPS URL on our domain, without exposing the Raspberry Pi directly to the internet.

## What Changed

### Before (Old Behavior)

- Admin access was only available on the same local network as the Raspberry Pi
- QR code encoded a LAN-scoped URL such as:
  - `http://family-hub.local:<port>/admin`
  - `http://<pi-lan-ip>:<port>/admin`
- This stopped working once the Pi moved to an isolated network because devices on the primary home network couldn't route to it

### After (New Behavior)

- Admin access is published through Cloudflare Tunnel at a public HTTPS URL:
  - **`https://admin.soft-relay.com`**
- Requests go through Cloudflare, then over an outbound encrypted tunnel from the Pi to Cloudflare
- No inbound ports are opened on the router/firewall
- The Pi remains on an isolated network
- Works from any device on any network (home Wi-Fi, cellular, remote)

## Configuration

### Environment Variables

Add the following to your `.env` file (see `.env.example`):

```bash
# Admin Access Configuration
ADMIN_BASE_URL=https://admin.soft-relay.com
ADMIN_PATH=/admin
```

### Variable Descriptions

- **`ADMIN_BASE_URL`**: The base URL for admin access (typically via Cloudflare Tunnel)
  - Production: `https://admin.soft-relay.com`
  - Staging/Dev: Can be `http://localhost:8000` for local development
  
- **`ADMIN_PATH`**: The path appended to the base URL
  - Default: `/admin`
  - Can be customized if needed

### Full Admin URL

The complete admin URL is constructed as: `{ADMIN_BASE_URL}{ADMIN_PATH}`

Example: `https://admin.soft-relay.com/admin`

## Code Changes

### 1. Admin Route (`src/routes/admin.js`)

**Removed:**
- `getLocalIpAddress()` function (no longer needed)
- Local IP address detection logic
- `os` module import

**Added:**
- `getAdminUrl()` function that reads from environment variables
- Configuration-based URL generation

**Modified:**
- QR code now generates with the configured admin URL (Cloudflare Tunnel)
- Passes `adminUrl` to template instead of `localAdminUrl`

### 2. Admin Dashboard View (`views/admin/index.ejs`)

**Modified:**
- Updated QR code section text:
  - "Scan to Access Admin Securely" (instead of "Scan to Open on Mobile")
  - "manage FamilyHub from anywhere - no need to be on the same Wi-Fi network"
- Display `adminUrl` instead of `localAdminUrl`
- Added security note: "🔒 Secure access via Cloudflare Tunnel"

### 3. Environment Configuration (`.env.example`)

**Added:**
- `ADMIN_BASE_URL` environment variable
- `ADMIN_PATH` environment variable
- Documentation comments

## Cloudflare Tunnel Architecture

### High-Level Overview

1. **Raspberry Pi** runs `cloudflared` which maintains an outbound tunnel to Cloudflare
2. **Cloudflare DNS** contains a record for:
   - `admin.soft-relay.com` → tunnel
3. **Cloudflare** routes requests to the Pi's local service:
   - `http://localhost:8000` (or configured port)
4. **No networking changes** required on the home router:
   - No port forwarding
   - No inbound firewall rules
   - Works across segmented networks

### Benefits

- **Global Access**: Works from anywhere (home network, cellular, remote)
- **Stable URL**: No dependency on LAN routing or mDNS (`.local`) resolution
- **Secure**: TLS termination, DDoS protection at Cloudflare edge
- **Isolated Network**: Pi remains on isolated network with no exposed ports

## Security Model

### Cloudflare as the Security Front Door

Cloudflare provides:
- **TLS termination** (HTTPS)
- **DDoS/edge protection**
- **Optional identity-based access control** (recommended)

### Required Admin Protection

At minimum, one of the following must be enforced:

1. **Cloudflare Zero Trust / Access** policy requiring login (preferred)
2. **Application-level authentication** (must exist regardless, but Cloudflare Access provides an additional outer layer)

⚠️ **Important**: The admin URL is globally reachable, so we should treat it as "internet exposed," even though the Pi is not directly exposed.

### Recommendations

1. **Enable Cloudflare Access** on `admin.soft-relay.com`:
   - Require email authentication
   - Or integrate with Google/Microsoft/etc.
   - Whitelist specific email addresses/domains

2. **Application-level authentication** should remain in place:
   - Session-based authentication
   - Login required for all admin routes
   - Consider adding 2FA for extra security

3. **Rate limiting** on admin endpoints:
   - Prevent brute force attacks
   - Can be configured at Cloudflare or application level

## Testing

### Acceptance Criteria

- [x] QR code generates with `https://admin.soft-relay.com/admin` URL
- [ ] A phone on the primary home network can open the QR link and reach admin
- [ ] A phone on cellular (off Wi-Fi) can open the same QR link and reach admin
- [ ] No inbound ports are opened on the isolated network router
- [ ] Admin access is protected by authentication (Cloudflare Access and/or app auth)
- [x] QR code no longer uses `.local` hostnames or private IPs

### Test Steps

1. **Desktop/Laptop on Home Network**:
   ```bash
   # Visit admin dashboard
   open https://admin.soft-relay.com/admin
   ```

2. **Mobile Device on Home Wi-Fi**:
   - Open camera app
   - Scan QR code from admin dashboard
   - Verify it opens `https://admin.soft-relay.com/admin`

3. **Mobile Device on Cellular (LTE/5G)**:
   - Disable Wi-Fi
   - Open camera app
   - Scan QR code from admin dashboard
   - Verify it opens `https://admin.soft-relay.com/admin`

4. **From Remote Location**:
   - From a different network/location
   - Visit `https://admin.soft-relay.com/admin`
   - Verify authentication challenge (if Cloudflare Access is enabled)

## Rollback Plan

If you need to revert to LAN-only access:

1. **Update `.env`**:
   ```bash
   ADMIN_BASE_URL=http://localhost:8000
   # Or remove these variables to use defaults
   ```

2. **Restart the application**:
   ```bash
   npm run dev  # or your start command
   ```

3. **QR codes will generate with local URL** (though functionality will be limited to LAN)

## Migration Checklist

- [x] Update `.env.example` with new admin configuration
- [x] Update `src/routes/admin.js` to use environment-based URL
- [x] Update `views/admin/index.ejs` UI text and display
- [x] Remove local IP detection logic
- [ ] Update actual `.env` file on Raspberry Pi with production values
- [ ] Restart application on Raspberry Pi
- [ ] Test QR code from mobile device on home network
- [ ] Test QR code from mobile device on cellular
- [ ] Configure Cloudflare Access (recommended)
- [ ] Document Cloudflare Tunnel setup (if not already documented)

## Cloudflare Tunnel Setup (Reference)

If the tunnel is not yet set up, here are the basic steps:

1. **Install `cloudflared` on Raspberry Pi**:
   ```bash
   wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
   sudo dpkg -i cloudflared-linux-arm64.deb
   ```

2. **Authenticate with Cloudflare**:
   ```bash
   cloudflared tunnel login
   ```

3. **Create a tunnel**:
   ```bash
   cloudflared tunnel create familyhub-admin
   ```

4. **Configure the tunnel** (`~/.cloudflared/config.yml`):
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /home/pi/.cloudflared/<tunnel-id>.json
   
   ingress:
     - hostname: admin.soft-relay.com
       service: http://localhost:8000
     - service: http_status:404
   ```

5. **Route DNS**:
   ```bash
   cloudflared tunnel route dns familyhub-admin admin.soft-relay.com
   ```

6. **Run the tunnel** (as a service):
   ```bash
   sudo cloudflared service install
   sudo systemctl start cloudflared
   sudo systemctl enable cloudflared
   ```

## Support

If you encounter issues:

1. Check that `.env` variables are set correctly
2. Restart the application
3. Verify Cloudflare Tunnel is running: `sudo systemctl status cloudflared`
4. Check Cloudflare dashboard for tunnel status
5. Review application logs for QR code generation errors

## Additional Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Cloudflare Access Documentation](https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/)
- [Node.js QRCode Library](https://www.npmjs.com/package/qrcode)
