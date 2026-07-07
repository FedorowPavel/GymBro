#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

pick_python() {
  for candidate in python3.12 python3.11 python3.10; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  echo "Python 3.10+ is required for cursor-sdk." >&2
  exit 1
}

PY="$(pick_python)"
echo "Using $PY ($($PY --version))"

if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi

.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env — fill TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER_IDS, CURSOR_API_KEY"
fi

echo "Setup done. Run: ./run.sh"
