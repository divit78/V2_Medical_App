-- Create the medical_reminder_db database
CREATE DATABASE IF NOT EXISTS medical_reminder_db;
USE medical_reminder_db;

-- Users table (replaces users.json)
CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('patient', 'doctor', 'guardian') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    is_active BOOLEAN DEFAULT TRUE,
    verification_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending'
);

-- Profiles table (replaces profiles.json)
CREATE TABLE profiles (
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
    
    -- Patient specific fields
    title VARCHAR(10),
    marital_status ENUM('Single', 'Married', 'Divorced', 'Widowed'),
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'),
    patient_id VARCHAR(20),
    
    -- Doctor specific fields
    specialization VARCHAR(100),
    consultation_fee DECIMAL(10,2),
    experience INT,
    hospital_clinic VARCHAR(200),
    license_number VARCHAR(100),
    qualification TEXT,
    availability JSON,
    certificate_path VARCHAR(500),
    license_path VARCHAR(500),
    
    -- Guardian specific fields
    relationship VARCHAR(50),
    connected_patient VARCHAR(20),
    
    profile_completion INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (connected_patient) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Medicines table (replaces medicines.json)
CREATE TABLE medicines (
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
);

-- Schedules table (replaces schedules.json)
CREATE TABLE schedules (
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
);

-- Prescriptions table (replaces prescriptions.json)
CREATE TABLE prescriptions (
    prescription_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    doctor_id VARCHAR(20),
    file_path VARCHAR(500),
    notes TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Medical Tests table (replaces medical_tests.json)
CREATE TABLE medical_tests (
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
);

-- Doctor Queries table (replaces doctor_queries.json)
CREATE TABLE doctor_queries (
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
);

-- Appointments table (replaces appointments.json)
CREATE TABLE appointments (
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
);

-- Guardian Requests table (replaces guardian_requests.json)
CREATE TABLE guardian_requests (
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
);

-- Patient Doctor Requests table (replaces patient_doctor_requests.json)
CREATE TABLE patient_doctor_requests (
    request_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    doctor_id VARCHAR(20) NOT NULL,
    status ENUM('pending', 'approved', 'denied') DEFAULT 'pending',
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_profiles_patient_id ON profiles(patient_id);
CREATE INDEX idx_medicines_patient_id ON medicines(patient_id);
CREATE INDEX idx_schedules_patient_id ON schedules(patient_id);
CREATE INDEX idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX idx_medical_tests_patient_id ON medical_tests(patient_id);
CREATE INDEX idx_doctor_queries_patient_id ON doctor_queries(patient_id);
CREATE INDEX idx_doctor_queries_doctor_id ON doctor_queries(doctor_id);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
