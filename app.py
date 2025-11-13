from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import json
import re
import os
import logging
from datetime import datetime, timedelta
from functools import wraps
import threading
from queue import Queue
import time
import hashlib
import io

# Optional imports with fallbacks
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError as e:
    GSPREAD_AVAILABLE = False
    print(f"Warning: gspread not available: {e}")

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError as e:
    BCRYPT_AVAILABLE = False
    print(f"Warning: bcrypt not available: {e}")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError as e:
    JWT_AVAILABLE = False
    print(f"Warning: jwt not available: {e}")

try:
    from werkzeug.utils import secure_filename
    WERKZEUG_AVAILABLE = True
except ImportError as e:
    WERKZEUG_AVAILABLE = False
    print(f"Warning: werkzeug not available: {e}")
    def secure_filename(filename):
        return filename

try:
    from pathlib import Path
    import shutil
    PATHLIB_AVAILABLE = True
except ImportError as e:
    PATHLIB_AVAILABLE = False
    print(f"Warning: pathlib not available: {e}")

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError as e:
    YT_DLP_AVAILABLE = False
    print(f"Warning: yt_dlp not available: {e}. Video downloads will be disabled.")

try:
    from concurrent.futures import ThreadPoolExecutor
    THREADPOOL_AVAILABLE = True
except ImportError as e:
    THREADPOOL_AVAILABLE = False
    print(f"Warning: ThreadPoolExecutor not available: {e}")

try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_API_AVAILABLE = True
except ImportError as e:
    GOOGLE_API_AVAILABLE = False
    print(f"Warning: Google API client not available: {e}")

# Note: boto3/AWS S3 is no longer used - removed to avoid security issues with credentials

# ==================== HARDCODED ENVIRONMENT VARIABLES ====================
# All environment variables are hardcoded here (no .env file needed)

# Vercel detection (check if VERCEL env var exists in system)
IS_VERCEL = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None

# Google Sheets Configuration
SHEET_ID = '1VV0v4_xmztdPlOS9iH-l6Aj6cTRDsifGdLj3QPQ0L0w'
CREDENTIALS_GID = '1409173850'
TICKETS_GID = '699848763'
REEDIT_GID = '1507772277'  # Re-edit videos sheet
DRIVE_FOLDER_ID = '1m5gFfXB0AifbAn387sTM_mr8gemi1Jte'

# JWT Secret Key (CHANGE THIS IN PRODUCTION!)
JWT_SECRET_KEY = 'your-secret-jwt-key-change-this-in-production-2024'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = ''  # Set your Google OAuth Client ID here
GOOGLE_CLIENT_SECRET = ''  # Set your Google OAuth Client Secret here
GOOGLE_PROJECT_ID = 'rare-shadow-467804-c6'
GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URI = 'https://oauth2.googleapis.com/token'

# Google Service Account Credentials (Base64 encoded)
GOOGLE_CREDENTIALS_BASE64 = 'ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAicmFyZS1zaGFkb3ctNDY3ODA0LWM2IiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiNTFjZTdlYWNjNmViMTFjZmJhOTc3YTZhY2JlYTRmMTc4Y2UwMmI0YiIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZnSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2d3Z2dTa0FnRUFBb0lCQVFEVk5Tazk0R1NMakhLb1xud20yRmx2TUdBNG1RNjhQb3lYYkFiMEEyekh3L0VLSVlxd3V0MXRWQ0RITkF6cytSS0FYdXNtVTRhMXJKSUYwWlxuYkxSN0l0VnRwWFJPY2syVHhSRmxXTkpnM3hiNlhBWi9iRHhOTmJNNDZoeW13cnBNNTdDOTRxbDlYSHE5YWpBdFxua3RNd2RnL3Z1eVlrMkpNUWkrZC9PenNPaExyY01rNnJFaWJ6dytVM003YXEzSEtzbkQ3dmhwL1hTdFVTb0hUa1xuekRPSFVaMUdzdzVLc1RCT3FHWkI1QTA0c3FjRzJHZGxwUnpkdVZjNndhZ2ZJTWhINWhlMlhIMmNxbGFMRmErUVxudSs1eEU4ZzZXZG5oci85YjZVWTFyUUpJSDFOaWw1ZDlLc2FVc0ZiQ2dtV1lUbmt5Q04rQkdEM1EybytNRU96Y1xuYTBOdjVCQzlBZ01CQUFFQ2dnRUFLcmtpNFFQUWtnZ2NSOFhpSlhWWWtIbHYvUXJKY0tIQ09wQndlU3Fqc1ExM1xudGVLOGplS3hUREZyZk82VU9GMmhScklYeDJUM3hickcvUnZEMUxMbnVyZC9aV0xST2MyeERUSnR3YnlpZ1p1a1xuTDY5MEsvS1pUY3ZYM3ZEQlhUekdOVjZ3b083QnA2Z2FMRit5RXhGdFl4Z0k3alE1MEFTQTZJVnBjYURXUXQ0eFxuM25PNWI1ZzNSUVFNUi9FU0JOeHZQaGhzWWowTld2Tjd1aTZzdi9xc0F6RFpJMjNRb2FQcUVrSzFObTFiVzAxL1xueGNZbU42NlZEWktJRStFaTFwYk9kNnozMmpPVysvMGFWMDgwZnVjL1JOY1h3b2c1Zis1UnVwS2JiWTJZMkVrSFxuWXM3MmRZYktyTHpCRVFybVpja0FQM3h3U1JsYTlhNFFqOWRwZmd5MHdRS0JnUUQrVkMyNmpKWGpwUEFGU0R6a1xuUkVsaHdVeHgxT1RjdDVvNGZDYXVqdkUzc3hZMVd6K2YrQmpkREpidVBsTmw1SUV4ODlzQVo0TzM1MHVHSSsrTVxudUlobTlqUzZybGdJTlR4M28veFVtT2s2aTQ4QitJNXFleitVajNieTF6R0pKTFh4SzB5TGdtQmVoajFCMkpxM1xuV1dCU1VLSVZlS1llSWZYSzQvL016UHNMblFLQmdRRFdtODltMmRRWUxlOHVxVVZqcU1vOXJHV0JOSHFMT0craVxuYjJjcm5rSlJlenFYMXpsRDJ4UFRSOU1TYStiT3U1SzJLbEZSc1QvekRGRmRaa2EvMXVBaGd3WktWSkVTWkJQQVxuV2tYQUI4RlMwZkVxZVRWMjVMT2FkRGFXTFl4MTJLeEsxR1A5b3prY0JuQ1lRYVcybGN3WTlYWGhIN1dueFpIUVxublpiNTl6VGZvUUtCZ0VuL08vN1hBSlZuVzk1dGtpbm9KR0dvMkJFV25EQUx5M2M3eUJWcHlZMG5NZ0w4TlpyWlxubUlKWU0ySEdDSVhRNGpZaWVVbTQxSDRoY2J2cG9MMFV3N3NSVDI0eFk3T2ZxYVExdGlqM0JJVGdMZytvdmVjRlxuVFE1d1gyOXdaUjA5N1NIcU15ODBFODNzeU0zcnM3Zzg3T1dHU0dKdTVBWklZemRROXhBalk3ZVJBb0dCQU1BYVxuS01WQUo0S2RXNFRCTU1QTXkzdjVYY01TWHI5UWZWMUJxM0IzOFpWT1lWeVo0MERDVWpUR0RrSm5JK3ZhSzdHMFxubjZZb3E3MjhRUGtDSEVLTTdZUVI3UWVNTzIvaTlXc3hZMDVKb3R1bjRlRExMdmlHTDk4S04vS21ReDBhSHQrOFxuenVTenZ1TS9RSHFLQ1BRdmtzcWtyaWdlWWxVVG5UcklWZVRiVEJFQkFvR0JBTVVVSThGenNoVlJsbWU3NHZ4Z1xuZmh0QTJQTGs0KzhwSUJuc3NQb1dVeitTLzdZc0NUK1ZjODJ6SFk5cTg4QkRSaGhkMzczVCtZUWlnMDk4TmEyOVxuYkhhOXN0MS8vdHA0bFM5MFQ2U3ByTllJZGduaFF4MUxyS0ErLzdMVzlMMThEbDZSTmt4eTFROTJvd2Jwd2FVM1xuTVEzbnI1bEFBZDRLWjU2NXo1akZTK0YrXG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4iLAogICJjbGllbnRfZW1haWwiOiAiZHJpdmUtYWNjZXNzLXNlcnZpY2VAcmFyZS1zaGFkb3ctNDY3ODA0LWM2LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwNjI0NTQwMzI0MDkwMzk0NjI0OCIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvZHJpdmUtYWNjZXNzLXNlcnZpY2UlNDByYXJlLXNoYWRvdy00Njc4MDQtYzYuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K'

# Apps Script Webhook URL (optional - leave empty if not using)
APPS_SCRIPT_URL = ''

# Note: AWS S3 is no longer used - all video uploads now go to Google Drive

# Port configuration
PORT = 5001

# ==================== END HARDCODED ENVIRONMENT VARIABLES ====================

# Configure logging
# On Vercel, use /tmp for writable directories, otherwise use local paths
if IS_VERCEL:
    LOG_DIR = '/tmp/logs'
    VIDEO_STORAGE_DIR = '/tmp/uploaded_videos'
else:
    LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
    VIDEO_STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'uploaded_videos')

# Create necessary directories (may fail on serverless, that's OK)
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(VIDEO_STORAGE_DIR, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

# Setup logger - use only StreamHandler if FileHandler fails
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, 'video_uploads.log')),
            logging.StreamHandler()
        ]
    )
except Exception:
    # Fallback to console only logging on serverless
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    error_msg = str(e)
    try:
        logger.error(f"Unhandled exception: {error_msg}", exc_info=True)
    except:
        print(f"Unhandled exception: {error_msg}")
        import traceback
        traceback.print_exc()
    
    return jsonify({
        "success": False,
        "error": error_msg,
        "message": "An unexpected error occurred"
    }), 500

# CORS Configuration - Allow specific origins for production
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://shortssprint.vercel.app",
            "https://shortssprits-backend-git-main-u-r.vercel.app",
            "https://shortssprits-backend.vercel.app",
            "https://ytsprint.netlify.app",
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Add explicit CORS headers for all responses
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    allowed_origins = [
        "https://shortssprint.vercel.app",
        "https://shortssprits-backend-git-main-u-r.vercel.app",
        "https://shortssprits-backend.vercel.app",
        "https://ytsprint.netlify.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'

    return response

# ==================== SCALABILITY ENHANCEMENTS ====================

# Cache configuration
class SimpleCache:
    """Thread-safe in-memory cache for Google Sheets data"""
    def __init__(self, ttl=300):  # 5 minutes default TTL
        self.cache = {}
        self.ttl = ttl
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key, value):
        with self.lock:
            self.cache[key] = (value, time.time())
    
    def clear(self):
        with self.lock:
            self.cache.clear()
    
    def delete(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]

# Initialize caches
sheets_cache = SimpleCache(ttl=300)  # Cache sheets data for 5 minutes
credentials_cache = SimpleCache(ttl=600)  # Cache credentials for 10 minutes
filters_cache = SimpleCache(ttl=300)  # Cache filters for 5 minutes

# Connection pooling for Google API clients
_gspread_client_instance = None
_client_lock = threading.Lock()

# Thread pool for async operations (disabled on Vercel serverless)
if IS_VERCEL or not THREADPOOL_AVAILABLE:
    executor = None  # ThreadPoolExecutor doesn't work well in serverless
else:
    executor = ThreadPoolExecutor(max_workers=10)

# Video download queue to prevent overload
video_download_queue = Queue(maxsize=50)
video_downloads_in_progress = {}
downloads_lock = threading.Lock()

# Request tracking for monitoring
request_counter = {'total': 0, 'successful': 0, 'failed': 0}
request_counter_lock = threading.Lock()

# ==================== END SCALABILITY ENHANCEMENTS ====================

# Allowed email domains for authentication
ALLOWED_EMAIL_DOMAINS = ['adda247.com', 'addaeducation.com', 'studyiq.com']


# Authorized JavaScript Origins (must match Google Cloud Console configuration)
AUTHORIZED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
    'https://shortssprint.vercel.app',
    'https://shortssprits-backend.vercel.app'
]

# Authorized Redirect URIs (must match Google Cloud Console configuration)
AUTHORIZED_REDIRECTS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
    'https://shortssprint.vercel.app',
    'https://shortssprits-backend.vercel.app'
]

def get_sheet_data():
    """Fetch data from Google Sheet using Google Visualization API (no auth required) with caching - reads only from main sheet (gid=0)"""
    try:
        # Check cache first
        cache_key = f'sheet_data_{SHEET_ID}'
        cached_data = sheets_cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Returning cached sheet data ({len(cached_data)} records)")
            return cached_data

        # Use Google Visualization API (works for public sheets without API key)
        # gid=0 ensures we read only from the main sheet (Final entries)
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&gid=0'

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            # Remove the JavaScript wrapper
            json_str = response.text
            json_str = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', json_str)

            if json_str:
                data = json.loads(json_str.group(1))

                if data.get('status') == 'ok':
                    table = data.get('table', {})
                    cols = table.get('cols', [])
                    rows = table.get('rows', [])

                    # Extract headers
                    headers = [col.get('label', col.get('id', '')) for col in cols]

                    # Skip first row if it contains headers
                    if rows and len(rows) > 0:
                        first_row_values = [(cell.get('v') if cell and cell.get('v') is not None else '') for cell in rows[0].get('c', [])]

                        # Check if first row is actually headers
                        if first_row_values == headers or 'Sr no.' in first_row_values:
                            headers = first_row_values
                            rows = rows[1:]

                    # Convert to list of dictionaries
                    records = []
                    for row in rows:
                        cells = row.get('c', [])
                        values = [(cell.get('v') if cell and cell.get('v') is not None else '') for cell in cells]

                        # Pad with empty strings if needed
                        values = values + [''] * (len(headers) - len(values))

                        record = dict(zip(headers, values))

                        # Clean up Sr no. field - remove leading single quote
                        if 'Sr no.' in record and isinstance(record['Sr no.'], str):
                            record['Sr no.'] = record['Sr no.'].lstrip("'")

                        records.append(record)

                    # Cache the results
                    sheets_cache.set(cache_key, records)
                    logger.debug(f"Cached sheet data ({len(records)} records)")
                    
                    return records
                else:
                    print(f"Error from API: {data.get('status')}")
                    return None
            else:
                print("Could not parse JSON response")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        error_msg = str(e)
        try:
            logger.error(f"Error accessing sheet: {error_msg}")
        except:
            print(f"Error accessing sheet: {error_msg}")
        import traceback
        traceback.print_exc()
        return None

def get_credentials_data():
    """Fetch credentials from the specific credentials sheet tab with caching"""
    try:
        # Check cache first
        cache_key = f'credentials_data_{SHEET_ID}_{CREDENTIALS_GID}'
        cached_data = credentials_cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Returning cached credentials data ({len(cached_data)} users)")
            return cached_data
        
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?gid={CREDENTIALS_GID}&tqx=out:json'
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            json_str = response.text
            json_str = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', json_str)

            if json_str:
                data = json.loads(json_str.group(1))

                if data.get('status') == 'ok':
                    table = data.get('table', {})
                    rows = table.get('rows', [])

                    # First row is headers, skip it
                    if rows and len(rows) > 0:
                        rows = rows[1:]

                    # Convert to list of user dictionaries
                    users = []
                    for row in rows:
                        cells = row.get('c', [])
                        values = [cell.get('v', '') if cell else '' for cell in cells]

                        if len(values) >= 4 and values[0]:  # Must have username
                            user = {
                                'username': str(values[0]) if values[0] else '',
                                'email': str(values[1]) if values[1] else '',
                                'password': str(values[2]) if values[2] else '',  # This will be the hashed password
                            }
                            users.append(user)

                    # Cache the results
                    credentials_cache.set(cache_key, users)
                    logger.debug(f"Cached credentials data ({len(users)} users)")
                    
                    return users
        return []
    except Exception as e:
        print(f"Error fetching credentials: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_gspread_client():
    """Initialize gspread client with service account credentials using connection pooling"""
    global _gspread_client_instance

    try:
        # Use existing client if available (connection pooling)
        # SKIP validation on Vercel to prevent cold start timeout
        with _client_lock:
            if _gspread_client_instance is not None:
                if IS_VERCEL:
                    # On serverless, trust the cached client without validation
                    return _gspread_client_instance
                else:
                    # Only validate in local development
                    try:
                        # Test if client is still valid
                        _gspread_client_instance.open_by_key(SHEET_ID)
                        return _gspread_client_instance
                    except Exception as e:
                        logger.warning(f"Cached gspread client invalid, recreating: {e}")
                        _gspread_client_instance = None
        
        # Use hardcoded base64 encoded credentials
        creds_base64 = GOOGLE_CREDENTIALS_BASE64

        # Define the scope
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets'
        ]

        if creds_base64:
            # Decode base64 credentials
            import base64
            creds_json = base64.b64decode(creds_base64).decode('utf-8')
            creds_dict = json.loads(creds_json)

            # Authenticate using credentials dictionary
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            
            with _client_lock:
                _gspread_client_instance = client
            
            logger.info("Created new gspread client (pooled)")
            return client

        # Fallback to local credentials.json file (for local development)
        creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if os.path.exists(creds_file):
            # Authenticate using service account file
            creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
            client = gspread.authorize(creds)
            
            with _client_lock:
                _gspread_client_instance = client
            
            logger.info("Created new gspread client (pooled)")
            return client

        return None
    except Exception as e:
        logger.error(f"Error initializing gspread client: {e}")
        import traceback
        traceback.print_exc()
        return None

# Google Drive service instance (connection pooling)
_drive_service_instance = None
_drive_service_lock = threading.Lock()

def get_drive_service():
    """Initialize Google Drive service with connection pooling"""
    global _drive_service_instance
    
    try:
        # Use existing service if available
        with _drive_service_lock:
            if _drive_service_instance is not None:
                return _drive_service_instance
        
        # Define the scope for Drive API
        scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Use hardcoded base64 encoded credentials
        creds_base64 = GOOGLE_CREDENTIALS_BASE64
        
        if creds_base64:
            # Decode base64 credentials
            import base64
            creds_json = base64.b64decode(creds_base64).decode('utf-8')
            creds_dict = json.loads(creds_json)
            
            # Authenticate using credentials dictionary
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            service = build('drive', 'v3', credentials=creds)
            
            with _drive_service_lock:
                _drive_service_instance = service
            
            logger.info("Created new Drive service (pooled)")
            return service
        
        # Fallback to local credentials.json file (for local development)
        creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if os.path.exists(creds_file):
            creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
            service = build('drive', 'v3', credentials=creds)
            
            with _drive_service_lock:
                _drive_service_instance = service
            
            logger.info("Created new Drive service from file (pooled)")
            return service
        
        return None
    except Exception as e:
        logger.error(f"Error initializing Drive service: {e}")
        import traceback
        traceback.print_exc()
        return None

def upload_video_to_drive(file_content, filename, mimetype='video/mp4'):
    """
    Upload video to Google Drive and return file ID and link.
    Returns (file_id, drive_link, error_message)
    """
    try:
        service = get_drive_service()
        
        if not service:
            return None, None, "Could not initialize Drive service"
        
        # Create file metadata
        file_metadata = {
            'name': filename,
            'parents': [DRIVE_FOLDER_ID]
        }
        
        # Create media from file content
        media = MediaIoBaseUpload(
            io.BytesIO(file_content),
            mimetype=mimetype,
            resumable=True
        )
        
        # Upload file
        logger.info(f"Starting Drive upload for: {filename}")
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink',
            supportsAllDrives=True  # Support for Shared Drives
        ).execute()
        
        file_id = file.get('id')
        logger.info(f"Drive upload successful: {filename} (ID: {file_id})")
        
        # Make file publicly accessible (anyone with link can view)
        try:
            service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                supportsAllDrives=True
            ).execute()
            logger.info(f"File permissions set: {filename} is now publicly accessible")
        except Exception as perm_error:
            logger.warning(f"Could not set public permissions for {filename}: {perm_error}")
            # Continue anyway, file is uploaded
        
        # Generate Drive link
        drive_link = f"https://drive.google.com/file/d/{file_id}/view"
        
        return file_id, drive_link, None
        
    except Exception as e:
        logger.error(f"Error uploading to Drive: {e}")
        import traceback
        traceback.print_exc()
        return None, None, str(e)

def save_video_locally(file_content, filename):
    """
    Save video file to local storage with error handling.
    Returns (success, local_path, error_message)
    """
    try:
        # Create timestamped filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = secure_filename(filename)
        local_filename = f"{timestamp}_{safe_filename}"
        local_path = os.path.join(VIDEO_STORAGE_DIR, local_filename)
        
        # Save file with atomic write (write to temp file, then move)
        temp_path = local_path + '.tmp'
        
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        # Verify file was written successfully
        if not os.path.exists(temp_path):
            raise Exception("Failed to write temporary file")
        
        file_size = os.path.getsize(temp_path)
        if file_size == 0:
            raise Exception("Written file is empty")
        
        # Move temp file to final location (atomic operation)
        shutil.move(temp_path, local_path)
        
        logger.info(f"Video saved locally: {local_filename} ({file_size} bytes)")
        return True, local_path, None
        
    except Exception as e:
        logger.error(f"Error saving video locally: {filename} - {str(e)}")
        import traceback
        traceback.print_exc()
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False, None, str(e)

def extract_youtube_video_id(url):
    """
    Extract YouTube video ID from various URL formats
    """
    if not url:
        return None
    
    patterns = [
        r'(?:youtube\.com\/shorts\/|youtu\.be\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def download_youtube_video(youtube_url, content_type='Unknown'):
    """
    Download YouTube video using yt-dlp and save it locally.
    Returns (success, local_path, video_info, error_message)
    """
    try:
        video_id = extract_youtube_video_id(youtube_url)
        if not video_id:
            return False, None, None, "Invalid YouTube URL"
        
        # Create timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_content_type = content_type.replace(' ', '_').replace('/', '_')
        output_filename = f"{timestamp}_{safe_content_type}_{video_id}.mp4"
        output_path = os.path.join(VIDEO_STORAGE_DIR, output_filename)
        
        logger.info(f"Starting YouTube download: {youtube_url} (ID: {video_id})")
        
        # Configure yt-dlp options with anti-bot detection measures
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Flexible format selection
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'age_limit': None,
            # Anti-bot detection headers
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash'],
                }
            },
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            # Add retries
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
        }
        
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            
            # Get video information
            video_info = {
                'id': video_id,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'upload_date': info.get('upload_date', ''),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', '')
            }
            
            # Verify file was downloaded
            if not os.path.exists(output_path):
                raise Exception("Downloaded file not found")
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception("Downloaded file is empty")
            
            logger.info(f"YouTube video downloaded successfully: {output_filename} ({file_size} bytes)")
            logger.info(f"Video title: {video_info['title']}")
            
            return True, output_path, video_info, None
            
    except Exception as e:
        error_msg = f"Error downloading YouTube video: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        
        # Clean up partial download if it exists
        if 'output_path' in locals() and os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"Cleaned up partial download: {output_path}")
            except:
                pass
        
        return False, None, None, str(e)

def write_to_credentials_sheet(username, email, password_hash):
    """Write new user credentials to the sheet with retry logic"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            client = get_gspread_client()

            if not client:
                return {
                    'success': False,
                    'message': 'Google Service Account credentials not found. Place credentials.json in backend folder.',
                    'temp_solution': f'Manually add to sheet: Username={username}, Email={email}, Hash={password_hash}'
                }

            # Open the spreadsheet and get the credentials worksheet
            spreadsheet = client.open_by_key(SHEET_ID)

            # Get the worksheet by gid
            worksheet = None
            for sheet in spreadsheet.worksheets():
                if str(sheet.id) == str(CREDENTIALS_GID):
                    worksheet = sheet
                    break

            if not worksheet:
                return {
                    'success': False,
                    'message': f'Worksheet with gid {CREDENTIALS_GID} not found'
                }

            # Append new user row
            new_row = [username, email, password_hash, password_hash]  # Username, Email, Password, Confirm Password
            worksheet.append_row(new_row)
            
            # Clear credentials cache after adding new user
            cache_key = f'credentials_data_{SHEET_ID}_{CREDENTIALS_GID}'
            credentials_cache.delete(cache_key)
            logger.info(f"Added new user and cleared credentials cache: {username}")

            return {
                'success': True,
                'message': 'User registered successfully'
            }

        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"Error writing to sheet (attempt {retry_count}/{max_retries}): {e}")
                time.sleep(1 * retry_count)  # Exponential backoff
            else:
                logger.error(f"Error writing to sheet after {max_retries} attempts: {e}")
                import traceback
                traceback.print_exc()
                return {
                    'success': False,
                    'message': f'Error writing to sheet: {str(e)}'
                }
    
    return {
        'success': False,
        'message': 'Max retries exceeded'
    }

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(username, email):
    """Generate JWT token for authenticated user"""
    payload = {
        'username': username,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.before_request
def track_request():
    """Middleware to track requests for monitoring"""
    with request_counter_lock:
        request_counter['total'] += 1

@app.after_request
def track_response(response):
    """Middleware to track successful/failed requests"""
    with request_counter_lock:
        if response.status_code < 400:
            request_counter['successful'] += 1
        else:
            request_counter['failed'] += 1
    return response

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    """Home endpoint - also handles OPTIONS for CORS preflight"""
    try:
        if request.method == 'OPTIONS':
            return '', 204
        
        # Simple response that should always work
        response_data = {
            "message": "Adda Education Dashboard API",
            "status": "running",
            "version": "2.0-scalable",
            "storage": "Google Drive"
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        error_msg = str(e)
        try:
            logger.error(f"Error in home endpoint: {error_msg}", exc_info=True)
        except:
            print(f"Error in home endpoint: {error_msg}")
            import traceback
            traceback.print_exc()
        
        # Return error response
        try:
            return jsonify({
                "message": "Adda Education Dashboard API",
                "status": "error",
                "error": error_msg
            }), 500
        except:
            # If even jsonify fails, return plain text
            return f"Error: {error_msg}", 500

@app.route('/health', methods=['GET'])
def health():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/health/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with service status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "google_sheets": "unknown",
            "video_storage": "unknown"
        },
        "cache": {
            "sheets_cache": "enabled",
            "credentials_cache": "enabled",
            "filters_cache": "enabled"
        }
    }
    
    # Check Google Sheets connectivity
    try:
        test_data = get_sheet_data()
        if test_data is not None:
            health_status["services"]["google_sheets"] = "healthy"
        else:
            health_status["services"]["google_sheets"] = "degraded"
    except Exception as e:
        health_status["services"]["google_sheets"] = "unhealthy"
        logger.error(f"Health check - Google Sheets failed: {e}")
    
    # Check video storage
    try:
        if os.path.exists(VIDEO_STORAGE_DIR) and os.access(VIDEO_STORAGE_DIR, os.W_OK):
            health_status["services"]["video_storage"] = "healthy"
        else:
            health_status["services"]["video_storage"] = "degraded"
    except Exception as e:
        health_status["services"]["video_storage"] = "unhealthy"
        logger.error(f"Health check - Video storage failed: {e}")
    
    # Overall status
    unhealthy_services = [k for k, v in health_status["services"].items() if v == "unhealthy"]
    if len(unhealthy_services) > 0:
        health_status["status"] = "unhealthy"
    elif any(v == "degraded" for v in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@app.route('/metrics', methods=['GET'])
def metrics():
    """Endpoint for monitoring metrics"""
    with request_counter_lock:
        stats = request_counter.copy()
    
    # Video storage stats
    video_count = 0
    total_size = 0
    if os.path.exists(VIDEO_STORAGE_DIR):
        for filename in os.listdir(VIDEO_STORAGE_DIR):
            file_path = os.path.join(VIDEO_STORAGE_DIR, filename)
            if os.path.isfile(file_path) and not filename.startswith('.'):
                total_size += os.path.getsize(file_path)
                video_count += 1
    
    # Downloads in progress
    with downloads_lock:
        downloads_count = len(video_downloads_in_progress)
    
    return jsonify({
        "requests": {
            "total": stats['total'],
            "successful": stats['successful'],
            "failed": stats['failed'],
            "success_rate": f"{(stats['successful'] / max(stats['total'], 1) * 100):.2f}%"
        },
        "videos": {
            "stored_locally": video_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "downloads_in_progress": downloads_count
        },
        "cache": {
            "enabled": True,
            "ttl_seconds": {
                "sheets": 300,
                "credentials": 600,
                "filters": 300
            }
        },
        "system": {
            "thread_pool_max_workers": 10,
            "video_queue_max_size": 50
        }
    }), 200

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Endpoint to manually clear all caches (admin use)"""
    try:
        sheets_cache.clear()
        credentials_cache.clear()
        filters_cache.clear()
        
        logger.info("All caches cleared manually")
        
        return jsonify({
            "success": True,
            "message": "All caches cleared successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """Fetch all data from Google Sheets (excluding Re-edit entries)"""
    try:
        records = get_sheet_data()
        if records is None:
            return jsonify({"error": "Failed to access sheet"}), 500

        # Filter out Re-edit entries (they should be in separate sheet, but just in case)
        filtered_records = [
            record for record in records
            if record.get('Edit', '').lower() != 're-edit'
        ]

        return jsonify({
            "success": True,
            "data": filtered_records,
            "count": len(filtered_records)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get unique values for filters (categories, subcategories, subjects) - excluding Re-edit entries"""
    try:
        records = get_sheet_data()
        if records is None:
            return jsonify({"error": "Failed to access sheet"}), 500

        # Filter out Re-edit entries
        filtered_records = [
            record for record in records
            if record.get('Edit', '').lower() != 're-edit'
        ]

        # Extract unique values from filtered records
        types = list(set([r.get('Content Type', '') for r in filtered_records if r.get('Content Type')]))
        subcategories = list(set([r.get('Sub category', '') for r in filtered_records if r.get('Sub category')]))
        subjects = list(set([r.get('Subject', '') for r in filtered_records if r.get('Subject')]))

        return jsonify({
            "success": True,
            "filters": {
                "types": sorted(types),
                "subcategories": sorted(subcategories),
                "subjects": sorted(subjects)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def get_main_worksheet():
    """Get the main data worksheet using gspread (gid=0 - Final entries only)"""
    try:
        client = get_gspread_client()
        if not client:
            return None

        spreadsheet = client.open_by_key(SHEET_ID)
        # Get the first worksheet (gid=0 - main data sheet for Final entries)
        worksheet = spreadsheet.get_worksheet(0)
        return worksheet
    except Exception as e:
        print(f"Error getting worksheet: {e}")
        return None

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    """
    Upload video file to Google Drive and local storage.
    - Saves all uploaded videos to local uploaded_videos folder
    - Uploads to Google Drive with shareable link (anyone with link can access)
    """
    local_path = None
    try:
        # Check if file is present
        if 'video' not in request.files:
            logger.warning("Upload attempted without video file")
            return jsonify({
                "success": False,
                "error": "No video file provided"
            }), 400

        file = request.files['video']

        if file.filename == '':
            logger.warning("Upload attempted with empty filename")
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400

        # Get content type and status from form data
        content_type = request.form.get('contentType', 'Unknown')
        status = request.form.get('status', '').strip()
        
        # Read file content
        file_content = file.read()
        original_filename = secure_filename(file.filename)
        
        # Get file extension
        file_extension = os.path.splitext(original_filename)[1] or '.mp4'
        
        # Create filename with content type if provided
        if content_type and content_type != 'Unknown':
            safe_content_type = content_type.replace(' ', '_').replace('/', '_')
            filename = f"{safe_content_type}_{original_filename}"
        else:
            filename = original_filename
            
        mimetype = file.content_type or 'video/mp4'
        
        file_size_mb = len(file_content) / (1024 * 1024)
        logger.info(f"Received video upload: {filename} ({file_size_mb:.2f} MB, {mimetype}), Status: {status}")

        # Always save video locally to uploaded_videos folder
        drive_link = None
        file_id = None
        local_path = None

        # Save video to local uploaded_videos folder
        success, local_path, save_error = save_video_locally(file_content, filename)
        if success:
            logger.info(f"✓ Video saved locally: {local_path}")
        else:
            logger.warning(f"Could not save video locally: {save_error}")

        # Upload to Google Drive (anyone with link can access)
        logger.info(f"Uploading video to Google Drive: {filename}")
        file_id, drive_link, drive_error = upload_video_to_drive(file_content, filename, mimetype)

        if drive_link:
            logger.info(f"✓ Video uploaded to Google Drive: {filename} -> {drive_link}")
        else:
            logger.error(f"Failed to upload to Google Drive: {drive_error}")

        # Prepare response
        response_data = {
            "success": True,
            "filename": filename,
            "file_size_mb": round(file_size_mb, 2),
        }

        if drive_link:
            response_data["video_id"] = file_id
            response_data["drive_link"] = drive_link
            response_data["uploaded_to_drive"] = True
            response_data["shareable_link"] = drive_link  # Anyone with link can access
        else:
            response_data["uploaded_to_drive"] = False
            response_data["error"] = drive_error or "Failed to upload to Google Drive"

        if local_path:
            response_data["local_path"] = local_path
            response_data["saved_locally"] = True
        else:
            response_data["saved_locally"] = False
        
        logger.info(f"✓ Upload complete: {filename} (Drive: {drive_link if drive_link else 'None'}, Local: {local_path if local_path else 'None'})")
        
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"CRITICAL ERROR in upload_video: {e}")
        import traceback
        traceback.print_exc()
        
        # If we have a local backup, mention it in the error response
        error_response = {
            "success": False,
            "error": str(e)
        }
        
        if local_path and os.path.exists(local_path):
            error_response["local_backup"] = local_path
            error_response["message"] = "Error occurred but video is saved locally"
        
        return jsonify(error_response), 500

@app.route('/api/video-info/<filename>', methods=['GET'])
def get_video_info(filename):
    """Get information about a locally stored video"""
    try:
        # Sanitize filename
        safe_filename = secure_filename(filename)
        video_path = os.path.join(VIDEO_STORAGE_DIR, safe_filename)
        
        if not os.path.exists(video_path):
            return jsonify({
                "success": False,
                "error": "Video not found"
            }), 404
        
        file_stats = os.stat(video_path)
        
        return jsonify({
            "success": True,
            "filename": safe_filename,
            "size_bytes": file_stats.st_size,
            "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/videos/list', methods=['GET'])
def list_videos():
    """List all locally stored videos"""
    try:
        videos = []
        
        if not os.path.exists(VIDEO_STORAGE_DIR):
            return jsonify({
                "success": True,
                "videos": [],
                "count": 0
            }), 200
        
        for filename in os.listdir(VIDEO_STORAGE_DIR):
            file_path = os.path.join(VIDEO_STORAGE_DIR, filename)
            
            # Skip directories and hidden files
            if os.path.isdir(file_path) or filename.startswith('.'):
                continue
            
            file_stats = os.stat(file_path)
            
            videos.append({
                "filename": filename,
                "size_bytes": file_stats.st_size,
                "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            })
        
        # Sort by creation time, newest first
        videos.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            "success": True,
            "videos": videos,
            "count": len(videos),
            "total_size_mb": round(sum(v['size_mb'] for v in videos), 2)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/videos/storage-stats', methods=['GET'])
def get_storage_stats():
    """Get storage statistics for locally stored videos"""
    try:
        total_size = 0
        video_count = 0
        
        if os.path.exists(VIDEO_STORAGE_DIR):
            for filename in os.listdir(VIDEO_STORAGE_DIR):
                file_path = os.path.join(VIDEO_STORAGE_DIR, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    total_size += os.path.getsize(file_path)
                    video_count += 1
        
        return jsonify({
            "success": True,
            "video_count": video_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
            "storage_path": VIDEO_STORAGE_DIR
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def async_youtube_download(youtube_url, content_type, download_id):
    """
    Async function to handle YouTube video downloads in background
    """
    try:
        logger.info(f"Starting async download {download_id}: {youtube_url}")
        
        # Update status
        with downloads_lock:
            video_downloads_in_progress[download_id]['status'] = 'downloading'
        
        # Download the video
        success, local_path, video_info, error = download_youtube_video(youtube_url, content_type)
        
        if not success:
            with downloads_lock:
                video_downloads_in_progress[download_id]['status'] = 'failed'
                video_downloads_in_progress[download_id]['error'] = error
            logger.error(f"Download {download_id} failed: {error}")
            return
        
        # Get file size
        file_size = os.path.getsize(local_path)
        file_size_mb = file_size / (1024 * 1024)
        filename = os.path.basename(local_path)
        
        # Update with download results
        with downloads_lock:
            video_downloads_in_progress[download_id]['status'] = 'completed'
            video_downloads_in_progress[download_id]['local_path'] = local_path
            video_downloads_in_progress[download_id]['filename'] = filename
            video_downloads_in_progress[download_id]['file_size_mb'] = round(file_size_mb, 2)
            video_downloads_in_progress[download_id]['video_info'] = video_info
            video_downloads_in_progress[download_id]['completed_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Async download {download_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in async download {download_id}: {e}")
        import traceback
        traceback.print_exc()
        with downloads_lock:
            video_downloads_in_progress[download_id]['status'] = 'failed'
            video_downloads_in_progress[download_id]['error'] = str(e)

@app.route('/api/download-youtube', methods=['POST'])
def download_youtube():
    """
    Download a YouTube video and save it locally.
    Accepts: { "youtube_url": "...", "content_type": "...", "async": true/false }
    
    If async=true, returns a download_id immediately and processes in background.
    Use /api/download-youtube/status/<download_id> to check progress.
    """
    try:
        data = request.get_json()
        
        if not data or 'youtube_url' not in data:
            return jsonify({
                "success": False,
                "error": "YouTube URL is required"
            }), 400
        
        youtube_url = data.get('youtube_url', '').strip()
        content_type = data.get('content_type', 'Unknown')
        async_mode = data.get('async', False)  # Enable async processing
        
        if not youtube_url:
            return jsonify({
                "success": False,
                "error": "YouTube URL cannot be empty"
            }), 400
        
        logger.info(f"Received YouTube download request: {youtube_url} (async={async_mode})")
        
        # Async mode - return immediately and process in background
        if async_mode:
            # Generate unique download ID
            download_id = hashlib.md5(f"{youtube_url}{time.time()}".encode()).hexdigest()
            
            # Check if queue is full
            with downloads_lock:
                if len(video_downloads_in_progress) >= 50:
                    return jsonify({
                        "success": False,
                        "error": "Download queue is full. Please try again later.",
                        "queue_size": len(video_downloads_in_progress)
                    }), 503
                
                # Initialize download status
                video_downloads_in_progress[download_id] = {
                    'status': 'queued',
                    'youtube_url': youtube_url,
                    'content_type': content_type,
                    'queued_at': datetime.utcnow().isoformat()
                }
            
            # Submit to thread pool (if available)
            if executor:
                executor.submit(async_youtube_download, youtube_url, content_type, download_id)
            else:
                # On serverless, run synchronously or return error
                return jsonify({
                    "success": False,
                    "error": "Async downloads not supported on serverless. Use async=false for synchronous download.",
                    "message": "Please set async=false in your request"
                }), 400
            
            return jsonify({
                "success": True,
                "download_id": download_id,
                "status": "queued",
                "message": "Download queued. Use /api/download-youtube/status/<download_id> to check progress.",
                "status_url": f"/api/download-youtube/status/{download_id}"
            }), 202
        
        # Synchronous mode - wait for completion (original behavior)
        success, local_path, video_info, error = download_youtube_video(youtube_url, content_type)
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to download YouTube video: {error}"
            }), 500
        
        # Get file size
        file_size = os.path.getsize(local_path)
        file_size_mb = file_size / (1024 * 1024)
        filename = os.path.basename(local_path)
        
        response_data = {
            "success": True,
            "local_path": local_path,
            "filename": filename,
            "file_size_mb": round(file_size_mb, 2),
            "video_info": video_info
        }
        
        logger.info(f"YouTube download successful: {filename} ({file_size_mb:.2f} MB)")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in download_youtube endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/download-youtube/status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    """
    Get the status of an async YouTube download
    """
    try:
        with downloads_lock:
            if download_id not in video_downloads_in_progress:
                return jsonify({
                    "success": False,
                    "error": "Download ID not found"
                }), 404
            
            status_data = video_downloads_in_progress[download_id].copy()
        
        return jsonify({
            "success": True,
            "download_id": download_id,
            **status_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting download status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/download-youtube/cleanup', methods=['POST'])
def cleanup_completed_downloads():
    """
    Clean up completed download records from memory
    """
    try:
        cleaned = 0
        with downloads_lock:
            completed_ids = [
                did for did, data in video_downloads_in_progress.items() 
                if data.get('status') in ['completed', 'failed']
            ]
            for did in completed_ids:
                del video_downloads_in_progress[did]
                cleaned += 1
        
        logger.info(f"Cleaned up {cleaned} completed download records")
        
        return jsonify({
            "success": True,
            "cleaned": cleaned,
            "message": f"Cleaned up {cleaned} completed download records"
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning up downloads: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/add', methods=['POST'])
def add_row():
    """Add a new row to the sheet using Apps Script webhook or direct API"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        # Check if this is a re-edit entry
        is_reedit = data.get('Edit', '').lower() == 're-edit'

        # Try using Apps Script webhook first (no credentials needed)
        apps_script_url = APPS_SCRIPT_URL

        if apps_script_url and not is_reedit:  # Use Apps Script only for non-reedit
            logger.info("Using Apps Script webhook to add row")
            try:
                # Send data to Apps Script webhook
                response = requests.post(apps_script_url, json=data, timeout=10)

                if response.status_code == 200:
                    result = response.json()

                    # Clear cache after adding row
                    cache_key = f'sheet_data_{SHEET_ID}'
                    sheets_cache.delete(cache_key)
                    filters_cache.clear()
                    logger.info(f"Added new row via Apps Script and cleared cache")

                    return jsonify(result), 200
                else:
                    logger.warning(f"Apps Script webhook failed: {response.status_code} - {response.text}")
                    # Fall through to try direct API method
            except Exception as e:
                logger.error(f"Apps Script webhook error: {e}, falling back to direct API")
                import traceback
                traceback.print_exc()
                # Fall through to try direct API method
        else:
            if is_reedit:
                logger.info("Re-edit entry detected, using direct API to save to re-edit sheet")
            else:
                logger.warning("APPS_SCRIPT_URL not configured, trying direct API method")

        # Fallback to direct API method (requires credentials)
        logger.info("Using direct Google Sheets API to add row")

        # Check if credentials are configured
        creds_base64 = GOOGLE_CREDENTIALS_BASE64
        creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
        has_creds = bool(creds_base64 or os.path.exists(creds_file))

        if not has_creds:
            logger.error("No Google credentials found. APPS_SCRIPT_URL and GOOGLE_CREDENTIALS_BASE64 are both missing.")
            return jsonify({
                "success": False,
                "error": "Google Sheets access not configured. Please set up either APPS_SCRIPT_URL or GOOGLE_CREDENTIALS_BASE64 in the code.",
                "help": "See APPS_SCRIPT_SETUP.md for Apps Script setup (recommended) or update GOOGLE_CREDENTIALS_BASE64 in app.py"
            }), 503

        # If this is a re-edit entry, save to re-edit sheet
        if is_reedit:
            client = get_gspread_client()
            if not client:
                return jsonify({
                    "success": False,
                    "error": "Could not initialize gspread client"
                }), 503

            spreadsheet = client.open_by_key(SHEET_ID)

            # Find re-edit worksheet by gid
            reedit_worksheet = None
            for sheet in spreadsheet.worksheets():
                if str(sheet.id) == str(REEDIT_GID):
                    reedit_worksheet = sheet
                    break

            if not reedit_worksheet:
                logger.error("Re-edit worksheet not found")
                return jsonify({
                    "success": False,
                    "error": "Re-edit worksheet not found"
                }), 503

            # Get headers from the re-edit sheet
            reedit_headers = reedit_worksheet.row_values(1)

            # Prepare row data for re-edit sheet
            # Columns: Sr no., Email, Vertical Name, Exam Name, Subject, Type of Content, Sub category, Video Link, Edit, VideoId
            reedit_row_data = []
            for header in reedit_headers:
                reedit_row_data.append(data.get(header, ''))

            # Append to re-edit sheet
            reedit_worksheet.append_row(reedit_row_data)
            logger.info(f"Added re-edit entry to re-edit sheet (gid={REEDIT_GID})")

            # Clear cache
            cache_key = f'sheet_data_{SHEET_ID}'
            sheets_cache.delete(cache_key)
            filters_cache.clear()

            return jsonify({
                "success": True,
                "message": "Re-edit entry added successfully to re-edit sheet"
            }), 200

        # For non-reedit entries (Final status), save to main sheet (gid=0)
        logger.info("Adding Final entry to main sheet (gid=0)")
        worksheet = get_main_worksheet()

        if not worksheet:
            logger.error("Failed to get worksheet. Check if credentials are valid and sheet is shared with service account.")
            return jsonify({
                "success": False,
                "error": "Could not access Google Sheet. Please verify: 1) GOOGLE_CREDENTIALS_BASE64 is set correctly in code, 2) Sheet is shared with service account email, 3) Service account has Editor permission.",
                "help": "See APPS_SCRIPT_SETUP.md for Apps Script setup (no credentials needed) or FIX_PERMISSIONS.md for permission issues"
            }), 503

        # Get headers from the first row
        headers = worksheet.row_values(1)

        # Build row data matching the headers order
        row_data = []
        for header in headers:
            row_data.append(data.get(header, ''))

        # Append the new row to main sheet (gid=0)
        worksheet.append_row(row_data)

        # Clear sheets cache after adding new row
        cache_key = f'sheet_data_{SHEET_ID}'
        sheets_cache.delete(cache_key)
        filters_cache.clear()  # Clear filters cache as well
        logger.info(f"Added Final entry to main sheet (gid=0) via direct API and cleared cache")

        return jsonify({
            "success": True,
            "message": "Row added successfully to main sheet"
        }), 200

    except Exception as e:
        logger.error(f"Error adding row: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/update/<int:row_id>', methods=['PUT'])
def update_row(row_id):
    """Update a specific row in the sheet"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        worksheet = get_main_worksheet()

        if not worksheet:
            return jsonify({
                "success": False,
                "error": "Could not access Google Sheet. Make sure credentials.json is configured."
            }), 503

        # Get headers from the first row
        headers = worksheet.row_values(1)

        # Build row data matching the headers order
        row_data = []
        for header in headers:
            row_data.append(data.get(header, ''))

        # Update the row (row_id + 2 because: +1 for header, +1 for 0-index to 1-index)
        actual_row = row_id + 2

        # Update each cell in the row
        for col_idx, value in enumerate(row_data, start=1):
            worksheet.update_cell(actual_row, col_idx, value)
        
        # Clear sheets cache after updating row
        cache_key = f'sheet_data_{SHEET_ID}'
        sheets_cache.delete(cache_key)
        filters_cache.clear()  # Clear filters cache as well
        logger.info(f"Updated row {row_id} and cleared sheet cache")

        return jsonify({
            "success": True,
            "message": "Row updated successfully"
        }), 200

    except Exception as e:
        print(f"Error updating row: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/delete/<int:row_id>', methods=['DELETE'])
def delete_row(row_id):
    """Delete a specific row from the sheet"""
    try:
        worksheet = get_main_worksheet()

        if not worksheet:
            return jsonify({
                "success": False,
                "error": "Could not access Google Sheet. Make sure credentials.json is configured."
            }), 503

        # Delete the row (row_id + 2 because: +1 for header, +1 for 0-index to 1-index)
        actual_row = row_id + 2
        worksheet.delete_rows(actual_row)
        
        # Clear sheets cache after deleting row
        cache_key = f'sheet_data_{SHEET_ID}'
        sheets_cache.delete(cache_key)
        filters_cache.clear()  # Clear filters cache as well
        logger.info(f"Deleted row {row_id} and cleared sheet cache")

        return jsonify({
            "success": True,
            "message": "Row deleted successfully"
        }), 200

    except Exception as e:
        print(f"Error deleting row: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get predefined categories and subcategories"""
    try:
        categories = {
            "Exam Pattern": [
                "Bank",
                "SSC",
                "Teaching",
                "State Exams",
                "UPSC",
                "Railway",
                "Other"
            ],
            "Syllabus Overview": [
                "Bank",
                "SSC",
                "Teaching",
                "State Exams",
                "UPSC",
                "Railway",
                "Other"
            ],
            "Preparation Strategy": [
                "Bank",
                "SSC",
                "Teaching",
                "State Exams",
                "UPSC",
                "Railway",
                "Other"
            ],
            "Study Plan": [
                "30 Days Plan",
                "60 Days Plan",
                "90 Days Plan",
                "6 Months Plan",
                "1 Year Plan",
                "Subject-wise Plan",
                "Other"
            ],
            "Conceptual Insights": [
                "Bank",
                "SSC",
                "Teaching",
                "State Exams",
                "Other"
            ],
            "Tips & Tricks / Shortcuts": [
                "Bank",
                "SSC",
                "Teaching",
                "State Exams",
                "Other"
            ],
            "PYQs / Practice Questions": [
                "Bank",
                "SSC",
                "Teaching",
                "State Exams",
                "Other"
            ],
            "Science / GK Facts": [
                "General Science",
                "Current Affairs",
                "Static GK",
                "History",
                "Geography",
                "Other"
            ],
            "Motivational Shorts": [
                "Success Stories",
                "Daily Motivation",
                "Study Tips",
                "Time Management",
                "Stress Management",
                "Other"
            ],
            "Classroom Moments": [
                "Teacher Highlights",
                "Student Interactions",
                "Funny Moments",
                "Teaching Methods",
                "Other"
            ],
            "Exam Life Situations": [
                "Exam Day Stories",
                "Preparation Journey",
                "Result Day",
                "Student Life",
                "Relatable Content",
                "Other"
            ]
        }

        return jsonify({
            "success": True,
            "categories": categories
        })
    except Exception as e:
        error_msg = str(e)
        try:
            logger.error(f"Error in get_categories: {error_msg}")
        except:
            print(f"Error in get_categories: {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@app.route('/api/exams', methods=['GET'])
def get_exams():
    """Get exam details with subjects"""
    try:
        exams = {
            "Bank Pre": {
                "exams": [
                    "SBI Clerk",
                    "SBI PO",
                    "IBPS CLERK",
                    "IBPS PO",
                    "LIC AAO",
                    "RRB PO",
                    "RRB Clerk"
                ],
                "subjects": [
                    "Reasoning",
                    "Quants",
                    "English",
                    "General Awareness",
                    "Current Affairs",
                    "Hindi",
                    "Computer",
                    "Other"
                ]
            },
            "Bank Post": {
                "exams": [
                    "JAIIB",
                    "CAIIB",
                    "IIBF CERTIFICATION COURSE",
                    "BANK PROMOTION EXAMS"
                ],
                "subjects": [
                    "AFM",
                    "RBWM",
                    "IEIFS",
                    "PPB",
                    "ABM",
                    "ABFM",
                    "BFM",
                    "BRBL",
                    "CAIIB Elective Subjects",
                    "CCP + AML",
                    "Foreign Exchange",
                    "Prevention of Cyber Crime",
                    "KYC + IBC + MSME",
                    "General Banking",
                    "Computer Knowledge",
                    "Banking Law",
                    "Other"
                ]
            },
            "SSC": {
                "exams": [
                    "GD",
                    "MTS",
                    "CHSL",
                    "CGL",
                    "Delhi Police",
                    "CPO",
                    "Steno"
                ],
                "subjects": [
                    "Other",
                    "Current Affairs",
                    "English",
                    "GK/GS",
                    "Maths",
                    "Reasoning",
                    "Science",
                    "Shorthand"
                ]
            },
            "Railway": {
                "exams": [
                    "RRB NTPC",
                    "ALP",
                    "Group D",
                    "RPF"
                ],
                "subjects": [
                    "Other",
                    "Current Affairs",
                    "GK/GS",
                    "Maths",
                    "Reasoning",
                    "Science"
                ]
            },
            "Police": {
                "exams": [
                    "UP Police",
                    "UP Homeguard",
                    "UP SI"
                ],
                "subjects": [
                    "Other",
                    "Current Affairs",
                    "English",
                    "GK/GS",
                    "Maths",
                    "Reasoning",
                    "Science",
                    "Hindi"
                ]
            },
            "teaching": {
                "exams": [
                    "CTET",
                    "LT Grade",
                    "Bihar STET",
                    "EMRS",
                    "UP GIC",
                    "NVS",
                    "KVS",
                    "HTET",
                    "BPSC TRE 4.0",
                    "UP TET",
                    "REET",
                    "DSSSB",
                    "TGT",
                    "PGT",
                    "PRT",
                    "TET Exams",
                    "AWES",
                    "SET Exams",
                    "Super TET",
                    "RPSC Teaching Exam",
                    "Sainik School Exams",
                    "West Bengal SSC Teacher Recruitment"
                ],
                "subjects": [
                    "Other",
                    "English",
                    "Hindi",
                    "Maths",
                    "Sanskrit",
                    "CDP",
                    "EVS",
                    "General Studies",
                    "Commerce",
                    "Urdu",
                    "Social Studies",
                    "Science",
                    "Home Science",
                    "Music",
                    "Arts",
                    "Social Science",
                    "Physical Education",
                    "Fine Arts",
                    "Physics",
                    "Chemistry",
                    "Biology",
                    "Zoology",
                    "History",
                    "Geography",
                    "Political Science",
                    "Sociology",
                    "Economics",
                    "Philosophy",
                    "Psychology",
                    "Botany",
                    "Computer Science",
                    "GA",
                    "Teaching Aptitude",
                    "Reasoning",
                    "Polity",
                    "Mathematics",
                    "Current Affairs",
                    "General Science"
                ]
            },
            "ugc": {
                "exams": [
                    "Paper 1",
                    "Paper 2",
                    "SET / SLET",
                    "CSIR NET"
                ],
                "subjects": [
                    "Other",
                    "General Paper",
                    "Political Science",
                    "Philosophy",
                    "Psychology",
                    "Sociology",
                    "History",
                    "Commerce",
                    "Education",
                    "Home Science",
                    "Physical Education",
                    "Law",
                    "Music",
                    "Sanskrit",
                    "Geography",
                    "Ayurveda",
                    "Biology",
                    "Hindi",
                    "Environmental Sciences",
                    "Computer Science and Applications",
                    "Library and Information Science",
                    "Urdu",
                    "English",
                    "Chemical Sciences",
                    "Earth Sciences",
                    "Life Sciences",
                    "Mathematical Sciences",
                    "Physical Sciences",
                    "General Aptitude"
                ]
            },
            "bihar": {
                "exams": [
                    "BPSC AEDO",
                    "BSSC CGL-4",
                    "Bihar Jeevika",
                    "Bihar SI Daroga",
                    "BSSC STENO",
                    "BSSC Inter level",
                    "BSSC Karyalay parichari",
                    "Bihar Police driver"
                ],
                "subjects": [
                    "Hindi",
                    "Maths",
                    "GK/GS",
                    "Reasoning",
                    "English",
                    "Science",
                    "Current Affairs",
                    "Subject Knowledge",
                    "Computer",
                    "Static GK",
                    "Other"
                ]
            },
            "Punjab": {
                "exams": [
                    "PSSSB", 
                    "Punjab police constable", 
                    "High court", 
                    "ETT/NTT", 
                    "PSTET", 
                    "Master Cadre", 
                    "Punjab PCS", 
                    "SSC", 
                    "Railways"
                ],
                "subjects": [
                    "Static & Current Affairs",
                    "General Knowledge",
                    "Basic Computer Knowledge",
                    "Logical Reasoning",
                    "Quantitative Aptitude",
                    "Numerical Aptitude",
                    "General English",
                    "Punjabi Language",
                    "Punjab GK",
                    "General Awareness",
                    "Arithmetic",
                    "Teaching Aptitude",
                    "Pedagogy",
                    "Information & Communication Technology (ICT)",
                    "Hindi Language",
                    "English Language",
                    "Mathematics",
                    "General Science",
                    "Social Science",
                    "Environmental Studies",
                    "Science",
                    "General Studies",
                    "Civil Services Aptitude Test (CSAT)",
                    "Reasoning",
                    "Other"
                ]
            },
            "bengal": {
                "exams": [
                    "WBSSC GROUP C & D",
                    "SSC MTS",
                    "RRB NTPC",
                    "WBP",
                    "Banking",
                    "WBCS"
                ],
                "subjects": [
                    "Current Affairs",
                    "History",
                    "Polity",
                    "Mathematics",
                    "Gk",
                    "Gs",
                    "English",
                    "General Studies",
                    "Static Gk",
                    "Reasoning",
                    "Banking Awareness",
                    "Geography",
                    "Other"
                ]
            },
            "Odia": {
                "exams": [
                    "Bed Entrance Exam",
                    "LTR MAINS ARTS OSSC CGL",
                    "OSSC PEO",
                    "SSD Sevak Sevika",
                    "Police Constable",
                    "RI AMIN MAINS",
                    "RRB NTPC",
                    "RRB Group D",
                    "RRb PO",
                    "IBPS Clerk",
                    "OPSC"
                ],
                "subjects": [
                    "Current Affairs",
                    "Reasoning",
                    "English",
                    "GK/GS",
                    "Geography",
                    "History",
                    "Polity",
                    "Pedagogy",
                    "Computer",
                    "Physics",
                    "Chemistry",
                    "Mathematics",
                    "Economics",
                    "Other"
                ]
            },
            "Tamil": {
                "exams": [
                    "TNPSC",
                    "TET",
                    "NTPC",
                    "TNUSRB Si",
                    "PC. IB",
                    "RPF",
                    "RRB JE",
                    "RRB GR D"
                ],
                "subjects": [
                    "Current Affairs",
                    "English",
                    "Maths",
                    "Geography",
                    "Science",
                    "Psychology",
                    "GK",
                    "Reasoning",
                    "Biology",
                    "Polity",
                    "History",
                    "GS",
                    "Other"
                ]
            },
            "Telugu": {
                "exams": [
                    "NTPC",
                    "Group-D",
                    "RRB Junior Engineer(CBT-1 Only)",
                    "MTS",
                    "CHSL",
                    "GD",
                    "CGL",
                    "Bank PO",
                    "Bank Clerk",
                    "APPSC & TGPSC"
                ],
                "subjects": [
                    "Mathematics",
                    "Reasoning",
                    "Polity",
                    "Economy",
                    "History",
                    "Geography",
                    "Current Affairs",
                    "Computer",
                    "Arithmetic",
                    "English",
                    "Banking/Financial Awareness",
                    "Credit Co-Operative",
                    "Science & Tech",
                    "Telangana Movement (for Telangana Exams only)",
                    "General Science (Physics + Chemistry + Biology)",
                    "Teaching Aptitude",
                    "Pedagogy",
                    "ICT",
                    "POCSO",
                    "Administrative Aptitude",
                    "Other"
                ]
            },
            "Agriculture": {
                "exams": [
                    "IBPS SO AFO",
                    "NABARD GRADE A",
                    "FCI AG III Technical",
                    "Haryana ADO/HDO",
                    "Punjab ADO/HDO",
                    "APSC ADO",
                    "FSSAI CFSO/TO",
                    "MP FSO",
                    "CUET PG Agriculture",
                    "UPCATET PG",
                    "NSC Trainee",
                    "IFFCO AGT",
                    "KRIBHCO FRT",
                    "Bihar Agriculture Coordinator",
                    "BPSC BAO/SDAO",
                    "BHO/SHDO",
                    "Bihar Jeevika Bharti",
                    "UPSSSC AGTA",
                    "Cane Supervisor",
                    "MP ESB",
                    "RPSC Agriculture Supervisor",
                    "DDA SO Horticulture",
                    "DSSSB SO Horticulture",
                    "NHB SHO",
                    "CCI JCE",
                    "CWC JTA",
                    "BSSC Field Assistant"
                ],
                "subjects": [
                    "Agronomy",
                    "Genetics & Plant Breeding",
                    "Entomology",
                    "Soil Science",
                    "Agri. Current Affairs",
                    "Horticulture",
                    "Allied Agriculture",
                    "Animal Husbandry",
                    "Plant Pathology",
                    "Food Science & Technology",
                    "Other"
                ]
            }
        }

        return jsonify({
            "success": True,
            "exams": exams
        })
    except Exception as e:
        error_msg = str(e)
        try:
            logger.error(f"Error in get_exams: {error_msg}")
        except:
            print(f"Error in get_exams: {error_msg}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@app.route('/api/ticket', methods=['POST'])
def raise_ticket():
    """Submit a ticket to the Google Sheet"""
    try:
        ticket_data = request.get_json()
        
        if not ticket_data:
            return jsonify({
                'success': False,
                'message': 'No ticket data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['Ticket ID', 'Vertical', 'Exam Name', 'Subject', 'Issue Type', 'Status', 'Issue Text']
        missing_fields = [field for field in required_fields if not ticket_data.get(field)]

        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Get gspread client
        client = get_gspread_client()
        if not client:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to Google Sheets'
            }), 500

        # Open the spreadsheet and get the tickets worksheet
        spreadsheet = client.open_by_key(SHEET_ID)

        # Try to find the tickets worksheet by gid
        tickets_worksheet = None
        for sheet in spreadsheet.worksheets():
            if str(sheet.id) == str(TICKETS_GID):
                tickets_worksheet = sheet
                break

        # If not found by gid, try to find by name "Tickets" or use first sheet
        if not tickets_worksheet:
            try:
                tickets_worksheet = spreadsheet.worksheet('Tickets')
            except:
                tickets_worksheet = spreadsheet.sheet1  # Use first sheet as fallback

        # Prepare row data in order (matching sheet columns)
        row_data = [
            ticket_data.get('Ticket ID', ''),
            ticket_data.get('Vertical', ''),
            ticket_data.get('Exam Name', ''),
            ticket_data.get('Subject', ''),
            ticket_data.get('Issue Type', ''),
            ticket_data.get('Status', 'Open'),
            ticket_data.get('Issue Text', '')
        ]
        
        # Append the row
        tickets_worksheet.append_row(row_data, value_input_option='RAW')
        
        logger.info(f"Ticket created successfully: {ticket_data.get('Ticket ID')}")
        
        return jsonify({
            'success': True,
            'message': 'Ticket raised successfully',
            'ticket_id': ticket_data.get('Ticket ID')
        }), 201
        
    except Exception as e:
        logger.error(f"Error raising ticket: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Failed to raise ticket',
            'error': str(e)
        }), 500

def verify_google_token(token):
    """
    Verify Google OAuth token and check domain restrictions
    Returns (success, user_data, error_message)
    """
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Verify issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return False, None, 'Invalid token issuer'
        
        # Extract user info
        email = idinfo.get('email', '')
        email_verified = idinfo.get('email_verified', False)
        
        if not email_verified:
            return False, None, 'Email not verified'
        
        # Check if email domain is allowed
        email_domain = email.split('@')[-1] if '@' in email else ''
        
        if email_domain not in ALLOWED_EMAIL_DOMAINS:
            return False, None, f'Access restricted to {", ".join(ALLOWED_EMAIL_DOMAINS)} domains only'
        
        # Extract user data
        user_data = {
            'email': email,
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'given_name': idinfo.get('given_name', ''),
            'family_name': idinfo.get('family_name', ''),
            'sub': idinfo.get('sub', '')  # Google user ID
        }
        
        return True, user_data, None
        
    except ValueError as e:
        # Invalid token
        logger.error(f"Google token verification failed: {e}")
        return False, None, 'Invalid or expired token'
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        return False, None, f'Token verification error: {str(e)}'

@app.route('/api/auth/google-login', methods=['POST'])
def google_login():
    """
    Authenticate user using Google OAuth token
    Expects: { "credential": "google_oauth_token" }
    Returns JWT token for API access
    """
    try:
        data = request.get_json()
        
        if not data or 'credential' not in data:
            return jsonify({
                'success': False,
                'message': 'Google credential token is required'
            }), 400
        
        google_token = data.get('credential', '').strip()
        
        if not google_token:
            return jsonify({
                'success': False,
                'message': 'Google credential cannot be empty'
            }), 400
        
        if not GOOGLE_CLIENT_ID:
            return jsonify({
                'success': False,
                'message': 'Google OAuth not configured on server'
            }), 503
        
        # Verify Google token and check domain
        success, user_data, error_msg = verify_google_token(google_token)
        
        if not success:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 401
        
        # Generate JWT token for our API
        token = generate_token(user_data['email'], user_data['email'])
        
        logger.info(f"Google login successful: {user_data['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'email': user_data['email'],
                'name': user_data['name'],
                'picture': user_data['picture'],
                'given_name': user_data['given_name'],
                'family_name': user_data['family_name']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Google login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/auth/google-verify', methods=['GET'])
@token_required
def google_verify_token(current_user):
    """Verify if JWT token is valid"""
    return jsonify({
        'success': True,
        'message': 'Token is valid',
        'user': current_user
    }), 200

@app.route('/api/auth/allowed-domains', methods=['GET'])
def get_allowed_domains():
    """Get list of allowed email domains"""
    return jsonify({
        'success': True,
        'allowed_domains': ALLOWED_EMAIL_DOMAINS,
        'google_client_id': GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else None
    }), 200

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirmPassword', '').strip()

        # Validation
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'}), 400
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

        # Password strength validation
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400

        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400

        # Check if user already exists
        users = get_credentials_data()
        for user in users:
            if user['username'].lower() == username.lower():
                return jsonify({'success': False, 'message': 'Username already exists'}), 409
            if user['email'].lower() == email.lower():
                return jsonify({'success': False, 'message': 'Email already registered'}), 409

        # Hash password
        password_hash = hash_password(password)

        # Write to sheet
        result = write_to_credentials_sheet(username, email, password_hash)

        # Check if write was successful
        if result['success']:
            # Generate token for auto-login after signup
            token = generate_token(username, email)

            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'username': username,
                    'email': email
                }
            }), 201
        else:
            # Write failed - likely missing credentials.json
            return jsonify({
                'success': False,
                'message': result.get('message', 'Failed to register user'),
                'instructions': {
                    'step1': 'Go to Google Cloud Console (console.cloud.google.com)',
                    'step2': 'Create a new project or select existing',
                    'step3': 'Enable Google Sheets API',
                    'step4': 'Create a service account and download JSON credentials',
                    'step5': 'Save the JSON file as credentials.json in the backend folder',
                    'step6': f'Share the Google Sheet with the service account email (found in credentials.json)',
                    'temp_workaround': result.get('temp_solution', 'Manually add user to sheet')
                },
                'user_data': {
                    'username': username,
                    'email': email,
                    'password_hash': password_hash
                }
            }), 503  # Service Unavailable

    except Exception as e:
        print(f"Signup error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Authenticate user by email domain only (No password required)"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        email = data.get('email', '').strip()

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        # Validate email format
        if '@' not in email:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400

        # Extract and validate domain
        email_domain = email.split('@')[-1].lower()
        
        if email_domain not in ALLOWED_EMAIL_DOMAINS:
            logger.warning(f"❌ Access denied for {email}: Domain '{email_domain}' not allowed")
            return jsonify({
                'success': False,
                'message': f'Access denied. Only emails from {", ".join(ALLOWED_EMAIL_DOMAINS)} are allowed.'
            }), 403

        logger.info(f"✅ Domain validation passed for: {email} ({email_domain})")

        # Extract username from email (part before @)
        username = email.split('@')[0]
        
        # Domain-based authentication
        user = {
            'username': username,
            'email': email
        }
        auth_source = 'Domain-based'

        # Generate JWT token
        token = generate_token(user['username'], user['email'])

        logger.info(f"✅ Login successful for {email} via {auth_source}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'username': user['username'],
                'email': user['email']
            },
            'auth_source': auth_source
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if token is valid"""
    return jsonify({
        'success': True,
        'message': 'Token is valid',
        'username': current_user
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    users = get_credentials_data()

    user = None
    for u in users:
        if u['username'] == current_user:
            user = u
            break

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'user': {
            'username': user['username'],
            'email': user['email']
        }
    }), 200

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint that doesn't depend on anything"""
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running!',
        'timestamp': str(datetime.now())
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with diagnostics"""
    try:
        diagnostics = {
            'status': 'running',
            'google_credentials_configured': bool(GOOGLE_CREDENTIALS_BASE64),
            'jwt_secret_configured': bool(JWT_SECRET_KEY),
            'credentials_gid': bool(CREDENTIALS_GID)
        }
        
        # Test Google Sheets connection
        try:
            client = get_gspread_client()
            diagnostics['google_sheets_connection'] = 'connected' if client else 'failed'
        except Exception as e:
            diagnostics['google_sheets_connection'] = f'error: {str(e)}'
        
        return jsonify(diagnostics), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Export app for Vercel serverless
# Vercel will look for 'app' or 'handler' variable
handler = app

# Ensure app is properly initialized for Vercel
try:
    # Test that app is ready
    if not app:
        raise RuntimeError("Flask app not initialized")
except Exception as e:
    print(f"Error initializing app: {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    # Use environment variable for port, default to 5001 to avoid AirPlay conflict on macOS
    port = int(PORT)
    app.run(debug=True, port=port, host='0.0.0.0')
