"""
Core AI agent for skill matching using Microsoft Agent Framework
"""

import asyncio
import json
import os
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

from ..models import (
    UserProfile,
    Opportunity,
    MatchScore,
    SkillGap,
    ExperienceLevel,
    OpportunityDatabase,
)
from ..utils.skill_matcher import SkillMatcher
from ..utils.data_loader import DataLoader


class SkillMatchAgent:
    """
    AI agent for intelligent skill matching and career recommendations
    """

    def __init__(
        self,
        github_token: str,
        model_id: str = "openai/gpt-5-mini",
        skills_db_path: str = "data/skills_database.json",
        opportunities_db_path: str = "data/opportunities_database.json",
    ):
        """
        Initialize the SkillMatch AI agent

        Args:
            github_token: GitHub personal access token for model access
            model_id: Model ID to use for AI matching
            skills_db_path: Path to skills database JSON file
            opportunities_db_path: Path to opportunities database JSON file
        """
        self.github_token = github_token
        self.model_id = model_id
        self.skills_db_path = skills_db_path
        self.opportunities_db_path = opportunities_db_path

        # Initialize components
        self.data_loader = DataLoader(skills_db_path, opportunities_db_path)
        self.skill_matcher = SkillMatcher(self.data_loader.skills_data)
        self.opportunities_db: Optional[OpportunityDatabase] = None

        # AI components
        self.openai_client: Optional[AsyncOpenAI] = None
        self.chat_client: Optional[OpenAIChatClient] = None
        self.agent: Optional[ChatAgent] = None

        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the AI agent and load data"""
        if self._initialized:
            return

        # Load data
        await self._load_data()

        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(
            base_url="https://models.github.ai/inference",
            api_key=self.github_token,
        )

        # Create chat client
        self.chat_client = OpenAIChatClient(
            async_client=self.openai_client, model_id=self.model_id
        )

        # Create the agent with tools
        self.agent = ChatAgent(
            chat_client=self.chat_client,
            name="SkillMatchAI",
            instructions=self._get_agent_instructions(),
            tools=self._get_agent_tools(),
        )

        self._initialized = True

    async def _load_data(self) -> None:
        """Load skills and opportunities data"""
        # Load opportunities database
        opportunities_data = self.data_loader.load_opportunities()
        self.opportunities_db = OpportunityDatabase(**opportunities_data)

    def _get_agent_instructions(self) -> str:
        """Get the system instructions for the AI agent"""
        return """
        You are SkillMatchAI, an expert career advisor and skill matching agent. Your role is to:
        
        1. **Analyze user profiles** - Understand their skills, experience, and career goals
        2. **Match opportunities** - Find the best jobs, projects, and learning paths
        3. **Identify skill gaps** - Help users understand what skills they need to develop
        4. **Provide recommendations** - Give actionable advice for career growth
        5. **Explain matches** - Clearly explain why opportunities are good fits
        
        **Your expertise includes:**
        - Programming languages and frameworks
        - Data science and machine learning
        - Web development technologies
        - Cloud and DevOps tools
        - Database technologies
        - Soft skills and professional development
        
        **Communication style:**
        - Be encouraging and supportive
        - Provide specific, actionable advice
        - Explain technical concepts clearly
        - Focus on growth opportunities
        - Consider both current skills and career aspirations
        
        **When matching opportunities:**
        - Consider skill level compatibility
        - Account for years of experience
        - Factor in user preferences (location, work type, salary)
        - Identify learning opportunities for skill gaps
        - Highlight transferable skills
        
        Use the available tools to analyze user profiles, calculate match scores, and find relevant opportunities.
        """

    def _get_agent_tools(self) -> List:
        """Get the tools available to the agent"""
        return [
            self.find_matching_opportunities,
            self.calculate_match_score,
            self.identify_skill_gaps,
            self.get_skill_recommendations,
            self.analyze_user_strengths,
            self.search_learning_opportunities,
        ]

    async def find_matching_opportunities(
        self,
        user_profile_json: str,
        opportunity_types: str = "job,project,learning",
        max_results: int = 10,
    ) -> str:
        """
        Find opportunities that match a user's profile

        Args:
            user_profile_json: JSON string of user profile
            opportunity_types: Comma-separated types to search (job,project,learning,internship)
            max_results: Maximum number of results to return
        """
        try:
            # Parse user profile
            profile_data = json.loads(user_profile_json)
            user_profile = UserProfile(**profile_data)

            # Get requested opportunity types
            types = [t.strip() for t in opportunity_types.split(",")]

            # Find matching opportunities
            matches = []
            for opportunity in self.opportunities_db.get_active_opportunities():
                if opportunity.opportunity_type.value in types:
                    match_score = self.skill_matcher.calculate_match_score(
                        user_profile, opportunity
                    )
                    matches.append(
                        {"opportunity": opportunity, "match_score": match_score}
                    )

            # Sort by match score and limit results
            matches.sort(key=lambda x: x["match_score"].overall_score, reverse=True)
            matches = matches[:max_results]

            # Format results
            results = []
            for match in matches:
                opp = match["opportunity"]
                score = match["match_score"]

                results.append(
                    {
                        "opportunity_id": opp.opportunity_id,
                        "title": opp.title,
                        "type": opp.opportunity_type.value,
                        "company": opp.company.name if opp.company else "N/A",
                        "location": opp.location or "Not specified",
                        "match_score": round(score.overall_score, 3),
                        "skill_match": round(score.skill_match_score, 3),
                        "experience_match": round(score.experience_score, 3),
                        "preference_match": round(score.preference_score, 3),
                        "explanation": score.explanation,
                        "strengths": score.strengths,
                        "skill_gaps": [
                            {
                                "skill": gap.skill_name,
                                "current": gap.current_level.value
                                if gap.current_level
                                else "None",
                                "required": gap.required_level.value,
                                "importance": gap.importance,
                            }
                            for gap in score.skill_gaps
                        ],
                    }
                )

            return json.dumps(
                {
                    "status": "success",
                    "total_matches": len(results),
                    "matches": results,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {"status": "error", "message": f"Error finding matches: {str(e)}"}
            )

    async def calculate_match_score(
        self, user_profile_json: str, opportunity_id: str
    ) -> str:
        """
        Calculate detailed match score for a specific opportunity

        Args:
            user_profile_json: JSON string of user profile
            opportunity_id: ID of the opportunity to match against
        """
        try:
            # Parse user profile
            profile_data = json.loads(user_profile_json)
            user_profile = UserProfile(**profile_data)

            # Find opportunity
            opportunity = self.opportunities_db.get_opportunity_by_id(opportunity_id)
            if not opportunity:
                return json.dumps(
                    {
                        "status": "error",
                        "message": f"Opportunity {opportunity_id} not found",
                    }
                )

            # Calculate match score
            match_score = self.skill_matcher.calculate_match_score(
                user_profile, opportunity
            )

            return json.dumps(
                {
                    "status": "success",
                    "opportunity_title": opportunity.title,
                    "overall_score": round(match_score.overall_score, 3),
                    "skill_match_score": round(match_score.skill_match_score, 3),
                    "experience_score": round(match_score.experience_score, 3),
                    "preference_score": round(match_score.preference_score, 3),
                    "explanation": match_score.explanation,
                    "strenghts": match_score.strengths,
                    "skill_gaps": [
                        {
                            "skill": gap.skill_name,
                            "category": gap.category,
                            "current_level": gap.current_level.value
                            if gap.current_level
                            else "None",
                            "required_level": gap.required_level.value,
                            "importance": gap.importance,
                        }
                        for gap in match_score.skill_gaps
                    ],
                    "recommendations": self._generate_recommendations(match_score),
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"Error calculating match score: {str(e)}",
                }
            )

    async def identify_skill_gaps(
        self, user_profile_json: str, target_role: str = ""
    ) -> str:
        """
        Identify skill gaps for career advancement

        Args:
            user_profile_json: JSON string of user profile
            target_role: Optional target role to analyze gaps for
        """
        try:
            profile_data = json.loads(user_profile_json)
            user_profile = UserProfile(**profile_data)

            if target_role:
                # Find opportunities matching the target role
                relevant_opportunities = []
                for opp in self.opportunities_db.get_active_opportunities():
                    if (
                        target_role.lower() in opp.title.lower()
                        or target_role.lower() in opp.description.lower()
                    ):
                        relevant_opportunities.append(opp)
            else:
                # Use all active opportunities
                relevant_opportunities = (
                    self.opportunities_db.get_active_opportunities()
                )

            # Collect skill gaps across opportunities
            all_gaps = {}
            for opp in relevant_opportunities[:10]:  # Limit to top 10 for analysis
                match_score = self.skill_matcher.calculate_match_score(
                    user_profile, opp
                )
                for gap in match_score.skill_gaps:
                    if gap.skill_id not in all_gaps:
                        all_gaps[gap.skill_id] = gap
                    else:
                        # Keep the highest importance
                        if gap.importance > all_gaps[gap.skill_id].importance:
                            all_gaps[gap.skill_id] = gap

            # Sort by importance
            sorted_gaps = sorted(
                all_gaps.values(), key=lambda g: g.importance, reverse=True
            )

            return json.dumps(
                {
                    "status": "success",
                    "target_role": target_role or "General career advancement",
                    "total_gaps": len(sorted_gaps),
                    "skill_gaps": [
                        {
                            "skill": gap.skill_name,
                            "category": gap.category,
                            "current_level": gap.current_level.value
                            if gap.current_level
                            else "None",
                            "required_level": gap.required_level.value,
                            "importance": gap.importance,
                            "priority": "High"
                            if gap.importance > 0.7
                            else "Medium"
                            if gap.importance > 0.4
                            else "Low",
                        }
                        for gap in sorted_gaps[:10]  # Top 10 gaps
                    ],
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"Error identifying skill gaps: {str(e)}",
                }
            )

    async def get_skill_recommendations(self, skill_gaps_json: str) -> str:
        """
        Get learning recommendations for skill gaps

        Args:
            skill_gaps_json: JSON string of skill gaps to address
        """
        try:
            gaps_data = json.loads(skill_gaps_json)

            recommendations = []
            for gap in gaps_data.get("skill_gaps", []):
                skill_name = gap["skill"]
                current_level = gap.get("current_level", "None")
                required_level = gap["required_level"]

                # Find relevant learning opportunities
                learning_opps = []
                for opp in self.opportunities_db.get_opportunities_by_type("learning"):
                    for skill in opp.get_all_skills():
                        if skill.skill_name.lower() == skill_name.lower():
                            learning_opps.append(opp)

                recommendations.append(
                    {
                        "skill": skill_name,
                        "current_level": current_level,
                        "target_level": required_level,
                        "learning_opportunities": [
                            {
                                "title": opp.title,
                                "provider": opp.learning_info.provider
                                if opp.learning_info
                                else "N/A",
                                "duration": opp.learning_info.duration
                                if opp.learning_info
                                else opp.duration,
                                "cost": opp.learning_info.cost
                                if opp.learning_info
                                else 0,
                                "certification": opp.learning_info.certification
                                if opp.learning_info
                                else False,
                            }
                            for opp in learning_opps[:3]  # Top 3 learning opportunities
                        ],
                        "general_advice": self._get_skill_learning_advice(
                            skill_name, current_level, required_level
                        ),
                    }
                )

            return json.dumps(
                {"status": "success", "recommendations": recommendations}, indent=2
            )

        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"Error getting recommendations: {str(e)}",
                }
            )

    async def analyze_user_strengths(self, user_profile_json: str) -> str:
        """
        Analyze user's strongest skills and areas of expertise

        Args:
            user_profile_json: JSON string of user profile
        """
        try:
            profile_data = json.loads(user_profile_json)
            user_profile = UserProfile(**profile_data)

            # Categorize skills by level and experience
            strengths = {}
            for skill in user_profile.skills:
                category = skill.category
                if category not in strengths:
                    strengths[category] = {
                        "expert": [],
                        "advanced": [],
                        "total_skills": 0,
                        "avg_experience": 0,
                    }

                strengths[category]["total_skills"] += 1
                if skill.years_experience:
                    strengths[category]["avg_experience"] += skill.years_experience

                if skill.level in [ExperienceLevel.EXPERT, ExperienceLevel.PROFICIENT]:
                    strengths[category]["expert"].append(
                        {
                            "skill": skill.skill_name,
                            "level": skill.level.value,
                            "experience": skill.years_experience or 0,
                        }
                    )
                elif skill.level == ExperienceLevel.ADVANCED:
                    strengths[category]["advanced"].append(
                        {
                            "skill": skill.skill_name,
                            "level": skill.level.value,
                            "experience": skill.years_experience or 0,
                        }
                    )

            # Calculate average experience per category
            for category in strengths:
                if strengths[category]["total_skills"] > 0:
                    strengths[category]["avg_experience"] = round(
                        strengths[category]["avg_experience"]
                        / strengths[category]["total_skills"],
                        1,
                    )

            # Identify top categories
            top_categories = sorted(
                strengths.items(),
                key=lambda x: len(x[1]["expert"]) + len(x[1]["advanced"]) * 0.7,
                reverse=True,
            )

            return json.dumps(
                {
                    "status": "success",
                    "total_experience_years": user_profile.get_total_experience_years(),
                    "strength_categories": dict(top_categories),
                    "top_skills": self._get_top_skills(user_profile),
                    "career_highlights": self._extract_career_highlights(user_profile),
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {"status": "error", "message": f"Error analyzing strengths: {str(e)}"}
            )

    async def search_learning_opportunities(
        self,
        skills_to_learn: str,
        difficulty_level: str = "any",
        max_cost: float = 1000.0,
    ) -> str:
        """
        Search for learning opportunities for specific skills

        Args:
            skills_to_learn: Comma-separated list of skills to learn
            difficulty_level: Preferred difficulty (beginner, intermediate, advanced, any)
            max_cost: Maximum cost for courses
        """
        try:
            skills_list = [s.strip().lower() for s in skills_to_learn.split(",")]

            learning_opps = []
            for opp in self.opportunities_db.get_opportunities_by_type("learning"):
                # Check if opportunity teaches any of the requested skills
                teaches_skill = False
                for req_skill in opp.get_all_skills():
                    if any(
                        skill in req_skill.skill_name.lower() for skill in skills_list
                    ):
                        teaches_skill = True
                        break

                if not teaches_skill:
                    continue

                # Check cost constraint
                if (
                    opp.learning_info
                    and opp.learning_info.cost
                    and opp.learning_info.cost > max_cost
                ):
                    continue

                # Check difficulty level
                if difficulty_level != "any" and opp.learning_info:
                    if (
                        difficulty_level.lower()
                        not in opp.learning_info.difficulty.lower()
                    ):
                        continue

                learning_opps.append(
                    {
                        "title": opp.title,
                        "provider": opp.learning_info.provider
                        if opp.learning_info
                        else "N/A",
                        "description": opp.description,
                        "duration": opp.learning_info.duration
                        if opp.learning_info
                        else opp.duration,
                        "difficulty": opp.learning_info.difficulty
                        if opp.learning_info
                        else "Not specified",
                        "cost": opp.learning_info.cost if opp.learning_info else 0,
                        "certification": opp.learning_info.certification
                        if opp.learning_info
                        else False,
                        "skills_taught": [
                            skill.skill_name for skill in opp.get_all_skills()
                        ],
                        "prerequisites": opp.learning_info.prerequisites
                        if opp.learning_info
                        else [],
                    }
                )

            return json.dumps(
                {
                    "status": "success",
                    "requested_skills": skills_list,
                    "total_opportunities": len(learning_opps),
                    "learning_opportunities": learning_opps,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"Error searching learning opportunities: {str(e)}",
                }
            )

    def _generate_recommendations(self, match_score: MatchScore) -> List[str]:
        """Generate actionable recommendations based on match score"""
        recommendations = []

        if match_score.overall_score >= 0.8:
            recommendations.append(
                "This is an excellent match! Consider applying immediately."
            )
        elif match_score.overall_score >= 0.6:
            recommendations.append(
                "This is a good match with some areas for improvement."
            )
        else:
            recommendations.append(
                "This opportunity might be challenging but could offer good growth."
            )

        if match_score.skill_gaps:
            high_priority_gaps = [
                gap for gap in match_score.skill_gaps if gap.importance > 0.7
            ]
            if high_priority_gaps:
                skills_list = ", ".join(
                    [gap.skill_name for gap in high_priority_gaps[:3]]
                )
                recommendations.append(f"Focus on developing: {skills_list}")

        if match_score.strengths:
            recommendations.append(
                f"Highlight your strengths in: {', '.join(match_score.strengths[:3])}"
            )

        return recommendations

    def _get_skill_learning_advice(
        self, skill_name: str, current_level: str, target_level: str
    ) -> str:
        """Get general advice for learning a specific skill"""
        advice_map = {
            "python": "Practice with real projects, contribute to open source, take online courses",
            "javascript": "Build web applications, learn modern frameworks, practice algorithms",
            "machine-learning": "Complete online courses, work with datasets, build ML projects",
            "react": "Build several React applications, learn hooks and state management",
            "sql": "Practice with real databases, learn query optimization, understand database design",
        }

        return advice_map.get(
            skill_name.lower(),
            f"Find online courses, practice through projects, join communities focused on {skill_name}",
        )

    def _get_top_skills(self, user_profile: UserProfile) -> List[Dict]:
        """Get user's top skills ranked by level and experience"""
        scored_skills = []

        for skill in user_profile.skills:
            # Score based on level and experience
            level_score = {
                ExperienceLevel.EXPERT: 4,
                ExperienceLevel.PROFICIENT: 3.5,
                ExperienceLevel.ADVANCED: 3,
                ExperienceLevel.COMPETENT: 2.5,
                ExperienceLevel.INTERMEDIATE: 2,
                ExperienceLevel.DEVELOPING: 1.5,
                ExperienceLevel.BEGINNER: 1,
            }.get(skill.level, 1)

            experience_score = min((skill.years_experience or 0) * 0.2, 2.0)
            total_score = level_score + experience_score

            scored_skills.append(
                {
                    "skill": skill.skill_name,
                    "category": skill.category,
                    "level": skill.level.value,
                    "experience": skill.years_experience or 0,
                    "score": total_score,
                }
            )

        # Return top 10 skills
        return sorted(scored_skills, key=lambda x: x["score"], reverse=True)[:10]

    def _extract_career_highlights(self, user_profile: UserProfile) -> List[str]:
        """Extract key career highlights from user profile"""
        highlights = []

        # Total experience
        total_exp = user_profile.get_total_experience_years()
        if total_exp > 0:
            highlights.append(f"{total_exp} years of professional experience")

        # Education highlights
        if user_profile.education:
            for edu in user_profile.education:
                if edu.degree:
                    highlights.append(f"{edu.degree} from {edu.institution}")

        # Top achievements from work experience
        for exp in user_profile.work_experience:
            if exp.achievements:
                highlights.extend(exp.achievements[:2])  # Top 2 achievements per role

        return highlights[:5]  # Top 5 highlights

    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Chat with the SkillMatch AI agent

        Args:
            message: User message
            context: Optional context (user profile, conversation history, etc.)
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Add context to message if provided
            if context:
                context_str = (
                    f"Context: {json.dumps(context, indent=2)}\n\nUser: {message}"
                )
            else:
                context_str = message

            # Get response from agent
            result = await self.agent.run(context_str)
            return result.text

        except Exception as e:
            return f"Error: {str(e)}"

    async def close(self) -> None:
        """Clean up resources"""
        if self.openai_client:
            await self.openai_client.close()
        self._initialized = False
