#!/bin/bash
set -e

echo "🚀 Installing FamilyHub (Node.js Edition)..."

# Check for Raspberry Pi
if grep -qi 'Raspberry Pi' /proc/device-tree/model 2>/dev/null; then
  echo '✅ Detected Raspberry Pi.'
else
  echo '⚠️  Warning: non-Pi environment.'
fi

# Install Node.js if not present
if ! command -v node &> /dev/null; then
  echo "📦 Installing Node.js..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# Install dependencies
echo "📦 Installing npm dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "📝 Creating .env file from .env.example..."
  cp .env.example .env
  echo "✅ .env file created. You can customize it if needed."
fi

# Initialize database
echo "🗄️  Initializing database..."
npm run migrate || echo "⚠️  Migration script not found, database will be initialized on first run"

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/familyhub.service > /dev/null <<EOF
[Unit]
Description=FamilyHub Node.js Application
After=network.target

[Service]
Type=simple
User=familyhub
WorkingDirectory=$(pwd)
Environment="NODE_ENV=production"
EnvironmentFile=$(pwd)/.env
ExecStart=$(which node) $(pwd)/server.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl enable familyhub
sudo systemctl restart familyhub

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your configuration"
echo "   2. systemctl status familyhub"
echo "   3. journalctl -u familyhub -f"
echo "   4. curl http://localhost:8000/health/healthz"
echo ""

# Create Chromium kiosk autostart (using HOST/PORT from .env)
if [ -f .env ]; then
  source .env
  HOST=${HOST:-0.0.0.0}
  PORT=${PORT:-8000}
  KIOSK_URL="http://${HOST}:${PORT}"
  
  echo "🖥️  Setting up Chromium kiosk autostart..."
  AUTOSTART_DIR="/home/familyhub/.config/autostart"
  sudo mkdir -p "$AUTOSTART_DIR"
  sudo chown -R familyhub:familyhub /home/familyhub/.config
  
  sudo -u familyhub bash -c "cat > '$AUTOSTART_DIR/familyhub-kiosk.desktop' <<EOF
[Desktop Entry]
Type=Application
Name=FamilyHub Kiosk
Exec=chromium-browser --noerrdialogs --disable-infobars --kiosk $KIOSK_URL
X-GNOME-Autostart-enabled=true
EOF"
  
  echo "✅ Kiosk autostart configured for $KIOSK_URL"
fi

echo "🎉 FamilyHub is ready!"
