#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8765}"

cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to run the local preview server." >&2
  exit 1
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port ${PORT} is already in use."
  echo "If the gallery is already running, open: http://localhost:${PORT}/"
  exit 0
fi

echo "Steerix Motion Gallery"
echo "Open: http://localhost:${PORT}/"
echo "Press Ctrl+C to stop."
echo

exec python3 -m http.server "$PORT"
