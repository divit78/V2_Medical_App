import streamlit as st
from .patient import patient_signup
from .doctor import doctor_signup
from .guardian import guardian_signup
from utils.css import load_css
from page.navigation import go_to

def signup_page():
    """Main signup page with enhanced healthcare styling - same logic as original"""
    load_css()
    
    # Enhanced CSS with healthcare green theme
    signup_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0fff0 50%, #e0f2e1 100%) !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        animation: none !important;
    }
    
    .signup-header {
        text-align: center;
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 15px 40px rgba(76, 175, 80, 0.3);
        animation: slideInDown 1s ease-out;
    }
    
    .signup-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        font-weight: 700;
        animation: bounceIn 1.2s ease-out;
    }
    
    .signup-header p {
        font-size: 1.3rem;
        margin: 0;
        opacity: 0.95;
        font-weight: 400;
        animation: fadeInUp 1s ease-out 0.5s both;
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.1) !important;
    }
    
    .stSelectbox > div > div:hover {
        border: 2px solid #4CAF50 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2) !important;
    }
    
    .stSelectbox > label {
        color: #2E7D32 !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50, #66BB6A) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 2rem !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3) !important;
        width: 100% !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.4) !important;
        background: linear-gradient(135deg, #66BB6A, #4CAF50) !important;
    }
    
    .user-type-description {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);
        animation: fadeIn 1s ease-out;
    }
    
    .user-type-description strong {
        color: #2E7D32;
        font-size: 1.1rem;
    }
    
    .feature-highlights {
        background: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 5px 20px rgba(76, 175, 80, 0.1);
        animation: slideInLeft 1.2s ease-out;
    }
    
    .feature-highlights h4 {
        color: #2E7D32;
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .feature-highlights ul {
        list-style: none;
        padding: 0;
    }
    
    .feature-highlights li {
        margin: 0.8rem 0;
        color: #1B5E20;
        font-size: 1rem;
        line-height: 1.5;
        padding-left: 2rem;
        position: relative;
    }
    
    .feature-highlights li:before {
        content: "🌟 ";
        position: absolute;
        left: 0;
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .signup-navigation {
        text-align: center;
        margin-top: 2rem;
        padding: 2rem;
        background: rgba(76, 175, 80, 0.08);
        border-radius: 15px;
        border: 1px solid rgba(76, 175, 80, 0.2);
        animation: fadeIn 1.5s ease-out;
    }
    
    .signup-navigation h4 {
        color: #2E7D32;
        margin-bottom: 1rem;
        font-size: 1.4rem;
    }
    
    .footer-section {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        background: rgba(76, 175, 80, 0.05);
        border-radius: 15px;
        border-top: 3px solid #4CAF50;
    }
    
    .footer-section p {
        margin: 0.5rem 0;
        color: #2E7D32;
    }
    
    .footer-section .main-text {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .footer-section .sub-text {
        font-size: 0.95rem;
        opacity: 0.8;
    }
    
    /* Enhanced animations */
    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-60px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-60px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes bounceIn {
        0% { opacity: 0; transform: scale(0.3); }
        50% { opacity: 1; transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Enhanced responsive design */
    @media (max-width: 768px) {
        .signup-header {
            padding: 2rem 1.5rem;
        }
        .signup-header h1 {
            font-size: 2.5rem;
        }
        .signup-header p {
            font-size: 1.1rem;
        }
        .feature-highlights {
            padding: 1.5rem;
        }
        .user-type-description {
            padding: 1.2rem;
        }
    }
    </style>
    """
    
    st.markdown(signup_css, unsafe_allow_html=True)
    
    # YOUR ORIGINAL HEADER
    st.markdown("""
    <div class="signup-header">
        <h1>📝 Create Account</h1>
        <p>Join Smart Medical Reminder - Your Healthcare Journey Starts Here!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # YOUR ORIGINAL USER TYPE SELECTION - SAME LOGIC
    user_type = st.selectbox(
        "Select your account type:",
        ["Patient", "Doctor", "Guardian"],
        help="Choose the type of account you want to create"
    )
    
    # YOUR ORIGINAL USER TYPE DESCRIPTIONS - ENHANCED STYLING ONLY
    if user_type == "Patient":
        st.markdown("""
        <div class="user-type-description">
            <strong>👤 Patient Account:</strong> Manage your medications, set reminders, 
            connect with doctors, and track your health journey with complete privacy and control.
        </div>
        """, unsafe_allow_html=True)
    elif user_type == "Doctor":
        st.markdown("""
        <div class="user-type-description">
            <strong>👨‍⚕️ Doctor Account:</strong> Connect with patients, manage appointments, 
            respond to queries, and provide medical guidance through our secure platform.
        </div>
        """, unsafe_allow_html=True)
    elif user_type == "Guardian":
        st.markdown("""
        <div class="user-type-description">
            <strong>👨‍👩‍👧‍👦 Guardian Account:</strong> Monitor and support your loved one's 
            medication schedule and health management with patient-approved access.
        </div>
        """, unsafe_allow_html=True)
    
    # YOUR ORIGINAL FEATURE HIGHLIGHTS - ENHANCED STYLING ONLY
    if user_type == "Patient":
        st.markdown("""
        <div class="feature-highlights">
            <h4>🌟 What you'll get as a Patient:</h4>
            <ul>
                <li>Smart medication reminders with customizable schedules</li>
                <li>Medicine inventory tracking and expiry alerts</li>
                <li>Doctor consultation booking and management</li>
                <li>Comprehensive health analytics dashboard</li>
                <li>Guardian access management and privacy controls</li>
                <li>Digital prescription management and history</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    elif user_type == "Doctor":
        st.markdown("""
        <div class="feature-highlights">
            <h4>🩺 What you'll get as a Doctor:</h4>
            <ul>
                <li>Patient connection requests and management</li>
                <li>Appointment scheduling and consultation tools</li>
                <li>Patient query responses and communication</li>
                <li>Prescription tracking and medication monitoring</li>
                <li>Medical test results and health analytics</li>
                <li>Professional profile showcase and credibility</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    elif user_type == "Guardian":
        st.markdown("""
        <div class="feature-highlights">
            <h4>🛡️ What you'll get as a Guardian:</h4>
            <ul>
                <li>Patient medication monitoring and adherence tracking</li>
                <li>Reminder notifications and health alerts</li>
                <li>Real-time health status updates and reports</li>
                <li>Emergency contact access and coordination</li>
                <li>Medication schedule oversight and support</li>
                <li>Care coordination tools and family communication</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # YOUR ORIGINAL FORM DISPLAY LOGIC - EXACT SAME
    if user_type == "Patient":
        patient_signup()
    elif user_type == "Doctor":
        doctor_signup()
    elif user_type == "Guardian":
        guardian_signup()
    
    # YOUR ORIGINAL NAVIGATION SECTION
    st.markdown("""
    <div class="signup-navigation">
        <h4>🔄 Already have an account?</h4>
        <p>Sign in to access your Smart Medical Reminder dashboard and continue managing your healthcare journey.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # YOUR ORIGINAL NAVIGATION BUTTONS - EXACT SAME LOGIC
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Sign In", key="goto_signin"):
            go_to('signin')
    
    with col2:
        if st.button("🏠 Back to Home", key="goto_home"):
            go_to('landing')
    
    # Enhanced footer
    st.markdown("""
    <div class="footer-section">
        <p class="main-text">🩺 Smart Medical Reminder - Empowering Healthcare Management</p>
        <p class="sub-text">Secure • Private • HIPAA Compliant • Trusted by Healthcare Professionals</p>
        <p class="sub-text">Join thousands of patients, doctors, and guardians managing healthcare together</p>
    </div>
    """, unsafe_allow_html=True)
