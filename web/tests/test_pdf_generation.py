#!/usr/bin/env python3
"""Test script for PDF generation with new Job model data structure."""

import os
import sys


def _add_web_root_to_path() -> None:
    """Ensure the web root is on sys.path for imports."""
    web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if web_root not in sys.path:
        sys.path.insert(0, web_root)


_add_web_root_to_path()


def test_pdf_generation() -> bool:
    """Test PDF generation with sample data matching new Job model structure."""
    profile_data = {
        "name": "Ruby Ferdianto",
        "title": "Software Developer",
        "location": "Singapore",
        "experience_level": "mid",
        "email_address": "ruby@example.com",
        "summary": "Experienced software developer with Python and web skills",
        "skills": [
            {"skill_name": "Python"},
            {"skill_name": "JavaScript"},
            {"skill_name": "SQL"},
            {"skill_name": "React"},
            {"skill_name": "Node.js"},
        ],
    }

    job_data = {
        "job_id": "test_job_123",
        "title": "Senior Software Engineer",
        "company_name": "TechCorp Singapore",
        "job_category": ["Information Technology", "Software Development"],
        "description": "Work on cutting-edge web applications",
        "keywords": "python javascript react node.js sql database agile scrum",
        "position_level": "Senior",
        "min_years_experience": "3-5 Years",
        "min_education_level": "Bachelor's Degree",
        "no_of_vacancies": 2,
        "min_salary": 5000,
        "max_salary": 8000,
        "salary_interval": "Monthly",
        "currency": "SGD",
        "employment_type": ["Full-time"],
        "work_arrangement": "Hybrid",
        "nearest_mrt_station": ["Marina Bay", "Raffles Place"],
        "timing_shift": ["Regular Hours"],
        "address": "1 Marina Boulevard, Singapore 018989",
        "postal_code": "018989",
        "website": "https://techcorp.sg",
        "company_description": "Leading technology company in Singapore.",
        "required_skills": ["Python", "JavaScript", "React", "SQL"],
        "match_percentage": 87.5,
        "skills_only_percentage": 82.0,
        "matched_skills": ["Python", "JavaScript", "React", "SQL"],
        "missing_skills": ["Docker", "Kubernetes"],
    }

    try:
        from services.pdf_generator import get_pdf_generator

        print("\ud83e\uddea Testing PDF generation with Job model structure...")
        pdf_gen = get_pdf_generator()

        pdf_bytes = pdf_gen.generate_application_pdf(profile_data, job_data)

        output_path = "test_application.pdf"
        with open(output_path, "wb") as file_handle:
            file_handle.write(pdf_bytes)

        print("\u2705 PDF generated successfully!")
        print(f"\ud83d\udcc4 File size: {len(pdf_bytes):,} bytes")
        print(f"\ud83d\udcbe Saved to: {output_path}")

        print("\n\ud83d\udccb Job Information Used:")
        print(f"   Title: {job_data['title']}")
        print(f"   Company: {job_data['company_name']}")
        print(f"   Categories: {job_data['job_category']}")
        print(
            f"   Salary: {job_data['currency']} {job_data['min_salary']:,} - "
            f"{job_data['max_salary']:,}"
        )
        print(f"   Location: {job_data['address']}")
        print(f"   Work Arrangement: {job_data['work_arrangement']}")
        print(f"   Match: {job_data['match_percentage']}%")

        return True

    except ImportError as exc:
        print(f"\u274c Missing dependency: {exc}")
        print("\ud83d\udca1 Install required packages: pip install reportlab")
        return False
    except Exception as exc:
        print(f"\u274c PDF generation failed: {exc}")
        return False


if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)