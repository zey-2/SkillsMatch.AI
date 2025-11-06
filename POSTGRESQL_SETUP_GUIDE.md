# PostgreSQL Implementation Guide for SkillMatch.AI

## Overview

This guide will help you migrate from JSON file storage to PostgreSQL database for SkillMatch.AI user profiles. **Yes, `psycopg2` is the correct library!** 

## Why PostgreSQL?

✅ **ACID Transactions** - Data integrity and consistency  
✅ **Concurrent Access** - Multiple users can safely access profiles  
✅ **Advanced Querying** - Complex searches and filtering  
✅ **Scalability** - Handle thousands of profiles efficiently  
✅ **Data Relationships** - Proper foreign keys and constraints  
✅ **Full-text Search** - Search across profile content  

## Quick Start

### 1. Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Install Python Dependencies

```bash
conda activate smai
pip install sqlalchemy>=2.0.23 psycopg2-binary>=2.9.7 alembic>=1.12.0
```

### 3. Configure Environment

Copy the provided configuration:
```bash
cp .env.postgresql .env
```

Edit `.env` with your PostgreSQL settings:
```bash
# Database connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=skillmatch
DB_USER=skillmatch_user
DB_PASSWORD=secure_password

# Enable PostgreSQL storage
STORAGE_TYPE=postgresql
```

### 4. Run Setup Script

```bash
python setup_postgresql.py
```

This script will:
- ✅ Install required Python packages
- ✅ Check PostgreSQL connection
- ✅ Create database and user
- ✅ Set up all database tables
- ✅ Migrate existing JSON profiles to PostgreSQL

### 5. Start Application

```bash
python web/app.py
```

Your profiles are now stored in PostgreSQL! 🎉

## Database Schema

### Core Tables

```sql
-- User profiles
user_profiles (user_id, name, email, location, summary, experience_level, ...)

-- Skills with proficiency details  
user_skills_detail (user_id, skill_id, level, years_experience, verified)
skills (skill_id, skill_name, category, description)

-- Work experience
work_experience (user_id, company, position, start_date, end_date, description)

-- Education
education (user_id, institution, degree, field_of_study, graduation_year, gpa)

-- Preferences and goals
user_preferences (user_id, work_types, desired_roles, salary_min, salary_max, ...)
career_goals (goal_text, category)
```

## Library Details

### Primary Libraries

1. **`psycopg2-binary`** - PostgreSQL adapter for Python
   - ✅ **Most popular** PostgreSQL library for Python
   - ✅ **Battle-tested** in production environments
   - ✅ **Easy installation** with binary package
   - ✅ **Full PostgreSQL feature support**

2. **`SQLAlchemy`** - ORM and database toolkit
   - ✅ **Object-Relational Mapping** for clean Python code
   - ✅ **Database migrations** with Alembic
   - ✅ **Connection pooling** for performance
   - ✅ **Cross-database compatibility**

### Alternative Libraries

- **`psycopg3`** - Newer version with async support
- **`asyncpg`** - Async-only PostgreSQL driver
- **`PyODBC`** - Generic database connector

**Recommendation:** Stick with `psycopg2-binary` for your use case - it's the most reliable choice.

## Features Included

### ✅ **Profile Management**
```python
from web.storage import profile_manager

# Save profile (works with both JSON and PostgreSQL)
profile_manager.save_profile(profile_data)

# Load profile
profile = profile_manager.load_profile('user_123')

# Search profiles
results = profile_manager.search_profiles(
    location='Singapore',
    experience_level='mid',
    skills=['Python', 'SQL']
)
```

### ✅ **Automatic Migration**
- Existing JSON profiles automatically migrated
- Maintains data integrity during migration
- No data loss, backward compatible

### ✅ **Development Flexibility**
```python
# Switch storage types via environment variable
STORAGE_TYPE=json        # Use JSON files (development)
STORAGE_TYPE=postgresql  # Use PostgreSQL (production)
```

### ✅ **Advanced Queries**
```sql
-- Find Python developers in Singapore with 3+ years experience
SELECT p.name, p.location, s.years_experience 
FROM user_profiles p
JOIN user_skills_detail usd ON p.user_id = usd.user_id
JOIN skills s ON usd.skill_id = s.id
WHERE p.location ILIKE '%Singapore%' 
  AND s.skill_name = 'Python'
  AND usd.years_experience >= 3;
```

## Troubleshooting

### Connection Issues
```bash
# Check PostgreSQL is running
pg_isready -d skillmatch

# Test connection
psql -h localhost -U skillmatch_user -d skillmatch
```

### Installation Issues
```bash
# Install PostgreSQL development headers (Linux)
sudo apt-get install libpq-dev python3-dev

# Install from source if binary fails
pip install psycopg2 --no-binary psycopg2
```

### Migration Issues
```bash
# Check existing profiles
python -c "from web.storage import profile_manager; print(len(profile_manager.list_profiles()))"

# Re-run migration
python setup_postgresql.py
```

## Performance Benefits

| Feature | JSON Files | PostgreSQL |
|---------|------------|------------|
| **Profile Search** | O(n) scan | O(log n) indexed |
| **Concurrent Access** | File locking issues | ACID transactions |
| **Data Integrity** | Manual validation | Schema constraints |
| **Complex Queries** | Application logic | SQL engine |
| **Scalability** | ~1K profiles | 100K+ profiles |

## Next Steps

1. **Test the Migration**: Run `python setup_postgresql.py`
2. **Verify Data**: Check that all profiles migrated correctly
3. **Update Application**: Set `STORAGE_TYPE=postgresql` in `.env`
4. **Monitor Performance**: Use PostgreSQL query tools
5. **Add Indexes**: Optimize frequently searched fields

## Production Considerations

- **Connection Pooling**: Use `pgbouncer` for high traffic
- **Backup Strategy**: Set up automated PostgreSQL backups  
- **Monitoring**: Add logging and performance metrics
- **Security**: Use SSL connections and proper user permissions
- **Scaling**: Consider read replicas for high-read workloads

Your SkillMatch.AI application is now ready for production-scale profile management! 🚀