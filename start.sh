#!/usr/bin/env bash
# Render / Linux — point d’entrée WSGI : Flask sous-jacent à Dash (PAS app:app).
set -euo pipefail
PORT="${PORT:-10000}"
exec gunicorn wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers 1 \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
