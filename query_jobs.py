#!/usr/bin/env python3
"""
Job Database Query Tool
Simple tool to query and explore the jobs database
"""

import os
import sys
from typing import List, Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def query_jobs_by_category():
    """Show job counts by category"""
    print("📊 Jobs by Category")
    print("-" * 30)
    
    try:
        from web.database.db_config import db_config
        from web.database.models import Job
        from sqlalchemy import func
        
        with db_config.session_scope() as session:
            results = session.query(
                Job.category, 
                func.count(Job.id).label('count')
            ).group_by(Job.category).order_by(func.count(Job.id).desc()).all()
            
            total = 0
            for category, count in results:
                print(f"  {category or 'Unknown'}: {count} jobs")
                total += count
            
            print(f"\n  Total: {total} jobs")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def search_jobs_by_skill(skill_name: str):
    """Search jobs that require a specific skill"""
    print(f"🔍 Jobs requiring '{skill_name}'")
    print("-" * 40)
    
    try:
        from web.database.db_config import db_config
        from web.database.models import Job
        from sqlalchemy_utils import ScalarListType
        
        with db_config.session_scope() as session:
            # Search for jobs where job_skill_set contains the skill
            jobs = session.query(Job).filter(
                Job.job_skill_set.contains([skill_name])
            ).limit(10).all()
            
            if not jobs:
                print(f"No jobs found requiring '{skill_name}'")
                return
            
            print(f"Found {len(jobs)} jobs (showing first 10):")
            for i, job in enumerate(jobs, 1):
                print(f"\n{i}. {job.job_title} ({job.category})")
                print(f"   Job ID: {job.job_id}")
                print(f"   Skills: {len(job.job_skill_set or [])} total")
                
                # Show matching skills context
                if job.job_skill_set:
                    matching_skills = [s for s in job.job_skill_set if skill_name.lower() in s.lower()]
                    if matching_skills:
                        print(f"   Matching: {matching_skills}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_top_skills():
    """Show most common skills across all jobs"""
    print("🔧 Top Skills in Job Postings")
    print("-" * 35)
    
    try:
        from web.database.db_config import db_config
        from web.database.models import Job
        from collections import Counter
        
        with db_config.session_scope() as session:
            jobs = session.query(Job).all()
            
            # Count all skills
            skill_counter = Counter()
            for job in jobs:
                if job.job_skill_set:
                    for skill in job.job_skill_set:
                        skill_counter[skill] += 1
            
            print(f"Top 20 most common skills:")
            for skill, count in skill_counter.most_common(20):
                print(f"  {skill}: {count} jobs")
            
            print(f"\nTotal unique skills: {len(skill_counter)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_job_details(job_id: str):
    """Show detailed information about a specific job"""
    print(f"📋 Job Details: {job_id}")
    print("-" * 40)
    
    try:
        from web.database.db_config import db_config
        from web.database.models import Job
        
        with db_config.session_scope() as session:
            job = session.query(Job).filter(Job.job_id == job_id).first()
            
            if not job:
                print(f"❌ Job not found: {job_id}")
                return
            
            print(f"Title: {job.job_title}")
            print(f"Category: {job.category}")
            print(f"Job ID: {job.job_id}")
            print(f"Created: {job.created_at}")
            
            print(f"\nDescription:")
            desc = job.job_description or "No description available"
            print(f"{desc[:500]}...")
            
            print(f"\nRequired Skills ({len(job.job_skill_set or [])}):")
            if job.job_skill_set:
                for i, skill in enumerate(job.job_skill_set, 1):
                    print(f"  {i}. {skill}")
            else:
                print("  No skills listed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main menu"""
    print("📊 Job Database Query Tool")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Show jobs by category")
        print("2. Search jobs by skill")
        print("3. Show top skills")
        print("4. Show job details")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            query_jobs_by_category()
        elif choice == '2':
            skill = input("Enter skill name to search: ").strip()
            if skill:
                search_jobs_by_skill(skill)
        elif choice == '3':
            show_top_skills()
        elif choice == '4':
            job_id = input("Enter job ID: ").strip()
            if job_id:
                show_job_details(job_id)
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()