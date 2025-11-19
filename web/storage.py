"""
Storage abstraction layer for SkillMatch.AI profiles
SQLite-only implementation
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

class SQLiteProfileStorage(ProfileStorage):
    """SQLite database profile storage"""
    
    def __init__(self):
        # Import database services
        try:
            from web.database.services import ProfileService
            from web.database.db_config import db_config
            self.ProfileService = ProfileService
            self.db_config = db_config
            self._db_available = True
        except ImportError as e:
            print(f"SQLite storage not available: {e}")
            self._db_available = False
            raise ImportError("Database services not available")
        
        if not self._db_available:
            raise RuntimeError("SQLite storage not available")
    
    def save_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Save profile to SQLite"""
        try:
            with self.db_config.session_scope() as session:
                service = self.ProfileService(session)
                profile_id = profile_data.get('user_id')
                
                if not profile_id:
                    print("Error: Profile data missing user_id")
                    return False
                
                # Check if profile exists
                existing = service.get_profile(profile_id)
                if existing:
                    service.update_profile(profile_id, profile_data)
                    print(f"Updated profile: {profile_id}")
                else:
                    service.create_profile(profile_data)
                    print(f"Created profile: {profile_id}")
                
                return True
        except Exception as e:
            print(f"Error saving profile to SQLite: {e}")
            return False
    
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load profile from SQLite"""
        try:
            with self.db_config.session_scope() as session:
                service = self.ProfileService(session)
                profile = service.get_profile(profile_id)
                return service.profile_to_dict(profile) if profile else None
        except Exception as e:
            print(f"Error loading profile from SQLite: {e}")
            return None
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all SQLite profiles"""
        try:
            with self.db_config.session_scope() as session:
                service = self.ProfileService(session)
                profiles = service.get_all_profiles()
                return [service.profile_to_dict(p) for p in profiles]
        except Exception as e:
            print(f"Error listing profiles from SQLite: {e}")
            return []
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile from SQLite (soft delete)"""
        try:
            with self.db_config.session_scope() as session:
                service = self.ProfileService(session)
                return service.delete_profile(profile_id)
        except Exception as e:
            print(f"Error deleting profile from SQLite: {e}")
            return False
    
    def search_profiles(self, **filters) -> List[Dict[str, Any]]:
        """Search profiles in SQLite"""
        try:
            with self.db_config.session_scope() as session:
                service = self.ProfileService(session)
                profiles = service.search_profiles(**filters)
                return [service.profile_to_dict(p) for p in profiles]
        except Exception as e:
            print(f"Error searching profiles in SQLite: {e}")
            return []

class ProfileManager:
    """Main profile manager - SQLite only"""
    
    def __init__(self):
        # SQLite storage only
        self.storage_type = 'sqlite'
        
        try:
            self.storage = SQLiteProfileStorage()
            print("✅ Using SQLite storage for profiles")
        except Exception as e:
            raise RuntimeError(f"SQLite storage is required but not available: {e}")
    
    def save_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Save a profile using the configured storage"""
        return self.storage.save_profile(profile_data)
    
    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load a profile by ID"""
        return self.storage.load_profile(profile_id)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles"""
        return self.storage.list_profiles()
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        return self.storage.delete_profile(profile_id)
    
    def search_profiles(self, **filters) -> List[Dict[str, Any]]:
        """Search profiles"""
        return self.storage.search_profiles(**filters)
    
    def get_storage_type(self) -> str:
        """Get current storage type"""
        return self.storage_type
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        profiles = self.list_profiles()
        return {
            'total_profiles': len(profiles),
            'storage_type': self.storage_type,
            'active_profiles': len([p for p in profiles if p.get('is_active', True)])
        }

# Global instance
profile_manager = ProfileManager()