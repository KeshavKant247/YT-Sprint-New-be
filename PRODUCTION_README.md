# Production Deployment Guide

## Quick Start (Production Server)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env with your production credentials
nano .env
```

Required environment variables:
- `GOOGLE_CREDENTIALS_BASE64` - Base64 encoded Google service account credentials
- `JWT_SECRET_KEY` - Strong random secret key
- `DRIVE_FOLDER_ID` - Google Drive folder ID for uploads
- `CREDENTIALS_GID` - Google Sheets credentials tab GID
- `PORT` - Server port (default: 5000)

### 3. Start Production Server
```bash
# Make script executable (first time only)
chmod +x start_production.sh

# Start server
./start_production.sh
```

The server will start with:
- Multiple worker processes (CPU cores × 2 + 1)
- 4 threads per worker
- Production-grade configuration
- Automatic log rotation

## Configuration

### Gunicorn Settings (gunicorn_config.py)

Adjust these based on your server:

```python
workers = multiprocessing.cpu_count() * 2 + 1  # Number of worker processes
threads = 4  # Threads per worker
worker_connections = 1000  # Max connections per worker
timeout = 120  # Request timeout (seconds)
max_requests = 1000  # Restart workers after N requests
```

### Cache Settings (app.py)

Adjust TTL (Time To Live) for caches:

```python
sheets_cache = SimpleCache(ttl=300)  # 5 minutes
credentials_cache = SimpleCache(ttl=600)  # 10 minutes
filters_cache = SimpleCache(ttl=300)  # 5 minutes
```

## Monitoring

### Health Checks
```bash
# Basic health check
curl http://localhost:5000/health

# Detailed health check
curl http://localhost:5000/health/detailed

# Performance metrics
curl http://localhost:5000/metrics
```

### Logs
```bash
# Access logs
tail -f logs/gunicorn_access.log

# Error logs
tail -f logs/gunicorn_error.log

# Video upload logs
tail -f logs/video_uploads.log
```

### Metrics Endpoint
Visit `http://localhost:5000/metrics` to see:
- Request statistics (total, successful, failed)
- Video storage statistics
- Cache status
- System configuration

## Scaling for More Users

### 100-200 Users
Default configuration should work fine.

### 200-500 Users
```python
# In gunicorn_config.py
workers = 8
threads = 4
```

### 500-1000 Users
```python
# In gunicorn_config.py
workers = 12
threads = 4

# Increase cache TTL for less frequent API calls
sheets_cache = SimpleCache(ttl=600)  # 10 minutes
```

### 1000+ Users
Consider horizontal scaling:
1. Deploy multiple instances
2. Add load balancer (Nginx)
3. Use Redis for distributed caching
4. Migrate to PostgreSQL from Google Sheets

## Performance Optimization

### 1. Enable Caching
Already enabled by default:
- Sheets data: 5 minutes
- Credentials: 10 minutes
- Filters: 5 minutes

### 2. Connection Pooling
Automatically enabled for Google API clients.

### 3. Clear Cache Manually
```bash
curl -X POST http://localhost:5000/cache/clear
```

### 4. Monitor Performance
```bash
# Watch metrics every 5 seconds
watch -n 5 'curl -s http://localhost:5000/metrics | python -m json.tool'
```

## Security

### 1. Change JWT Secret
```bash
# Generate strong secret
openssl rand -hex 32

# Add to .env
JWT_SECRET_KEY=<generated-secret>
```

### 2. HTTPS/SSL
Uncomment in `gunicorn_config.py`:
```python
keyfile = '/path/to/ssl/key.pem'
certfile = '/path/to/ssl/cert.pem'
```

### 3. Firewall
```bash
# Allow only necessary ports
ufw allow 5000/tcp
ufw enable
```

## Systemd Service (Auto-start on Boot)

Create `/etc/systemd/system/adda-api.service`:
```ini
[Unit]
Description=Adda Education Dashboard API
After=network.target

[Service]
Type=forking
User=your-user
WorkingDirectory=/path/to/shortssprints/backend
ExecStart=/path/to/shortssprints/backend/start_production.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable adda-api
sudo systemctl start adda-api
sudo systemctl status adda-api
```

## Troubleshooting

### High CPU Usage
- Reduce number of workers
- Increase cache TTL
- Check for infinite loops in logs

### High Memory Usage
- Lower `max_requests` to restart workers more frequently
- Reduce cache TTL
- Check for memory leaks in video processing

### Slow Response Times
- Check cache hit rate in `/metrics`
- Verify Google API isn't rate-limited
- Increase number of workers

### Connection Errors
- Verify Google credentials in .env
- Check Google API quotas
- Review connection pool logs

## Backup & Recovery

### Backup Videos
```bash
# Backup uploaded videos
tar -czf videos_backup_$(date +%Y%m%d).tar.gz uploaded_videos/
```

### Backup Logs
```bash
# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## Updates & Maintenance

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Restart Server
```bash
# Find and kill gunicorn
pkill -f gunicorn

# Restart
./start_production.sh
```

### Zero-Downtime Reload
```bash
# Send HUP signal for graceful reload
kill -HUP $(cat /tmp/gunicorn_adda.pid)
```

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review metrics at `/metrics` endpoint
3. Check health status at `/health/detailed`
4. See SCALABILITY_GUIDE.md for performance tuning

---

**Current Status**: ✅ Production-ready for 500+ concurrent users


