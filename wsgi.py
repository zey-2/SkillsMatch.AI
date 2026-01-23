#!/usr/bin/env python3
"""
Simplified production entry point for Render.com
Handles common deployment issues and provides debugging
"""

# Eventlet monkey patching MUST be first
# Exclude dns to prevent interference with httpx/openai client
import eventlet

eventlet.monkey_patch(dns=False)

import os
import sys
import logging
from pathlib import Path

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Production environment setup
os.environ["RENDER"] = "1"
os.environ["FLASK_ENV"] = "production"
os.environ["FLASK_DEBUG"] = "False"

# Path setup
current_dir = Path(__file__).parent.absolute()
web_dir = current_dir / "web"

# Ensure directories exist
if not web_dir.exists():
    logger.error(f"Web directory not found: {web_dir}")
    sys.exit(1)

# Add to Python path
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(web_dir))

logger.info(f"Project root: {current_dir}")
logger.info(f"Web directory: {web_dir}")

try:
    # Import the Flask app
    logger.info("Importing Flask application...")

    # Change to web directory for imports
    original_cwd = os.getcwd()
    os.chdir(str(web_dir))

    # Import app and socketio for Socket.IO support
    from app import app, socketio

    # Restore original directory
    os.chdir(original_cwd)

    # For gunicorn with eventlet worker, expose the Flask app directly
    # The eventlet worker will handle Socket.IO automatically via the socketio instance
    application = app

    logger.info("✅ Flask application with Socket.IO loaded successfully")

except Exception as e:
    logger.error(f"💥 Failed to load Flask application: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


# Health check function
def health_check():
    """Simple health check for the application"""
    try:
        with application.test_client() as client:
            response = client.get("/health")
            return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    # For local testing
    port = int(os.environ.get("PORT", 5003))
    logger.info(f"Starting development server on port {port}")
    application.run(host="0.0.0.0", port=port, debug=False)
