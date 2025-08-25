import streamlit as st
from datetime import datetime, date
from config.constants import USERS_FILE, PROFILES_FILE
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

def patient_signup():
    """Patient registration with enhanced validation - same logic as original"""
    
    # Enhanced CSS styling
    st.markdown("""
    <style>
    .stApp {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .patient-info {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 4px solid #2196F3;
        box-shadow: 0 5px 20px rgba(33, 150, 243, 0.1);
    }
    
    .patient-info h4 {
        color: #1565C0;
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
    
    .password-requirements h5 {
        margin: 0 0 1rem 0;
        color: #B8860B;
        font-size: 1.1rem;
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
        background: linear-gradient(135deg, #2196F3, #64B5F6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Patient information section
    st.markdown("""
    <div class="patient-info">
        <h4>🏥 Patient Account Benefits</h4>
        <p><strong>As a Patient, you can:</strong></p>
        <ul>
            <li>💊 Manage all your medications and prescriptions</li>
            <li>⏰ Set up smart medication reminders</li>
            <li>📅 Schedule and track medical appointments</li>
            <li>📋 Store and access your medical records</li>
            <li>👨‍👩‍👧‍👦 Connect with trusted guardians and family members</li>
        </ul>
        <p><strong>🔒 Your Privacy:</strong> All your health data is encrypted and secure.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Requirements info
    # st.markdown("""
    # <div class="password-requirements">
    #     <h5>📧 Email & Password Requirements:</h5>
    #     <ul>
    #         <li><strong>Email:</strong> Must contain @ symbol and valid domain (e.g., user@domain.com)</li>
    #         <li><strong>Password:</strong> 8+ chars, 1 uppercase, 1 digit, 1 special char</li>
    #     </ul>
    #     <p><strong>Valid Examples:</strong><br>
    #     📧 Email: "john@gmail.com", "user@company.org"<br>
    #     🔒 Password: "Patient123!", "MyHealth@1"</p>
    # </div>
    # """, unsafe_allow_html=True)
    
    st.markdown("#### 👤 Patient Registration")
    with st.form("patient_signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*", key="pat_full_name")
            title = st.selectbox("Title*", ["Mr.", "Mrs.", "Ms.", "Dr.", "Master"], key="pat_title")
            username = st.text_input("Username*", key="pat_username")
            
            # Enhanced email field
            email = st.text_input("Email Address*", key="pat_email", 
                                 placeholder="example@domain.com", 
                                 help="Must contain @ symbol and valid domain")
            
            dob = st.date_input("Date of Birth*", max_value=date.today(), key="pat_dob")
        
        with col2:
            marital_status = st.selectbox("Marital Status*", ["Single","Married","Divorced","Widowed"], key="pat_marital")
            blood_group = st.selectbox("Blood Group*", ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"], key="pat_blood")
            gender = st.selectbox("Gender*", ["Male","Female","Other","Prefer not to say"], key="pat_gender")
            
            # Enhanced mobile with country code
            country_codes = get_country_codes()
            country = st.selectbox("Country*", list(country_codes.keys()), 
                                  index=0, key="pat_country")  # Default to India (+91)
            
            if country == "Other":
                country_code = st.text_input("Country Code*", placeholder="+xx", key="pat_custom_code")
            else:
                country_code = country_codes[country]
            
            mobile_number = st.text_input("Mobile Number*", 
                                        placeholder="9876543210", 
                                        help=f"Enter number for {country.split(' ')[0]}", 
                                        key="pat_mobile_num")
        
        # Password fields
        st.markdown("---")
        st.subheader("🔐 Account Security")
        
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Password*", type="password", key="pat_password")
        with col4:
            confirm_password = st.text_input("Confirm Password*", type="password", key="pat_confirm_password")
        
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
        
        terms = st.checkbox("Accept Terms & Conditions*", key="pat_terms")
        submitted = st.form_submit_button("Sign Up")

    # YOUR ORIGINAL LOGIC WITH ENHANCED VALIDATION
    if submitted:
        # Combine mobile number with country code
        if country == "Other" and country_code:
            full_mobile = f"{country_code}{mobile_number}"
        else:
            full_mobile = f"{country_code}{mobile_number}"
        
        # Step 1: Check required fields
        if not all([full_name, username, email, mobile_number, password, confirm_password]):
            st.error("Fill all fields marked *")
            return
        
        # Step 2: Email validation (CRITICAL - blocks account creation)
        is_email_valid, email_error = is_valid_email(email)
        if not is_email_valid:
            st.markdown(f"""
            <div class="validation-error">
                <h5>❌ Email Validation Failed:</h5>
                <p><strong>{email_error}</strong></p>
                <p><strong>Examples of valid emails:</strong><br>
                • user@gmail.com<br>
                • john.doe@company.org<br>
                • contact@example.net</p>
            </div>
            """, unsafe_allow_html=True)
            return  # CRITICAL: Prevents account creation
        
        # Step 3: Password validation (CRITICAL - blocks account creation)
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
                <p><strong>Valid Examples:</strong> Patient123!, MyHealth@1, SecurePass1#</p>
            </div>
            """, unsafe_allow_html=True)
            return  # CRITICAL: Prevents account creation
        
        # Step 4: Password match check
        if password != confirm_password:
            st.error("Passwords do not match!")
            return
        
        # Step 5: Terms acceptance
        if not terms:
            st.error("Please accept the terms.")
            return
        
        # Step 6: Check existing users
        users = load_json(USERS_FILE)
        profiles = load_json(PROFILES_FILE)
        if any(u.get('username') == username for u in users.values()):
            st.error("Username exists!")
            return
        
        # Step 7: Create account ONLY if all validations pass
        try:
            patient_id = generate_id("PAT")
            users[patient_id] = {
                "username": username,
                "password": hash_password(password),
                "user_type": "patient",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True
            }
            
            profiles[patient_id] = {
                "full_name": full_name,
                "title": title,
                "username": username,
                "email": email,
                "mobile": full_mobile,
                "country": country,
                "dob": dob.isoformat(),
                "marital_status": marital_status,
                "blood_group": blood_group,
                "gender": gender,
                "patient_id": patient_id,
                "profile_completion": 80,
                "created_at": datetime.now().isoformat(),
                "city": ""  # For optional search functionality later
            }
            
            save_json(USERS_FILE, users)
            save_json(PROFILES_FILE, profiles)
            
            st.markdown(f"""
            <div class="success-card">
                <h3>🎉 Patient Account Created Successfully!</h3>
                <p><strong>Your Patient ID:</strong> {patient_id}</p>
                <p><strong>Username:</strong> {username}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Mobile:</strong> {full_mobile}</p>
                <p><strong>Blood Group:</strong> {blood_group}</p>
                <p><strong>Security:</strong> ✅ All requirements met</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
            
            if st.button("Go to Sign In"):
                go_to('signin')
                
        except Exception as e:
            st.error(f"Failed to create account: {e}")
