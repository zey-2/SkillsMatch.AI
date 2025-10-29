"""
Basic test to verify SkillMatch.AI functionality
"""
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from skillmatch.models import UserProfile, SkillItem, ExperienceLevel
    from skillmatch.utils import DataLoader, SkillMatcher
    
    print("✅ Successfully imported SkillMatch.AI modules")
    
    # Test data loading
    try:
        data_loader = DataLoader(
            skills_db_path="data/skills_database.json",
            opportunities_db_path="data/opportunities_database.json"
        )
        
        skills_data = data_loader.skills_data
        opportunities_data = data_loader.opportunities_data
        
        print(f"✅ Loaded skills database with {len(skills_data.get('skill_categories', {}))} categories")
        print(f"✅ Loaded opportunities database with {len(opportunities_data.get('opportunities', []))} opportunities")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)
    
    # Test skill matcher
    try:
        skill_matcher = SkillMatcher(skills_data)
        print("✅ Successfully initialized SkillMatcher")
        
        # Test with sample profile
        with open("profiles/john_developer.json", "r") as f:
            profile_data = json.load(f)
        
        user_profile = UserProfile(**profile_data)
        print(f"✅ Successfully loaded user profile: {user_profile.name}")
        
        # Calculate portfolio score
        portfolio_scores = skill_matcher.calculate_skill_portfolio_score(user_profile)
        print("✅ Successfully calculated skill portfolio scores")
        
        for category, score in portfolio_scores.items():
            if score > 0:
                print(f"   {category}: {score:.2%}")
        
    except Exception as e:
        print(f"❌ Error with skill matching: {e}")
        sys.exit(1)
    
    print("\n🎉 All basic tests passed! SkillMatch.AI is ready to use.")
    print("\nNext steps:")
    print("1. Get a GitHub Personal Access Token: https://github.com/settings/tokens")
    print("2. Run: python skillmatch.py setup")
    print("3. Try: python skillmatch.py match --profile profiles/john_developer.json")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure you have installed all dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)