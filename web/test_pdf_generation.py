#!/usr/bin/env python3
"""
Test script for PDF generation with new Job model data structure
"""

import sys
import os

# Add the web directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pdf_generation():
    """Test PDF generation with sample data matching new Job model structure"""
    
    # Sample profile data
    profile_data = {
        'name': 'Ruby Ferdianto',
        'title': 'Software Developer',
        'location': 'Singapore',
        'experience_level': 'mid',
        'email_address': 'ruby@example.com',
        'summary': 'Experienced software developer with expertise in Python and web development',
        'skills': [
            {'skill_name': 'Python'},
            {'skill_name': 'JavaScript'},
            {'skill_name': 'SQL'},
            {'skill_name': 'React'},
            {'skill_name': 'Node.js'}
        ]
    }
    
    # Sample job data using new Job model structure
    job_data = {
        'job_id': 'test_job_123',
        'title': 'Senior Software Engineer',
        'company_name': 'TechCorp Singapore',
        'job_category': ['Information Technology', 'Software Development'],
        'description': 'Exciting opportunity to work on cutting-edge web applications',
        'keywords': 'python javascript react node.js sql database web development agile scrum',
        'position_level': 'Senior',
        'min_years_experience': '3-5 Years',
        'min_education_level': 'Bachelor\'s Degree',
        'no_of_vacancies': 2,
        'min_salary': 5000,
        'max_salary': 8000,
        'salary_interval': 'Monthly',
        'currency': 'SGD',
        'employment_type': ['Full-time'],
        'work_arrangement': 'Hybrid',
        'nearest_mrt_station': ['Marina Bay', 'Raffles Place'],
        'timing_shift': ['Regular Hours'],
        'address': '1 Marina Boulevard, Singapore 018989',
        'postal_code': '018989',
        'website': 'https://techcorp.sg',
        'company_description': 'Leading technology company in Singapore specializing in innovative software solutions.',
        'required_skills': ['Python', 'JavaScript', 'React', 'SQL'],
        'match_percentage': 87.5,
        'skills_only_percentage': 82.0,
        'matched_skills': ['Python', 'JavaScript', 'React', 'SQL'],
        'missing_skills': ['Docker', 'Kubernetes']
    }
    
    try:
        from services.pdf_generator import get_pdf_generator
        
        print("🧪 Testing PDF generation with new Job model structure...")
        pdf_gen = get_pdf_generator()
        
        # Generate PDF
        pdf_bytes = pdf_gen.generate_application_pdf(profile_data, job_data)
        
        # Save test PDF
        output_path = 'test_application.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ PDF generated successfully!")
        print(f"📄 File size: {len(pdf_bytes):,} bytes")
        print(f"💾 Saved to: {output_path}")
        
        # Print some key information from the job data
        print(f"\n📋 Job Information Used:")
        print(f"   Title: {job_data['title']}")
        print(f"   Company: {job_data['company_name']}")
        print(f"   Categories: {job_data['job_category']}")
        print(f"   Salary: {job_data['currency']} {job_data['min_salary']:,} - {job_data['max_salary']:,}")
        print(f"   Location: {job_data['address']}")
        print(f"   Work Arrangement: {job_data['work_arrangement']}")
        print(f"   Match: {job_data['match_percentage']}%")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install required packages: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)