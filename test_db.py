from utils.db_helper import DatabaseHelper

def test_connection():
    db = DatabaseHelper()
    try:
        db.connect()
        print("✅ Database connection successful!")
        
        # Test saving a request manually
        test_request = {
            'patient_id': 'PAT20001',
            'doctor_id': 'DOC10002', 
            'status': 'pending',
            'requested_at': '2025-08-20T00:00:00'
        }
        
        result = db.save_patient_doctor_request('TEST123', test_request)
        print(f"✅ Save result: {result}")
        
        # Test loading requests
        requests = db.load_patient_doctor_requests()
        print(f"✅ Total requests found: {len(requests)}")
        
        db.close_connection()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_connection()
