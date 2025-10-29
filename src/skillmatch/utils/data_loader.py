"""
Data loading utilities for SkillMatch.AI
"""
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class DataLoader:
    """
    Utility class for loading skills and opportunities data
    """
    
    def __init__(self, skills_db_path: str, opportunities_db_path: str):
        """
        Initialize data loader with file paths
        
        Args:
            skills_db_path: Path to skills database JSON file
            opportunities_db_path: Path to opportunities database JSON file
        """
        self.skills_db_path = Path(skills_db_path)
        self.opportunities_db_path = Path(opportunities_db_path)
        self._skills_data: Optional[Dict[str, Any]] = None
        self._opportunities_data: Optional[Dict[str, Any]] = None
    
    @property
    def skills_data(self) -> Dict[str, Any]:
        """Get skills data, loading if necessary"""
        if self._skills_data is None:
            self._skills_data = self.load_skills()
        return self._skills_data
    
    @property
    def opportunities_data(self) -> Dict[str, Any]:
        """Get opportunities data, loading if necessary"""
        if self._opportunities_data is None:
            self._opportunities_data = self.load_opportunities()
        return self._opportunities_data
    
    def load_skills(self) -> Dict[str, Any]:
        """
        Load skills database from JSON file
        
        Returns:
            Dictionary containing skills data
        """
        try:
            if not self.skills_db_path.exists():
                raise FileNotFoundError(f"Skills database not found: {self.skills_db_path}")
            
            with open(self.skills_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._skills_data = data
            return data
            
        except Exception as e:
            raise Exception(f"Error loading skills database: {str(e)}")
    
    def load_opportunities(self) -> Dict[str, Any]:
        """
        Load opportunities database from JSON file
        
        Returns:
            Dictionary containing opportunities data
        """
        try:
            if not self.opportunities_db_path.exists():
                raise FileNotFoundError(f"Opportunities database not found: {self.opportunities_db_path}")
            
            with open(self.opportunities_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._opportunities_data = data
            return data
            
        except Exception as e:
            raise Exception(f"Error loading opportunities database: {str(e)}")
    
    def get_skill_by_id(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """
        Get skill information by skill ID
        
        Args:
            skill_id: The skill identifier
            
        Returns:
            Skill information dictionary or None if not found
        """
        skills_data = self.skills_data
        
        # Search through all categories
        for category_id, category_data in skills_data.get("skill_categories", {}).items():
            if "skills" in category_data:
                if skill_id in category_data["skills"]:
                    skill_info = category_data["skills"][skill_id].copy()
                    skill_info["category"] = category_id
                    skill_info["skill_id"] = skill_id
                    return skill_info
        
        return None
    
    def get_skills_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all skills in a specific category
        
        Args:
            category: Category identifier
            
        Returns:
            Dictionary of skills in the category
        """
        skills_data = self.skills_data
        category_data = skills_data.get("skill_categories", {}).get(category, {})
        return category_data.get("skills", {})
    
    def get_all_skills(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all skills from all categories
        
        Returns:
            Dictionary mapping skill_id to skill information
        """
        all_skills = {}
        skills_data = self.skills_data
        
        for category_id, category_data in skills_data.get("skill_categories", {}).items():
            if "skills" in category_data:
                for skill_id, skill_info in category_data["skills"].items():
                    skill_copy = skill_info.copy()
                    skill_copy["category"] = category_id
                    skill_copy["skill_id"] = skill_id
                    all_skills[skill_id] = skill_copy
        
        return all_skills
    
    def get_related_skills(self, skill_id: str) -> List[str]:
        """
        Get skills related to the given skill
        
        Args:
            skill_id: The skill identifier
            
        Returns:
            List of related skill IDs
        """
        skill_info = self.get_skill_by_id(skill_id)
        if skill_info:
            return skill_info.get("related_skills", [])
        return []
    
    def get_category_weight(self, category: str) -> float:
        """
        Get the weight for a skill category
        
        Args:
            category: Category identifier
            
        Returns:
            Category weight (default 1.0 if not found)
        """
        skills_data = self.skills_data
        return skills_data.get("skill_weights", {}).get(category, 1.0)
    
    def get_level_value(self, level: str) -> int:
        """
        Get numeric value for a skill level
        
        Args:
            level: Level string (e.g., "beginner", "advanced")
            
        Returns:
            Numeric level value (default 1 if not found)
        """
        skills_data = self.skills_data
        return skills_data.get("level_values", {}).get(level, 1)
    
    def search_skills(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for skills by name or description
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching skills
        """
        query_lower = query.lower()
        results = []
        
        all_skills = self.get_all_skills()
        
        for skill_id, skill_info in all_skills.items():
            # Check if query matches skill name or description
            name_match = query_lower in skill_info.get("name", "").lower()
            desc_match = query_lower in skill_info.get("description", "").lower()
            
            if name_match or desc_match:
                results.append(skill_info)
        
        return results[:limit]
    
    def validate_skill_level(self, skill_id: str, level: str) -> bool:
        """
        Validate that a skill level is valid for a given skill
        
        Args:
            skill_id: The skill identifier
            level: The level to validate
            
        Returns:
            True if level is valid for the skill
        """
        skill_info = self.get_skill_by_id(skill_id)
        if skill_info:
            valid_levels = skill_info.get("levels", [])
            return level in valid_levels
        return False
    
    def reload_data(self) -> None:
        """Force reload of all data from files"""
        self._skills_data = None
        self._opportunities_data = None