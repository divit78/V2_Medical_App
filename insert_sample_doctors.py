import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_helper import DatabaseHelper
from utils.auth import hash_password  # Import your hash function
from datetime import datetime

def insert_sample_doctors():
    """Insert sample doctors into the database"""
    db = DatabaseHelper()
    
    try:
        db.connect()
        print("Connected to database...")

        # Generate proper hashed password
        hashed_password = hash_password('password')
        print(f"Using hashed password: {hashed_password}")

        # Sample users data with correct password hash
        users = [
            {
                'user_id': 'DOC10001', 'username': 'dr_smith', 
                'password': hashed_password,  # Use properly hashed password
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(), 
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            },
            {
                'user_id': 'DOC10002', 'username': 'dr_jones',
                'password': hashed_password,
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(),
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            },
            {
                'user_id': 'DOC10003', 'username': 'dr_lee',
                'password': hashed_password,
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(),
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            },
            {
                'user_id': 'DOC10004', 'username': 'dr_patel',
                'password': hashed_password,
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(),
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            },
            {
                'user_id': 'DOC10005', 'username': 'dr_garcia',
                'password': hashed_password,
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(),
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            },
            {
                'user_id': 'DOC10006', 'username': 'dr_wilson',
                'password': hashed_password,
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(),
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            },
            {
                'user_id': 'DOC10007', 'username': 'dr_brown',
                'password': hashed_password,
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(),
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            },
            {
                'user_id': 'DOC10008', 'username': 'dr_davis',
                'password': hashed_password,
                'user_type': 'doctor', 'created_at': datetime.now().isoformat(),
                'last_login': None, 'is_active': True, 'verification_status': 'approved'
            }
        ]

        # ... rest of your profiles data remains the same ...
        profiles = [
            # Your existing profiles data here
        ]

        # First, delete existing doctor records to avoid duplicates
        print("Removing existing doctor records...")
        
        # Insert users
        print("Inserting users...")
        for user in users:
            db.save_user(user['user_id'], user)

        # Insert profiles  
        print("Inserting profiles...")
        for profile in profiles:
            db.save_profile(profile['user_id'], profile)

        print("✅ Sample doctors inserted successfully!")
        print(f"✅ Added {len(users)} doctors to the database")
        print("Login credentials: username = dr_smith, dr_jones, etc. | password = 'password'")

    except Exception as e:
        print(f"❌ Error inserting sample doctors: {e}")
        
    finally:
        db.close_connection()

if __name__ == "__main__":
    insert_sample_doctors()
