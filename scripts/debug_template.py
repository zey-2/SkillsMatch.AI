#!/usr/bin/env python3
"""
Debug template rendering issue
"""
import sys
import os
sys.path.insert(0, '/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI')

from web.app import app
from flask import render_template_string

def debug_template_rendering():
    with app.app_context():
        from web.storage import profile_manager
        
        # Get profiles data exactly as in the route
        profiles_data = profile_manager.list_profiles()
        profile_files = []
        
        from datetime import datetime
        def parse_datetime(date_str):
            if not date_str:
                return None
            try:
                if isinstance(date_str, str):
                    if 'T' in date_str:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except:
                return None
        
        for profile_data in profiles_data:
            profile_obj = {
                'id': profile_data.get('user_id', profile_data.get('name', 'unknown')),
                'filename': f"{profile_data.get('user_id', profile_data.get('name', 'unknown'))}.json",
                'name': profile_data.get('name', 'Unknown'),
                'email': profile_data.get('email', ''),
                'title': profile_data.get('title', 'No title'),
                'experience_level': profile_data.get('experience_level', 'not_specified'),
                'skills': profile_data.get('skills', []),
                'industries': profile_data.get('industries', []),
                'location': profile_data.get('location', ''),
                'resume_file': profile_data.get('resume_file'),
                'skills_count': len(profile_data.get('skills', [])),
                'experience_years': sum(exp.get('years', 0) or 0 for exp in profile_data.get('work_experience', [])),
                'created_at': parse_datetime(profile_data.get('created_at')) or datetime.now(),
                'modified': parse_datetime(profile_data.get('updated_at')) or datetime.now()
            }
            profile_files.append(profile_obj)
        
        print(f"✅ Prepared {len(profile_files)} profiles for template")
        
        # Test simple template
        simple_template = """
Profile count: {{ profiles|length }}
{% if profiles %}
HAS PROFILES: Yes
{% for profile in profiles %}
- {{ profile.name }} ({{ profile.id }})
{% endfor %}
{% else %}
HAS PROFILES: No
{% endif %}
"""
        
        result = render_template_string(simple_template, profiles=profile_files)
        print("🧪 Simple template test result:")
        print(result)
        
        # Test if it's a truthiness issue
        print(f"\n🔍 Debugging template variables:")
        print(f"profiles type: {type(profile_files)}")
        print(f"profiles length: {len(profile_files)}")
        print(f"profiles bool: {bool(profile_files)}")
        print(f"profiles[0] type: {type(profile_files[0]) if profile_files else 'N/A'}")
        if profile_files:
            print(f"profiles[0] keys: {list(profile_files[0].keys())}")

if __name__ == "__main__":
    debug_template_rendering()