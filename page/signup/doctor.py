import streamlit as st
from datetime import datetime
import os
from config.constants import USERS_FILE, PROFILES_FILE, UPLOAD_DIR
from utils.auth import hash_password
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from page.navigation import go_to


class ValidationHelper:
    """Simple validation utilities"""
    
    @staticmethod
    def validate_password(pwd):
        if len(pwd) < 8 or not any(c.isdigit() for c in pwd) or not any(c.isupper() for c in pwd):
            return False, "Password needs 8+ chars, 1 digit, 1 uppercase"
        return True, "Valid password"
    
    @staticmethod
    def validate_email(email):
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Invalid email format"
        return True, "Valid email"


class FileHelper:
    """Simple file operations"""
    
    @staticmethod
    def save_file(file, user_id):
        if not file:
            return None
        folder = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        return path


class DoctorSignup:
    """Main doctor signup class"""
    
    def __init__(self):
        self.validator = ValidationHelper()
        self.file_helper = FileHelper()
    
    def render(self):
        st.markdown("""<style>
        .doctor-info{background:#E8F5E8;padding:2rem;border-radius:15px;margin:1.5rem 0;border-left:4px solid #4CAF50}
        .success-card{background:#d4edda;border:1px solid #4CAF50;color:#155724;padding:2rem;border-radius:15px;margin:2rem 0}
        .stButton>button{background:#4CAF50!important;color:white!important;border:none!important;border-radius:10px!important}
        </style>""", unsafe_allow_html=True)
        
        # Info section
        st.markdown("""<div class="doctor-info">
        <h4>🩺 Doctor Account Benefits</h4>
        <p>Connect with patients, manage consultations, access medical records</p>
        </div>""", unsafe_allow_html=True)
        
        # Form
        with st.form("doctor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name*")
                username = st.text_input("Username*")
                mobile = st.text_input("Mobile Number*")
                email = st.text_input("Email*")
                password = st.text_input("Password*", type="password")
            
            with col2:
                specialization = st.text_input("Specialization*")
                hospital = st.text_input("Hospital/Clinic*")
                experience = st.number_input("Experience (years)*", min_value=0)
                consultation_fee = st.number_input("Consultation Fee (₹)*", min_value=0, value=500)
                confirm_password = st.text_input("Confirm Password*", type="password")
            
            # Real-time validation
            if email:
                valid, msg = self.validator.validate_email(email)
                st.success(f"✅ {msg}") if valid else st.error(f"❌ {msg}")
            
            if password:
                valid, msg = self.validator.validate_password(password)
                st.success(f"✅ {msg}") if valid else st.error(f"❌ {msg}")
            
            terms = st.checkbox("Accept Terms*")
            submitted = st.form_submit_button("Sign Up")
            
            if submitted:
                self._handle_signup(full_name, username, mobile, email, password, 
                                  confirm_password, specialization, hospital, 
                                  experience, consultation_fee, terms)
    
    def _handle_signup(self, full_name, username, mobile, email, password, 
                      confirm_password, specialization, hospital, experience, 
                      consultation_fee, terms):
        
        # Basic validation
        if not all([full_name, username, mobile, email, password, specialization, hospital]) or not terms:
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
            doctor_id = generate_id("DOC")
            
            # Save user
            users[doctor_id] = {
                "username": username,
                "password": hash_password(password),
                "user_type": "doctor",
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            # Save profile
            profiles = load_json(PROFILES_FILE)
            profiles[doctor_id] = {
                "full_name": full_name,
                "username": username,
                "mobile": mobile,
                "email": email,
                "specialization": specialization,
                "hospital_clinic": hospital,
                "experience": experience,
                "consultation_fee": consultation_fee,
                "doctor_id": doctor_id,
                "created_at": datetime.now().isoformat()
            }
            
            save_json(USERS_FILE, users)
            save_json(PROFILES_FILE, profiles)
            
            # Success message
            st.markdown(f"""<div class="success-card">
            <h3>🎉 Doctor Account Created!</h3>
            <p><strong>Doctor ID:</strong> {doctor_id}</p>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Status:</strong> ✅ Active</p>
            </div>""", unsafe_allow_html=True)
            
            st.balloons()
            if st.button("Go to Sign In"):
                go_to('signin')
                
        except Exception as e:
            st.error(f"Error creating account: {e}")


def doctor_signup():
    """Main entry point"""
    signup = DoctorSignup()
    signup.render()
