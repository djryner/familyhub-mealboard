#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME=${APP_NAME:-familyhub}
APP_USER=${APP_USER:-pi}
APP_DIR=${APP_DIR:-/home/pi/familyhub}
ENV_FILE=${ENV_FILE:-/etc/default/${APP_NAME}}
SECRET_DIR=${SECRET_DIR:-/etc/${APP_NAME}}
SECRET_PATH=${SECRET_PATH:-${SECRET_DIR}/service_account.json}

log(){ echo "$1 $2"; }
info(){ log "ℹ️" "$*"; }
success(){ log "✅" "$*"; }
warn(){ log "⚠️" "$*"; }

[[ $EUID -eq 0 ]] || { echo "Must run as root"; exit 1; }

mkdir -p "$SECRET_DIR"
chmod 0750 "$SECRET_DIR"

BACKED_UP_ENV=""
backup_env(){
  if [[ -f "$ENV_FILE" && -z "$BACKED_UP_ENV" ]]; then
    BACKED_UP_ENV=1
    local backup="${ENV_FILE}.bak-$(date +%Y%m%d-%H%M%S)"
    cp "$ENV_FILE" "$backup"
    info "Backup of env at $backup"
  fi
}

merge_kv(){
  local file="$1" key="$2" val="$3" tmp
  backup_env
  tmp=$(mktemp)
  if [[ -f "$file" ]]; then
    awk -v k="$key" -v v="$val" 'BEGIN{found=0}
      $0~"^"k"=" {print k"="v; found=1; next}
      {print}
      END{if(!found) print k"="v}' "$file" > "$tmp"
  else
    printf '%s=%s\n' "$key" "$val" > "$tmp"
  fi
  install -m 0644 "$tmp" "$file"
}

command -v whiptail >/dev/null && HAVE_WHIPTAIL=1 || HAVE_WHIPTAIL=0

ask(){
  local prompt="$1" default="$2" val
  if [[ $HAVE_WHIPTAIL -eq 1 ]]; then
    val=$(whiptail --inputbox "$prompt" 8 60 "$default" 3>&1 1>&2 2>&3) || exit 1
  else
    read -rp "$prompt [$default]: " val
    val=${val:-$default}
  fi
  echo "$val"
}

yesno(){
  local prompt="$1" default="$2" ans
  if [[ $HAVE_WHIPTAIL -eq 1 ]]; then
    if [[ "$default" == "Y" ]]; then
      whiptail --yesno "$prompt" 8 60 && return 0 || return 1
    else
      whiptail --yesno "$prompt" 8 60 && return 0 || return 1
    fi
  else
    read -rp "$prompt [${default}/n]: " ans
    ans=${ans:-$default}
    [[ "$ans" =~ ^[Yy]$ ]]
  fi
}

HOST=$(ask "Host to bind" "${HOST:-0.0.0.0}")
PORT=$(ask "Port" "${PORT:-8000}")
while ! [[ "$PORT" =~ ^[0-9]+$ && $PORT -ge 1 && $PORT -le 65535 ]]; do
  warn "Port must be 1-65535"
  PORT=$(ask "Port" "8000")
done
FAMILYHUB_HEALTH_ENABLED=$(ask "Enable health endpoint (true/false)" "${FAMILYHUB_HEALTH_ENABLED:-true}")
FAMILYHUB_CALENDAR_ID=$(ask "Google Calendar ID (optional)" "${FAMILYHUB_CALENDAR_ID:-}")

# Secret handling
REPLACE_SECRET=1
if [[ -f "$SECRET_PATH" ]]; then
  if yesno "Service account exists. Replace?" "n"; then
    REPLACE_SECRET=1
  else
    REPLACE_SECRET=0
  fi
fi

if [[ $REPLACE_SECRET -eq 1 ]]; then
  backup=""
  if [[ -f "$SECRET_PATH" ]]; then
    backup="${SECRET_PATH}.bak-$(date +%Y%m%d-%H%M%S)"
    cp "$SECRET_PATH" "$backup"
    info "Backup of old secret at $backup"
  fi
  if yesno "Provide path to JSON file? (No to paste)" "Y"; then
    SRC=$(ask "Path to service account JSON" "")
    install -m 0600 "$SRC" "$SECRET_PATH"
  else
    tmp=$(mktemp)
    echo "Paste JSON, end with Ctrl-D:" >&2
    cat > "$tmp"
    install -m 0600 "$tmp" "$SECRET_PATH"
    rm -f "$tmp"
  fi
fi
chown root:root "$SECRET_PATH"
chmod 0600 "$SECRET_PATH"

merge_kv "$ENV_FILE" "HOST" "$HOST"
merge_kv "$ENV_FILE" "PORT" "$PORT"
merge_kv "$ENV_FILE" "FAMILYHUB_HEALTH_ENABLED" "$FAMILYHUB_HEALTH_ENABLED"
if [[ -n "$FAMILYHUB_CALENDAR_ID" ]]; then
  merge_kv "$ENV_FILE" "FAMILYHUB_CALENDAR_ID" "$FAMILYHUB_CALENDAR_ID"
fi
merge_kv "$ENV_FILE" "GOOGLE_APPLICATION_CREDENTIALS" "$SECRET_PATH"

success "Updated $ENV_FILE"
cat "$ENV_FILE"
