#!/usr/bin/env python3
"""
Quick demonstration of SkillMatch.AI capabilities
"""
import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from skillmatch import SkillMatchAgent, UserProfile


async def demo_without_ai():
    """Demo the core matching without requiring GitHub token"""
    print("🎯 SkillMatch.AI Demo - Core Functionality")
    print("=" * 50)
    
    from skillmatch.utils import DataLoader, SkillMatcher
    
    # Load data
    data_loader = DataLoader(
        skills_db_path="data/skills_database.json",
        opportunities_db_path="data/opportunities_database.json"
    )
    
    skill_matcher = SkillMatcher(data_loader.skills_data)
    opportunities_data = data_loader.opportunities_data
    
    # Load sample profile
    with open("profiles/john_developer.json", "r") as f:
        profile_data = json.load(f)
    
    user_profile = UserProfile(**profile_data)
    
    print(f"\n👤 User Profile: {user_profile.name}")
    print(f"📍 Location: {user_profile.location}")
    print(f"💼 Experience: {user_profile.get_total_experience_years()} years")
    print(f"🎯 Skills: {len(user_profile.skills)} skills across {len(set(s.category for s in user_profile.skills))} categories")
    
    # Show skill portfolio
    portfolio_scores = skill_matcher.calculate_skill_portfolio_score(user_profile)
    print(f"\n📊 Skill Portfolio Strengths:")
    for category, score in sorted(portfolio_scores.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            # Get category name from skills data
            category_info = data_loader.skills_data.get('categories', {}).get(category, {})
            category_name = category_info.get('category_name', category.replace('_', ' ').title())
            print(f"   {category_name}: {score:.1%}")
    
    # Load opportunities
    from skillmatch.models import OpportunityDatabase
    opportunities_db = OpportunityDatabase(**opportunities_data)
    
    print(f"\n🔍 Available Opportunities: {len(opportunities_db.opportunities)}")
    
    # Calculate matches for top opportunities
    print(f"\n🎯 Top Matches:")
    matches = []
    
    for opportunity in opportunities_db.opportunities:
        match_score = skill_matcher.calculate_match_score(user_profile, opportunity)
        matches.append((opportunity, match_score))
    
    # Sort by overall score
    matches.sort(key=lambda x: x[1].overall_score, reverse=True)
    
    for i, (opportunity, match_score) in enumerate(matches[:3], 1):
        print(f"\n{i}. {opportunity.title}")
        print(f"   Company: {opportunity.company.name if opportunity.company else 'N/A'}")
        print(f"   Type: {opportunity.opportunity_type.value.title()}")
        print(f"   Match Score: {match_score.overall_score:.1%}")
        print(f"   Skills: {match_score.skill_match_score:.1%} | Experience: {match_score.experience_score:.1%} | Preferences: {match_score.preference_score:.1%}")
        
        if match_score.strengths:
            print(f"   ✅ Strengths: {', '.join(match_score.strengths[:2])}")
        
        if match_score.skill_gaps:
            gaps = [f"{gap.skill_name} ({gap.required_level.value})" for gap in match_score.skill_gaps[:2]]
            print(f"   📚 Skills to develop: {', '.join(gaps)}")
    
    print(f"\n💡 Analysis Complete!")
    print(f"   • Found {len([m for m in matches if m[1].overall_score > 0.7])} high-quality matches (>70%)")
    print(f"   • Found {len([m for m in matches if m[1].overall_score > 0.5])} good matches (>50%)")
    
    # Show skill gaps across all opportunities
    all_gaps = {}
    for opportunity, match_score in matches:
        for gap in match_score.skill_gaps:
            if gap.skill_id not in all_gaps or gap.importance > all_gaps[gap.skill_id].importance:
                all_gaps[gap.skill_id] = gap
    
    top_gaps = sorted(all_gaps.values(), key=lambda g: g.importance, reverse=True)[:5]
    if top_gaps:
        print(f"\n📈 Top Skills to Develop:")
        for gap in top_gaps:
            print(f"   • {gap.skill_name}: {gap.current_level.value if gap.current_level else 'None'} → {gap.required_level.value} (Priority: {gap.importance:.1%})")


async def demo_with_ai():
    """Demo with AI agent - requires GitHub token"""
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("❌ GitHub token not found. Set GITHUB_TOKEN environment variable to try AI features.")
        return
    
    print("\n🤖 SkillMatch.AI Agent Demo")
    print("=" * 50)
    
    try:
        # Initialize agent
        agent = SkillMatchAgent(
            github_token=github_token,
            model_id="openai/gpt-4.1-mini"
        )
        await agent.initialize()
        
        # Load sample profile
        with open("profiles/john_developer.json", "r") as f:
            profile_data = json.load(f)
        
        profile_json = json.dumps(profile_data, default=str)
        
        print("🔍 Finding matches with AI analysis...")
        
        # Find matches
        matches_result = await agent.find_matching_opportunities(
            user_profile_json=profile_json,
            max_results=3
        )
        
        matches_data = json.loads(matches_result)
        if matches_data['status'] == 'success':
            print(f"✅ Found {matches_data['total_matches']} matches")
            
            # Show top match with AI explanation
            if matches_data['matches']:
                top_match = matches_data['matches'][0]
                print(f"\n🏆 Top AI-Recommended Match:")
                print(f"   {top_match['title']} at {top_match['company']}")
                print(f"   Overall Score: {top_match['match_score']:.1%}")
                print(f"   💬 AI Explanation: {top_match['explanation']}")
        
        # Demonstrate chat capability
        print("\n💬 AI Career Advisor Chat:")
        chat_questions = [
            "What are my strongest skills?",
            "What skills should I focus on developing next?",
            "How can I improve my chances for senior data scientist roles?"
        ]
        
        for question in chat_questions:
            print(f"\n❓ {question}")
            response = await agent.chat(question, context={"user_profile": profile_data})
            print(f"🤖 {response[:200]}..." if len(response) > 200 else f"🤖 {response}")
        
        await agent.close()
        
    except Exception as e:
        print(f"❌ AI Demo error: {e}")


async def main():
    """Run the demo"""
    print("🎯 Welcome to SkillMatch.AI Demo!")
    print("This demonstrates the intelligent career matching system")
    print()
    
    # Always run core demo
    await demo_without_ai()
    
    # Try AI demo if token available
    await demo_with_ai()
    
    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print("\nTo try SkillMatch.AI yourself:")
    print("1. Get a GitHub token: https://github.com/settings/tokens")
    print("2. Set environment variable: export GITHUB_TOKEN='your_token'")
    print("3. Run: python skillmatch.py setup")
    print("4. Try: python skillmatch.py match --profile profiles/john_developer.json")
    print("\nFor more info, see README.md")


if __name__ == "__main__":
    asyncio.run(main())