# SkillsMatch.AI - Deployment Guide

## Overview

This guide covers deploying SkillsMatch.AI to production environments. The application supports multiple deployment strategies including local development, Docker containers, and cloud platforms.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites

- Python 3.11+
- Conda or virtualenv
- Git
- SQLite3 (included with Python)
- Redis (optional, for caching)

### Installation Steps

#### 1. Create Conda Environment

```bash
conda create -n smai python=3.11
conda activate smai
```

#### 2. Clone Repository

```bash
git clone https://github.com/rubyferdianto/SkillsMatch.AI.git
cd SkillsMatch.AI
```

#### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (for testing, linting)
pip install -r requirements.dev.txt
```

#### 4. Configure Environment

Create `.env` file in project root:

```bash
# AI Configuration
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///web/data/skillsmatch.db

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/skillsmatch.log

# Cache Configuration
CACHE_TYPE=simple  # or 'redis' for production
CACHE_REDIS_URL=redis://localhost:6379/0

# API Configuration
API_PORT=5000
API_HOST=127.0.0.1
```

#### 5. Initialize Database

```bash
python web/app.py
# Database initializes automatically on first run
```

#### 6. Run Development Server

```bash
python web/app.py
# App runs on http://127.0.0.1:5000
```

### Verify Installation

1. Open http://127.0.0.1:5000 in browser
2. Check `/api/health` endpoint returns `{"status": "healthy"}`
3. Verify database is created at `web/data/skillsmatch.db`

## Docker Deployment

### Docker Setup

#### 1. Build Docker Image

```bash
docker build -t skillsmatch-ai:latest .
```

#### 2. Create .env File

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

#### 3. Run Container

```bash
docker run -d \
  --name skillsmatch \
  -p 5000:5000 \
  --env-file .env \
  -v skillsmatch-data:/app/web/data \
  -v skillsmatch-logs:/app/logs \
  skillsmatch-ai:latest
```

#### 4. Verify Container

```bash
# Check container is running
docker ps | grep skillsmatch

# View logs
docker logs skillsmatch

# Access API
curl http://localhost:5000/api/health
```

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  skillsmatch:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      DATABASE_URL: sqlite:///web/data/skillsmatch.db
    volumes:
      - skillsmatch-data:/app/web/data
      - skillsmatch-logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  skillsmatch-data:
  skillsmatch-logs:
  redis-data:
```

Run with Docker Compose:

```bash
docker-compose up -d

# View logs
docker-compose logs -f skillsmatch

# Stop services
docker-compose down
```

## Cloud Deployment

### Render Deployment

SkillsMatch.AI includes Render.yaml configuration for easy deployment.

#### 1. Connect Repository

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Select SkillsMatch.AI repo

#### 2. Configure Service

- **Build Command**: `pip install -r requirements-render.txt && python init_sqlite.py`
- **Start Command**: `gunicorn -c gunicorn.conf.py wsgi:app`
- **Environment**: Python 3.11

#### 3. Set Environment Variables

In Render dashboard, add:

```
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
FLASK_ENV=production
SECRET_KEY=<random-secret-key>
DATABASE_URL=sqlite:///web/data/skillsmatch.db
LOG_LEVEL=INFO
```

#### 4. Deploy

- Push changes to main branch
- Render automatically deploys
- Check deployment logs for errors

### AWS Deployment

#### Using Elastic Beanstalk

1. Install AWS EB CLI:
```bash
pip install awsebcli
```

2. Initialize EB:
```bash
eb init -p python-3.11 skillsmatch-ai
```

3. Create environment:
```bash
eb create skillsmatch-prod
```

4. Deploy:
```bash
eb deploy
```

### Heroku Deployment (Legacy)

Note: Heroku free tier has been discontinued. Use Render or AWS instead.

## Environment Configuration

### Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FLASK_ENV` | string | `development` | Flask environment (development/production) |
| `FLASK_DEBUG` | bool | `False` | Enable debug mode |
| `SECRET_KEY` | string | Required | Flask secret key for sessions |
| `DATABASE_URL` | string | `sqlite:///web/data/skillsmatch.db` | Database connection URL |
| `OPENAI_API_KEY` | string | Optional | OpenAI API key for GPT models |
| `GITHUB_TOKEN` | string | Optional | GitHub token for Models API |
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `LOG_FILE` | string | `logs/skillsmatch.log` | Log file path |
| `CACHE_TYPE` | string | `simple` | Cache backend (simple/redis) |
| `CACHE_REDIS_URL` | string | `redis://localhost:6379/0` | Redis URL |
| `API_PORT` | int | `5000` | API server port |
| `API_HOST` | string | `127.0.0.1` | API server host |

### Configuration Files

- **web/config.py**: Flask application configuration
- **web/database/db_config.py**: Database configuration
- **web/config/ai_config.py**: AI service configuration
- **mypy.ini**: Type checking configuration
- **pytest.ini**: Testing configuration

## Database Setup

### SQLite Setup

SQLite is the default database for development and small deployments.

#### Initialize Database

```bash
# Automatic on first app.py run, or manually:
python init_sqlite.py
```

#### Verify Database

```bash
# Check database exists and has tables
sqlite3 web/data/skillsmatch.db ".tables"

# Export schema
sqlite3 web/data/skillsmatch.db ".schema" > schema.sql
```

### PostgreSQL Setup (Production Recommended)

For production deployments, use PostgreSQL:

#### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

#### 2. Create Database and User

```bash
psql -U postgres
```

```sql
CREATE DATABASE skillsmatch_db;
CREATE USER skillsmatch_user WITH PASSWORD 'secure_password';
ALTER ROLE skillsmatch_user SET client_encoding TO 'utf8';
ALTER ROLE skillsmatch_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE skillsmatch_user SET default_transaction_deferrable TO on;
ALTER ROLE skillsmatch_user SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE skillsmatch_db TO skillsmatch_user;
\q
```

#### 3. Update Environment

```bash
# .env
DATABASE_URL=postgresql://skillsmatch_user:secure_password@localhost/skillsmatch_db
```

#### 4. Migrate Schema

```bash
# Using Flask-Migrate (if available)
flask db upgrade

# Or manually run schema
psql -U skillsmatch_user -d skillsmatch_db < schema.sql
```

## Monitoring & Logging

### Structured Logging

The application uses structured JSON logging for production:

```python
from web.utils.logging_config import get_logger

logger = get_logger(__name__)
logger.info("User login", extra={"user_id": "123", "timestamp": "2024-01-18"})
```

### Log Files

- **Application Logs**: `logs/skillsmatch.log`
- **Error Logs**: `logs/skillsmatch_error.log`
- **Access Logs**: Handled by web server (Gunicorn/Nginx)

### Monitoring Stack

#### Recommended Tools

- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Prometheus + Grafana
- **Tracing**: Jaeger or Zipkin
- **Alerting**: PagerDuty, Slack

#### Example: Sentry Integration

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://<key>@sentry.io/<project>",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
)
```

### Health Checks

```bash
# Check API health
curl http://localhost:5000/api/health

# Response:
{
  "status": "healthy",
  "timestamp": "2024-01-18T10:30:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_service": "healthy"
  }
}
```

## Backup & Recovery

### Database Backup

#### SQLite Backup

```bash
# Create backup
cp web/data/skillsmatch.db web/data/skillsmatch_backup_$(date +%Y%m%d).db

# Restore from backup
cp web/data/skillsmatch_backup_20240118.db web/data/skillsmatch.db
```

#### PostgreSQL Backup

```bash
# Full backup
pg_dump -U skillsmatch_user -d skillsmatch_db > backup_20240118.sql

# Restore from backup
psql -U skillsmatch_user -d skillsmatch_db < backup_20240118.sql

# With compression
pg_dump -U skillsmatch_user -d skillsmatch_db | gzip > backup_20240118.sql.gz
gunzip -c backup_20240118.sql.gz | psql -U skillsmatch_user -d skillsmatch_db
```

### Backup Schedule

Recommended backup strategy:

- **Hourly**: Incremental backups (last 24 hours)
- **Daily**: Full backup (last 7 days)
- **Weekly**: Full backup (last 4 weeks)
- **Monthly**: Full backup (archive)

### Backup Storage

- Store backups in multiple locations
- Use cloud storage (S3, GCS, Azure Blob)
- Encrypt sensitive backups
- Test recovery procedures regularly

## Troubleshooting

### Common Issues

#### 1. Import Errors on Startup

**Problem**: `ModuleNotFoundError` on app startup

**Solution**:
```bash
# Ensure environment is activated
conda activate smai

# Reinstall dependencies
pip install -r requirements.txt

# Check PYTHONPATH
echo $PYTHONPATH

# Verify import manually
python -c "from web.app import create_app; print('OK')"
```

#### 2. Database Locked

**Problem**: `database is locked` error

**Solution**:
```bash
# Check for running processes
ps aux | grep python

# Kill any stray processes
kill -9 <pid>

# Verify database integrity
sqlite3 web/data/skillsmatch.db "PRAGMA integrity_check;"
```

#### 3. API Key Issues

**Problem**: AI features not working

**Solution**:
```bash
# Verify environment variables loaded
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# Check .env file exists and is readable
ls -la .env

# Validate API key format
# OpenAI: sk-...
# GitHub: ghp_...

# Test API connectivity
python scripts/check_ai_config.py
```

#### 4. Performance Issues

**Problem**: Slow responses

**Solution**:
```bash
# Check database indexes
sqlite3 web/data/skillsmatch.db "SELECT * FROM sqlite_master WHERE type='index';"

# Enable query profiling
export LOG_LEVEL=DEBUG

# Check cache hit rate
python scripts/check_cache_stats.py

# Profile slow operations
python -m cProfile -s cumtime web/app.py
```

### Debug Mode

Enable debug mode for development:

```bash
# In .env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG

# Or via environment
export FLASK_DEBUG=1
python web/app.py
```

### Getting Help

1. Check [API Documentation](./API_DOCUMENTATION.md)
2. Review [Troubleshooting Guide](./docs/troubleshooting.md)
3. Check logs for error messages
4. Open issue on [GitHub](https://github.com/rubyferdianto/SkillsMatch.AI/issues)

---

**Last Updated**: January 18, 2026
**Maintained By**: SkillsMatch.AI Team
**Version**: 1.0.0
