# SkillsMatch.AI Test Infrastructure - Quick Reference

## Environment Setup

```bash
# Create conda environment
conda create -n smai python=3.11

# Activate
conda activate smai

# Install dependencies
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

---

## Running Tests

### Basic Execution

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/ -m unit -v

# Run integration tests only
pytest tests/ -m integration -v

# Run fast tests only
pytest tests/ -m "not slow" -v

# Quiet mode (summary only)
pytest tests/ -q
```

### With Options

```bash
# Show print statements
pytest tests/ -v --capture=no

# Stop on first failure
pytest tests/ -x

# Re-run last failed tests
pytest --lf

# Run with coverage
pytest tests/ --cov=src --cov=web --cov-report=html

# Show slowest tests
pytest tests/ --durations=10
```

### Specific Tests

```bash
# Run specific file
pytest tests/test_matching_logic.py -v

# Run specific test class
pytest tests/test_matching_logic.py::TestSkillMatching -v

# Run specific test
pytest tests/test_matching_logic.py::TestSkillMatching::test_exact_skill_match -v

# Run matching pattern
pytest tests/ -k "test_match" -v
```

### Watch Mode (Auto-rerun on changes)

```bash
# Install pytest-watch
pip install pytest-watch

# Watch all tests
ptw tests/

# Watch specific directory
ptw tests/test_matching_logic.py
```

---

## Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov=web --cov-report=html

# View coverage report
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
firefox htmlcov/index.html
```

---

## Available Fixtures

### Using Fixtures

```python
def test_example(junior_developer_profile):
    """Test with profile fixture."""
    assert junior_developer_profile["total_years_experience"] == 2
```

### Profile Fixtures

```python
def test_profiles(junior_developer_profile, 
                  senior_developer_profile, 
                  data_scientist_profile):
    """Test with all profile types."""
    pass
```

### Job Fixtures

```python
def test_jobs(junior_python_job,
              senior_architect_job,
              ml_engineer_job,
              job_listings):
    """Test with job fixtures."""
    pass
```

### Mock Fixtures

```python
def test_ai(mock_openai_client,
            mock_ai_match_response,
            mock_ai_summary):
    """Test with AI mocks."""
    pass
```

### Flask Fixtures

```python
def test_endpoint(client):
    """Test with Flask client."""
    response = client.get("/")
    assert response.status_code == 200
```

### Parametrized Fixtures

```python
def test_levels(experience_level):
    """Test with parametrized fixture."""
    # experience_level: "junior", "mid", or "senior"
    pass
```

---

## Test Markers

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only integration tests
pytest tests/ -m integration -v

# Skip slow tests
pytest tests/ -m "not slow" -v

# Run smoke tests
pytest tests/ -m smoke -v

# View all markers
pytest --markers
```

### Available Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (>5 seconds)
- `@pytest.mark.requires_db` - Needs database
- `@pytest.mark.requires_api` - Needs external API
- `@pytest.mark.smoke` - Smoke tests

---

## GitHub Actions / CI/CD

### Manual Trigger (if configured)

```bash
# Trigger tests workflow
git push origin your-branch

# Check results at:
# https://github.com/your-repo/actions
```

### Workflows Available

**tests.yml**:
- Unit tests: `pytest -m unit`
- Integration tests: `pytest -m integration`
- Security: Bandit, Safety
- Coverage: Codecov

**lint.yml**:
- Pylint analysis
- black formatting
- isort sorting
- flake8 linting
- mypy typing

---

## Writing New Tests

### Simple Test

```python
@pytest.mark.unit
def test_simple():
    """Simple test."""
    assert 1 + 1 == 2
```

### Test with Fixture

```python
@pytest.mark.unit
def test_with_fixture(junior_developer_profile):
    """Test using fixture."""
    assert junior_developer_profile["experience_level"] == "junior"
```

### Test with Multiple Scenarios

```python
@pytest.mark.unit
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),
    (3, 4),
])
def test_multiple(input, expected):
    """Test multiple scenarios."""
    assert input + 1 == expected
```

### Test with Exception

```python
@pytest.mark.unit
def test_exception():
    """Test exception handling."""
    with pytest.raises(ValueError):
        int("not a number")
```

### Integration Test

```python
@pytest.mark.integration
def test_endpoint(client):
    """Test API endpoint."""
    try:
        response = client.get("/")
        assert response.status_code == 200
    except Exception:
        pytest.skip("Endpoint not available")
```

---

## Code Quality Tools

### Manual Checks

```bash
# Check formatting with black
black --check src/ web/ tests/ --line-length=120

# Check imports with isort
isort --check-only src/ web/ tests/

# Check linting with flake8
flake8 src/ web/ tests/ --max-line-length=120

# Check types with mypy
mypy src/ web/ --ignore-missing-imports

# Check security with bandit
bandit -r src/ web/ -f json

# Check dependencies with safety
safety check --json
```

### Auto-Fixes

```bash
# Format with black
black src/ web/ tests/ --line-length=120

# Sort imports with isort
isort src/ web/ tests/
```

---

## Pytest Configuration

### File: pytest.ini

```ini
[pytest]
testpaths = tests web/tests
markers = 
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
addopts = -v --tb=short
```

### Common Options

```bash
# Verbose output
pytest -v

# Quiet output
pytest -q

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Show traceback (long/short/line/native)
pytest --tb=short
```

---

## Fixtures Reference

### Profile Data

```python
junior_developer_profile = {
    "profile_id": "dev_001",
    "experience_level": "junior",
    "total_years_experience": 2,
    "skills": [
        {"skill_id": "python", "level": "advanced"},
        {"skill_id": "django", "level": "intermediate"},
        {"skill_id": "javascript", "level": "intermediate"},
    ]
}
```

### Job Data

```python
junior_python_job = {
    "job_id": "job_001",
    "title": "Junior Python Developer",
    "experience_level": "junior",
    "salary_range": {"min": 80000, "max": 120000},
    "required_skills": [
        {"skill_id": "python", "level": "intermediate"},
    ]
}
```

---

## Debugging Tests

### Print Debug Info

```python
def test_debug(junior_developer_profile):
    """Test with debug output."""
    print(f"Profile: {junior_developer_profile}")
    
    # Run with: pytest tests/ -s -v
```

### Use pdb Debugger

```python
def test_with_pdb():
    """Test with debugger."""
    import pdb
    x = 1
    pdb.set_trace()  # Execution will pause here
    y = 2
```

### Use pytest's --pdb Option

```bash
# Drop into debugger on failure
pytest tests/ --pdb

# Drop into debugger on first failure
pytest tests/ -x --pdb
```

---

## Common Issues

### Import Error

```bash
# Solution: Run from project root
cd /path/to/SkillsMatch.AI
pytest tests/
```

### Fixture Not Found

```bash
# Check fixture is in conftest.py
# Check conftest.py is in correct directory
# Restart pytest

pytest --fixtures  # List all fixtures
```

### Test Hangs

```bash
# Add timeout
@pytest.mark.timeout(10)
def test_something():
    pass

# Or use: pip install pytest-timeout
```

### Permission Denied (Windows)

```bash
# Clear pytest cache
pytest --cache-clear

# Or manually delete:
rm -rf .pytest_cache
```

---

## Performance Tuning

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPUs)
pytest tests/ -n auto

# Run with specific number of workers
pytest tests/ -n 4
```

### Slow Test Detection

```bash
# Show slowest tests
pytest tests/ --durations=10

# Mark slow test
@pytest.mark.slow
def test_something():
    pass

# Skip slow tests
pytest tests/ -m "not slow" -v
```

---

## CI/CD Integration

### Before Committing

```bash
# Run all tests locally
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src --cov=web --cov-report=term-missing

# Format code
black src/ web/ tests/
isort src/ web/ tests/
```

### Before Pushing

```bash
# Verify tests still pass
pytest tests/ -v

# Verify no imports sorted
isort --check-only src/ web/ tests/

# Verify formatting
black --check src/ web/ tests/
```

### GitHub Actions Monitoring

1. Navigate to: https://github.com/your-repo/actions
2. Click on workflow run
3. View test output in logs
4. Check coverage in Codecov (if linked)

---

## Helpful Resources

### Documentation

- `docs/TESTING.md` - Comprehensive testing guide
- `PHASE_1B_IMPLEMENTATION_REPORT.md` - What was built
- `TECHNICAL_DEBT_STATUS.md` - Overall progress
- `pytest.ini` - Test configuration
- `tests/conftest.py` - Available fixtures

### External Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Python Testing Best Practices](https://realpython.com/python-testing/)

### Project Files

- Test files: `tests/test_*.py`
- Fixtures: `tests/conftest.py`
- CI/CD workflows: `.github/workflows/`
- pytest config: `pytest.ini`

---

## Quick Checklist for New Tests

- [ ] Test file named `test_*.py`
- [ ] Test function named `test_*`
- [ ] Added appropriate marker (`@pytest.mark.unit` or `.integration`)
- [ ] Uses fixtures instead of hardcoded data
- [ ] Tests one thing only
- [ ] Has docstring explaining what it tests
- [ ] No external API calls (use mocks)
- [ ] No hardcoded file paths
- [ ] Verifies both success and failure cases
- [ ] Added to appropriate test class

---

## Quick Commands Summary

```bash
# Setup
conda create -n smai python=3.11
conda activate smai
pip install -r requirements.txt requirements.dev.txt

# Testing
pytest tests/ -v                           # All tests
pytest tests/ -m unit -v                   # Unit only
pytest tests/ --cov=src --cov=web          # With coverage

# Code Quality
black src/ web/ tests/                     # Format
isort src/ web/ tests/                     # Sort imports
pytest tests/ --cov --cov-report=html      # Coverage report

# Debug
pytest tests/ -v -s                        # Show output
pytest tests/ -x                           # Stop on failure
pytest tests/ --pdb                        # Debug on failure

# CI/CD
git push origin your-branch                # Trigger workflows
# Check: https://github.com/your-repo/actions
```

---

*Quick Reference - SkillsMatch.AI Test Infrastructure*
*Phase 1B Complete*
