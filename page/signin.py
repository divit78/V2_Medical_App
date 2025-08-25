import streamlit as st
from utils.auth import verify_password
from utils.file_ops import load_json, save_json  # Added missing import
from config.constants import USERS_FILE
from page.navigation import go_to
from utils.css import load_css
from datetime import datetime


def signin_page():
    load_css()
    
    # Custom CSS for sign-in page with light green theme
    signin_css = """
    <style>
        /* Background with light green color */
        .stApp {
            background: #CFEBAE !important;
            animation: none !important;
        }
        
        /* Header section with orange theme */
        .signin-header {
            text-align: center;
            background: linear-gradient(135deg, #FF8A65, #FF7043);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 10px 30px rgba(255, 138, 101, 0.3);
            animation: slideInDown 1s ease-out;
        }
        
        .signin-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: bounceIn 1.2s ease-out;
        }
        
        .signin-header p {
            font-size: 1.1rem;
            margin: 0;
            opacity: 0.95;
            animation: fadeInUp 1s ease-out 0.5s both;
        }
        
        /* User type selection styling */
        .user-type-container {
            background: rgba(255, 255, 255, 0.9);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            animation: fadeInUp 1s ease-out;
        }
        
        .user-type-card {
            background: linear-gradient(135deg, #FFE5B4 0%, #FFCC80 100%);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #FF8C00;
            animation: slideInLeft 0.8s ease-out;
        }
        
        .user-type-card h4 {
            color: #FF7043;
            margin-bottom: 0.5rem;
        }
        
        .user-type-card p {
            color: #555;
            margin: 0.2rem 0;
            font-size: 0.9rem;
        }
        
        /* Form styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid rgba(255, 140, 0, 0.3) !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border: 2px solid #FF8C00 !important;
            box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.2) !important;
            transform: translateY(-2px) !important;
        }
        
        .stTextInput > label {
            color: #FF7043 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        
        .stSelectbox > label {
            color: #FF7043 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        
        .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid rgba(255, 140, 0, 0.3) !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #FF8C00, #FFA500) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 12px 2rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3) !important;
            width: 100% !important;
            animation: buttonFloat 3s ease-in-out infinite !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(255, 140, 0, 0.5) !important;
            background: linear-gradient(135deg, #FFA500, #FF8C00) !important;
        }
        
        /* Form container styling */
        .element-container {
            animation: slideInLeft 0.8s ease-out;
        }
        
        /* Success/Error messages */
        .stAlert {
            border-radius: 10px !important;
            border-left: 4px solid #FF8C00 !important;
            animation: slideInRight 0.5s ease-out !important;
        }
        
        /* Links styling */
        .signin-links {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(255, 138, 101, 0.1);
            border-radius: 10px;
            animation: fadeIn 1.5s ease-out;
        }
        
        .signin-links a {
            color: #FF7043;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .signin-links a:hover {
            color: #FF8C00;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Welcome back section */
        .welcome-back {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #FFE5B4 0%, #FFCC80 100%);
            border-radius: 15px;
            margin-bottom: 2rem;
            color: #FF7043;
            animation: fadeIn 1.5s ease-out;
        }
        
        .welcome-back h3 {
            margin: 0;
            font-size: 1.3rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInDown {
            from {
                opacity: 0;
                transform: translateY(-50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                opacity: 1;
                transform: scale(1.05);
            }
            70% {
                transform: scale(0.9);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes buttonFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-2px); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .signin-main-container {
                margin: 1rem;
                padding: 2rem 1.5rem;
            }
            .signin-header h1 {
                font-size: 2rem;
            }
        }
    </style>
    """
    
    st.markdown(signin_css, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="signin-main-container">', unsafe_allow_html=True)
    
    # Header Section
    st.markdown("""
    <div class="signin-header">
        <h1>🔐 Welcome Back</h1>
        <p>Sign in to your Smart Medical Reminder account</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    <div class="welcome-back">
        <h3>👋 Ready to manage your health?</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # User type selection
    st.markdown('<div class="user-type-container">', unsafe_allow_html=True)
    st.markdown("### 👤 Select Your Account Type")
    
    user_type = st.selectbox(
        "Account Type",
        ["patient", "doctor", "guardian"],
        format_func=lambda x: {
            "patient": "🏥 Patient Account",
            "doctor": "👨‍⚕️ Doctor Account", 
            "guardian": "👨‍👩‍👧‍👦 Guardian Account"
        }[x]
    )
    
    # Show user type specific info
    if user_type == "patient":
        st.markdown('''
        <div class="user-type-card">
            <h4>🏥 Patient Account Features</h4>
            <p>• Manage your medications and reminders</p>
            <p>• Book appointments with doctors</p>
            <p>• Track your health records and medical tests</p>
            <p>• Connect with guardians for support</p>
        </div>
        ''', unsafe_allow_html=True)
    elif user_type == "doctor":
        st.markdown('''
        <div class="user-type-card">
            <h4>👨‍⚕️ Doctor Account Features</h4>
            <p>• Manage patient appointments and schedules</p>
            <p>• Respond to patient queries and consultations</p>
            <p>• Access patient medical records and history</p>
            <p>• Prescribe medications and order tests</p>
        </div>
        ''', unsafe_allow_html=True)
    elif user_type == "guardian":
        st.markdown('''
        <div class="user-type-card">
            <h4>👨‍👩‍👧‍👦 Guardian Account Features</h4>
            <p>• Monitor connected patient's medications</p>
            <p>• Track appointment schedules and reminders</p>
            <p>• Access medical records (with patient approval)</p>
            <p>• Receive health updates and medication alerts</p>
        </div>
        ''', unsafe_allow_html=True)
    
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
        
        # Sign-in button
        submitted = st.form_submit_button("🚀 Sign In")
        
        if submitted:
            if not username or not password:
                st.error("⚠️ Please enter both username and password.")
            else:
                # Load users data
                users = load_json(USERS_FILE)
                
                # Find user by username and user type
                user_found = None
                user_id = None
                
                for uid, user_data in users.items():
                    if (user_data.get('username') == username and 
                        user_data.get('user_type') == user_type):
                        user_found = user_data
                        user_id = uid
                        break
                
                if user_found is None:
                    st.error(f"❌ No {user_type} account found with username '{username}'. Please check your username and account type, or sign up.")
                    st.info(f"💡 Make sure you selected the correct account type: **{user_type.title()}**")
                elif not user_found.get('is_active', True):
                    st.error("❌ Your account is currently inactive. Please contact support.")
                else:
                    # Verify password
                    if verify_password(password, user_found['password']):
                        # Update last login
                        users[user_id]['last_login'] = datetime.now().isoformat()
                        save_json(USERS_FILE, users)
                        
                        # Set session state
                        st.session_state.user_id = user_id
                        st.session_state.user_type = user_type
                        
                        st.success(f"✅ Welcome back, {user_found.get('username', 'User')}!")
                        st.balloons()
                        
                        # Navigate based on user type
                        if user_type == 'patient':
                            go_to('patient_dashboard')
                        elif user_type == 'doctor':
                            go_to('doctor_dashboard')
                        elif user_type == 'guardian':
                            go_to('guardian_dashboard')
                        else:
                            go_to('landing')
                            
                    else:
                        st.error("❌ Incorrect password. Please try again.")
    
    # Additional options
    st.markdown("""
    <div class="signin-links">
        <p>🆕 Don't have an account? <strong>Create one now!</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Sign Up", key="goto_signup"):
            go_to('signup')
    
    with col2:
        if st.button("🏠 Back to Home", key="goto_home"):
            go_to('landing')
    
    # Close main container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; color: rgba(255, 255, 255, 0.8);">
        <p>🩺 Smart Medical Reminder - Your Healthcare Companion</p>
    </div>
    """, unsafe_allow_html=True)
