#!/usr/bin/env python3
"""
Job CSV Import Script
Import job postings from all_job_post.csv into PostgreSQL database
- Creates Jobs table
- Processes job_skill_set and adds new skills to Skills table
- Imports all job data
"""

import os
import sys
import pandas as pd
import ast
import json
from datetime import datetime
from typing import List, Set
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def parse_skill_set(skill_set_str: str) -> List[str]:
    """Parse the job_skill_set string into a list of skills"""
    try:
        # Try to parse as Python literal (list)
        if skill_set_str.startswith('[') and skill_set_str.endswith(']'):
            skills = ast.literal_eval(skill_set_str)
            if isinstance(skills, list):
                return [skill.strip() for skill in skills if skill.strip()]
        
        # If not a list format, try comma-separated
        if ',' in skill_set_str:
            skills = [skill.strip().strip("'\"") for skill in skill_set_str.split(',')]
            return [skill for skill in skills if skill]
        
        # Single skill
        return [skill_set_str.strip().strip("'\"")]
        
    except (ValueError, SyntaxError) as e:
        print(f"Warning: Could not parse skill set '{skill_set_str[:100]}...': {e}")
        return []

def normalize_skill_name(skill: str) -> str:
    """Normalize skill name for consistency"""
    # Remove extra whitespace and convert to title case
    skill = skill.strip()
    
    # Handle acronyms (keep them uppercase)
    if skill.isupper() and len(skill) <= 6:
        return skill
    
    # Title case for regular skills
    return skill.title()

def create_skill_id(skill_name: str) -> str:
    """Create a unique skill ID from skill name"""
    # Convert to lowercase, replace spaces and special chars with underscores
    skill_id = re.sub(r'[^a-zA-Z0-9\s]', '', skill_name.lower())
    skill_id = re.sub(r'\s+', '_', skill_id)
    return skill_id

def import_jobs_csv():
    """Import jobs from CSV file"""
    print("🚀 Starting Job CSV Import Process")
    print("=" * 50)
    
    try:
        # Import database modules
        from web.database.db_config import db_config
        from web.database.models import Job, Skill
        
        print("✅ Database modules loaded")
        
        # Create database tables
        print("📊 Creating database tables...")
        db_config.create_tables()
        print("✅ Database tables created/verified")
        
        # Load CSV file
        csv_file = "all_job_post.csv"
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return False
        
        print(f"📁 Loading CSV file: {csv_file}")
        df = pd.read_csv(csv_file)
        print(f"✅ CSV loaded: {len(df)} jobs found")
        
        # Start database session
        with db_config.session_scope() as session:
            print("🔄 Processing job data...")
            
            # Track skills to add
            all_skills = set()
            existing_skills = set()
            
            # Get existing skills from database
            existing_skill_records = session.query(Skill).all()
            for skill_record in existing_skill_records:
                existing_skills.add(skill_record.skill_name.lower())
            
            print(f"📋 Found {len(existing_skills)} existing skills in database")
            
            # Process each job
            jobs_processed = 0
            jobs_skipped = 0
            
            for index, row in df.iterrows():
                try:
                    # Check if job already exists
                    existing_job = session.query(Job).filter(Job.job_id == str(row['job_id'])).first()
                    if existing_job:
                        jobs_skipped += 1
                        if jobs_skipped % 100 == 0:
                            print(f"⏭️  Skipped {jobs_skipped} existing jobs...")
                        continue
                    
                    # Parse skills from job_skill_set
                    job_skills = parse_skill_set(str(row['job_skill_set']))
                    normalized_skills = []
                    
                    for skill in job_skills:
                        normalized_skill = normalize_skill_name(skill)
                        if normalized_skill:
                            normalized_skills.append(normalized_skill)
                            all_skills.add(normalized_skill)
                    
                    # Create job record
                    job = Job(
                        job_id=str(row['job_id']),
                        category=str(row['category']) if pd.notna(row['category']) else None,
                        job_title=str(row['job_title']),
                        job_description=str(row['job_description']) if pd.notna(row['job_description']) else None,
                        job_skill_set=normalized_skills
                    )
                    
                    session.add(job)
                    jobs_processed += 1
                    
                    if jobs_processed % 100 == 0:
                        print(f"✅ Processed {jobs_processed} jobs...")
                        session.flush()  # Flush periodically
                    
                except Exception as e:
                    print(f"⚠️  Error processing job {row.get('job_id', 'unknown')}: {e}")
                    continue
            
            print(f"📊 Job processing complete: {jobs_processed} new jobs, {jobs_skipped} skipped")
            
            # Add new skills to Skills table
            print("🔧 Processing skills...")
            new_skills = []
            
            for skill_name in all_skills:
                if skill_name.lower() not in existing_skills:
                    skill = Skill(
                        skill_id=create_skill_id(skill_name),
                        skill_name=skill_name,
                        category='Job Requirement',  # Default category for job skills
                        description=f'Skill extracted from job postings: {skill_name}'
                    )
                    new_skills.append(skill)
            
            # Commit jobs first
            print("💾 Committing job data to database...")
            session.commit()
            
            # Add new skills to database (handle duplicates individually)
            if new_skills:
                print(f"➕ Adding {len(new_skills)} new skills to database...")
                skills_added = 0
                skills_skipped = 0
                
                for skill in new_skills:
                    try:
                        # Check if skill_id already exists
                        existing = session.query(Skill).filter(Skill.skill_id == skill.skill_id).first()
                        if not existing:
                            session.add(skill)
                            session.commit()  # Commit each skill individually
                            skills_added += 1
                        else:
                            skills_skipped += 1
                            
                        if (skills_added + skills_skipped) % 500 == 0:
                            print(f"   Processed {skills_added + skills_skipped} skills...")
                            
                    except Exception as e:
                        print(f"⚠️  Error adding skill {skill.skill_name}: {e}")
                        session.rollback()  # Rollback this skill and continue
                        skills_skipped += 1
                
                print(f"✅ Skills added: {skills_added}, skipped (duplicates): {skills_skipped}")
            else:
                print("✅ No new skills to add")
            
            print("\n" + "=" * 50)
            print("🎉 Import Summary:")
            print(f"   Jobs imported: {jobs_processed}")
            print(f"   Jobs skipped (already exist): {jobs_skipped}")
            print(f"   New skills added: {len(new_skills)}")
            print(f"   Total unique skills found: {len(all_skills)}")
            print("✅ Import completed successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_import():
    """Verify the import was successful"""
    print("\n🔍 Verifying Import Results")
    print("-" * 30)
    
    try:
        from web.database.db_config import db_config
        from web.database.models import Job, Skill
        
        with db_config.session_scope() as session:
            # Count jobs
            job_count = session.query(Job).count()
            print(f"✅ Jobs in database: {job_count}")
            
            # Count skills
            skill_count = session.query(Skill).count()
            print(f"✅ Skills in database: {skill_count}")
            
            # Show sample jobs
            print("\n📋 Sample Jobs:")
            sample_jobs = session.query(Job).limit(3).all()
            for i, job in enumerate(sample_jobs, 1):
                print(f"  {i}. {job.job_title} ({job.category})")
                print(f"     Skills: {len(job.job_skill_set or [])} skills")
            
            # Show some new skills
            print("\n🔧 Sample Skills:")
            sample_skills = session.query(Skill).filter(
                Skill.category == 'Job Requirement'
            ).limit(5).all()
            for skill in sample_skills:
                print(f"  - {skill.skill_name}")
            
            print("✅ Verification complete!")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")

def main():
    """Main function"""
    print("📊 Job CSV Import Tool")
    print("Importing jobs from all_job_post.csv into PostgreSQL")
    print("=" * 60)
    
    # Check CSV file exists
    if not os.path.exists("all_job_post.csv"):
        print("❌ CSV file 'all_job_post.csv' not found!")
        print("Please make sure the file is in the current directory.")
        return
    
    # Import jobs
    success = import_jobs_csv()
    
    if success:
        # Verify import
        verify_import()
        
        print("\n🎯 Next Steps:")
        print("1. Check your PostgreSQL database for the 'jobs' table")
        print("2. Verify the data looks correct")
        print("3. You can safely delete the CSV file after verification")
        print("\n📝 Database Tables Created:")
        print("  - jobs (job postings)")
        print("  - skills (updated with new skills)")
    else:
        print("\n❌ Import failed. Please check the errors above.")

if __name__ == '__main__':
    main()