# Deployment (SQLite on Render)

SQLite is the default database for Render deployments.

## Render Build
```bash
pip install -r requirements-render.txt && python init_sqlite.py
```

## Render Start
```bash
gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2
```

## Env Vars
- `USE_SQLITE=true`
- `RENDER=true`
- `OPENAI_API_KEY=...`
- `GITHUB_TOKEN=...` (optional)
