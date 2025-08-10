#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
APP_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
VENV_DIR="$APP_DIR/.venv"
ENV_LOCAL="$APP_DIR/.env"
ENV_SYSTEM="/etc/default/familyhub"

ensure_venv(){
  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip wheel
    if [[ -f "$APP_DIR/requirements.txt" ]]; then
      "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
    fi
  fi
}

ensure_venv

ENV_USED=""
if [[ -f "$ENV_LOCAL" ]]; then
  set -a; source "$ENV_LOCAL"; set +a
  ENV_USED="$ENV_LOCAL"
else
  if [[ -f "$ENV_SYSTEM" ]]; then
    set -a; source "$ENV_SYSTEM"; set +a
    ENV_USED="$ENV_SYSTEM"
  fi
fi

if [[ -n "$ENV_USED" ]]; then
  echo "Using env from $ENV_USED"
else
  echo "No env file found; running with current environment"
fi

exec "$VENV_DIR/bin/python" "$APP_DIR/main.py"
