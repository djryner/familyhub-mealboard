#!/bin/bash
set -e

if grep -qi 'Raspberry Pi' /proc/device-tree/model 2>/dev/null; then
  echo 'Detected Raspberry Pi.'
else
  echo 'Warning: non-Pi environment.'
fi

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip pkg-config libsystemd-dev
sudo pip3 install --break-system-packages -U sdnotify flask fastapi

if [ ! -f /etc/default/familyhub ]; then
  sudo tee /etc/default/familyhub > /dev/null <<'EOF'
HOST=0.0.0.0
PORT=8000
FAMILYHUB_HEALTH_ENABLED=true
EOF
fi

sudo cp systemd/familyhub.service /etc/systemd/system/familyhub.service
sudo systemctl daemon-reload
sudo systemctl enable familyhub
sudo systemctl start familyhub

echo 'Service installed. Test with:'
echo '  systemctl status familyhub'
echo '  journalctl -u familyhub -e -f'
echo '  curl -f http://127.0.0.1:8000/healthz || curl -f http://127.0.0.1:8030/healthz'
