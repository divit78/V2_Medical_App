import streamlit as st
from .patient import patient_signup
from .doctor import doctor_signup
from .guardian import guardian_signup
from utils.css import load_css
from page.navigation import go_to


class UserTypeInfo:
    """Simple class for user type information"""
    def __init__(self, title, description, features):
        self.title = title
        self.description = description
        self.features = features
    
    def render_description(self):
        return f'<div class="user-type-description"><strong>{self.title}</strong> {self.description}</div>'
    
    def render_features(self):
        features_html = ''.join([f'<li>{feature}</li>' for feature in self.features])
        return f'<div class="feature-highlights"><h4>🌟 Key Features:</h4><ul>{features_html}</ul></div>'


class SignupPage:
    """Main signup page class"""
    
    def __init__(self):
        self.user_types = {
            "Patient": UserTypeInfo(
                "👤 Patient Account:",
                "Manage medications, set reminders, connect with doctors, and track health.",
                [
                    "Smart medication reminders",
                    "Doctor consultation booking", 
                    "Health analytics dashboard",
                    "Digital prescription management"
                ]
            ),
            "Doctor": UserTypeInfo(
                "👨‍⚕️ Doctor Account:",
                "Connect with patients, manage appointments, and provide medical guidance.",
                [
                    "Patient connection management",
                    "Appointment scheduling tools",
                    "Patient query responses",
                    "Professional profile showcase"
                ]
            ),
            "Guardian": UserTypeInfo(
                "👨‍👩‍👧‍👦 Guardian Account:",
                "Monitor and support loved one's health with patient-approved access.",
                [
                    "Medication monitoring",
                    "Health status updates",
                    "Emergency coordination",
                    "Care coordination tools"
                ]
            )
        }
        
        self.signup_functions = {
            "Patient": patient_signup,
            "Doctor": doctor_signup,
            "Guardian": guardian_signup
        }
    
    def render(self):
        """Render the signup page"""
        load_css()
        self._load_styles()
        
        # Header
        self._render_header()
        
        # User type selection
        user_type = self._render_user_type_selector()
        
        # User type info
        self._render_user_type_info(user_type)
        
        # Signup form
        self._render_signup_form(user_type)
        
        # Navigation
        self._render_navigation()
        
        # Footer
        self._render_footer()
    
    def _load_styles(self):
        """Load CSS styles"""
        st.markdown("""<style>
        .stApp{background:linear-gradient(135deg,#e8f5e8 0%,#f0fff0 50%,#e0f2e1 100%)!important;font-family:'Inter','Segoe UI',sans-serif}
        .signup-header{text-align:center;background:linear-gradient(135deg,#4CAF50,#66BB6A);padding:3rem 2rem;border-radius:20px;margin-bottom:2rem;color:white;box-shadow:0 15px 40px rgba(76,175,80,0.3)}
        .signup-header h1{font-size:3rem;margin-bottom:0.5rem;text-shadow:2px 2px 4px rgba(0,0,0,0.2);font-weight:700}
        .signup-header p{font-size:1.3rem;margin:0;opacity:0.95;font-weight:400}
        .stSelectbox>div>div{background:rgba(255,255,255,0.95)!important;border:2px solid rgba(76,175,80,0.3)!important;border-radius:12px!important}
        .stSelectbox>label{color:#2E7D32!important;font-weight:600!important;font-size:1.2rem!important}
        .stButton>button{background:linear-gradient(135deg,#4CAF50,#66BB6A)!important;color:white!important;border:none!important;border-radius:12px!important;padding:14px 2rem!important;font-size:1.2rem!important;font-weight:600!important;width:100%!important}
        .user-type-description{background:rgba(255,255,255,0.95);padding:1.5rem;border-radius:12px;margin:1.5rem 0;border-left:4px solid #4CAF50}
        .feature-highlights{background:rgba(255,255,255,0.9);padding:2rem;border-radius:15px;margin:2rem 0;border-left:4px solid #4CAF50}
        .feature-highlights h4{color:#2E7D32;margin-bottom:1.5rem;font-size:1.3rem;font-weight:600}
        .feature-highlights ul{list-style:none;padding:0}
        .feature-highlights li{margin:0.8rem 0;color:#1B5E20;padding-left:2rem;position:relative}
        .feature-highlights li:before{content:"🌟 ";position:absolute;left:0;color:#4CAF50;font-weight:bold}
        .signup-navigation{text-align:center;margin-top:2rem;padding:2rem;background:rgba(76,175,80,0.08);border-radius:15px}
        .footer-section{text-align:center;margin-top:3rem;padding:2rem;background:rgba(76,175,80,0.05);border-radius:15px}
        </style>""", unsafe_allow_html=True)
    
    def _render_header(self):
        """Render page header"""
        st.markdown("""<div class="signup-header">
            <h1>📝 Create Account</h1>
            <p>Join Smart Medical Reminder - Your Healthcare Journey Starts Here!</p>
        </div>""", unsafe_allow_html=True)
    
    def _render_user_type_selector(self):
        """Render user type selector"""
        return st.selectbox(
            "Select your account type:", 
            ["Patient", "Doctor", "Guardian"], 
            help="Choose the type of account you want to create"
        )
    
    def _render_user_type_info(self, user_type):
        """Render user type information"""
        if user_type in self.user_types:
            user_info = self.user_types[user_type]
            st.markdown(user_info.render_description(), unsafe_allow_html=True)
            st.markdown(user_info.render_features(), unsafe_allow_html=True)
    
    def _render_signup_form(self, user_type):
        """Render signup form"""
        if user_type in self.signup_functions:
            self.signup_functions[user_type]()
    
    def _render_navigation(self):
        """Render navigation section"""
        st.markdown("""<div class="signup-navigation">
            <h4>🔄 Already have an account?</h4>
            <p>Sign in to access your Smart Medical Reminder dashboard</p>
        </div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔐 Sign In", key="goto_signin"):
                go_to('signin')
        
        with col2:
            if st.button("🏠 Back to Home", key="goto_home"):
                go_to('landing')
    
    def _render_footer(self):
        """Render footer"""
        st.markdown("""<div class="footer-section">
            <p><strong>🩺 Smart Medical Reminder</strong></p>
            <p>Secure • Private • Trusted by Healthcare Professionals</p>
        </div>""", unsafe_allow_html=True)


def signup_page():
    """Main entry point"""
    page = SignupPage()
    page.render()
