"""
Skill matching algorithms and utilities for SkillMatch.AI
"""
import math
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from ..models import (
    UserProfile,
    Opportunity,
    MatchScore,
    SkillGap,
    SkillItem,
    RequiredSkill,
    ExperienceLevel,
    PreferenceType
)


class SkillMatcher:
    """
    Core skill matching engine for calculating compatibility between users and opportunities
    """
    
    def __init__(self, skills_data: Dict[str, Any]):
        """
        Initialize skill matcher with skills database
        
        Args:
            skills_data: Skills database containing categories, weights, and level values
        """
        self.skills_data = skills_data
        self.skill_categories = skills_data.get("skill_categories", {})
        self.skill_weights = skills_data.get("skill_weights", {})
        self.level_values = skills_data.get("level_values", {})
        
        # Build skill lookup for fast access
        self._build_skill_lookup()
    
    def _build_skill_lookup(self) -> None:
        """Build internal lookup tables for skills"""
        self.skill_lookup = {}
        self.category_lookup = {}
        
        for category_id, category_data in self.skill_categories.items():
            for skill_id, skill_info in category_data.get("skills", {}).items():
                self.skill_lookup[skill_id] = {
                    **skill_info,
                    "category": category_id,
                    "skill_id": skill_id
                }
                self.category_lookup[skill_id] = category_id
    
    def calculate_match_score(self, user_profile: UserProfile, opportunity: Opportunity) -> MatchScore:
        """
        Calculate comprehensive match score between user and opportunity
        
        Args:
            user_profile: User's profile with skills and preferences
            opportunity: Job/project/learning opportunity
            
        Returns:
            MatchScore with detailed scoring breakdown
        """
        # Calculate individual score components
        skill_match_score = self._calculate_skill_match_score(user_profile, opportunity)
        experience_score = self._calculate_experience_score(user_profile, opportunity)
        preference_score = self._calculate_preference_score(user_profile, opportunity)
        
        # Extract skill gaps and strengths
        skill_gaps = self._identify_skill_gaps(user_profile, opportunity)
        strengths = self._identify_strengths(user_profile, opportunity)
        
        # Calculate overall score with weights
        overall_score = (
            skill_match_score * 0.5 +
            experience_score * 0.3 +
            preference_score * 0.2
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            overall_score, skill_match_score, experience_score, preference_score, skill_gaps
        )
        
        return MatchScore(
            overall_score=min(overall_score, 1.0),
            skill_match_score=skill_match_score,
            experience_score=experience_score,
            preference_score=preference_score,
            skill_gaps=skill_gaps,
            strengths=strengths,
            explanation=explanation
        )
    
    def _calculate_skill_match_score(self, user_profile: UserProfile, opportunity: Opportunity) -> float:
        """Calculate how well user's skills match opportunity requirements"""
        if not opportunity.get_all_skills():
            return 1.0  # No skill requirements
        
        user_skills_dict = {skill.skill_id: skill for skill in user_profile.skills}
        total_weight = 0.0
        matched_weight = 0.0
        
        # Check each required skill
        for required_skill in opportunity.get_all_skills():
            skill_weight = required_skill.importance
            total_weight += skill_weight
            
            if required_skill.skill_id in user_skills_dict:
                user_skill = user_skills_dict[required_skill.skill_id]
                
                # Calculate skill level match
                user_level_value = self.level_values.get(user_skill.level.value, 1)
                required_level_value = self.level_values.get(required_skill.required_level.value, 1)
                
                # Score based on how user's level compares to required level
                if user_level_value >= required_level_value:
                    level_match = 1.0  # Meets or exceeds requirement
                else:
                    level_match = user_level_value / required_level_value  # Partial match
                
                # Consider experience years if available
                experience_bonus = 0.0
                if user_skill.years_experience and user_skill.years_experience > 0:
                    # Bonus for experience, capped at 0.2
                    experience_bonus = min(user_skill.years_experience * 0.05, 0.2)
                
                skill_match = min(level_match + experience_bonus, 1.0)
                matched_weight += skill_weight * skill_match
            else:
                # Check for related skills
                related_match = self._check_related_skills(required_skill.skill_id, user_skills_dict)
                matched_weight += skill_weight * related_match
        
        return matched_weight / total_weight if total_weight > 0 else 0.0
    
    def _calculate_experience_score(self, user_profile: UserProfile, opportunity: Opportunity) -> float:
        """Calculate experience level compatibility"""
        user_experience = user_profile.get_total_experience_years()
        required_experience = opportunity.min_experience_years or 0
        
        if required_experience == 0:
            return 1.0  # No experience requirement
        
        if user_experience >= required_experience:
            # Bonus for having more experience, but with diminishing returns
            excess_exp = user_experience - required_experience
            bonus = min(excess_exp * 0.1, 0.3)  # Max 30% bonus
            return min(1.0 + bonus, 1.0)
        else:
            # Penalty for having less experience
            return user_experience / required_experience
    
    def _calculate_preference_score(self, user_profile: UserProfile, opportunity: Opportunity) -> float:
        """Calculate how well opportunity matches user preferences"""
        score_components = []
        
        # Work type preference
        if user_profile.preferences.work_type and opportunity.work_type:
            work_type_match = any(
                pref in opportunity.work_type 
                for pref in user_profile.preferences.work_type
            )
            score_components.append(1.0 if work_type_match else 0.3)
        
        # Location preference
        if user_profile.preferences.locations and opportunity.location:
            location_match = any(
                loc.lower() in opportunity.location.lower()
                for loc in user_profile.preferences.locations
            )
            score_components.append(1.0 if location_match else 0.5)
        
        # Salary preference (for jobs)
        if (user_profile.preferences.salary_min and 
            opportunity.salary_info and 
            opportunity.salary_info.max_salary):
            
            if opportunity.salary_info.max_salary >= user_profile.preferences.salary_min:
                score_components.append(1.0)
            else:
                # Partial score based on how close it is
                ratio = opportunity.salary_info.max_salary / user_profile.preferences.salary_min
                score_components.append(max(ratio, 0.2))
        
        # Industry/company preference
        if (user_profile.preferences.industries and 
            opportunity.company and 
            opportunity.company.industry):
            
            industry_match = any(
                industry.lower() in opportunity.company.industry.lower()
                for industry in user_profile.preferences.industries
            )
            score_components.append(1.0 if industry_match else 0.4)
        
        # Return average if we have components, otherwise neutral score
        return sum(score_components) / len(score_components) if score_components else 0.7
    
    def _identify_skill_gaps(self, user_profile: UserProfile, opportunity: Opportunity) -> List[SkillGap]:
        """Identify skills that user lacks or needs to improve"""
        user_skills_dict = {skill.skill_id: skill for skill in user_profile.skills}
        skill_gaps = []
        
        for required_skill in opportunity.get_all_skills():
            current_level = None
            
            if required_skill.skill_id in user_skills_dict:
                user_skill = user_skills_dict[required_skill.skill_id]
                current_level = user_skill.level
                
                # Check if user's level is sufficient
                user_level_value = self.level_values.get(user_skill.level.value, 1)
                required_level_value = self.level_values.get(required_skill.required_level.value, 1)
                
                if user_level_value >= required_level_value:
                    continue  # No gap for this skill
            
            # Create skill gap
            skill_info = self.skill_lookup.get(required_skill.skill_id, {})
            gap = SkillGap(
                skill_id=required_skill.skill_id,
                skill_name=required_skill.skill_name,
                category=required_skill.category,
                current_level=current_level,
                required_level=required_skill.required_level,
                importance=required_skill.importance,
                learning_resources=[]  # Could be populated with actual resources
            )
            skill_gaps.append(gap)
        
        # Sort by importance
        skill_gaps.sort(key=lambda gap: gap.importance, reverse=True)
        return skill_gaps
    
    def _identify_strengths(self, user_profile: UserProfile, opportunity: Opportunity) -> List[str]:
        """Identify areas where user strongly matches opportunity"""
        user_skills_dict = {skill.skill_id: skill for skill in user_profile.skills}
        strengths = []
        
        for required_skill in opportunity.get_all_skills():
            if required_skill.skill_id in user_skills_dict:
                user_skill = user_skills_dict[required_skill.skill_id]
                
                # Check if user exceeds requirements
                user_level_value = self.level_values.get(user_skill.level.value, 1)
                required_level_value = self.level_values.get(required_skill.required_level.value, 1)
                
                if user_level_value > required_level_value:
                    strengths.append(user_skill.skill_name)
                elif user_level_value == required_level_value and user_skill.years_experience and user_skill.years_experience > 2:
                    strengths.append(f"{user_skill.skill_name} (experienced)")
        
        # Also identify strong categories
        category_strengths = defaultdict(int)
        for skill in user_profile.skills:
            if skill.level in [ExperienceLevel.ADVANCED, ExperienceLevel.EXPERT, ExperienceLevel.PROFICIENT]:
                category_strengths[skill.category] += 1
        
        # Add category strengths if user has 3+ advanced skills in a category
        for category, count in category_strengths.items():
            if count >= 3:
                category_info = self.skill_categories.get(category, {})
                category_name = category_info.get("category_name", category)
                strengths.append(f"Strong in {category_name}")
        
        return list(set(strengths))  # Remove duplicates
    
    def _check_related_skills(self, required_skill_id: str, user_skills_dict: Dict[str, SkillItem]) -> float:
        """Check if user has related skills that partially satisfy requirement"""
        skill_info = self.skill_lookup.get(required_skill_id, {})
        related_skills = skill_info.get("related_skills", [])
        
        best_match = 0.0
        for related_skill_id in related_skills:
            if related_skill_id in user_skills_dict:
                user_skill = user_skills_dict[related_skill_id]
                user_level_value = self.level_values.get(user_skill.level.value, 1)
                
                # Related skills provide partial match (max 60% of full match)
                related_match = min(user_level_value / 4.0, 0.6)
                best_match = max(best_match, related_match)
        
        return best_match
    
    def _generate_explanation(
        self,
        overall_score: float,
        skill_score: float,
        experience_score: float,
        preference_score: float,
        skill_gaps: List[SkillGap]
    ) -> str:
        """Generate human-readable explanation of the match"""
        explanation_parts = []
        
        # Overall assessment
        if overall_score >= 0.8:
            explanation_parts.append("This is an excellent match for your profile.")
        elif overall_score >= 0.6:
            explanation_parts.append("This is a good match with some areas for growth.")
        elif overall_score >= 0.4:
            explanation_parts.append("This opportunity could be challenging but offers learning potential.")
        else:
            explanation_parts.append("This may be a stretch opportunity requiring significant skill development.")
        
        # Skill match details
        if skill_score >= 0.8:
            explanation_parts.append("Your skills align very well with the requirements.")
        elif skill_score >= 0.6:
            explanation_parts.append("You have most of the required skills.")
        elif skill_score >= 0.4:
            explanation_parts.append("You have some relevant skills but would need to develop others.")
        else:
            explanation_parts.append("Significant skill development would be needed.")
        
        # Experience assessment
        if experience_score >= 1.0:
            explanation_parts.append("Your experience level meets or exceeds requirements.")
        elif experience_score >= 0.7:
            explanation_parts.append("Your experience is close to what's required.")
        else:
            explanation_parts.append("You may need more experience for this role.")
        
        # Preference alignment
        if preference_score >= 0.8:
            explanation_parts.append("The opportunity aligns well with your preferences.")
        elif preference_score >= 0.6:
            explanation_parts.append("The opportunity partially matches your preferences.")
        
        # Skill gaps
        if skill_gaps:
            high_priority_gaps = [gap for gap in skill_gaps[:3] if gap.importance > 0.7]
            if high_priority_gaps:
                gap_names = [gap.skill_name for gap in high_priority_gaps]
                explanation_parts.append(f"Key skills to develop: {', '.join(gap_names)}.")
        
        return " ".join(explanation_parts)
    
    def find_similar_skills(self, skill_id: str, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Find skills similar to the given skill
        
        Args:
            skill_id: The skill to find similar skills for
            limit: Maximum number of similar skills to return
            
        Returns:
            List of tuples (skill_id, similarity_score)
        """
        skill_info = self.skill_lookup.get(skill_id)
        if not skill_info:
            return []
        
        similar_skills = []
        skill_category = skill_info["category"]
        related_skills = skill_info.get("related_skills", [])
        
        # Related skills have high similarity
        for related_skill_id in related_skills:
            if related_skill_id in self.skill_lookup:
                similar_skills.append((related_skill_id, 0.8))
        
        # Skills in same category have medium similarity
        category_skills = self.skill_categories.get(skill_category, {}).get("skills", {})
        for other_skill_id in category_skills.keys():
            if other_skill_id != skill_id and other_skill_id not in related_skills:
                similar_skills.append((other_skill_id, 0.6))
        
        # Sort by similarity and limit results
        similar_skills.sort(key=lambda x: x[1], reverse=True)
        return similar_skills[:limit]
    
    def calculate_skill_portfolio_score(self, user_profile: UserProfile) -> Dict[str, float]:
        """
        Calculate overall skill portfolio strength by category
        
        Args:
            user_profile: User's profile with skills
            
        Returns:
            Dictionary mapping category to strength score (0-1)
        """
        category_scores = {}
        
        for category_id, category_data in self.skill_categories.items():
            category_skills = user_profile.get_skills_by_category(category_id)
            
            if not category_skills:
                category_scores[category_id] = 0.0
                continue
            
            # Calculate average skill level in category
            total_score = 0.0
            max_possible_score = 0.0
            
            for skill in category_skills:
                skill_level_value = self.level_values.get(skill.level.value, 1)
                experience_bonus = min((skill.years_experience or 0) * 0.1, 0.5)
                skill_score = skill_level_value + experience_bonus
                
                total_score += skill_score
                max_possible_score += 4.5  # Max level (4) + max experience bonus (0.5)
            
            category_scores[category_id] = min(total_score / max_possible_score, 1.0)
        
        return category_scores