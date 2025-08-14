from utils.db_helper import db
import os
import json
from datetime import datetime

def load_json(file_path):
    """
    Load data from database instead of JSON files.
    This maintains compatibility with existing code.
    """
    try:
        if 'users' in file_path.lower():
            return db.load_users()
        elif 'profiles' in file_path.lower():
            return db.load_profiles()
        elif 'medicines' in file_path.lower():
            return db.load_medicines()
        elif 'schedules' in file_path.lower():
            return db.load_schedules()
        elif 'prescriptions' in file_path.lower():
            return db.load_prescriptions()
        elif 'medical_tests' in file_path.lower():
            return db.load_medical_tests()
        elif 'doctor_queries' in file_path.lower():
            return db.load_doctor_queries()
        elif 'appointments' in file_path.lower():
            return db.load_appointments()
        elif 'guardian_requests' in file_path.lower():
            return db.load_guardian_requests()
        elif 'patient_doctor_requests' in file_path.lower():
            return db.load_patient_doctor_requests()
        else:
            return {}
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

def save_json(file_path, data):
    """
    Save data to database instead of JSON files.
    Routes to appropriate database save function.
    """
    try:
        if 'users' in file_path.lower():
            for user_id, user_data in data.items():
                db.save_user(user_id, user_data)
        elif 'profiles' in file_path.lower():
            for user_id, profile_data in data.items():
                db.save_profile(user_id, profile_data)
        elif 'medicines' in file_path.lower():
            for medicine_id, medicine_data in data.items():
                db.save_medicine(medicine_id, medicine_data)
        elif 'schedules' in file_path.lower():
            for schedule_id, schedule_data in data.items():
                db.save_schedule(schedule_id, schedule_data)
        elif 'prescriptions' in file_path.lower():
            for prescription_id, prescription_data in data.items():
                db.save_prescription(prescription_id, prescription_data)
        # Add other save operations as needed
    except Exception as e:
        print(f"Error saving data: {e}")

def ensure_dir_exists(directory):
    """Ensure that a directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def save_uploaded_file(uploaded_file, directory, filename=None):
    """Save an uploaded file and return the file path"""
    ensure_dir_exists(directory)
    
    if filename is None:
        filename = uploaded_file.name
    
    file_path = os.path.join(directory, filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def generate_unique_id(prefix=""):
    """Generate a unique ID with optional prefix"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"{prefix}{timestamp}" if prefix else timestamp
