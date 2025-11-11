from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from ktu_scrape_site import main as scrape_main
import json
import os
import subprocess
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for WordPress integration

# Cache for announcements data
cache = {
    "data": None,
    "last_updated": None,
    "is_scraping": False
}
cache_lock = threading.Lock()

JSON_FILE = "ktu_announcements.json"
CACHE_DURATION = 3600  # 1 hour in seconds

def run_scraper():
    """Run the scraper in a safe way"""
    with cache_lock:
        if cache["is_scraping"]:
            print("Scraper already running, skipping...")
            return
        cache["is_scraping"] = True

    try:
        print(f"[{datetime.now()}] Starting scraper...")
        # Use subprocess instead of os.system for security
        result = subprocess.run(
            ["python3", "ktu_scrape_site.py"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode == 0:
            print(f"[{datetime.now()}] Scraper completed successfully")
            # Load the new data into cache
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    new_data = json.load(f)
                with cache_lock:
                    cache["data"] = new_data
                    cache["last_updated"] = time.time()
        else:
            print(f"[{datetime.now()}] Scraper failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now()}] Scraper timed out")
    except Exception as e:
        print(f"[{datetime.now()}] Scraper error: {e}")
    finally:
        with cache_lock:
            cache["is_scraping"] = False

def load_initial_cache():
    """Load existing JSON file into cache on startup"""
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            with cache_lock:
                cache["data"] = data
                cache["last_updated"] = time.time()
            print("Loaded existing data into cache")
    except Exception as e:
        print(f"Failed to load initial cache: {e}")

# Initialize cache on startup
load_initial_cache()

# Set up background scheduler to run scraper every 30 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_scraper, trigger="interval", minutes=30)
scheduler.start()

# Run scraper on startup if cache is empty
if cache["data"] is None:
    threading.Thread(target=run_scraper, daemon=True).start()

@app.route('/')
def home():
    return {
        "message": "KTU Announcements API running",
        "endpoints": {
            "/api/ktu/announcements": "Get all announcements (cached)",
            "/api/ktu/refresh": "Force refresh announcements (triggers scraper)",
            "/api/ktu/status": "Get cache status"
        }
    }

@app.route('/api/ktu/announcements')
def announcements():
    """Get announcements from cache"""
    try:
        with cache_lock:
            if cache["data"] is None:
                # No data yet, check if file exists
                if os.path.exists(JSON_FILE):
                    with open(JSON_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    cache["data"] = data
                    cache["last_updated"] = time.time()
                    return jsonify(data)
                else:
                    return jsonify({
                        "error": "Data not available yet. Scraper is running...",
                        "retry_after": 30
                    }), 503

            # Check if cache is stale
            cache_age = time.time() - cache["last_updated"]
            if cache_age > CACHE_DURATION and not cache["is_scraping"]:
                # Trigger background refresh
                threading.Thread(target=run_scraper, daemon=True).start()

            # Return cached data with metadata
            response = cache["data"].copy()
            response["cache_age_seconds"] = int(cache_age)
            response["cached_at"] = datetime.fromtimestamp(cache["last_updated"]).isoformat()

            return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ktu/refresh')
def refresh():
    """Force refresh - trigger scraper immediately"""
    try:
        with cache_lock:
            if cache["is_scraping"]:
                return jsonify({
                    "message": "Scraper already running",
                    "status": "in_progress"
                }), 429

        # Start scraper in background
        threading.Thread(target=run_scraper, daemon=True).start()

        return jsonify({
            "message": "Scraper started",
            "status": "running",
            "estimated_time": "30-60 seconds"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ktu/status')
def status():
    """Get cache and scraper status"""
    with cache_lock:
        return jsonify({
            "is_scraping": cache["is_scraping"],
            "has_data": cache["data"] is not None,
            "last_updated": datetime.fromtimestamp(cache["last_updated"]).isoformat() if cache["last_updated"] else None,
            "cache_age_seconds": int(time.time() - cache["last_updated"]) if cache["last_updated"] else None,
            "announcement_count": cache["data"]["count"] if cache["data"] else 0
        })

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
