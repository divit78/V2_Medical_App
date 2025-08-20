import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_helper import DatabaseHelper
from utils.auth import hash_password
from datetime import datetime

def insert_patients():
    """Insert sample Indian patients into the database"""
    db = DatabaseHelper()
    
    try:
        db.connect()
        print("Connected to database...")

        hashed_password = hash_password('password123')

        indian_patients = [
            {
                'user_id': 'PAT20001',
                'username': 'rajesh_kumar',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Rajesh Kumar',
                'title': 'Mr.',
                'mobile': '9876543210',
                'email': 'rajesh.kumar@gmail.com',
                'dob': '1985-03-15',
                'gender': 'Male',
                'blood_group': 'B+',
                'marital_status': 'Married',
                'address': '12/4, Gandhi Nagar, Sector 15',
                'city': 'Delhi',
                'pincode': '110001',
                'state': 'Delhi',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20002',
                'username': 'priya_sharma',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Priya Sharma',
                'title': 'Mrs.',
                'mobile': '9845632107',
                'email': 'priya.sharma@yahoo.com',
                'dob': '1992-07-22',
                'gender': 'Female',
                'blood_group': 'A+',
                'marital_status': 'Single',
                'address': '45, MG Road, Koramangala',
                'city': 'Bangalore',
                'pincode': '560034',
                'state': 'Karnataka',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20003',
                'username': 'amit_patel',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Amit Patel',
                'title': 'Mr.',
                'mobile': '9723456789',
                'email': 'amit.patel@hotmail.com',
                'dob': '1978-11-05',
                'gender': 'Male',
                'blood_group': 'O+',
                'marital_status': 'Married',
                'address': '203, Satellite Tower, SG Highway',
                'city': 'Ahmedabad',
                'pincode': '380015',
                'state': 'Gujarat',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20004',
                'username': 'sunita_singh',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Sunita Singh',
                'title': 'Mrs.',
                'mobile': '9415678923',
                'email': 'sunita.singh@gmail.com',
                'dob': '1989-01-18',
                'gender': 'Female',
                'blood_group': 'AB+',
                'marital_status': 'Married',
                'address': '78, Civil Lines, Near Railway Station',
                'city': 'Lucknow',
                'pincode': '226001',
                'state': 'Uttar Pradesh',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20005',
                'username': 'ravi_reddy',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Ravi Reddy',
                'title': 'Mr.',
                'mobile': '9849123456',
                'email': 'ravi.reddy@outlook.com',
                'dob': '1983-06-30',
                'gender': 'Male',
                'blood_group': 'A-',
                'marital_status': 'Married',
                'address': '156, Banjara Hills, Road No. 3',
                'city': 'Hyderabad',
                'pincode': '500034',
                'state': 'Telangana',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20006',
                'username': 'meera_nair',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Meera Nair',
                'title': 'Ms.',
                'mobile': '9847562318',
                'email': 'meera.nair@gmail.com',
                'dob': '1995-04-12',
                'gender': 'Female',
                'blood_group': 'O-',
                'marital_status': 'Single',
                'address': '89, Marine Drive, Ernakulam',
                'city': 'Kochi',
                'pincode': '682031',
                'state': 'Kerala',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20007',
                'username': 'vikram_singh',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Vikram Singh',
                'title': 'Mr.',
                'mobile': '9828374651',
                'email': 'vikram.singh@yahoo.in',
                'dob': '1976-09-25',
                'gender': 'Male',
                'blood_group': 'B-',
                'marital_status': 'Married',
                'address': '234, Pink City Plaza, MI Road',
                'city': 'Jaipur',
                'pincode': '302001',
                'state': 'Rajasthan',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20008',
                'username': 'kavita_joshi',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Kavita Joshi',
                'title': 'Mrs.',
                'mobile': '9823145679',
                'email': 'kavita.joshi@rediffmail.com',
                'dob': '1987-12-08',
                'gender': 'Female',
                'blood_group': 'AB-',
                'marital_status': 'Married',
                'address': '67, Baner Road, Pune West',
                'city': 'Pune',
                'pincode': '411045',
                'state': 'Maharashtra',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20009',
                'username': 'suresh_yadav',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Suresh Yadav',
                'title': 'Mr.',
                'mobile': '9935647821',
                'email': 'suresh.yadav@gmail.com',
                'dob': '1990-02-14',
                'gender': 'Male',
                'blood_group': 'O+',
                'marital_status': 'Single',
                'address': '45, Park Street, Near Victoria Memorial',
                'city': 'Kolkata',
                'pincode': '700016',
                'state': 'West Bengal',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20010',
                'username': 'anita_das',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Anita Das',
                'title': 'Ms.',
                'mobile': '9437829456',
                'email': 'anita.das@outlook.com',
                'dob': '1993-08-03',
                'gender': 'Female',
                'blood_group': 'A+',
                'marital_status': 'Single',
                'address': '123, Janpath, Unit-8',
                'city': 'Bhubaneswar',
                'pincode': '751012',
                'state': 'Odisha',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20011',
                'username': 'deepak_gupta',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Deepak Gupta',
                'title': 'Mr.',
                'mobile': '9452318769',
                'email': 'deepak.gupta@gmail.com',
                'dob': '1981-05-20',
                'gender': 'Male',
                'blood_group': 'B+',
                'marital_status': 'Married',
                'address': '89, Mall Road, Near Clock Tower',
                'city': 'Dehradun',
                'pincode': '248001',
                'state': 'Uttarakhand',
                'nationality': 'Indian'
            },
            {
                'user_id': 'PAT20012',
                'username': 'sneha_iyer',
                'password': hashed_password,
                'user_type': 'patient',
                'full_name': 'Sneha Iyer',
                'title': 'Mrs.',
                'mobile': '9944567123',
                'email': 'sneha.iyer@yahoo.com',
                'dob': '1988-10-15',
                'gender': 'Female',
                'blood_group': 'O+',
                'marital_status': 'Married',
                'address': '456, T. Nagar, Anna Salai',
                'city': 'Chennai',
                'pincode': '600017',
                'state': 'Tamil Nadu',
                'nationality': 'Indian'
            }
        ]

        print("Inserting Indian patients...")
        
        for patient in indian_patients:
            # Insert into users table
            user_data = {
                'username': patient['username'],
                'password': patient['password'],
                'user_type': patient['user_type'],
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'verification_status': 'approved'
            }
            db.save_user(patient['user_id'], user_data)
            
            # Insert into profiles table
            profile_data = {
                'full_name': patient['full_name'],
                'username': patient['username'],
                'title': patient['title'],
                'mobile': patient['mobile'],
                'email': patient['email'],
                'dob': patient['dob'],
                'gender': patient['gender'],
                'blood_group': patient['blood_group'],
                'marital_status': patient['marital_status'],
                'address': patient['address'],
                'city': patient['city'],
                'pincode': patient['pincode'],
                'state': patient['state'],
                'nationality': patient['nationality'],
                'patient_id': patient['user_id'],
                'profile_completion': 85,
                'created_at': datetime.now().isoformat()
            }
            db.save_profile(patient['user_id'], profile_data)
            
        print(f"✅ Successfully inserted {len(indian_patients)} Indian patients!")
        print("Login credentials: username as shown above | password = 'password123'")
        print("\nSample login credentials:")
        print("Username: rajesh_kumar | Password: password123")
        print("Username: priya_sharma | Password: password123")
        print("Username: amit_patel | Password: password123")
        
    except Exception as e:
        print(f"❌ Error inserting patients: {e}")
        
    finally:
        db.close_connection()

if __name__ == "__main__":
    insert_patients()
