# CCI SurveyHUB — Agent Instructions

## Project Overview
Flask web application for the Chamber of Commerce to create, distribute, collect, and analyse business surveys. Uses SQLite + SQLAlchemy, Jinja2 templates, and Bootstrap 5.

## Build & Run Commands

```bash
# Activate virtual environment
venv\Scripts\activate

# Run development server
python run.py

# Install dependencies (if requirements.txt is fixed)
pip install -r requirements.txt
```

## Test Commands

No test suite exists yet. To add one, use pytest:

```bash
# Install pytest
pip install pytest

# Run all tests
pytest

# Run a single test file
pytest tests/test_models.py

# Run a single test function
pytest tests/test_models.py::test_user_creation

# Run with verbose output
pytest -v
```

## Lint Commands

No linter configured yet. Recommended setup:

```bash
pip install flake8 black
flake8 app/
black app/ --check
black app/ --diff
```

## Code Style Guidelines

### Python
- **Imports**: Standard library first, third-party second, local last. Group with blank lines.
- **Formatting**: 4 spaces indentation. Max line length 100.
- **Types**: Not currently used. Optional type hints are welcome.
- **Naming**:
  - `snake_case` for variables, functions, methods
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - Blueprint names should match the route file name (e.g., `auth = Blueprint('auth', __name__)`)
- **Models**:
  - Always define `__tablename__` explicitly
  - Include `__repr__` on every model
  - Use `db.relationship(..., lazy=True)` for relationships
  - Use `cascade='all, delete-orphan'` for owned collections
  - Use `datetime.utcnow` for timestamps (pending migration to `datetime.now(timezone.utc)`)
- **Error handling**: Use `try/except` sparingly. Log errors with `app.logger.error()` or `flash()` for UI feedback.
- **No `print()` statements** in production code. Use Flask's `current_app.logger`.

### Flask
- Use the **app factory pattern** (`create_app()` in `app/__init__.py`).
- Register all blueprints in `app/__init__.py`.
- Use `url_for()` for all internal links in templates and redirects.
- Use `flash()` with categories (`success`, `danger`, `warning`, `info`) for user feedback.
- Apply `@login_required` to admin routes. Public survey routes must stay open.

### Templates
- All templates **must extend `base.html`** using `{% extends "base.html" %}` and `{% block content %}`.
- Use Bootstrap 5 classes for UI components.
- Use `{{ url_for('static', filename='...') }}` for static assets.
- Keep inline styles to a minimum. Use `app/static/css/main.css` for custom styles.

### Database
- SQLite is the primary database. Use Flask-SQLAlchemy ORM.
- Run migrations manually via `db.create_all()` inside `app.app_context()`.
- Never commit secrets, database files (`instance/surveyhub.db`), or `__pycache__`.

### Files
- `requirements.txt` is currently **UTF-16 encoded** (broken). Rewrite it in UTF-8 when updating.
- Root-level HTML files (`dashboard.html`, `login.html`, etc.) are standalone prototypes. Migrate them into `app/templates/` as Jinja templates when wiring up routes.

## Security
- `SECRET_KEY` is hardcoded in `app/__init__.py` for dev only. Do not use in production.
- Never log or expose `password_hash` values.
- Validate all user inputs (email, SIRET, phone) on both client and server side.
