"""
SSG-WSG Developer Portal API Integration Service
Complete service for fetching and managing course data from SSG-WSG API
"""

import os
import logging
import requests
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    from sqlalchemy.orm import Session
    from ..database.models import Course
    from ..database.db_config import db_config
except ImportError as e:
    try:
        # Fallback for direct script usage
        from web.database.models import Course
        from web.database.db_config import db_config
    except ImportError:
        print(f"Database modules not available: {e}")
        Course = None
        db_config = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSGWSGAPIClient:
    """Client for SSG-WSG Developer Portal API"""
    
    def __init__(self):
        self.base_url = "https://api.ssg-wsg.gov.sg"
        self.api_key = os.getenv('SSGWSG_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}' if self.api_key else '',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if not self.api_key:
            logger.warning("SSG-WSG API key not found. Set SSGWSG_API_KEY environment variable.")
    
    def get_courses(self, page: int = 0, size: int = 100, **filters) -> Dict[str, Any]:
        """
        Fetch courses from SSG-WSG API
        
        Args:
            page: Page number (0-based)
            size: Number of records per page (max 100)
            **filters: Additional filters for course search
        
        Returns:
            API response containing courses data
        """
        endpoint = f"{self.base_url}/courses/courseRuns"
        
        params = {
            'page': page,
            'size': size,
            'sortBy[0]': 'course.title',
            'sortOrder[0]': 'asc'
        }
        
        # Add optional filters
        if filters.get('course_type'):
            params['course.courseType.description'] = filters['course_type']
        
        if filters.get('skills'):
            params['skills'] = filters['skills']
            
        if filters.get('sectors'):
            params['sectors'] = filters['sectors']
            
        if filters.get('delivery_mode'):
            params['deliveryMode'] = filters['delivery_mode']
        
        try:
            logger.info(f"Fetching courses from SSG-WSG API - Page {page}, Size {size}")
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data.get('data', {}).get('courses', []))} courses")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching courses from SSG-WSG API: {e}")
            return {'data': {'courses': []}, 'meta': {'totalPages': 0}}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing API response: {e}")
            return {'data': {'courses': []}, 'meta': {'totalPages': 0}}
    
    def get_course_details(self, course_reference_number: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific course
        
        Args:
            course_reference_number: Course reference number
            
        Returns:
            Course details or None if not found
        """
        endpoint = f"{self.base_url}/courses/courseRuns"
        params = {
            'course.referenceNumber': course_reference_number
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            courses = data.get('data', {}).get('courses', [])
            
            if courses:
                return courses[0]  # Return first matching course
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching course details: {e}")
            return None
    
    def search_courses_by_skills(self, skills: List[str]) -> List[Dict[str, Any]]:
        """
        Search courses by relevant skills
        
        Args:
            skills: List of skill names to search for
            
        Returns:
            List of matching courses
        """
        all_courses = []
        
        for skill in skills:
            try:
                # Search courses containing the skill
                courses_data = self.get_courses(skills=skill, size=50)
                courses = courses_data.get('data', {}).get('courses', [])
                all_courses.extend(courses)
                
                # Add a small delay to respect API rate limits
                import time
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error searching courses for skill '{skill}': {e}")
                continue
        
        # Remove duplicates based on course reference number
        unique_courses = {}
        for course in all_courses:
            ref_num = course.get('course', {}).get('referenceNumber')
            if ref_num and ref_num not in unique_courses:
                unique_courses[ref_num] = course
        
        return list(unique_courses.values())

class CourseService:
    """Service for managing courses in the database"""
    
    def __init__(self):
        self.api_client = SSGWSGAPIClient()
    
    def sync_courses_from_api(self, max_pages: int = 10) -> Dict[str, int]:
        """
        Sync courses from SSG-WSG API to database
        
        Args:
            max_pages: Maximum number of pages to fetch
            
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            'total_fetched': 0,
            'new_courses': 0,
            'updated_courses': 0,
            'errors': 0
        }
        
        db = db_config.get_session()
        
        try:
            # Fetch courses page by page
            current_page = 0
            
            while current_page < max_pages:
                courses_data = self.api_client.get_courses(page=current_page, size=100)
                courses = courses_data.get('data', {}).get('courses', [])
                
                if not courses:
                    break
                
                stats['total_fetched'] += len(courses)
                
                # Process each course
                for course_data in courses:
                    try:
                        course_info = self._parse_course_data(course_data)
                        if course_info:
                            existing_course = db.query(Course).filter(
                                Course.course_reference_number == course_info['course_reference_number']
                            ).first()
                            
                            if existing_course:
                                # Update existing course
                                for key, value in course_info.items():
                                    if key != 'id':
                                        setattr(existing_course, key, value)
                                existing_course.updated_at = datetime.utcnow()
                                stats['updated_courses'] += 1
                            else:
                                # Create new course
                                new_course = Course(**course_info)
                                db.add(new_course)
                                stats['new_courses'] += 1
                    
                    except Exception as e:
                        logger.error(f"Error processing course: {e}")
                        stats['errors'] += 1
                        continue
                
                # Commit changes for this page
                db.commit()
                
                # Check if we've reached the last page
                total_pages = courses_data.get('meta', {}).get('totalPages', 0)
                if current_page >= total_pages - 1:
                    break
                
                current_page += 1
                
                # Add delay to respect rate limits
                import time
                time.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error during course sync: {e}")
            db.rollback()
            stats['errors'] += 1
        
        finally:
            db.close()
        
        logger.info(f"Course sync completed: {stats}")
        return stats
    
    def _parse_course_data(self, course_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse course data from API response into database format
        
        Args:
            course_data: Raw course data from API
            
        Returns:
            Parsed course information or None if invalid
        """
        try:
            course = course_data.get('course', {})
            run = course_data.get('runs', [{}])[0] if course_data.get('runs') else {}
            
            # Extract basic course information
            course_info = {
                'course_id': str(course.get('id', '')),
                'course_reference_number': course.get('referenceNumber', ''),
                'title': course.get('title', ''),
                'description': course.get('description', ''),
                'provider': course.get('trainingProvider', {}).get('name', ''),
                'provider_code': course.get('trainingProvider', {}).get('code', ''),
                
                # Course details
                'duration': run.get('duration', ''),
                'course_type': course.get('courseType', {}).get('description', ''),
                'delivery_mode': run.get('modeOfTraining', ''),
                
                # Skills and categories
                'skills_taught': course.get('skills', []),
                'skills_framework': course.get('skillsFramework', []),
                'categories': course.get('categories', []),
                'sectors': course.get('sectors', []),
                
                # Requirements
                'eligibility_criteria': course.get('eligibilityCriteria', ''),
                'prerequisites': course.get('prerequisites', ''),
                'target_audience': course.get('targetAudience', ''),
                
                # Pricing
                'course_fee': self._parse_float(run.get('courseFee')),
                'nett_fee_citizen': self._parse_float(run.get('nettFeeCitizen')),
                'nett_fee_pr': self._parse_float(run.get('nettFeePR')),
                'funding_available': run.get('fundingInformation', []),
                
                # Schedule and location
                'schedule': run.get('schedule', {}),
                'locations': run.get('venues', []),
                
                # Quality
                'accreditation': course.get('accreditation', ''),
                'certification': course.get('certification', ''),
                
                # Metadata
                'external_url': course.get('coursePageUrl', ''),
                'last_updated': datetime.utcnow()
            }
            
            # Only return if we have minimum required fields
            if course_info['course_reference_number'] and course_info['title']:
                return course_info
            else:
                logger.warning(f"Incomplete course data: missing reference number or title")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing course data: {e}")
            return None
    
    def _parse_float(self, value: Any) -> Optional[float]:
        """Safely parse float value"""
        try:
            if value is None or value == '':
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_courses_for_user_skills(self, user_skills: List[str], limit: int = 10) -> List[Course]:
        """
        Get recommended courses based on user skills
        
        Args:
            user_skills: List of user's skills
            limit: Maximum number of courses to return
            
        Returns:
            List of recommended courses
        """
        db = db_config.get_session()
        
        try:
            # Search for courses that match user skills
            courses = db.query(Course).filter(
                Course.is_active == True
            ).all()
            
            # Score courses based on skill matches
            scored_courses = []
            
            for course in courses:
                score = 0
                skills_taught = course.skills_taught or []
                
                # Calculate relevance score based on skill matches
                for user_skill in user_skills:
                    for course_skill in skills_taught:
                        if isinstance(course_skill, dict):
                            skill_name = course_skill.get('skillName', '').lower()
                        else:
                            skill_name = str(course_skill).lower()
                        
                        if user_skill.lower() in skill_name or skill_name in user_skill.lower():
                            score += 1
                
                if score > 0:
                    scored_courses.append((course, score))
            
            # Sort by relevance score and return top courses
            scored_courses.sort(key=lambda x: x[1], reverse=True)
            return [course for course, score in scored_courses[:limit]]
            
        finally:
            db.close()
    
    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """Get course by database ID"""
        db = db_config.get_session()
        
        try:
            return db.query(Course).filter(Course.id == course_id).first()
        finally:
            db.close()
    
    def search_courses(self, query: str, filters: Dict[str, Any] = None) -> List[Course]:
        """
        Search courses by title, description, or skills
        
        Args:
            query: Search query
            filters: Additional filters
            
        Returns:
            List of matching courses
        """
        db = db_config.get_session()
        
        try:
            base_query = db.query(Course).filter(Course.is_active == True)
            
            # Text search
            if query:
                search_filter = (
                    Course.title.ilike(f'%{query}%') |
                    Course.description.ilike(f'%{query}%') |
                    Course.provider.ilike(f'%{query}%')
                )
                base_query = base_query.filter(search_filter)
            
            # Apply additional filters
            if filters:
                if filters.get('course_type'):
                    base_query = base_query.filter(Course.course_type == filters['course_type'])
                
                if filters.get('provider'):
                    base_query = base_query.filter(Course.provider == filters['provider'])
                
                if filters.get('max_fee'):
                    base_query = base_query.filter(Course.course_fee <= filters['max_fee'])
            
            return base_query.limit(50).all()
            
        finally:
            db.close()

# Global course service instance
course_service = CourseService()