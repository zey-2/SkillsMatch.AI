# Repository Guidelines

## Project Structure & Module Organization
- `src/skillmatch/`: Core Python package (agents, models, utils).
- `web/`: Flask web app, with `templates/` and `static/` plus `services/` and `utils/`.
- `data/vector_db/`: TF-IDF vector database artifacts (JSON + pickle).
- `uploads/`: User uploads (e.g., resumes).
- `config/` and `web/config/`: Configuration assets.
- Entry points: `skillmatch.py` (CLI), `web/app.py` (local web), `wsgi.py` (production).
- Utility scripts live in `scripts/`.

## Build, Test, and Development Commands
- `conda create -n smai python=3.11` and `conda activate smai`: Required environment.
- `pip install -r requirements.txt`: Install runtime dependencies.
- `pip install -r requirements.dev.txt`: Install dev tools (pytest, black, flake8, isort, mypy, bandit).
- `python web/app.py`: Run the Flask web app locally (port 5000).
- `python skillmatch.py match --profile profiles/john_developer.json`: Run a sample match.
- `python scripts/initialize_vector_db.py`: Build the vector DB.
- `./build.sh`: Render build script (SQLite setup).

## Coding Style & Naming Conventions
- Python style: PEP 8, 4-space indentation, type hints where practical.
- Format/lint: `black` and `flake8` are standard; `isort` and `mypy` are available in dev deps.
- Naming: `snake_case` for modules/functions, `PascalCase` for classes, `test_*.py` for tests.

## Testing Guidelines
- Framework: `pytest` (with `pytest-flask`, `pytest-cov`, `pytest-mock`).
- Tests live in `tests/` and `web/tests/`.
- Run examples: `pytest tests/test_profiles_route.py` or `pytest web/tests/test_*.py`.

## Commit & Pull Request Guidelines
- Git history favors short, imperative messages (e.g., “Fix …”, “Add …”); emojis appear occasionally. Keep it concise and descriptive.
- PRs: branch from `main`, include a clear summary, add tests for new behavior, update docs when APIs change, and ensure lint/tests pass before opening.

## Configuration & Security
- Use `.env.example` as a template; keep secrets out of git.
- Follow `API_SECURITY_GUIDE.md` for API key handling and production hardening.
