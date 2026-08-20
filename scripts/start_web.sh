#!/usr/bin/env bash
# Dedicated launcher for Next.js Web Application (Port 3000)
cd "$(dirname "$0")/../client-template" || exit 1
echo "🚀 Starting Next.js Web App on http://localhost:3000..."
npm run dev
