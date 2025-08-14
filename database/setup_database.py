import pymysql
import os
from config.constants import DB_CONFIG

def setup_database():
    """Initialize the database with schema"""
    try:
        print("Setting up database...")
        
        # Connect without specifying database first
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(20) PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                user_type ENUM('patient', 'doctor', 'guardian') NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME NULL,
                is_active BOOLEAN DEFAULT TRUE,
                verification_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending'
            )
            ''')
            
            # Create profiles table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                user_id VARCHAR(20) PRIMARY KEY,
                full_name VARCHAR(200),
                username VARCHAR(100),
                mobile VARCHAR(20),
                alt_mobile VARCHAR(20),
                email VARCHAR(100),
                emergency_name VARCHAR(200),
                emergency_number VARCHAR(20),
                address TEXT,
                city VARCHAR(100),
                pincode VARCHAR(10),
                state VARCHAR(100),
                nationality VARCHAR(100),
                gender ENUM('Male', 'Female', 'Other') DEFAULT 'Male',
                dob DATE,
                photo_path VARCHAR(500),
                title VARCHAR(10),
                marital_status ENUM('Single', 'Married', 'Divorced', 'Widowed'),
                blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'),
                patient_id VARCHAR(20),
                specialization VARCHAR(100),
                consultation_fee DECIMAL(10,2),
                experience INT,
                hospital_clinic VARCHAR(200),
                license_number VARCHAR(100),
                qualification TEXT,
                availability JSON,
                certificate_path VARCHAR(500),
                license_path VARCHAR(500),
                relationship VARCHAR(50),
                connected_patient VARCHAR(20),
                profile_completion INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            # Create medicines table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                medicine_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                name VARCHAR(200) NOT NULL,
                contents TEXT,
                quantity INT NOT NULL,
                expiry_date DATE NOT NULL,
                purpose VARCHAR(300),
                instructions TEXT,
                take_with_food ENUM('Before Food', 'After Food', 'With Food') DEFAULT 'After Food',
                category ENUM('General', 'Antibiotic', 'Painkiller', 'Vitamin', 'Other') DEFAULT 'General',
                image_path VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            # Create schedules table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                schedule_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                medicine_id VARCHAR(20) NOT NULL,
                doses_per_day INT NOT NULL,
                times JSON,
                before_after_food ENUM('Before Eating', 'After Eating', 'With Food') DEFAULT 'After Eating',
                precaution TEXT,
                remaining_quantity INT DEFAULT 0,
                last_taken DATETIME,
                next_dose_time DATETIME,
                missed_doses INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE
            )
            ''')
            
            # Create prescriptions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions (
                prescription_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                doctor_id VARCHAR(20),
                file_path VARCHAR(500),
                notes TEXT,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
            ''')
            
            # Create medical_tests table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_tests (
                test_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                doctor_id VARCHAR(20),
                test_type VARCHAR(200),
                file_path VARCHAR(500),
                notes TEXT,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ordered_at DATETIME,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
            ''')
            
            # Create doctor_queries table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_queries (
                query_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                doctor_id VARCHAR(20),
                question TEXT NOT NULL,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                appointment_type ENUM('No Appointment', 'Video Call', 'Clinic Visit') DEFAULT 'No Appointment',
                preferred_date DATE,
                preferred_time TIME,
                status ENUM('pending', 'answered', 'cancelled') DEFAULT 'pending',
                doctor_response TEXT,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
            ''')
            
            # Create appointments table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                doctor_id VARCHAR(20) NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                type ENUM('Video Call', 'Clinic Visit') NOT NULL,
                status ENUM('scheduled', 'completed', 'cancelled', 'rescheduled') DEFAULT 'scheduled',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            # Create guardian_requests table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS guardian_requests (
                request_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                guardian_id VARCHAR(20) NOT NULL,
                guardian_name VARCHAR(200),
                relationship VARCHAR(50),
                mobile VARCHAR(20),
                email VARCHAR(100),
                status ENUM('pending', 'approved', 'denied') DEFAULT 'pending',
                requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (guardian_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            # Create patient_doctor_requests table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_doctor_requests (
                request_id VARCHAR(20) PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                doctor_id VARCHAR(20) NOT NULL,
                status ENUM('pending', 'approved', 'denied') DEFAULT 'pending',
                requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')

        connection.commit()
        print("✅ Database and tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    setup_database()
