import os

# Database configuration - UPDATE THESE WITH YOUR CREDENTIALS
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'root',  # Replace with your MySQL password
    'database': 'medical_reminder_db'
}

# Application constants
UPLOAD_DIR = "uploads"
PROFILE_UPLOAD_DIR = "uploads/profiles"
MEDICINE_UPLOAD_DIR = "uploads/medicines"
PRESCRIPTION_UPLOAD_DIR = "uploads/prescriptions"
MEDICAL_TEST_UPLOAD_DIR = "uploads/medical_tests"

# Legacy file paths (for backward compatibility)
DATA_DIR = os.path.join("medical_app", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
GUARDIAN_REQUESTS_FILE = os.path.join(DATA_DIR, "guardian_requests.json")
MEDICINES_FILE = os.path.join(DATA_DIR, "medicines.json")
SCHEDULES_FILE = os.path.join(DATA_DIR, "schedules.json")
PRESCRIPTIONS_FILE = os.path.join(DATA_DIR, "prescriptions.json")
MEDICAL_TESTS_FILE = os.path.join(DATA_DIR, "medical_tests.json")
DOCTOR_QUERIES_FILE = os.path.join(DATA_DIR, "doctor_queries.json")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
PATIENT_DOCTOR_REQUESTS_FILE = os.path.join(DATA_DIR, "patient_doctor_requests.json")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
