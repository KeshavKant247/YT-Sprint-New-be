# Vercel serverless function entry point
import sys
import os

# Add parent directory to path so we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Insert at the beginning to ensure our module is found first
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import and expose the Flask app
try:
    from app import app
    print("Flask app imported successfully")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to import Flask app: {e}")
    import traceback
    traceback.print_exc()

    # Create a minimal fallback app
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        import traceback
        return jsonify({
            "error": "Failed to initialize application",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "path": path,
            "sys_path": sys.path
        }), 500
