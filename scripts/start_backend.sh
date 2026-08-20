#!/usr/bin/env bash
# Dedicated launcher for FastAPI Backend API (Port 8000)
cd "$(dirname "$0")/.." || exit 1
echo "🚀 Starting FastAPI Backend API on http://localhost:8000..."
./venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
