# How to Run SkillsMatch.AI

## Quick Start

### 1. Activate Environment
```bash
conda activate smai
```

### 2. Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python web/app.py
```

The app will start on `http://127.0.0.1:5003` by default.

---

## What to Expect

### ✅ Successful Startup Output
```
✅ Running in correct conda environment: smai
✅ SQLite database configured
✅ Successfully imported database.models
✅ Database models loaded
✅ Core utilities
✅ Initialized AI Skill Matcher with [provider]
 * Running on http://127.0.0.1:5003
```

### ⚠️ Warnings (Normal)
These warnings are OK and don't break the app:
- "SkillMatch core modules not available" - some advanced features may be degraded
- "AI credentials not found" - app will use fallback/demo mode
- These are graceful fallbacks - the app still works!

---

## Features Available

### ✅ Always Available
- User profile creation
- Job listings
- Profile-to-job matching (basic algorithm)
- Dashboard and statistics
- HTML web interface

### ⚠️ Available with AI Keys
- AI-powered skill explanations
- AI interview tips
- AI career suggestions
- AI skill gap analysis
- Enhanced job recommendations

To use AI features, set environment variables in `.env`:
```bash
OPENAI_API_KEY=sk-...
# OR
GITHUB_TOKEN=ghp_...
```

### ⚠️ Available with External APIs
- Fetch jobs from FindSGJobs API
- Job search and filtering

---

## Testing the App

### 1. Check Dashboard
Navigate to: `http://127.0.0.1:5003/`
- Should show dashboard with statistics

### 2. Create a Profile
Navigate to: `http://127.0.0.1:5003/profile/create`
- Fill in profile details
- Add skills
- Submit

### 3. View Jobs
Navigate to: `http://127.0.0.1:5003/jobs`
- Should show job listings

### 4. Match Profile to Jobs
Navigate to: `http://127.0.0.1:5003/match`
- Select a profile
- See matching results

### 5. Test API
```bash
# List profiles
curl http://127.0.0.1:5003/api/profiles

# List jobs
curl http://127.0.0.1:5003/api/jobs

# Get health status
curl http://127.0.0.1:5003/api/health
```

---

## Troubleshooting

### Error: "Not running in 'smai' conda environment"
**Fix**: Activate the environment first
```bash
conda activate smai
python web/app.py
```

### Error: "No module named 'flask_cors'"
**Fix**: Install missing dependencies
```bash
pip install -r requirements.txt
```

### Error: "DATABASE_URL environment variable not set"
**This is OK** - The app will use SQLite fallback automatically

### Warning: "SkillMatch core modules not available"
**This is OK** - The app runs with degraded functionality but still works

### AI Features Not Working
**This is OK** - Set API keys in `.env` to enable AI features

---

## Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
# AI Services
OPENAI_API_KEY=sk-your-key-here
GITHUB_TOKEN=ghp_your-token-here

# Database (optional, uses SQLite if not set)
DATABASE_URL=postgresql://user:password@localhost/skillsmatch

# Flask Config
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

---

## Architecture (Phase 2)

The app is organized into:

### Services Layer (`web/services/`)
- `ProfileService` - User profile management
- `JobService` - Job operations
- `MatchingService` - Job matching algorithm
- `AIService` - AI-powered features

### Blueprints (Routes) (`web/blueprints/`)
- `profiles.py` - Profile routes
- `jobs.py` - Job routes
- `matching.py` - Matching routes
- `dashboard.py` - Dashboard routes
- `api.py` - REST API routes

### Configuration (`web/config.py`)
- Auto-detects development/production/testing environments
- Handles configuration for each environment

---

## Ports and URLs

| Service | URL |
|---------|-----|
| Web App | http://127.0.0.1:5003 |
| API | http://127.0.0.1:5003/api |
| Dashboard | http://127.0.0.1:5003/dashboard |
| Profiles | http://127.0.0.1:5003/profiles |
| Jobs | http://127.0.0.1:5003/jobs |
| Matching | http://127.0.0.1:5003/match |

---

## Development Tips

### Enable Debug Mode
Set environment variable:
```bash
set FLASK_ENV=development
python web/app.py
```

### Check Imports
```bash
python -c "from web.services import ProfileService; print('✅ Services OK')"
python -c "from skillmatch import SkillMatchAgent; print('✅ SkillMatch OK')"
```

### Database Setup
Database auto-initializes on first run:
```bash
# Located at: web/data/skillsmatch.db
```

### View Logs
Flask logs are printed to console during development.

---

## Next Steps

After Phase 2 completion, you can:

1. **Deploy** - Use the current setup for production
2. **Phase 3** - Performance optimization (caching, indexing)
3. **Phase 4** - Polish & documentation
4. **Extend** - Add new features (WebSocket updates, advanced search, etc.)

---

## Support

For issues or questions:
1. Check the warning/error message
2. Review logs in the terminal
3. Check `.env` file for missing API keys
4. Ensure `smai` conda environment is activated

The app is designed to degrade gracefully - if one feature fails, others continue to work!
