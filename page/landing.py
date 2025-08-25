import streamlit as st
from page.navigation import go_to
from utils.css import load_css
import time

def landing_page():
    """
    Landing page for Smart Medical Reminder App with Orange Theme
    """
    load_css()
    
    # Custom CSS for landing page matching patient dashboard colors
    landing_css = """
    <style>
        /* Background matching patient dashboard's orange gradient */
        .stApp {
            background: #847DC7;
            animation: none !important;
        }
        
        /* Main landing container with same styling as patient dashboard */
        .landing-main-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 1200px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: fadeInUp 1s ease-out;
        }
        
        /* Hero section with orange theme */
        .landing-header {
            text-align: center;
            background: linear-gradient(135deg, #FF8A65, #FF7043);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 10px 30px rgba(255, 138, 101, 0.3);
            animation: slideInDown 1s ease-out;
        }
        
        .landing-header h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: bounceIn 1.2s ease-out;
        }
        
        .landing-header p {
            font-size: 1.3rem;
            margin-bottom: 0;
            opacity: 0.95;
            animation: fadeInUp 1s ease-out 0.5s both;
        }
        
        /* Feature cards with orange styling */
        .feature-card {
            background: linear-gradient(135deg, #FF8A65, #FF7043);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(255, 138, 101, 0.2);
            text-align: center;
            transition: all 0.4s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            height: 100%;
            color: white;
            margin: 1rem 0;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .feature-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(255, 138, 101, 0.4);
            animation: pulse 0.6s ease-in-out;
        }
        
        .feature-icon {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            animation: rotate360 2s ease-in-out infinite;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        .feature-description {
            line-height: 1.6;
            margin-bottom: 1.5rem;
            opacity: 0.9;
        }
        
        /* CTA section with matching orange theme */
        .cta-section {
            background: linear-gradient(135deg, #FFE5B4 0%, #FFCC80 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 3rem 0;
            color: #FF7043;
            box-shadow: 0 10px 30px rgba(255, 138, 101, 0.2);
            animation: fadeIn 1.5s ease-out;
        }
        
        .cta-section h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            animation: textGlow 2s ease-in-out infinite alternate;
        }
        
        .cta-section p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        /* Buttons with orange theme and animations */
        .stButton > button {
            background: linear-gradient(135deg, #FF8C00, #FFA500) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 1rem 2rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3) !important;
            animation: buttonFloat 3s ease-in-out infinite !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 0 8px 25px rgba(255, 140, 0, 0.5) !important;
            background: linear-gradient(135deg, #FFA500, #FF8C00) !important;
        }
        
        /* Stats section */
        .stats-section {
            background: rgba(255, 255, 255, 0.8);
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            animation: slideInLeft 1s ease-out;
        }
        
        .stat-item {
            text-align: center;
            padding: 1rem;
            animation: countUp 2s ease-out;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #FF7043;
            display: block;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1rem;
            margin-top: 0.5rem;
        }
        
        /* Testimonials */
        .testimonial {
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid #FF7043;
            animation: slideInRight 1s ease-out;
        }
        
        .testimonial-text {
            font-style: italic;
            color: #555;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        
        .testimonial-author {
            font-weight: bold;
            color: #FF7043;
        }
        
        /* How it works section */
        .how-it-works-step {
            text-align: center;
            padding: 1.5rem;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            margin: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            animation: fadeInUp 1s ease-out;
        }
        
        .how-it-works-step:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .step-number {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #FF8C00, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: bounce 2s infinite;
        }
        
        /* Footer section */
        .footer-section {
            background: linear-gradient(135deg, #FF7043, #FF5722);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-top: 3rem;
            text-align: center;
            animation: fadeIn 1.5s ease-out;
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
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInDown {
            from {
                opacity: 0;
                transform: translateY(-100px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
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
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes rotate360 {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes buttonFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-3px); }
        }
        
        @keyframes textGlow {
            0% { text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
            100% { text-shadow: 2px 2px 8px rgba(255, 138, 101, 0.4); }
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes countUp {
            from { transform: scale(0.5); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .landing-header h1 { font-size: 2.5rem; }
            .landing-header p { font-size: 1.1rem; }
            .cta-section h2 { font-size: 2rem; }
            .feature-card { margin: 0.5rem 0; }
        }
    </style>
    """
    
    st.markdown(landing_css, unsafe_allow_html=True)
    
    # Main container
    # st.markdown('<div class="landing-main-container">', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="landing-header">
        <h1>🩺 Smart Medical Reminder</h1>
        <p>Your Personal Healthcare Companion - Never Miss a Dose Again!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Action Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔐 Sign In", key="landing_signin"):
                go_to('signin')
        
        with col_btn2:
            if st.button("📝 Sign Up", key="landing_signup"):
                go_to('signup')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Features Section
    st.markdown("## 🌟 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💊</div>
            <div class="feature-title">Medicine Management</div>
            <div class="feature-description">
                Easily add, track, and manage all your medications with detailed information 
                including dosage, expiry dates, and instructions.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⏰</div>
            <div class="feature-title">Smart Reminders</div>
            <div class="feature-description">
                Set up personalized medication schedules with intelligent reminders 
                that ensure you never miss a dose.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👨‍⚕️</div>
            <div class="feature-title">Doctor Consultation</div>
            <div class="feature-description">
                Connect with healthcare professionals, ask questions, and schedule 
                appointments directly through the platform.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Health Analytics</div>
            <div class="feature-description">
                Track your medication adherence, view health trends, and 
                get insights into your wellness journey.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Guardian Support</div>
            <div class="feature-description">
                Allow family members or caregivers to monitor your medication 
                schedule and receive important updates.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <div class="feature-title">User-Friendly Interface</div>
            <div class="feature-description">
                Intuitive design that's easy to use for all age groups, 
                with clear navigation and accessible features.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("""
    <div class="stats-section">
        <h2 style="text-align: center; color: #FF7043; margin-bottom: 2rem;">📈 Platform Statistics</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-number">1000+</span>
            <div class="stat-label">Active Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-number">5000+</span>
            <div class="stat-label">Medicines Tracked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-number">95%</span>
            <div class="stat-label">Adherence Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-number">24/7</span>
            <div class="stat-label">Support Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to Action Section
    st.markdown("""
    <div class="cta-section">
        <h2>Ready to Take Control of Your Health? 🚀</h2>
        <p>Join thousands of users who trust Smart Medical Reminder for their healthcare needs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("## 🔄 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="how-it-works-step">
            <div class="step-number">1️⃣</div>
            <h3>Sign Up</h3>
            <p>Create your account and set up your profile with basic health information.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="how-it-works-step">
            <div class="step-number">2️⃣</div>
            <h3>Add Medicines</h3>
            <p>Input your medications with details like dosage, timing, and special instructions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="how-it-works-step">
            <div class="step-number">3️⃣</div>
            <h3>Stay Healthy</h3>
            <p>Receive timely reminders and track your health journey with detailed analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Final CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_cta1, col_cta2 = st.columns(2)
        
        with col_cta1:
            if st.button("🎉 Get Started - Sign Up", key="cta_signup"):
                go_to('signup')
        
        with col_cta2:
            if st.button("👋 Already a User? Sign In", key="cta_signin"):
                go_to('signin')
    
    # Testimonials Section
    st.markdown("## 💬 What Our Users Say")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">
                "This app has completely transformed how I manage my medications. 
                The reminders are perfect and I never miss a dose anymore!"
            </div>
            <div class="testimonial-author">- Sarah M., Patient</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">
                "As a doctor, I love how this platform helps my patients stay compliant 
                with their medication schedules. Great tool for healthcare!"
            </div>
            <div class="testimonial-author">- Dr. James L., Physician</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer Section
    st.markdown("""
    <div class="footer-section">
        <h3>🩺 Smart Medical Reminder</h3>
        <p>Your trusted healthcare companion</p>
        <p style="margin-top: 1rem; opacity: 0.9;">
            © 2024 Smart Medical Reminder. All rights reserved. | 
            Made with ❤️ for better healthcare management
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Close main container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add some spacing at the bottom
    st.markdown("<br><br>", unsafe_allow_html=True)

# Optional: Add a function to show app info in sidebar
def show_app_info():
    """Display app information in sidebar"""
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info("""
    **Smart Medical Reminder** helps you:
    
    • 💊 Manage medications
    • ⏰ Set smart reminders  
    • 👨‍⚕️ Connect with doctors
    • 📊 Track health analytics
    • 🛡️ Share with guardians
    
    **Version:** 2.0  
    **Database:** MySQL
    """)

# Call the info function if needed
if __name__ == "__main__":
    landing_page()
