import pymysql
import json
from datetime import datetime
from config.constants import DB_CONFIG

class DatabaseHelper:
    def __init__(self):
        self.connection = None
    
    def connect(self, create_db_if_missing=False):
        """Establish database connection"""
        try:
            if create_db_if_missing:
                # Connect without database to create it
                temp_connection = pymysql.connect(
                    host=DB_CONFIG['host'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                with temp_connection.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
                temp_connection.close()
            
            # Now connect to the specific database
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    return cursor.rowcount
        except Exception as e:
            print(f"Query execution error: {e}")
            raise
    
    def load_users(self):
        """Load all users - replaces load_json(USERS_FILE)"""
        try:
            query = "SELECT * FROM users"
            result = self.execute_query(query)
            return {user['user_id']: user for user in result}
        except Exception:
            return {}
    
    def save_user(self, user_id, user_data):
        """Save or update user - replaces save_json for users"""
        try:
            # Patch user_data with default values for missing fields
            defaults = {
                'created_at': None,
                'last_login': None,
                'is_active': True,
                'verification_status': 'pending'
            }
            
            # Add missing fields with default values
            for key, default_val in defaults.items():
                if key not in user_data:
                    user_data[key] = default_val
            
            query = """
            INSERT INTO users (user_id, username, password, user_type, created_at, last_login, is_active, verification_status)
            VALUES (%(user_id)s, %(username)s, %(password)s, %(user_type)s, %(created_at)s, %(last_login)s, %(is_active)s, %(verification_status)s)
            ON DUPLICATE KEY UPDATE
            username=VALUES(username), password=VALUES(password), user_type=VALUES(user_type),
            last_login=VALUES(last_login), is_active=VALUES(is_active), verification_status=VALUES(verification_status)
            """
            user_data['user_id'] = user_id
            return self.execute_query(query, user_data)
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def load_profiles(self):
        """Load all profiles - replaces load_json(PROFILES_FILE)"""
        try:
            query = "SELECT * FROM profiles"
            result = self.execute_query(query)
            return {profile['user_id']: profile for profile in result}
        except Exception:
            return {}
    
    def save_profile(self, user_id, profile_data):
        """Save or update profile - replaces save_json for profiles"""
        try:
            # Patch profile_data with default values for missing fields
            defaults = {
                'full_name': None, 'username': None, 'mobile': None, 'alt_mobile': None,
                'email': None, 'emergency_name': None, 'emergency_number': None,
                'address': None, 'city': None, 'pincode': None, 'state': None,
                'nationality': None, 'gender': 'Male', 'dob': None, 'photo_path': None,
                'title': None, 'marital_status': None, 'blood_group': None,
                'patient_id': None, 'specialization': None, 'consultation_fee': None,
                'experience': None, 'hospital_clinic': None, 'license_number': None,
                'qualification': None, 'availability': None, 'certificate_path': None,
                'license_path': None, 'relationship': None, 'connected_patient': None,
                'profile_completion': 0, 'created_at': None
            }
            
            # Add missing fields with default values
            for key, default_val in defaults.items():
                if key not in profile_data:
                    profile_data[key] = default_val
            
            # Convert lists to JSON for availability field
            if 'availability' in profile_data and isinstance(profile_data['availability'], list):
                profile_data['availability'] = json.dumps(profile_data['availability'])
            
            query = """
            INSERT INTO profiles (user_id, full_name, username, mobile, alt_mobile, email, emergency_name, emergency_number,
                                 address, city, pincode, state, nationality, gender, dob, photo_path, title, marital_status,
                                 blood_group, patient_id, specialization, consultation_fee, experience, hospital_clinic,
                                 license_number, qualification, availability, certificate_path, license_path, relationship,
                                 connected_patient, profile_completion, created_at)
            VALUES (%(user_id)s, %(full_name)s, %(username)s, %(mobile)s, %(alt_mobile)s, %(email)s, %(emergency_name)s,
                    %(emergency_number)s, %(address)s, %(city)s, %(pincode)s, %(state)s, %(nationality)s, %(gender)s,
                    %(dob)s, %(photo_path)s, %(title)s, %(marital_status)s, %(blood_group)s, %(patient_id)s,
                    %(specialization)s, %(consultation_fee)s, %(experience)s, %(hospital_clinic)s, %(license_number)s,
                    %(qualification)s, %(availability)s, %(certificate_path)s, %(license_path)s, %(relationship)s,
                    %(connected_patient)s, %(profile_completion)s, %(created_at)s)
            ON DUPLICATE KEY UPDATE
            full_name=VALUES(full_name), username=VALUES(username), mobile=VALUES(mobile), alt_mobile=VALUES(alt_mobile),
            email=VALUES(email), emergency_name=VALUES(emergency_name), emergency_number=VALUES(emergency_number),
            address=VALUES(address), city=VALUES(city), pincode=VALUES(pincode), state=VALUES(state),
            nationality=VALUES(nationality), gender=VALUES(gender), dob=VALUES(dob), photo_path=VALUES(photo_path),
            title=VALUES(title), marital_status=VALUES(marital_status), blood_group=VALUES(blood_group),
            patient_id=VALUES(patient_id), specialization=VALUES(specialization), consultation_fee=VALUES(consultation_fee),
            experience=VALUES(experience), hospital_clinic=VALUES(hospital_clinic), license_number=VALUES(license_number),
            qualification=VALUES(qualification), availability=VALUES(availability), certificate_path=VALUES(certificate_path),
            license_path=VALUES(license_path), relationship=VALUES(relationship), connected_patient=VALUES(connected_patient),
            profile_completion=VALUES(profile_completion), updated_at=CURRENT_TIMESTAMP
            """
            profile_data['user_id'] = user_id
            return self.execute_query(query, profile_data)
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
    
    def load_medicines(self):
        """Load all medicines - replaces load_json(MEDICINES_FILE)"""
        try:
            query = "SELECT * FROM medicines"
            result = self.execute_query(query)
            return {medicine['medicine_id']: medicine for medicine in result}
        except Exception:
            return {}
    
    def save_medicine(self, medicine_id, medicine_data):
        """Save or update medicine - replaces save_json for medicines"""
        try:
            defaults = {
                'contents': None, 'purpose': None, 'instructions': None,
                'take_with_food': 'After Food', 'category': 'General',
                'image_path': None, 'created_at': None
            }
            
            for key, default_val in defaults.items():
                if key not in medicine_data:
                    medicine_data[key] = default_val
            
            query = """
            INSERT INTO medicines (medicine_id, patient_id, name, contents, quantity, expiry_date, purpose,
                                  instructions, take_with_food, category, image_path, created_at)
            VALUES (%(medicine_id)s, %(patient_id)s, %(name)s, %(contents)s, %(quantity)s, %(expiry_date)s,
                    %(purpose)s, %(instructions)s, %(take_with_food)s, %(category)s, %(image_path)s, %(created_at)s)
            ON DUPLICATE KEY UPDATE
            patient_id=VALUES(patient_id), name=VALUES(name), contents=VALUES(contents), quantity=VALUES(quantity),
            expiry_date=VALUES(expiry_date), purpose=VALUES(purpose), instructions=VALUES(instructions),
            take_with_food=VALUES(take_with_food), category=VALUES(category), image_path=VALUES(image_path)
            """
            medicine_data['medicine_id'] = medicine_id
            return self.execute_query(query, medicine_data)
        except Exception as e:
            print(f"Error saving medicine: {e}")
            return False
    
    def load_schedules(self):
        """Load all schedules - replaces load_json(SCHEDULES_FILE)"""
        try:
            query = "SELECT * FROM schedules"
            result = self.execute_query(query)
            for schedule in result:
                if schedule.get('times'):
                    schedule['times'] = json.loads(schedule['times']) if isinstance(schedule['times'], str) else schedule['times']
            return {schedule['schedule_id']: schedule for schedule in result}
        except Exception:
            return {}
    
    def save_schedule(self, schedule_id, schedule_data):
        """Save or update schedule - replaces save_json for schedules"""
        try:
            defaults = {
                'precaution': None, 'remaining_quantity': 0, 'last_taken': None,
                'next_dose_time': None, 'missed_doses': 0, 'created_at': None
            }
            
            for key, default_val in defaults.items():
                if key not in schedule_data:
                    schedule_data[key] = default_val
            
            if 'times' in schedule_data and isinstance(schedule_data['times'], list):
                schedule_data['times'] = json.dumps(schedule_data['times'])
            
            query = """
            INSERT INTO schedules (schedule_id, patient_id, medicine_id, doses_per_day, times, before_after_food,
                                  precaution, remaining_quantity, last_taken, next_dose_time, missed_doses, created_at)
            VALUES (%(schedule_id)s, %(patient_id)s, %(medicine_id)s, %(doses_per_day)s, %(times)s, %(before_after_food)s,
                    %(precaution)s, %(remaining_quantity)s, %(last_taken)s, %(next_dose_time)s, %(missed_doses)s, %(created_at)s)
            ON DUPLICATE KEY UPDATE
            patient_id=VALUES(patient_id), medicine_id=VALUES(medicine_id), doses_per_day=VALUES(doses_per_day),
            times=VALUES(times), before_after_food=VALUES(before_after_food), precaution=VALUES(precaution),
            remaining_quantity=VALUES(remaining_quantity), last_taken=VALUES(last_taken),
            next_dose_time=VALUES(next_dose_time), missed_doses=VALUES(missed_doses)
            """
            schedule_data['schedule_id'] = schedule_id
            return self.execute_query(query, schedule_data)
        except Exception as e:
            print(f"Error saving schedule: {e}")
            return False
    
    def load_prescriptions(self):
        """Load all prescriptions"""
        try:
            query = "SELECT * FROM prescriptions"
            result = self.execute_query(query)
            return {prescription['prescription_id']: prescription for prescription in result}
        except Exception:
            return {}
    
    def save_prescription(self, prescription_id, prescription_data):
        """Save or update prescription"""
        try:
            defaults = {
                'doctor_id': None, 'file_path': None, 'notes': None, 'uploaded_at': None
            }
            
            for key, default_val in defaults.items():
                if key not in prescription_data:
                    prescription_data[key] = default_val
            
            query = """
            INSERT INTO prescriptions (prescription_id, patient_id, doctor_id, file_path, notes, uploaded_at)
            VALUES (%(prescription_id)s, %(patient_id)s, %(doctor_id)s, %(file_path)s, %(notes)s, %(uploaded_at)s)
            ON DUPLICATE KEY UPDATE
            patient_id=VALUES(patient_id), doctor_id=VALUES(doctor_id), file_path=VALUES(file_path), 
            notes=VALUES(notes), uploaded_at=VALUES(uploaded_at)
            """
            prescription_data['prescription_id'] = prescription_id
            return self.execute_query(query, prescription_data)
        except Exception as e:
            print(f"Error saving prescription: {e}")
            return False
    
    def load_medical_tests(self):
        """Load all medical tests"""
        try:
            query = "SELECT * FROM medical_tests"
            result = self.execute_query(query)
            return {test['test_id']: test for test in result}
        except Exception:
            return {}
    
    def load_doctor_queries(self):
        """Load all doctor queries"""
        try:
            query = "SELECT * FROM doctor_queries"
            result = self.execute_query(query)
            return {query['query_id']: query for query in result}
        except Exception:
            return {}
    
    def load_appointments(self):
        """Load all appointments"""
        try:
            query = "SELECT * FROM appointments"
            result = self.execute_query(query)
            return {appointment['appointment_id']: appointment for appointment in result}
        except Exception:
            return {}
    
    def load_guardian_requests(self):
        """Load all guardian requests"""
        try:
            query = "SELECT * FROM guardian_requests"
            result = self.execute_query(query)
            grouped_requests = {}
            for request in result:
                patient_id = request['patient_id']
                if patient_id not in grouped_requests:
                    grouped_requests[patient_id] = []
                grouped_requests[patient_id].append(request)
            return grouped_requests
        except Exception:
            return {}
    
    def load_patient_doctor_requests(self):
        """Load all patient doctor requests"""
        try:
            query = "SELECT * FROM patient_doctor_requests"
            result = self.execute_query(query)
            return {request['request_id']: request for request in result}
        except Exception:
            return {}
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

# Create global instance
db = DatabaseHelper()
