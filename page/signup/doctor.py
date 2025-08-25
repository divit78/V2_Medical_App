# doctor.py - enhanced version with strict validation

import streamlit as st
from datetime import datetime
import os
from config.constants import USERS_FILE, PROFILES_FILE, UPLOAD_DIR
from utils.auth import hash_password
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from page.navigation import go_to

def is_valid_password(password):
    """STRICT password validation - ALL conditions must be met"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit (0-9)."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    special_chars = "!@#$%^&*(),.?\":{}|<>_+=[]\\/-`~"
    if not any(char in special_chars for char in password):
        return False, "Password must contain at least one special character."
    return True, "Password is valid."

def is_valid_email(email):
    """FIXED email validation - handles all edge cases properly"""
    if not email or not email.strip():
        return False, "Email address is required."
    
    email = email.strip()
    
    if '@' not in email:
        return False, "Email must contain @ symbol."
    
    if email.count('@') != 1:
        return False, "Email must contain exactly one @ symbol."
    
    try:
        parts = email.split('@')
        if len(parts) != 2:
            return False, "Email must have both username and domain parts."
        
        local, domain = parts
        
        if not local or not local.strip():
            return False, "Email must have a username part before @ symbol."
        
        if not domain or not domain.strip():
            return False, "Email must have a domain part after @ symbol."
        
        if '.' not in domain:
            return False, "Email domain must contain a dot (e.g., .com, .org)."
        
        if domain.startswith('.') or domain.endswith('.'):
            return False, "Email domain cannot start or end with a dot."
        
        if '..' in domain:
            return False, "Email domain cannot contain consecutive dots."
        
        return True, "Email is valid."
        
    except Exception:
        return False, "Invalid email format."

def get_country_codes():
    """Return dictionary of countries and their phone codes"""
    return {
        "India (+91)": "+91",
        "United States (+1)": "+1",
        "United Kingdom (+44)": "+44",
        "Canada (+1)": "+1",
        "Australia (+61)": "+61",
        "Germany (+49)": "+49",
        "France (+33)": "+33",
        "Japan (+81)": "+81",
        "China (+86)": "+86",
        "Brazil (+55)": "+55",
        "South Africa (+27)": "+27",
        "Singapore (+65)": "+65",
        "UAE (+971)": "+971",
        "Saudi Arabia (+966)": "+966",
        "Other": "Other"
    }

def save_uploaded_file(uploaded_file, user_id):
    """Save uploaded file to user's directory - original function unchanged"""
    if uploaded_file is not None:
        user_folder = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def doctor_signup():
    """Doctor registration with enhanced validation - same logic as original"""
    
    st.markdown("""
    <style>
    .stApp {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .doctor-info {
        background: linear-gradient(135deg, #E8F5E8, #C8E6C9);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 5px 20px rgba(76, 175, 80, 0.1);
    }
    
    .doctor-info h4 {
        color: #2E7D32;
        margin: 0 0 1rem 0;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .password-requirements {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid #FFC107;
        color: #856404;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .validation-error {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid #F44336;
        color: #C62828;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda, #c8e6c9);
        border: 1px solid #4CAF50;
        color: #155724;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        animation: slideInUp 0.5s ease-out;
    }
    
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50, #66BB6A) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3) !important;
    }
    
    .stFileUploader {
        background: rgba(76, 175, 80, 0.05);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(76, 175, 80, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Doctor info section
    st.markdown("""
    <div class="doctor-info">
        <h4>🩺 Doctor Account Benefits</h4>
        <p><strong>As a Doctor, you can:</strong></p>
        <ul>
            <li>👥 Connect with patients and monitor their health</li>
            <li>💊 Review and manage patient medications</li>
            <li>📅 Schedule and manage consultations</li>
            <li>📋 Access patient medical records (with permission)</li>
            <li>💼 Manage your practice and set consultation fees</li>
            <li>🏥 Build your professional network</li>
        </ul>
        <p><strong>✅ Instant Access:</strong> Your account will be activated immediately after registration.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Requirements info
    # st.markdown("""
    # <div class="password-requirements">
    #     <h5>📧 Email & Password Requirements:</h5>
    #     <ul>
    #         <li><strong>Email:</strong> Must contain @ symbol and valid domain (e.g., doctor@hospital.com)</li>
    #         <li><strong>Password:</strong> 8+ chars, 1 uppercase, 1 digit, 1 special char</li>
    #     </ul>
    #     <p><strong>Valid Examples:</strong><br>
    #     📧 Email: "doctor@hospital.com", "drsmith@clinic.org"<br>
    #     🔒 Password: "Doctor123!", "MedPass@1"</p>
    # </div>
    # """, unsafe_allow_html=True)
    
    st.markdown("#### 🩺 Doctor Registration")
    with st.form("doctor_signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name*", key="doc_full_name")
            username = st.text_input("Username*", key="doc_username")
            
            # Enhanced mobile with country code
            country_codes = get_country_codes()
            country = st.selectbox("Country*", list(country_codes.keys()), 
                                  index=0, key="doc_country")  # Default to India
            
            if country == "Other":
                country_code = st.text_input("Country Code*", placeholder="+xx", key="doc_custom_code")
            else:
                country_code = country_codes[country]
                
            mobile_number = st.text_input("Mobile Number*", 
                                        placeholder="9876543210", 
                                        help=f"Enter number for {country.split(' ')[0]}", 
                                        key="doc_mobile_num")
            
            # Enhanced email
            email = st.text_input("Email*", key="doc_email",
                                 placeholder="doctor@hospital.com", 
                                 help="Must contain @ symbol and valid domain")
        with col2:
            specialization = st.text_input("Specialization*", key="doc_specialization")
            consultation_fee = st.number_input("Consultation Fee (₹)*", min_value=0, value=500, key="doc_fee")
            experience = st.number_input("Years of Experience*", min_value=0, max_value=50, key="doc_exp")
            password = st.text_input("Password*", type="password", key="doc_password")
            confirm_password = st.text_input("Confirm Password*", type="password", key="doc_confirm_password")
        
        # Real-time validations
        if email:
            is_email_valid, email_msg = is_valid_email(email)
            if is_email_valid:
                st.success("✅ Email format is valid")
            else:
                st.error(f"❌ {email_msg}")
        
        if password:
            is_pwd_valid, pwd_msg = is_valid_password(password)
            if is_pwd_valid:
                st.success("✅ Password meets all requirements")
            else:
                st.error(f"❌ {pwd_msg}")
        
        col3, col4 = st.columns(2)
        with col3:
            hospital = st.text_input("Hospital/Clinic Name*", key="doc_hospital")
            license_num = st.text_input("Medical License Number*", key="doc_license")
            qualification = st.text_area("Qualifications*", key="doc_qualification")
        with col4:
            address = st.text_area("Practice Address*", key="doc_address")
            city = st.text_input("City*", key="doc_city")
            availability = st.multiselect("Available Days*", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], key="doc_availability")
            
        degree_file = st.file_uploader("Degree Certificate (Optional)", type=['pdf','jpg','jpeg','png'], key="doc_degree")
        license_file = st.file_uploader("Medical License (Optional)", type=['pdf','jpg','jpeg','png'], key="doc_license_file")
        
        terms = st.checkbox("Accept Terms*", key="doc_terms")
        submitted = st.form_submit_button("Sign Up")

    # YOUR ORIGINAL LOGIC WITH ENHANCED VALIDATION
    if submitted:
        # Combine mobile number with country code
        if country == "Other" and country_code:
            full_mobile = f"{country_code}{mobile_number}"
        else:
            full_mobile = f"{country_code}{mobile_number}"
        
        required = [full_name, username, email, mobile_number, specialization, hospital, license_num, qualification, address, city, password, confirm_password]
        if not all(required) or not terms:
            st.error("Fill all fields marked * and accept terms.")
            return
        
        # Email validation (CRITICAL - blocks account creation)
        is_email_valid, email_error = is_valid_email(email)
        if not is_email_valid:
            st.markdown(f"""
            <div class="validation-error">
                <h5>❌ Email Validation Failed:</h5>
                <p><strong>{email_error}</strong></p>
                <p><strong>Examples of valid emails:</strong><br>
                • doctor@hospital.com<br>
                • drsmith@clinic.org<br>
                • medical@center.net</p>
            </div>
            """, unsafe_allow_html=True)
            return  # CRITICAL: Prevents account creation
        
        # Password validation (CRITICAL - blocks account creation)
        if password != confirm_password:
            st.error("Passwords do not match!")
            return
        
        is_pwd_valid, pwd_error = is_valid_password(password)
        if not is_pwd_valid:
            st.markdown(f"""
            <div class="validation-error">
                <h5>❌ Password Requirements Not Met:</h5>
                <p><strong>{pwd_error}</strong></p>
                <p>Your password must have:<br>
                • At least 8 characters<br>
                • At least 1 uppercase letter (A-Z)<br>
                • At least 1 digit (0-9)<br>
                • At least 1 special character (!@#$%^&*)</p>
                <p><strong>Valid Examples:</strong> Doctor123!, MedPass@1, Clinic1#</p>
            </div>
            """, unsafe_allow_html=True)
            return  # CRITICAL: Prevents account creation
        
        users = load_json(USERS_FILE)
        profiles = load_json(PROFILES_FILE)
        if any(u.get('username') == username for u in users.values()):
            st.error("Username exists!")
            return
        
        try:
            doctor_id = generate_id("DOC")
            cert_path = save_uploaded_file(degree_file, doctor_id) if degree_file else None
            license_path = save_uploaded_file(license_file, doctor_id) if license_file else None
            
            users[doctor_id] = {
                "username": username,
                "password": hash_password(password),
                "user_type": "doctor",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True,
                "verification_status": "approved"  # No verification required
            }
            profiles[doctor_id] = {
                "full_name": full_name,
                "username": username,
                "mobile": full_mobile,
                "email": email,
                "country": country,
                "specialization": specialization,
                "consultation_fee": consultation_fee,
                "experience": experience,
                "hospital_clinic": hospital,
                "license_number": license_num,
                "qualification": qualification,
                "address": address,
                "city": city,
                "availability": availability,
                "doctor_id": doctor_id,
                "certificate_path": cert_path,
                "license_path": license_path,
                "profile_completion": 95,
                "created_at": datetime.now().isoformat()
            }
            
            save_json(USERS_FILE, users)
            save_json(PROFILES_FILE, profiles)
            
            st.markdown(f"""
            <div class="success-card">
                <h3>🎉 Doctor Account Created Successfully!</h3>
                <p><strong>Your Doctor ID:</strong> {doctor_id}</p>
                <p><strong>Username:</strong> {username}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Mobile:</strong> {full_mobile}</p>
                <p><strong>Specialization:</strong> {specialization}</p>
                <p><strong>Status:</strong> ✅ Active & Ready</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
            if st.button("Go to Sign In"):
                go_to('signin')
                
        except Exception as e:
            st.error(f"Failed to create doctor account: {e}")
