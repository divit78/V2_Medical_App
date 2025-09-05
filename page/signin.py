import streamlit as st
from utils.auth import verify_password
from utils.file_ops import load_json, save_json
from config.constants import USERS_FILE
from page.navigation import go_to
from utils.css import load_css
from datetime import datetime


class UserTypeInfo:
    """Simple class for user type information"""
    def __init__(self, title, features):
        self.title = title
        self.features = features
    
    def render(self):
        features_html = ''.join([f'<p>{feature}</p>' for feature in self.features])
        return f'<div class="user-type-card"><h4>{self.title}</h4>{features_html}</div>'


class AuthenticationService:
    """Handle authentication logic"""
    
    @staticmethod
    def authenticate_user(username, password, user_type):
        """Authenticate user and return result"""
        users = load_json(USERS_FILE)
        
        # Find user
        for uid, user_data in users.items():
            if (user_data.get('username') == username and 
                user_data.get('user_type') == user_type):
                
                # Check if account is active
                if not user_data.get('is_active', True):
                    return {'success': False, 'error': 'inactive', 'message': 'Account is inactive'}
                
                # Check password
                if verify_password(password, user_data['password']):
                    # Update last login
                    users[uid]['last_login'] = datetime.now().isoformat()
                    save_json(USERS_FILE, users)
                    
                    return {
                        'success': True, 
                        'user_id': uid, 
                        'user_type': user_type,
                        'username': user_data.get('username', 'User')
                    }
                else:
                    return {'success': False, 'error': 'password', 'message': 'Incorrect password'}
        
        return {'success': False, 'error': 'not_found', 'message': f'No {user_type} account found'}


class SignInPage:
    """Main sign-in page class"""
    
    def __init__(self):
        self.auth_service = AuthenticationService()
        self.user_type_info = {
            "patient": UserTypeInfo("🏥 Patient Account Features", [
                "• Manage your medications and reminders",
                "• Book appointments with doctors", 
                "• Track your health records and medical tests",
                "• Connect with guardians for support"
            ]),
            "doctor": UserTypeInfo("👨‍⚕️ Doctor Account Features", [
                "• Manage patient appointments and schedules",
                "• Respond to patient queries and consultations",
                "• Access patient medical records and history",
                "• Prescribe medications and order tests"
            ]),
            "guardian": UserTypeInfo("👨‍👩‍👧‍👦 Guardian Account Features", [
                "• Monitor connected patient's medications",
                "• Track appointment schedules and reminders",
                "• Access medical records (with patient approval)",
                "• Receive health updates and medication alerts"
            ])
        }
    
    def render(self):
        """Render the sign-in page"""
        load_css()
        self._load_styles()
        
        # Header
        self._render_header()
        
        # Welcome message
        self._render_welcome()
        
        # Sign-in form
        self._render_signin_form()
        
        # Navigation links
        self._render_navigation()
        
        # Footer
        self._render_footer()
    
    def _load_styles(self):
        st.markdown("""<style>
        .stApp{background:#CFEBAE!important}
        .signin-header{text-align:center;background:linear-gradient(135deg,#FF8A65,#FF7043);padding:2rem;border-radius:15px;margin-bottom:2rem;color:white;box-shadow:0 10px 30px rgba(255,138,101,0.3)}
        .signin-header h1{font-size:2.5rem;margin-bottom:0.5rem;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
        .signin-header p{font-size:1.1rem;margin:0;opacity:0.95}
        # .user-type-container{background:rgba(255,255,255,0.9);padding:1.5rem;border-radius:15px;margin-bottom:2rem;box-shadow:0 5px 15px rgba(0,0,0,0.1)}
        .user-type-card{background:linear-gradient(135deg,#FFE5B4 0%,#FFCC80 100%);padding:1rem;border-radius:10px;margin:1rem 0;border-left:4px solid #FF8C00}
        .user-type-card h4{color:#FF7043;margin-bottom:0.5rem}
        .user-type-card p{color:#555;margin:0.2rem 0;font-size:0.9rem}
        .stTextInput>div>div>input{background:rgba(255,255,255,0.9)!important;border:2px solid rgba(255,140,0,0.3)!important;border-radius:10px!important;padding:12px 16px!important}
        .stTextInput>div>div>input:focus{border:2px solid #FF8C00!important;box-shadow:0 0 0 3px rgba(255,140,0,0.2)!important}
        .stButton>button{background:linear-gradient(135deg,#FF8C00,#FFA500)!important;color:white!important;border:none!important;border-radius:25px!important;padding:12px 2rem!important;font-size:1.1rem!important;font-weight:bold!important;width:100%!important}
        .stButton>button:hover{transform:translateY(-3px) scale(1.02)!important;box-shadow:0 8px 25px rgba(255,140,0,0.5)!important}
        .welcome-back{text-align:center;padding:1.5rem;background:linear-gradient(135deg,#FFE5B4 0%,#FFCC80 100%);border-radius:15px;margin-bottom:2rem;color:#FF7043}
        .signin-links{text-align:center;margin-top:2rem;padding:1rem;background:rgba(255,138,101,0.1);border-radius:10px}
        </style>""", unsafe_allow_html=True)
    
    def _render_header(self):
        st.markdown("""<div class="signin-header">
            <h1>🔐 Welcome Back</h1>
            <p>Sign in to your Smart Medical Reminder account</p>
        </div>""", unsafe_allow_html=True)
    
    def _render_welcome(self):
        st.markdown("""<div class="welcome-back">
            <h3>👋 Ready to manage your health?</h3>
        </div>""", unsafe_allow_html=True)
    
    def _render_signin_form(self):
        # User type selection
        st.markdown('<div class="user-type-container">', unsafe_allow_html=True)
        st.markdown("### 👤 Select Your Account Type")
        
        user_type_options = {
            "patient": "🏥 Patient Account",
            "doctor": "👨‍⚕️ Doctor Account", 
            "guardian": "👨‍👩‍👧‍👦 Guardian Account"
        }
        
        user_type = st.selectbox(
            "Account Type", 
            ["patient", "doctor", "guardian"], 
            format_func=lambda x: user_type_options[x]
        )
        
        # Show user type info
        if user_type in self.user_type_info:
            st.markdown(self.user_type_info[user_type].render(), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sign-in form
        with st.form("signin_form"):
            st.markdown("### 📧 Enter Your Credentials")
            
            username = st.text_input(
                "Username", 
                placeholder="Enter your username",
                help=f"Use the username you registered with for your {user_type} account"
            )
            
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                help="Enter your account password"
            )
            
            submitted = st.form_submit_button("🚀 Sign In")
            
            if submitted:
                self._handle_signin(username, password, user_type)
    
    def _handle_signin(self, username, password, user_type):
        """Handle sign-in form submission"""
        if not username or not password:
            st.error("⚠️ Please enter both username and password.")
            return
        
        # Authenticate user
        result = self.auth_service.authenticate_user(username, password, user_type)
        
        if result['success']:
            # Set session state
            st.session_state.user_id = result['user_id']
            st.session_state.user_type = result['user_type']
            
            st.success(f"✅ Welcome back, {result['username']}!")
            st.balloons()
            
            # Navigate to appropriate dashboard
            navigation_map = {
                'patient': 'patient_dashboard',
                'doctor': 'doctor_dashboard', 
                'guardian': 'guardian_dashboard'
            }
            go_to(navigation_map.get(user_type, 'landing'))
        else:
            # Handle different error types
            if result['error'] == 'not_found':
                st.error(f"❌ No {user_type} account found with username '{username}'. Please check your username and account type, or sign up.")
                st.info(f"💡 Make sure you selected the correct account type: **{user_type.title()}**")
            elif result['error'] == 'inactive':
                st.error("❌ Your account is currently inactive. Please contact support.")
            elif result['error'] == 'password':
                st.error("❌ Incorrect password. Please try again.")
    
    def _render_navigation(self):
        st.markdown("""<div class="signin-links">
            <p>🆕 Don't have an account? <strong>Create one now!</strong></p>
        </div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Sign Up", key="goto_signup"):
                go_to('signup')
        with col2:
            if st.button("🏠 Back to Home", key="goto_home"):
                go_to('landing')
    
    def _render_footer(self):
        st.markdown('''<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: rgba(255, 255, 255, 0.8);">
            <p>🩺 Smart Medical Reminder - Your Healthcare Companion</p>
        </div>''', unsafe_allow_html=True)


def signin_page():
    """Main entry point"""
    page = SignInPage()
    page.render()


if __name__ == "__main__":
    signin_page()
