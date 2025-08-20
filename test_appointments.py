from utils.db_helper import db
from datetime import datetime

def test_appointments():
    print("=== Testing Appointments ===")
    
    # Test appointment creation
    test_appointment = {
        'patient_id': 'PAT20001',
        'doctor_id': 'DOC10001', 
        'appointment_date': '2025-08-20',
        'appointment_time': '14:30',
        'type': 'Video Call',
        'status': 'requested',
        'notes': 'Test appointment for debugging',
        'created_at': datetime.now().isoformat()
    }
    
    print("1. Testing appointment save...")
    result = db.save_appointment('TEST_APT_002', test_appointment)
    print(f"   Save result: {result}")
    
    print("2. Testing appointment load...")
    appointments = db.load_appointments()
    print(f"   Total appointments: {len(appointments)}")
    
    for apt_id, apt in appointments.items():
        print(f"   - {apt_id}: Patient {apt.get('patient_id')} → Doctor {apt.get('doctor_id')} on {apt.get('appointment_date')} at {apt.get('appointment_time')} (Status: {apt.get('status')})")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_appointments()
