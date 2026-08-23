#!/usr/bin/env bash
# Dedicated launcher for Next.js Web Application (Port 3009)
cd "$(dirname "$0")/../client-template" || exit 1
echo "🚀 Starting Next.js Web App on http://localhost:3009..."
npm run dev
