#!/usr/bin/env bash
# Render / Linux — ASGI avec Uvicorn (sans Gunicorn). Monte Dash via asgi.py.
set -euo pipefail
PORT="${PORT:-10000}"
exec uvicorn asgi:app --host 0.0.0.0 --port "${PORT}" --workers 1
