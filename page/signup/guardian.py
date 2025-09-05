import streamlit as st
from datetime import datetime
from config.constants import USERS_FILE, PROFILES_FILE, GUARDIAN_REQUESTS_FILE
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


class GuardianSignup:
    """Main guardian signup class"""
    
    def __init__(self):
        self.validator = ValidationHelper()
    
    def render(self):
        st.markdown("#### 👨‍👩‍👧‍👦 Guardian Registration")
        
        # Simple CSS
        st.markdown("""<style>
        .guardian-info{background:#E8F5E8;padding:2rem;border-radius:15px;margin:1.5rem 0;border-left:4px solid #4CAF50}
        .success-card{background:#d4edda;border:1px solid #4CAF50;color:#155724;padding:2rem;border-radius:15px;margin:2rem 0}
        .stButton>button{background:#4CAF50!important;color:white!important;border:none!important;border-radius:10px!important}
        </style>""", unsafe_allow_html=True)
        
        # Info section
        st.markdown("""<div class="guardian-info">
        <h4>👨‍👩‍👧‍👦 About Guardian Accounts</h4>
        <p>Monitor patient medications, appointments, and medical records (with approval)</p>
        </div>""", unsafe_allow_html=True)
        
        # Form
        with st.form("guardian_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name*")
                username = st.text_input("Username*")
                mobile = st.text_input("Mobile Number*")
                email = st.text_input("Email*")
                relationship = st.selectbox("Relationship*", 
                    ["Parent", "Spouse", "Sibling", "Child", "Friend", "Caregiver", "Other"])
            
            with col2:
                patient_id = st.text_input("Patient ID/Username*", 
                    help="Ask patient for their ID or username")
                password = st.text_input("Password*", type="password")
                confirm_password = st.text_input("Confirm Password*", type="password")
                address = st.text_area("Address (optional)")
            
            # Real-time validation
            if email:
                valid, msg = self.validator.validate_email(email)
                st.success(f"✅ {msg}") if valid else st.error(f"❌ {msg}")
            
            if password:
                valid, msg = self.validator.validate_password(password)
                st.success(f"✅ {msg}") if valid else st.error(f"❌ {msg}")
            
            terms = st.checkbox("Accept Terms & Privacy Policy*")
            consent = st.checkbox("I consent to access patient data (with approval)*")
            
            submitted = st.form_submit_button("Create Guardian Account")
            
            if submitted:
                self._handle_signup(full_name, username, mobile, email, relationship,
                                  patient_id, password, confirm_password, address,
                                  terms, consent)
    
    def _handle_signup(self, full_name, username, mobile, email, relationship,
                      patient_id, password, confirm_password, address,
                      terms, consent):
        
        # Basic validation
        required = [full_name, username, mobile, email, patient_id, password]
        if not all(required) or not terms or not consent:
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
        
        # Find patient
        profiles = load_json(PROFILES_FILE)
        connected_patient_id = None
        patient_profile = None
        
        for uid, prof in profiles.items():
            if (patient_id in [prof.get('patient_id'), prof.get('username'), uid] and 
                users.get(uid, {}).get('user_type') == 'patient'):
                connected_patient_id = uid
                patient_profile = prof
                break
        
        if not connected_patient_id:
            st.error("Patient not found! Check Patient ID/Username")
            return
        
        # Create account
        try:
            guardian_id = generate_id("GUA")
            
            # Save user
            users[guardian_id] = {
                "username": username,
                "password": hash_password(password),
                "user_type": "guardian",
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            # Save profile
            profiles[guardian_id] = {
                "full_name": full_name,
                "username": username,
                "mobile": mobile,
                "email": email,
                "relationship": relationship,
                "guardian_id": guardian_id,
                "connected_patient": connected_patient_id,
                "address": address,
                "created_at": datetime.now().isoformat()
            }
            
            save_json(USERS_FILE, users)
            save_json(PROFILES_FILE, profiles)
            
            # Create guardian request
            try:
                from utils.db_helper import db
                request_id = generate_id("REQ")
                request_data = {
                    "patient_id": connected_patient_id,
                    "guardian_id": guardian_id,
                    "guardian_name": full_name,
                    "relationship": relationship,
                    "mobile": mobile,
                    "email": email,
                    "status": "pending",
                    "requested_at": datetime.now().isoformat()
                }
                
                db.connect()
                db.save_guardian_request(request_id, request_data)
                st.success("✅ Access request sent to patient!")
                
            except Exception:
                # Fallback to JSON
                guardian_requests = load_json(GUARDIAN_REQUESTS_FILE)
                if connected_patient_id not in guardian_requests:
                    guardian_requests[connected_patient_id] = []
                
                guardian_requests[connected_patient_id].append({
                    "guardian_id": guardian_id,
                    "guardian_name": full_name,
                    "relationship": relationship,
                    "mobile": mobile,
                    "email": email,
                    "status": "pending",
                    "requested_at": datetime.now().isoformat()
                })
                save_json(GUARDIAN_REQUESTS_FILE, guardian_requests)
                st.success("✅ Request sent via backup system!")
            
            # Success message
            st.markdown(f"""<div class="success-card">
            <h3>🎉 Guardian Account Created!</h3>
            <p><strong>Guardian ID:</strong> {guardian_id}</p>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Patient:</strong> {patient_profile.get('full_name', 'Unknown')}</p>
            <p><strong>Status:</strong> Pending Patient Approval</p>
            </div>""", unsafe_allow_html=True)
            
            st.balloons()
            if st.button("Go to Sign In"):
                go_to('signin')
                
        except Exception as e:
            st.error(f"Error creating account: {e}")


def guardian_signup():
    """Main entry point"""
    signup = GuardianSignup()
    signup.render()
