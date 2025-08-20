import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_helper import DatabaseHelper
from datetime import datetime

def test_connection():
    print("Testing database connection...")
    db = DatabaseHelper()
    try:
        db.connect()
        print("✅ Database connected successfully!")
        
        # Test manual insert
        test_request = {
            'patient_id': 'PAT20001',
            'doctor_id': 'DOC10001',
            'status': 'pending',
            'requested_at': datetime.now().isoformat()
        }
        
        print("Testing manual insert...")
        result = db.save_patient_doctor_request('TEST_REQ_123', test_request)
        print(f"✅ Insert result: {result}")
        
        # Test loading
        print("Testing data loading...")
        requests = db.load_patient_doctor_requests()
        print(f"✅ Found {len(requests)} total requests in database")
        
        if requests:
            for req_id, req in requests.items():
                print(f"  - {req_id}: Patient {req['patient_id']} → Doctor {req['doctor_id']} ({req['status']})")
        else:
            print("  - No requests found")
        
        db.close_connection()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()

