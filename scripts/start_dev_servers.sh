#!/usr/bin/env bash
# Combined launcher for Next.js Web App and FastAPI Backend API
DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=================================================="
echo "  REBUILDLY DEV SERVERS LAUNCHER"
echo "=================================================="
echo "1. Next.js Web App:  http://localhost:3009"
echo "2. FastAPI Backend:  http://localhost:8009"
echo "3. Redis Commander:  http://localhost:8089"
echo "=================================================="

# Kill any lingering uvicorn/next instances on ports 3009 or 8009
fuser -k 8009/tcp >/dev/null 2>&1
fuser -k 3009/tcp >/dev/null 2>&1

echo "Starting Next.js Web App..."
(cd "$DIR/client-template" && npm run build && npm run start) &

echo "Starting FastAPI Backend API..."
(cd "$DIR" && ./venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8009 --reload) &

wait
