#!/bin/bash

# Production startup script for Adda Education Dashboard API
# This script starts the Flask application using Gunicorn for handling 500+ concurrent users

echo "=========================================="
echo "Starting Adda Education API (Production)"
echo "=========================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Creating template .env file..."
    cat > .env << 'EOL'
# Google Sheets Configuration
CREDENTIALS_GID=1409173850
DRIVE_FOLDER_ID=1m5gFfXB0AifbAn387sTM_mr8gemi1Jte

# JWT Secret (CHANGE THIS IN PRODUCTION!)
JWT_SECRET_KEY=your-secret-key-change-in-production-$(openssl rand -hex 32)

# Server Configuration
PORT=5000
FLASK_ENV=production

# Google Credentials (Base64 encoded - for production deployment)
# GOOGLE_CREDENTIALS_BASE64=your_base64_encoded_credentials_here
EOL
    echo "Template .env created. Please configure it before running in production!"
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Create necessary directories
mkdir -p logs
mkdir -p uploaded_videos

# Check if requirements are installed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  - Workers: $(python3 -c 'import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)')"
echo "  - Port: ${PORT:-5000}"
echo "  - Environment: ${FLASK_ENV:-production}"
echo "  - Log Directory: ./logs"
echo "  - Video Storage: ./uploaded_videos"
echo ""

# Start the application with Gunicorn
echo "Starting Gunicorn..."
echo "=========================================="
echo ""

# Option 1: Run in foreground (recommended for Docker/systemd)
gunicorn --config gunicorn_config.py app:app

# Option 2: Run in background (uncomment to use)
# gunicorn --config gunicorn_config.py app:app --daemon
# echo "Gunicorn started in background. Check logs/ directory for output."
# echo "To stop: kill \$(cat /tmp/gunicorn_adda.pid)"


