import os
import json
from datetime import datetime


class DatabaseRouter:
    """Route file operations to database"""
    
    def __init__(self):
        self.file_type_map = {
            'users': ('load_users', 'save_user'),
            'profiles': ('load_profiles', 'save_profile'),
            'medicines': ('load_medicines', 'save_medicine'),
            'schedules': ('load_schedules', 'save_schedule'),
            'prescriptions': ('load_prescriptions', 'save_prescription'),
            'medical_tests': ('load_medical_tests', 'save_medical_test'),
            'doctor_queries': ('load_doctor_queries', 'save_doctor_query'),
            'appointments': ('load_appointments', 'save_appointment'),
            'guardian_requests': ('load_guardian_requests', 'save_guardian_request'),
            'patient_doctor_requests': ('load_patient_doctor_requests', 'save_patient_doctor_request')
        }
    
    def get_file_type(self, file_path):
        """Determine file type from path"""
        file_path_lower = file_path.lower()
        for file_type in self.file_type_map.keys():
            if file_type in file_path_lower:
                return file_type
        return None
    
    def load_data(self, file_path):
        """Load data from database based on file path"""
        try:
            from utils.db_helper import db
            
            file_type = self.get_file_type(file_path)
            if file_type and file_type in self.file_type_map:
                load_method = self.file_type_map[file_type][0]
                return getattr(db, load_method)()
            
            return {}
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    
    def save_data(self, file_path, data):
        """Save data to database based on file path"""
        try:
            from utils.db_helper import db
            
            file_type = self.get_file_type(file_path)
            if file_type and file_type in self.file_type_map:
                save_method = self.file_type_map[file_type][1]
                
                for item_id, item_data in data.items():
                    getattr(db, save_method)(item_id, item_data)
            
        except Exception as e:
            print(f"Error saving data: {e}")


class FileManager:
    """Handle file operations"""
    
    @staticmethod
    def ensure_dir_exists(directory):
        """Ensure directory exists, create if it doesn't"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def save_uploaded_file(uploaded_file, directory, filename=None):
        """Save an uploaded file and return the file path"""
        FileManager.ensure_dir_exists(directory)
        
        if filename is None:
            filename = uploaded_file.name
        
        file_path = os.path.join(directory, filename)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    
    @staticmethod
    def generate_unique_id(prefix=""):
        """Generate a unique ID with optional prefix"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"{prefix}{timestamp}" if prefix else timestamp


# Global instances
db_router = DatabaseRouter()
file_manager = FileManager()


# Keep original functions for backward compatibility
def load_json(file_path):
    """Load data from database (backward compatible)"""
    return db_router.load_data(file_path)


def save_json(file_path, data):
    """Save data to database (backward compatible)"""
    db_router.save_data(file_path, data)


def ensure_dir_exists(directory):
    """Ensure directory exists (backward compatible)"""
    return file_manager.ensure_dir_exists(directory)


def save_uploaded_file(uploaded_file, directory, filename=None):
    """Save uploaded file (backward compatible)"""
    return file_manager.save_uploaded_file(uploaded_file, directory, filename)


def generate_unique_id(prefix=""):
    """Generate unique ID (backward compatible)"""
    return file_manager.generate_unique_id(prefix)
