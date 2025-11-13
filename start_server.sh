#!/bin/bash

echo "================================"
echo "Starting Backend Server"
echo "================================"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "❌ Error: credentials.json not found!"
    echo "Please ensure credentials.json is in the backend folder"
    exit 1
fi

echo "✓ Found credentials.json"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found, creating from .env.example"
    cp .env.example .env
fi

echo "✓ Environment configured"
echo ""

# Install/update dependencies
echo "Checking dependencies..."
pip3 install -r requirements.txt --quiet

echo "✓ Dependencies installed"
echo ""

# Kill any existing Flask process on port 5000
echo "Checking for existing Flask processes..."
if lsof -ti:5000 > /dev/null 2>&1; then
    echo "⚠️  Port 5000 is in use, killing existing process..."
    lsof -ti:5000 | xargs kill -9
    sleep 1
fi

echo "✓ Port 5000 is available"
echo ""

# Start Flask server
echo "================================"
echo "🚀 Starting Flask Server..."
echo "================================"
echo ""
echo "Backend will be available at: http://localhost:5000"
echo "Press CTRL+C to stop the server"
echo ""

python3 app.py
