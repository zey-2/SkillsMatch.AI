#!/usr/bin/env python3
"""
Debug script to inspect the Helpdesk Officer job data
"""

import sys
import os
sys.path.append('web')

from database.db_config import DatabaseConfig
from database.models import Job

def inspect_job():
    """Inspect the problematic job data"""
    
    job_id = "job_623069552991014912_44"
    
    try:
        db_config = DatabaseConfig()
        session = db_config.SessionLocal()
        
        job = session.query(Job).filter(Job.job_id == job_id).first()
        
        if job:
            print(f"🔍 Job ID: {job.job_id}")
            print(f"🔍 Title: {job.title}")
            print(f"🔍 Company: {job.company_name}")
            print(f"🔍 Job Category: {job.job_category} (type: {type(job.job_category)})")
            print(f"🔍 Min Years Experience: {job.min_years_experience} (type: {type(job.min_years_experience)})")
            print(f"🔍 Position Level: {job.position_level} (type: {type(job.position_level)})")
            print(f"🔍 Min Education Level: {job.min_education_level} (type: {type(job.min_education_level)})")
            print(f"🔍 Keywords: {job.keywords[:100] if job.keywords else 'None'}...")
            print(f"🔍 Employment Type: {job.employment_type} (type: {type(job.employment_type)})")
            print(f"🔍 Work Arrangement: {job.work_arrangement} (type: {type(job.work_arrangement)})")
            
            # Check if any field is a list that shouldn't be
            problematic_fields = []
            for field_name in ['min_years_experience', 'position_level', 'min_education_level', 'employment_type', 'work_arrangement']:
                field_value = getattr(job, field_name)
                if isinstance(field_value, list):
                    problematic_fields.append((field_name, field_value))
            
            if problematic_fields:
                print(f"\n🚨 PROBLEMATIC LIST FIELDS FOUND:")
                for field_name, field_value in problematic_fields:
                    print(f"   - {field_name}: {field_value} (should not be a list)")
            else:
                print(f"\n✅ All expected scalar fields are properly typed")
                
        else:
            print(f"❌ Job {job_id} not found")
            
        session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_job()