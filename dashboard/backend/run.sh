#!/bin/bash
# Empathy Memory Dashboard API - Development Runner
# Quick start script for local development

set -e

cd "$(dirname "$0")"

echo "==================================================================="
echo "Empathy Memory Dashboard API - Starting Development Server"
echo "==================================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "Starting server on http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Health: http://localhost:8000/ping"
echo "- WebSocket: ws://localhost:8000/ws/metrics"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run with auto-reload
uvicorn dashboard.backend.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
