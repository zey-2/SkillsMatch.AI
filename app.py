#!/usr/bin/env python3
"""
Production entry point for SkillsMatch.AI on Render.com
"""
import os
import sys
from pathlib import Path

# Set production environment variables
os.environ['RENDER'] = '1'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Add current directory and web directory to Python path
current_dir = Path(__file__).parent.absolute()
web_dir = current_dir / 'web'

sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(web_dir))

print(f"🔍 Current directory: {current_dir}")
print(f"🔍 Web directory: {web_dir}")
print(f"🔍 Python path: {sys.path[:3]}")

# Try multiple import strategies
app = None
application = None

try:
    # Strategy 1: Direct import from web.app
    print("🔄 Trying: from web.app import app")
    from web.app import app
    application = app
    print("✅ Success: Direct import from web.app")
except ImportError as e1:
    print(f"❌ Strategy 1 failed: {e1}")
    
    try:
        # Strategy 2: Change to web directory and import
        print("🔄 Trying: Change to web directory")
        os.chdir(str(web_dir))
        from app import app
        application = app
        print("✅ Success: Import from web directory")
    except ImportError as e2:
        print(f"❌ Strategy 2 failed: {e2}")
        
        try:
            # Strategy 3: Add web to path and import app directly
            print("🔄 Trying: Direct app import with path modification")
            sys.path.insert(0, str(web_dir))
            import app as web_app
            application = web_app.app
            print("✅ Success: Direct app import")
        except Exception as e3:
            print(f"❌ Strategy 3 failed: {e3}")
            print("💥 All import strategies failed!")
            sys.exit(1)

if not application:
    print("💥 Failed to initialize Flask application!")
    sys.exit(1)

print("✅ Flask application successfully initialized for production")

if __name__ == '__main__':
    # For direct running (development)
    port = int(os.environ.get('PORT', 5003))
    application.run(host='0.0.0.0', port=port, debug=False)