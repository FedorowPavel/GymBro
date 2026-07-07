#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy NO_PROXY no_proxy

exec .venv/bin/python main.py
