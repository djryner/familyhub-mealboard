#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME=${APP_NAME:-familyhub}
APP_USER=${APP_USER:-pi}
APP_DIR=${APP_DIR:-/home/pi/familyhub}
VENV_DIR=${VENV_DIR:-$APP_DIR/.venv}
ENV_FILE=${ENV_FILE:-/etc/default/$APP_NAME}
SECRET_DIR=${SECRET_DIR:-/etc/$APP_NAME}
SECRET_PATH=${SECRET_PATH:-$SECRET_DIR/service_account.json}
LOCK_FILE=/var/lock/${APP_NAME}-setup.lock
DRY_RUN=${DRY_RUN:-0}

log(){ echo "$1 $2"; }
info(){ log "ℹ️" "$*"; }
success(){ log "✅" "$*"; }
warn(){ log "⚠️" "$*"; }

run(){
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "DRY RUN: $*"
  else
    eval "$@"
  fi
}

# acquire lock
exec 9>"$LOCK_FILE"
flock -n 9 || { echo "Another setup is running"; exit 1; }
trap 'flock -u 9' EXIT

# preflight
[[ $EUID -eq 0 ]] || { echo "Run as root"; exit 1; }
[[ $(ps -p 1 -o comm=) == systemd ]] || { echo "systemd required"; exit 1; }
PY_VER=$(python3 -c 'import sys; print(".".join(map(str,sys.version_info[:2])))')
if [[ "$(printf '%s\n3.11\n' "$PY_VER" | sort -V | head -n1)" != "3.11" ]]; then
echo "Python >=3.11 required"; exit 1
fi

info "Installing dependencies"
run apt-get update -y
run apt-get install -y python3-venv python3-pip pkg-config libsystemd-dev whiptail

ensure_venv(){
  local recreate=0
  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    recreate=1
  else
    local vver=$("$VENV_DIR/bin/python" -c 'import sys; print(".".join(map(str,sys.version_info[:2])))')
    [[ "$vver" != "$PY_VER" ]] && recreate=1
  fi
  if [[ $recreate -eq 1 ]]; then
    info "Creating virtualenv"
    run rm -rf "$VENV_DIR"
    run python3 -m venv "$VENV_DIR"
  fi
  run "$VENV_DIR/bin/pip" install --upgrade pip wheel
  if [[ -f "$APP_DIR/requirements.txt" ]]; then
    run "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
  fi
}
ensure_venv

ensure_kv(){
  local file="$1" key="$2" val="$3" tmp
  if grep -q "^$2=" "$file" 2>/dev/null; then
    return
  fi
  tmp=$(mktemp)
  if [[ -f "$file" ]]; then
    cat "$file" > "$tmp"
  fi
  printf '%s=%s\n' "$key" "$val" >> "$tmp"
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "DRY RUN: update $file with $key=$val"
    rm -f "$tmp"
  else
    install -m 0644 "$tmp" "$file"
  fi
}

if [[ ! -f "$ENV_FILE" ]]; then
  info "Environment file missing; running configure_env.sh"
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "DRY RUN: scripts/configure_env.sh"
  else
    scripts/configure_env.sh
  fi
else
  ensure_kv "$ENV_FILE" "GOOGLE_APPLICATION_CREDENTIALS" "$SECRET_PATH"
  chmod 0644 "$ENV_FILE"
fi

if [[ ! -f "$SECRET_PATH" ]]; then
  info "Service account missing; running configure_env.sh"
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "DRY RUN: scripts/configure_env.sh"
  else
    scripts/configure_env.sh
  fi
else
  chmod 0600 "$SECRET_PATH"
  chown root:root "$SECRET_PATH"
fi
mkdir -p "$SECRET_DIR"
chmod 0750 "$SECRET_DIR"
chown root:root "$SECRET_DIR"

install_service(){
  local unit="/etc/systemd/system/${APP_NAME}.service" tmp backup
  if systemctl is-active --quiet ${APP_NAME}.service; then
    run systemctl stop ${APP_NAME}.service || true
  fi
  tmp=$(mktemp)
  cat > "$tmp" <<SERV
[Unit]
Description=FamilyHub Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
# To enable sdnotify/watchdog later, switch to:
# Type=notify
# WatchdogSec=30s
User=${APP_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${ENV_FILE}
ExecStart=${VENV_DIR}/bin/python ${APP_DIR}/main.py
Restart=on-failure
RestartSec=2
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERV
  if [[ -f "$unit" ]]; then
    backup="${unit}.bak-$(date +%Y%m%d-%H%M%S)"
    run cp "$unit" "$backup"
  fi
  run install -m 0644 "$tmp" "$unit"
  rm -f "$tmp"
  run systemctl daemon-reload
  run systemctl enable --now ${APP_NAME}.service
}
install_service

if [[ "$DRY_RUN" != 1 ]]; then
  sleep 1
  if ! systemctl is-active --quiet ${APP_NAME}.service; then
    warn "Service failed to start; last logs:"; journalctl -u ${APP_NAME}.service -n 50 || true; exit 1
  fi
  success "Service ${APP_NAME}.service is active"
fi

success "Setup complete"
info "Re-run this script anytime: sudo bash scripts/setup_pi.sh"
