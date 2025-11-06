"""
Storage abstraction layer for SkillMatch.AI profiles
Supports both JSON file storage and PostgreSQL database
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

class ProfileStorage(ABC):
    """Abstract base class for profile storage"""
    
    @abstractmethod
    def save_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Save a profile"""
        pass
    
    @abstractmethod
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load a profile by ID"""
        pass
    
    @abstractmethod
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles"""
        pass
    
    @abstractmethod
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        pass
    
    @abstractmethod
    def search_profiles(self, **filters) -> List[Dict[str, Any]]:
        """Search profiles with filters"""
        pass

class PostgreSQLProfileStorage(ProfileStorage):
    """PostgreSQL database profile storage"""
    
    def __init__(self):
        # Lazy import to avoid dependency issues
        try:
            # Try the full path first
            from web.database.services import ProfileService
            from web.database.models import get_db
            self.ProfileService = ProfileService
            self.get_db = get_db
            self._db_available = True
        except ImportError:
            try:
                # Fallback for when running from web directory
                from database.services import ProfileService
                from database.models import get_db
                self.ProfileService = ProfileService
                self.get_db = get_db
                self._db_available = True
            except ImportError as e:
                print(f"PostgreSQL storage not available: {e}")
                self._db_available = False
    
    def _get_service(self):
        """Get profile service with database session"""
        if not self._db_available:
            raise RuntimeError("PostgreSQL storage not available")
        
        db = next(self.get_db())
        return self.ProfileService(db), db
    
    def save_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Save profile to PostgreSQL"""
        try:
            service, db = self._get_service()
            
            profile_id = profile_data.get('user_id') or profile_data.get('name', '').lower().replace(' ', '_')
            
            # Check if profile exists
            existing = service.get_profile(profile_id)
            if existing:
                service.update_profile(profile_id, profile_data)
            else:
                profile_data['user_id'] = profile_id
                service.create_profile(profile_data)
            
            db.close()
            return True
        except Exception as e:
            print(f"Error saving profile to PostgreSQL: {e}")
            return False
    
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load profile from PostgreSQL"""
        try:
            service, db = self._get_service()
            profile = service.get_profile(profile_id)
            
            if profile:
                profile_dict = service.profile_to_dict(profile)
                db.close()
                return profile_dict
            
            db.close()
            return None
        except Exception as e:
            print(f"Error loading profile from PostgreSQL: {e}")
            return None
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all PostgreSQL profiles"""
        try:
            service, db = self._get_service()
            profiles = service.get_all_profiles()
            
            # Convert to dictionaries before closing the session
            profile_dicts = [service.profile_to_dict(p) for p in profiles]
            db.close()
            
            return profile_dicts
        except Exception as e:
            print(f"Error listing profiles from PostgreSQL: {e}")
            return []
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile from PostgreSQL (soft delete)"""
        try:
            service, db = self._get_service()
            result = service.delete_profile(profile_id)
            db.close()
            return result
        except Exception as e:
            print(f"Error deleting profile from PostgreSQL: {e}")
            return False
    
    def search_profiles(self, **filters) -> List[Dict[str, Any]]:
        """Search profiles in PostgreSQL"""
        try:
            service, db = self._get_service()
            profiles = service.search_profiles(
                skills=filters.get('skills'),
                location=filters.get('location'),
                experience_level=filters.get('experience_level'),
                limit=filters.get('limit', 50)
            )
            db.close()
            
            return [service.profile_to_dict(p) for p in profiles]
        except Exception as e:
            print(f"Error searching profiles in PostgreSQL: {e}")
            return []

class ProfileManager:
    """Profile manager that handles both storage types"""
    
    def __init__(self, storage_type: str = None):
        # Force PostgreSQL storage only
        self.storage_type = 'postgresql'
        
        try:
            self.storage = PostgreSQLProfileStorage()
            print("✅ Using PostgreSQL storage for profiles")
        except Exception as e:
            print(f"❌ PostgreSQL not available: {e}")
            raise RuntimeError("PostgreSQL storage is required. JSON storage has been removed.")
    
    def save_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Save profile using configured storage"""
        return self.storage.save_profile(profile_data)
    
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load profile using configured storage"""
        return self.storage.load_profile(profile_id)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List profiles using configured storage"""
        return self.storage.list_profiles()
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile using configured storage"""
        return self.storage.delete_profile(profile_id)
    
    def search_profiles(self, **filters) -> List[Dict[str, Any]]:
        """Search profiles using configured storage"""
        return self.storage.search_profiles(**filters)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about current storage"""
        return {
            'type': self.storage_type,
            'class': self.storage.__class__.__name__,
            'available_methods': ['save_profile', 'load_profile', 'list_profiles', 'delete_profile', 'search_profiles']
        }

# Global profile manager instance
profile_manager = ProfileManager()