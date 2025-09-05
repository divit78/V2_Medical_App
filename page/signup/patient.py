import streamlit as st
from datetime import datetime, date
from config.constants import USERS_FILE, PROFILES_FILE
from utils.auth import hash_password
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from page.navigation import go_to


class ValidationHelper:
    """Simple validation utilities"""
    
    @staticmethod
    def validate_password(password):
        if len(password) < 8 or not any(c.isdigit() for c in password) or not any(c.isupper() for c in password):
            return False, "Password needs 8+ chars, 1 digit, 1 uppercase"
        return True, "Valid password"
    
    @staticmethod
    def validate_email(email):
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Invalid email format"
        return True, "Valid email"


class PatientSignup:
    """Main patient signup class"""
    
    def __init__(self):
        self.validator = ValidationHelper()
    
    def render(self):
        # Simple CSS
        st.markdown("""<style>
        .patient-info{background:#E3F2FD;padding:2rem;border-radius:15px;margin:1.5rem 0;border-left:4px solid #2196F3}
        .success-card{background:#d4edda;border:1px solid #4CAF50;color:#155724;padding:2rem;border-radius:15px;margin:2rem 0}
        .stButton>button{background:#2196F3!important;color:white!important;border:none!important;border-radius:10px!important}
        </style>""", unsafe_allow_html=True)
        
        # Info section
        st.markdown("""<div class="patient-info">
        <h4>🏥 Patient Account Benefits</h4>
        <p>Manage medications, set reminders, schedule appointments, store medical records</p>
        </div>""", unsafe_allow_html=True)
        
        st.markdown("#### 👤 Patient Registration")
        
        # Form
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name*")
                username = st.text_input("Username*")
                email = st.text_input("Email*", placeholder="user@domain.com")
                mobile = st.text_input("Mobile Number*")
                dob = st.date_input("Date of Birth*", max_value=date.today())
            
            with col2:
                gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
                blood_group = st.selectbox("Blood Group*", 
                    ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
                marital_status = st.selectbox("Marital Status*", 
                    ["Single", "Married", "Divorced", "Widowed"])
                password = st.text_input("Password*", type="password")
                confirm_password = st.text_input("Confirm Password*", type="password")
            
            # Real-time validation
            if email:
                valid, msg = self.validator.validate_email(email)
                st.success(f"✅ {msg}") if valid else st.error(f"❌ {msg}")
            
            if password:
                valid, msg = self.validator.validate_password(password)
                st.success(f"✅ {msg}") if valid else st.error(f"❌ {msg}")
            
            terms = st.checkbox("Accept Terms & Conditions*")
            submitted = st.form_submit_button("Sign Up")
            
            if submitted:
                self._handle_signup(full_name, username, email, mobile, dob, 
                                  gender, blood_group, marital_status, 
                                  password, confirm_password, terms)
    
    def _handle_signup(self, full_name, username, email, mobile, dob, 
                      gender, blood_group, marital_status, 
                      password, confirm_password, terms):
        
        # Basic validation
        required = [full_name, username, email, mobile, password]
        if not all(required) or not terms:
            st.error("Fill all required fields and accept terms")
            return
        
        if password != confirm_password:
            st.error("Passwords don't match")
            return
        
        # Email validation
        email_valid, email_msg = self.validator.validate_email(email)
        if not email_valid:
            st.error(f"Email error: {email_msg}")
            return
        
        # Password validation
        pwd_valid, pwd_msg = self.validator.validate_password(password)
        if not pwd_valid:
            st.error(f"Password error: {pwd_msg}")
            return
        
        # Check username
        users = load_json(USERS_FILE)
        if any(u.get('username') == username for u in users.values()):
            st.error("Username already exists")
            return
        
        # Create account
        try:
            patient_id = generate_id("PAT")
            
            # Save user
            users[patient_id] = {
                "username": username,
                "password": hash_password(password),
                "user_type": "patient",
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            # Save profile
            profiles = load_json(PROFILES_FILE)
            profiles[patient_id] = {
                "full_name": full_name,
                "username": username,
                "email": email,
                "mobile": mobile,
                "dob": dob.isoformat(),
                "gender": gender,
                "blood_group": blood_group,
                "marital_status": marital_status,
                "patient_id": patient_id,
                "created_at": datetime.now().isoformat()
            }
            
            save_json(USERS_FILE, users)
            save_json(PROFILES_FILE, profiles)
            
            # Success message
            st.markdown(f"""<div class="success-card">
            <h3>🎉 Patient Account Created!</h3>
            <p><strong>Patient ID:</strong> {patient_id}</p>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Blood Group:</strong> {blood_group}</p>
            </div>""", unsafe_allow_html=True)
            
            st.balloons()
            if st.button("Go to Sign In"):
                go_to('signin')
                
        except Exception as e:
            st.error(f"Error creating account: {e}")


def patient_signup():
    """Main entry point"""
    signup = PatientSignup()
    signup.render()
