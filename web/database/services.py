"""
Database service layer for user profile operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import json

from .models import (
    UserProfile, UserSkill, Skill, WorkExperience, 
    Education, UserPreferences, CareerGoal
)

class ProfileService:
    """Service class for user profile database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Create a new user profile"""
        # Create user profile
        profile = UserProfile(
            user_id=profile_data.get('user_id') or profile_data.get('name', '').lower().replace(' ', '_'),
            name=profile_data.get('name'),
            email_address=profile_data.get('email'),
            title=profile_data.get('title'),
            location=profile_data.get('location'),
            bio=profile_data.get('bio'),
            goals=profile_data.get('goals'),
            summary=profile_data.get('summary'),
            experience_level=profile_data.get('experience_level'),
            resume_file=profile_data.get('resume_file')
        )
        
        self.db.add(profile)
        self.db.flush()  # Get the ID
        
        # Add skills
        if 'skills' in profile_data:
            self._add_user_skills(profile.user_id, profile_data['skills'])
        
        # Add work experience
        if 'work_experience' in profile_data:
            self._add_work_experience(profile.user_id, profile_data['work_experience'])
        
        # Add education
        if 'education' in profile_data:
            self._add_education(profile.user_id, profile_data['education'])
        
        # Add preferences
        if 'preferences' in profile_data:
            self._add_preferences(profile.user_id, profile_data['preferences'])
        
        # Add career goals
        if 'career_goals' in profile_data:
            self._add_career_goals(profile.user_id, profile_data['career_goals'])
        
        self.db.commit()
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def get_all_profiles(self) -> List[UserProfile]:
        """Get all active profiles"""
        return self.db.query(UserProfile).filter(UserProfile.is_active == True).all()
    
    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update existing profile"""
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        # Update basic fields
        for field in ['name', 'title', 'location', 'bio', 'goals', 'summary', 'experience_level']:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        
        # Handle email field mapping
        if 'email' in profile_data:
            profile.email_address = profile_data['email']
        
        profile.updated_at = datetime.utcnow()
        
        # Update related data (remove and re-add for simplicity)
        if 'skills' in profile_data:
            # Clear existing skills
            self.db.query(UserSkill).filter(UserSkill.user_id == user_id).delete()
            self._add_user_skills(user_id, profile_data['skills'])
        
        if 'work_experience' in profile_data:
            # Clear existing work experience
            self.db.query(WorkExperience).filter(WorkExperience.user_id == user_id).delete()
            self._add_work_experience(user_id, profile_data['work_experience'])
        
        if 'education' in profile_data:
            # Clear existing education
            self.db.query(Education).filter(Education.user_id == user_id).delete()
            self._add_education(user_id, profile_data['education'])
        
        if 'preferences' in profile_data:
            # Update preferences
            existing_prefs = self.db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            if existing_prefs:
                self.db.delete(existing_prefs)
                self.db.flush()  # Ensure delete is processed before insert
            self._add_preferences(user_id, profile_data['preferences'])
        
        if 'career_goals' in profile_data:
            # Clear existing career goals
            profile.career_goals.clear()
            self._add_career_goals(user_id, profile_data['career_goals'])
        
        self.db.commit()
        return profile
    
    def delete_profile(self, user_id: str) -> bool:
        """Soft delete profile"""
        profile = self.get_profile(user_id)
        if profile:
            profile.is_active = False
            profile.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def search_profiles(self, 
                       skills: Optional[List[str]] = None,
                       location: Optional[str] = None,
                       experience_level: Optional[str] = None,
                       limit: int = 50) -> List[UserProfile]:
        """Search profiles with filters"""
        query = self.db.query(UserProfile).filter(UserProfile.is_active == True)
        
        if location:
            query = query.filter(UserProfile.location.ilike(f"%{location}%"))
        
        if experience_level:
            query = query.filter(UserProfile.experience_level == experience_level)
        
        if skills:
            # Join with skills and filter
            skill_ids = self.db.query(Skill.id).filter(Skill.skill_name.in_(skills)).subquery()
            query = query.join(UserSkill).filter(UserSkill.skill_id.in_(skill_ids))
        
        return query.limit(limit).all()
    
    def profile_to_dict(self, profile: UserProfile) -> Dict[str, Any]:
        """Convert SQLAlchemy profile to dictionary (for JSON compatibility)"""
        result = {
            'user_id': profile.user_id,
            'name': profile.name,
            'email': profile.email_address,  # Map email_address to email
            'title': profile.title,
            'location': profile.location,
            'bio': profile.bio,
            'goals': profile.goals,  # Add the goals field
            'summary': profile.summary,
            'experience_level': profile.experience_level,
            'resume_file': profile.resume_file,
            'created_at': profile.created_at.isoformat() if profile.created_at else None,
            'updated_at': profile.updated_at.isoformat() if profile.updated_at else None,
            'is_active': profile.is_active,
            'skills': [],
            'work_experience': [],
            'education': [],
            'career_goals': [],
            'preferences': {}
        }
        
        # Add skills
        for user_skill in profile.skills:
            result['skills'].append({
                'skill_id': user_skill.skill.skill_id,
                'skill_name': user_skill.skill.skill_name,
                'category': user_skill.skill.category,
                'level': user_skill.level,
                'years_experience': user_skill.years_experience,
                'verified': user_skill.verified
            })
        
        # Add work experience
        for exp in profile.work_experience:
            result['work_experience'].append({
                'company': exp.company,
                'position': exp.position,
                'start_date': exp.start_date.isoformat() if exp.start_date else None,
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'years': exp.years,
                'description': exp.description,
                'employment_status': exp.employment_status,
                'key_skills': exp.key_skills,
                'achievements': exp.achievements
            })
        
        # Add education
        for edu in profile.education:
            result['education'].append({
                'institution': edu.institution,
                'degree': edu.degree,
                'field_of_study': edu.field_of_study,
                'start_date': edu.start_date.isoformat() if edu.start_date else None,
                'end_date': edu.end_date.isoformat() if edu.end_date else None,
                'graduation_year': edu.graduation_year,
                'gpa': edu.gpa,
                'relevant_coursework': edu.relevant_coursework
            })
        
        # Add career goals
        result['career_goals'] = [goal.goal_text for goal in profile.career_goals]
        
        # Add preferences
        if profile.preferences:
            result['preferences'] = {
                'work_types': profile.preferences.work_types,
                'work_type': profile.preferences.work_type,
                'desired_roles': profile.preferences.desired_roles,
                'salary_min': profile.preferences.salary_min,
                'salary_max': profile.preferences.salary_max,
                'locations': profile.preferences.locations,
                'industries': profile.preferences.industries,
                'company_size': profile.preferences.company_size,
                'remote_preference': profile.preferences.remote_preference,
                'growth_areas': profile.preferences.growth_areas,
                'availability': profile.preferences.availability
            }
        
        return result
    
    def _add_user_skills(self, user_id: str, skills_data: List[Dict]):
        """Add skills for a user"""
        for skill_data in skills_data:
            # Get or create skill
            skill = self.db.query(Skill).filter(Skill.skill_id == skill_data.get('skill_id')).first()
            if not skill:
                skill = Skill(
                    skill_id=skill_data.get('skill_id'),
                    skill_name=skill_data.get('skill_name'),
                    category=skill_data.get('category', 'other')
                )
                self.db.add(skill)
                self.db.flush()
            
            # Create user skill
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill.id,
                level=skill_data.get('level'),
                years_experience=skill_data.get('years_experience'),
                verified=skill_data.get('verified', False)
            )
            self.db.add(user_skill)
    
    def _add_work_experience(self, user_id: str, work_exp_data: List[Dict]):
        """Add work experience for a user"""
        for exp_data in work_exp_data:
            work_exp = WorkExperience(
                user_id=user_id,
                company=exp_data.get('company'),
                position=exp_data.get('position'),
                start_date=self._parse_datetime(exp_data.get('start_date')),
                end_date=self._parse_datetime(exp_data.get('end_date')),
                years=exp_data.get('years'),
                description=exp_data.get('description'),
                employment_status=exp_data.get('employment_status'),
                key_skills=exp_data.get('key_skills', []),
                achievements=exp_data.get('achievements', [])
            )
            self.db.add(work_exp)
    
    def _add_education(self, user_id: str, education_data: List[Dict]):
        """Add education for a user"""
        for edu_data in education_data:
            education = Education(
                user_id=user_id,
                institution=edu_data.get('institution'),
                degree=edu_data.get('degree'),
                field_of_study=edu_data.get('field_of_study'),
                start_date=self._parse_datetime(edu_data.get('start_date')),
                end_date=self._parse_datetime(edu_data.get('end_date')),
                graduation_year=edu_data.get('graduation_year'),
                gpa=edu_data.get('gpa'),
                relevant_coursework=edu_data.get('relevant_coursework', [])
            )
            self.db.add(education)
    
    def _add_preferences(self, user_id: str, pref_data: Dict):
        """Add preferences for a user"""
        preferences = UserPreferences(
            user_id=user_id,
            work_types=pref_data.get('work_types', []),
            work_type=pref_data.get('work_type', []),
            desired_roles=pref_data.get('desired_roles', []),
            salary_min=pref_data.get('salary_min'),
            salary_max=pref_data.get('salary_max'),
            locations=pref_data.get('locations', []),
            industries=pref_data.get('industries', []),
            company_size=pref_data.get('company_size', []),
            remote_preference=pref_data.get('remote_preference'),
            growth_areas=pref_data.get('growth_areas', []),
            availability=pref_data.get('availability')
        )
        self.db.add(preferences)
    
    def _add_career_goals(self, user_id: str, goals_data: List[str]):
        """Add career goals for a user"""
        profile = self.get_profile(user_id)
        for goal_text in goals_data:
            # Get or create goal
            goal = self.db.query(CareerGoal).filter(CareerGoal.goal_text == goal_text).first()
            if not goal:
                goal = CareerGoal(goal_text=goal_text)
                self.db.add(goal)
                self.db.flush()
            
            # Associate with user
            if goal not in profile.career_goals:
                profile.career_goals.append(goal)
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string"""
        if not date_str:
            return None
        try:
            # Handle ISO format
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Handle date only
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None

class JSONToPostgreSQLMigrator:
    """Migrate existing JSON profiles to PostgreSQL"""
    
    def __init__(self, db: Session):
        self.db = db
        self.profile_service = ProfileService(db)
    
    def migrate_profile(self, json_file_path: str) -> bool:
        """Migrate a single JSON profile to PostgreSQL"""
        try:
            with open(json_file_path, 'r') as f:
                profile_data = json.load(f)
            
            # Check if profile already exists
            existing = self.profile_service.get_profile(profile_data.get('user_id', ''))
            if existing:
                print(f"Profile {profile_data.get('name')} already exists, updating...")
                self.profile_service.update_profile(existing.user_id, profile_data)
            else:
                print(f"Creating new profile for {profile_data.get('name')}...")
                self.profile_service.create_profile(profile_data)
            
            return True
        except Exception as e:
            print(f"Error migrating {json_file_path}: {e}")
            return False
    
    def migrate_all_profiles(self, profiles_dir: str) -> Dict[str, int]:
        """Migrate all JSON profiles from directory"""
        import os
        import glob
        
        stats = {'success': 0, 'failed': 0}
        
        json_files = glob.glob(os.path.join(profiles_dir, '*.json'))
        
        for json_file in json_files:
            if self.migrate_profile(json_file):
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        return stats