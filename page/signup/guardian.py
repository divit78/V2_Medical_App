import streamlit as st
from datetime import datetime
from config.constants import USERS_FILE, PROFILES_FILE, GUARDIAN_REQUESTS_FILE
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

def guardian_signup():
    """Guardian signup with enhanced validation - same logic as original"""
    st.markdown("#### 👨‍👩‍👧‍👦 Guardian Registration")
    
    st.markdown("""
    <style>
    .stApp {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .guardian-info {
        background: linear-gradient(135deg, #E8F5E8, #C8E6C9);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 5px 20px rgba(76, 175, 80, 0.1);
    }
    
    .guardian-info h4 {
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
    </style>
    """, unsafe_allow_html=True)
    
    # Guardian info section
    st.markdown("""
    <div class="guardian-info">
        <h4>👨‍👩‍👧‍👦 About Guardian Accounts</h4>
        <p><strong>As a Guardian, you can:</strong></p>
        <ul>
            <li>🔍 Monitor your patient's medication schedules and adherence</li>
            <li>📅 View appointment history and upcoming medical visits</li>
            <li>📋 Access medical records and test results (with approval)</li>
            <li>📊 Generate health reports and track progress</li>
        </ul>
        <p><strong>Privacy Protection:</strong> Patient must approve your access request before you can view their data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Requirements info
    # st.markdown("""
    # <div class="password-requirements">
    #     <h5>📧 Email & Password Requirements:</h5>
    #     <ul>
    #         <li><strong>Email:</strong> Must contain @ symbol and valid domain (e.g., guardian@domain.com)</li>
    #         <li><strong>Password:</strong> 8+ chars, 1 uppercase, 1 digit, 1 special char</li>
    #     </ul>
    #     <p><strong>Valid Examples:</strong><br>
    #     📧 Email: "parent@gmail.com", "care@family.org"<br>
    #     🔒 Password: "Guardian123!", "Family@1"</p>
    # </div>
    # """, unsafe_allow_html=True)
    
    with st.form("guardian_signup_form"):
        st.subheader("👤 Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*", key="gua_full_name")
            username = st.text_input("Username*", key="gua_username")
            
            # Enhanced mobile with country code
            country_codes = get_country_codes()
            country = st.selectbox("Country*", list(country_codes.keys()), 
                                  index=0, key="gua_country")  # Default to India
            
            if country == "Other":
                country_code = st.text_input("Country Code*", placeholder="+xx", key="gua_custom_code")
            else:
                country_code = country_codes[country]
                
            mobile_number = st.text_input("Mobile Number*", 
                                        placeholder="9876543210", 
                                        help=f"Enter number for {country.split(' ')[0]}", 
                                        key="gua_mobile_num")
            
            # Enhanced email
            email = st.text_input("Email Address*", key="gua_email",
                                 placeholder="guardian@domain.com", 
                                 help="Must contain @ symbol and valid domain")
        
        with col2:
            relationship = st.selectbox(
                "Relationship to Patient*",
                ["Select Relationship", "Parent", "Spouse", "Sibling", "Child", "Friend", "Caregiver", "Relative", "Other"],
                key="gua_relationship"
            )
            emergency_contact = st.text_input("Emergency Contact", key="gua_emergency_contact")
            address = st.text_area("Address", key="gua_address", height=100)
        
        # Real-time validations
        if email:
            is_email_valid, email_msg = is_valid_email(email)
            if is_email_valid:
                st.success("✅ Email format is valid")
            else:
                st.error(f"❌ {email_msg}")
        
        st.markdown("---")
        st.subheader("🔗 Patient Connection")
        
        patient_id_username = st.text_input(
            "Patient ID or Username to Connect*", 
            key="gua_patient_id",
            help="Ask the patient for their exact ID, username, or registered mobile number"
        )
        
        st.markdown("---")
        st.subheader("🔐 Account Security")
        col3, col4 = st.columns(2)
        
        with col3:
            password = st.text_input("Password*", type="password", key="gua_password")
        
        with col4:
            confirm_password = st.text_input("Confirm Password*", type="password", key="gua_confirm_password")
        
        if password:
            is_pwd_valid, pwd_msg = is_valid_password(password)
            if is_pwd_valid:
                st.success("✅ Password meets all requirements")
            else:
                st.error(f"❌ {pwd_msg}")
        
        st.markdown("---")
        st.subheader("📋 Terms and Conditions")
        
        terms = st.checkbox("I accept the Terms & Conditions and Privacy Policy*", key="gua_terms")
        consent = st.checkbox("I consent to access patient health data (subject to patient approval)*", key="gua_consent")
        privacy = st.checkbox("I understand that I will only view, not modify, patient data*", key="gua_privacy")
        
        submitted = st.form_submit_button("🔐 Create Guardian Account", type="primary", use_container_width=True)
        
        # YOUR ORIGINAL LOGIC WITH ENHANCED VALIDATION
        if submitted:
            # Combine mobile number with country code
            if country == "Other" and country_code:
                full_mobile = f"{country_code}{mobile_number}"
            else:
                full_mobile = f"{country_code}{mobile_number}"
            
            validation_errors = []
            
            required_fields = {
                'full_name': full_name,
                'username': username,
                'mobile': mobile_number,
                'email': email,
                'patient_id_username': patient_id_username,
                'password': password,
                'confirm_password': confirm_password
            }
            
            for field_name, field_value in required_fields.items():
                if not field_value or not field_value.strip():
                    validation_errors.append(f"Please fill in {field_name.replace('_', ' ')}")
            
            if relationship == "Select Relationship":
                validation_errors.append("Please select your relationship to the patient")
            
            # Email validation (CRITICAL - blocks account creation)
            is_email_valid, email_error = is_valid_email(email)
            if not is_email_valid:
                validation_errors.append(email_error)
            
            # Password validation (CRITICAL - blocks account creation)
            is_pwd_valid, pwd_error = is_valid_password(password)
            if not is_pwd_valid:
                validation_errors.append(pwd_error)
            
            if password != confirm_password:
                validation_errors.append("Passwords do not match")
            
            if not all([terms, consent, privacy]):
                validation_errors.append("Please accept all terms, consent, and privacy acknowledgments")
            
            if validation_errors:
                st.error("❌ Please fix the following errors:")
                for error in validation_errors:
                    st.write(f"• {error}")
                return  # CRITICAL: Prevents account creation
            
            # YOUR ORIGINAL ACCOUNT CREATION LOGIC
            users = load_json(USERS_FILE)
            profiles = load_json(PROFILES_FILE)
            
            if any(u.get('username') == username for u in users.values()):
                st.error("❌ Username already exists! Please choose a different one.")
                return
            
            if any(p.get('email') == email for p in profiles.values()):
                st.error("❌ Email already registered! Please use a different email.")
                return
            
            # Find patient by multiple criteria
            connected_patient_id = None
            patient_profile = None
            
            for uid, prof in profiles.items():
                if (patient_id_username in [
                    prof.get('patient_id'), 
                    prof.get('username'), 
                    prof.get('mobile'),
                    uid
                ] and users.get(uid, {}).get('user_type') == 'patient'):
                    connected_patient_id = uid
                    patient_profile = prof
                    break
            
            if not connected_patient_id:
                st.error("❌ Patient not found! Please check the Patient ID, username, or mobile number.")
                
                patients = [(prof.get('full_name'), prof.get('username'), prof.get('mobile'), uid) 
                           for uid, prof in profiles.items() 
                           if users.get(uid, {}).get('user_type') == 'patient']
                
                if patients:
                    with st.expander("🔍 Available Patients (for reference)"):
                        st.write("Ask the patient for one of these details:")
                        for name, uname, mob, pid in patients[:3]:
                            st.write(f"• **{name}** - Username: `{uname}`, Mobile: `{mob}`, ID: `{pid}`")
                
                return
            
            # Create guardian account
            guardian_id = generate_id("GUA")
            
            try:
                users[guardian_id] = {
                    "username": username,
                    "password": hash_password(password),
                    "user_type": "guardian",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "is_active": True,
                    "verification_status": "approved"
                }
                
                profiles[guardian_id] = {
                    "full_name": full_name,
                    "username": username,
                    "mobile": full_mobile,
                    "email": email,
                    "country": country,
                    "relationship": relationship,
                    "guardian_id": guardian_id,
                    "connected_patient": connected_patient_id,
                    "emergency_contact": emergency_contact,
                    "address": address,
                    "profile_completion": 90,
                    "created_at": datetime.now().isoformat()
                }
                
                save_json(USERS_FILE, users)
                save_json(PROFILES_FILE, profiles)
                
                st.success("✅ Guardian account created successfully!")
                
                # YOUR ORIGINAL REQUEST CREATION LOGIC
                try:
                    from utils.db_helper import db
                    
                    request_id = generate_id("REQ")
                    request_data = {
                        "patient_id": connected_patient_id,
                        "guardian_id": guardian_id,
                        "guardian_name": full_name,
                        "relationship": relationship,
                        "mobile": full_mobile,
                        "email": email,
                        "status": "pending",
                        "requested_at": datetime.now().isoformat()
                    }
                    
                    db.connect()
                    result = db.save_guardian_request(request_id, request_data)
                    
                    if result:
                        st.success("✅ Access request sent to patient for approval!")
                        st.balloons()
                        
                        st.markdown(f"""
                        <div class="success-card">
                            <h3>🎉 Guardian Account Created Successfully!</h3>
                            <p><strong>Your Guardian ID:</strong> {guardian_id}</p>
                            <p><strong>Username:</strong> {username}</p>
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Mobile:</strong> {full_mobile}</p>
                            <p><strong>Patient:</strong> {patient_profile.get('full_name', 'Unknown')}</p>
                            <p><strong>Status:</strong> Pending Patient Approval</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Go to Sign In"):
                            go_to('signin')
                            
                except Exception as e:
                    # YOUR ORIGINAL FALLBACK LOGIC
                    guardian_requests = load_json(GUARDIAN_REQUESTS_FILE)
                    if connected_patient_id not in guardian_requests:
                        guardian_requests[connected_patient_id] = []
                    
                    guardian_requests[connected_patient_id].append({
                        "guardian_id": guardian_id,
                        "guardian_name": full_name,
                        "relationship": relationship,
                        "mobile": full_mobile,
                        "email": email,
                        "status": "pending",
                        "requested_at": datetime.now().isoformat()
                    })
                    
                    save_json(GUARDIAN_REQUESTS_FILE, guardian_requests)
                    st.success("✅ Request sent successfully via backup system!")
                    
                    st.markdown(f"""
                    <div class="success-card">
                        <h3>🎉 Guardian Account Created Successfully!</h3>
                        <p><strong>Your Guardian ID:</strong> {guardian_id}</p>
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Patient:</strong> {patient_profile.get('full_name', 'Unknown')}</p>
                        <p><strong>Status:</strong> Pending Patient Approval</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Go to Sign In"):
                        go_to('signin')
                    
            except Exception as e:
                st.error(f"❌ Failed to create guardian account: {e}")
