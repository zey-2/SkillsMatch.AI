# Gunicorn configuration for Render.com deployment
import os

# Server socket - Render expects PORT to be set and detected via 127.0.0.1
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = int(os.environ.get("WEB_CONCURRENCY", 1))
worker_class = "eventlet"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = False
timeout = 300
keepalive = 5

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "skillsmatch-ai"

# Server mechanics
daemon = False
pidfile = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
