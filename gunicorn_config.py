# Gunicorn configuration for production deployment
# This file configures the WSGI server to handle 500+ concurrent users

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = 'sync'  # or 'gevent' for async (requires gevent package)
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 100  # Add randomness to prevent all workers restarting at once
timeout = 120  # Worker timeout (important for video downloads)
keepalive = 5

# Process naming
proc_name = 'adda_education_api'

# Logging
accesslog = os.path.join(os.path.dirname(__file__), 'logs', 'gunicorn_access.log')
errorlog = os.path.join(os.path.dirname(__file__), 'logs', 'gunicorn_error.log')
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server mechanics
daemon = False  # Set to True to run as daemon
pidfile = '/tmp/gunicorn_adda.pid'
user = None  # Run as current user
group = None
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = '/path/to/ssl/key.pem'
# certfile = '/path/to/ssl/cert.pem'

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print(f"Starting Gunicorn with {workers} workers")
    print(f"Binding to {bind}")
    print(f"Process name: {proc_name}")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    print("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"Worker {worker.pid} was interrupted")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    print(f"Worker {worker.pid} was aborted")

# Preload application for better performance
preload_app = True

# Enable hot reload in development (set to False in production)
reload = os.getenv('FLASK_ENV') == 'development'

# Thread settings
threads = 4  # Number of threads per worker

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

print("""
===========================================
Gunicorn Configuration Loaded
===========================================
Workers: {}
Worker Class: {}
Max Requests per Worker: {}
Timeout: {}s
Binding: {}
===========================================
""".format(workers, worker_class, max_requests, timeout, bind))


