# Testing Guide - SkillsMatch.AI

A comprehensive guide for running, writing, and maintaining tests in the SkillsMatch.AI project.

---

## Quick Start

### Run All Tests
```bash
pytest tests/ -v
```

### Run Unit Tests Only
```bash
pytest tests/ -m unit -v
```

### Run Integration Tests Only
```bash
pytest tests/ -m integration -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov=web --cov-report=html
```

---

## Test Structure

### Test Organization

```
tests/
├── conftest.py                    # Shared fixtures (15+ categories)
├── test_matching_logic.py         # Unit tests (36 tests, 9 classes)
├── test_integration_api.py        # Integration tests (26 tests, 9 classes)
├── test_database.py               # Database operations (planned)
└── test_performance.py            # Load/performance tests (planned)

web/tests/
├── test_production.py
├── test_dashboard.py
├── test_database.py
└── test_pdf_generation.py
```

### Test Markers

Tests are categorized with markers for selective execution:

```bash
# Run only fast tests
pytest tests/ -m "not slow" -v

# Run only tests requiring API
pytest tests/ -m requires_api -v

# Run smoke tests
pytest tests/ -m smoke -v
```

**Available Markers:**
- `@pytest.mark.unit` - Unit tests (no external dependencies)
- `@pytest.mark.integration` - Integration tests (with API/database)
- `@pytest.mark.slow` - Tests taking >5 seconds
- `@pytest.mark.requires_db` - Tests needing database
- `@pytest.mark.requires_api` - Tests needing external APIs
- `@pytest.mark.smoke` - Quick smoke tests

---

## Fixtures (conftest.py)

### Profile Fixtures

Represents different user experience levels:

```python
def test_example(junior_developer_profile):
    """Test with junior developer data."""
    assert junior_developer_profile["experience_level"] == "junior"
    assert junior_developer_profile["total_years_experience"] == 2
```

**Available Profiles:**
- `junior_developer_profile` - 2 years experience
- `senior_developer_profile` - 8 years experience
- `data_scientist_profile` - 5 years experience

### Job Fixtures

Represents different job listings:

```python
def test_match(job_listings):
    """Test with all job types."""
    assert len(job_listings) == 3
    assert "job_ml_engineer_001" in [j["job_id"] for j in job_listings]
```

**Available Jobs:**
- `junior_python_job` - Entry-level role, $80-120K
- `senior_architect_job` - Senior role, $200-300K
- `ml_engineer_job` - Mid-level ML, $150-200K

### Mock Fixtures

For testing without external dependencies:

```python
def test_ai_matching(mock_openai_client, mock_ai_match_response):
    """Test matching with mocked AI."""
    # Use mock_openai_client instead of real API
    # Use mock_ai_match_response for test data
    pass
```

**Available Mocks:**
- `mock_openai_client` - OpenAI API mock
- `mock_ai_match_response` - Match result mock
- `mock_ai_summary` - AI summary mock

### Flask Fixtures

For testing routes and endpoints:

```python
def test_homepage(client):
    """Test homepage endpoint."""
    response = client.get("/")
    assert response.status_code == 200
```

**Available:**
- `app` - Flask test application
- `client` - Flask test client
- `runner` - Flask CLI runner

### Parametrized Fixtures

For testing multiple values:

```python
def test_experience_levels(experience_level):
    """Test different experience levels."""
    assert experience_level in ["junior", "mid", "senior"]
```

**Available Parametrized:**
- `years_of_experience` - [1, 2, 3, 5, 8]
- `skill_level` - ["beginner", "intermediate", "advanced", "expert"]
- `experience_level` - ["junior", "mid", "senior"]

---

## Writing Tests

### Unit Test Template

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.unit
class TestMyFeature:
    """Tests for my feature."""
    
    def test_happy_path(self, fixture_data):
        """Test successful scenario."""
        # Arrange
        input_data = fixture_data
        expected = "success"
        
        # Act
        result = my_function(input_data)
        
        # Assert
        assert result == expected
    
    def test_error_handling(self):
        """Test error scenario."""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            my_function(invalid_input)
    
    @pytest.mark.parametrize("input,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_multiple_scenarios(self, input, expected):
        """Test multiple scenarios."""
        assert my_function(input) == expected
```

### Integration Test Template

```python
@pytest.mark.integration
class TestMyEndpoint:
    """Integration tests for my endpoint."""
    
    def test_api_endpoint(self, client, junior_developer_profile):
        """Test API endpoint."""
        try:
            response = client.post(
                "/api/my-endpoint",
                json=junior_developer_profile
            )
            assert response.status_code in [200, 400]
        except Exception:
            pytest.skip("Endpoint not available")
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@patch('web.services.ai_skill_matcher.openai.ChatCompletion.create')
def test_ai_matching(self, mock_create, mock_ai_match_response):
    """Test AI matching with mock."""
    mock_create.return_value = mock_ai_match_response
    
    result = match_profiles(profile, job)
    
    assert result["score"] == 85
    mock_create.assert_called_once()
```

---

## Test Coverage

### Check Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov=web --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Coverage Configuration

Minimum coverage requirement: **70%**

Coverage is measured across:
- `src/` - Core SkillsMatch modules
- `web/` - Flask web application

Excluded from coverage:
- Test files
- `__pycache__` directories
- Virtual environments
- Abstract methods

### Improving Coverage

1. **Identify uncovered code**:
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

2. **Add tests for gaps**:
   - Look for red lines in HTML coverage report
   - Write tests for edge cases
   - Test error paths

3. **Verify improvement**:
   ```bash
   pytest --cov=src --cov-report=html
   ```

---

## Running Tests Locally

### Setup Environment

```bash
# Create conda environment
conda create -n smai python=3.11

# Activate environment
conda activate smai

# Install dependencies
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

### Execute Tests

```bash
# Run all tests
pytest tests/ -v

# Run with output capture disabled (see print statements)
pytest tests/ -v --capture=no

# Run failing tests
pytest --lf

# Run last failed tests and stop on first failure
pytest --lf -x

# Run tests matching pattern
pytest tests/ -k "test_match" -v

# Run tests and stop at first failure
pytest tests/ -x
```

### Watch Tests During Development

```bash
# Install pytest-watch
pip install pytest-watch

# Watch for changes and re-run tests
ptw tests/
```

---

## CI/CD Pipeline

### Automatic Testing

Tests run automatically on:
- **Push** to `main` or `develop` branches
- **Pull requests** to `main` or `develop`

### GitHub Actions Workflows

#### tests.yml - Main Testing Pipeline
```
Triggers: Push to main/develop, Pull requests
Python Versions: 3.10, 3.11
Jobs:
  1. Test Job
     - Unit tests: pytest -m unit
     - Integration tests: pytest -m integration
     - Coverage to Codecov
  
  2. Security Job
     - Bandit security scanning
     - Safety vulnerability checks
  
  3. Build Job
     - Package build verification
     - Import validation
```

#### lint.yml - Code Quality Pipeline
```
Triggers: Pull requests to main/develop
Checks:
  - Pylint analysis
  - isort import sorting
  - black formatting
  - flake8 linting
  - mypy type checking
Auto-fixes: PR comments with suggestions
```

### Viewing Results

1. **GitHub Actions Tab**:
   - Navigate to Actions tab in repository
   - Click on workflow run
   - View test output

2. **Pull Request Checks**:
   - Test results shown in PR checks
   - Click "Details" to see full output

3. **Coverage Reports**:
   - Coverage uploaded to Codecov
   - Badge shows overall coverage percentage

---

## Best Practices

### DO ✅

- **Use descriptive test names**: `test_junior_dev_matches_junior_job_correctly`
- **One assertion per test** (ideally): Test one thing at a time
- **Use fixtures**: Don't hardcode test data in tests
- **Test edge cases**: Empty inputs, None values, extreme values
- **Isolate tests**: Tests should be independent
- **Use mocks**: Avoid external dependencies in unit tests
- **Mark slow tests**: Use `@pytest.mark.slow` for tests >5 seconds
- **Document complex tests**: Add docstrings explaining what/why
- **Keep tests DRY**: Use fixtures and parametrization to reduce duplication

### DON'T ❌

- **Don't share state**: Each test should be independent
- **Don't test implementation details**: Test behavior, not internals
- **Don't create real files**: Use `temp_resume_file` fixture or `tmpdir`
- **Don't make network requests**: Mock external APIs
- **Don't use sleep()**: Use proper wait mechanisms
- **Don't create database records**: Use mocks or test database
- **Don't hardcode values**: Use fixtures or parametrization
- **Don't catch all exceptions**: Catch specific exceptions

---

## Common Testing Patterns

### Testing Exceptions

```python
def test_validation_error():
    """Test that invalid input raises exception."""
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email("not-an-email")
```

### Testing with Multiple Values

```python
@pytest.mark.parametrize("skill,level", [
    ("python", "expert"),
    ("javascript", "advanced"),
    ("sql", "intermediate"),
])
def test_skill_levels(skill, level):
    """Test different skills and levels."""
    profile = create_profile_with_skill(skill, level)
    assert profile.get_skill(skill).level == level
```

### Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_matching():
    """Test asynchronous matching."""
    result = await async_match_profiles(profile, job)
    assert result["score"] > 0
```

### Testing Database Operations

```python
@pytest.mark.requires_db
def test_save_profile(mock_database_session):
    """Test saving profile to database."""
    profile = create_profile()
    
    mock_database_session.add(profile)
    mock_database_session.commit()
    
    assert profile.profile_id is not None
```

### Mocking Time

```python
from unittest.mock import patch
from datetime import datetime

@patch('module.datetime')
def test_with_mocked_time(mock_datetime):
    """Test code that depends on current time."""
    mock_datetime.now.return_value = datetime(2024, 1, 1)
    
    result = get_time_based_data()
    assert result.year == 2024
```

---

## Troubleshooting

### Issue: Fixture Not Found

**Error**: `fixture 'my_fixture' not found`

**Solution**: 
- Check that fixture is defined in `conftest.py`
- Ensure `conftest.py` is in correct directory (same as test)
- Restart pytest if using watch mode

### Issue: Import Error in Tests

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
- Run pytest from project root: `cd /path/to/SkillsMatch.AI`
- Check `pytest.ini` has correct `testpaths`
- Install dependencies: `pip install -r requirements.dev.txt`

### Issue: Test Hangs/Timeout

**Error**: Test never completes

**Solution**:
- Add timeout: `@pytest.mark.timeout(10)`
- Install pytest-timeout: `pip install pytest-timeout`
- Check for infinite loops in test code
- Check for real network calls (should be mocked)

### Issue: Flaky Tests (Intermittent Failures)

**Causes**:
- Random test ordering (use `--randomly-dont-shuffle` to debug)
- Shared state between tests
- Time-dependent code not mocked
- External API flakiness

**Solutions**:
- Isolate tests better
- Mock all external dependencies
- Use mocks for time/dates
- Add retry mechanism for external APIs

### Issue: Permission Denied (Windows)

**Error**: `PermissionError: [WinError 5]`

**Solution**:
- Close any open file handles
- Check that database file isn't locked
- Restart Python shell
- Use `pytest --cache-clear`

---

## Performance

### Test Execution Time Goals

- **Unit tests**: < 1 second per test
- **Integration tests**: < 5 seconds per test
- **All tests**: < 30 seconds

### Profiling Tests

```bash
# Show slowest tests
pytest tests/ --durations=10

# Show detailed timing
pytest tests/ -v --durations=0 --tb=no
```

### Optimizing Slow Tests

1. Move to integration mark: `@pytest.mark.integration`
2. Mock external calls
3. Use smaller datasets
4. Parallelize with pytest-xdist:
   ```bash
   pip install pytest-xdist
   pytest tests/ -n auto
   ```

---

## Continuous Improvement

### Monthly Review

- Check coverage trend
- Review failing tests
- Analyze test execution time
- Update fixtures as codebase evolves

### Quarterly Updates

- Add tests for new features
- Refactor flaky tests
- Optimize performance bottlenecks
- Update documentation

---

## Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest Fixtures**: https://docs.pytest.org/en/stable/fixture.html
- **Testing Best Practices**: https://docs.pytest.org/en/stable/goodpractices.html
- **Our Test Files**: See tests/ directory for examples

---

## Contact & Support

For testing-related questions:
1. Check this guide first
2. Review example tests in `tests/` directory
3. Check pytest documentation
4. Review GitHub Actions logs for CI/CD issues

---

*Testing Guide - SkillsMatch.AI*
*Updated: Phase 1B Completion*
