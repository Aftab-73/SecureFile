#!/bin/sh
PROJECT_DIR="/home/aftab/securefilr"  # Agar main folder ka naam same hai to rahne den, nahi to change karen
VENV_PY="/home/aftab/securefilr/.venv/bin/python"
cd "$PROJECT_DIR" || exit 1
exec "$VENV_PY" -m securefile.cli gui