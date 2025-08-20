import streamlit as st
from page.navigation import go_to
from utils.css import load_css
import time

def landing_page():
    """
    Landing page for Smart Medical Reminder App
    """
    load_css()
    
    # Custom CSS for landing page
    landing_css = """
    <style>
        /* Landing page specific styles */
        .landing-header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .landing-header h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: fadeInDown 1s ease-out;
        }
        
        .landing-header p {
            font-size: 1.3rem;
            margin-bottom: 0;
            opacity: 0.9;
            animation: fadeInUp 1s ease-out 0.3s both;
        }
        
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid #e1e8ed;
            height: 100%;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        
        .feature-description {
            color: #555;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        
        .cta-section {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 3rem 0;
            color: white;
        }
        
        .cta-section h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        .cta-section p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.95;
        }
        
        .landing-button {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 25px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 0.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .landing-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            text-decoration: none;
            color: white;
        }
        
        .landing-button.secondary {
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        }
        
        .stats-section {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 1rem;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            display: block;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1rem;
            margin-top: 0.5rem;
        }
        
        .testimonial {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid #667eea;
        }
        
        .testimonial-text {
            font-style: italic;
            color: #555;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        
        .testimonial-author {
            font-weight: bold;
            color: #2c3e50;
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
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        .footer-section {
            background: #2c3e50;
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-top: 3rem;
            text-align: center;
        }
    </style>
    """
    
    st.markdown(landing_css, unsafe_allow_html=True)
    
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
            if st.button("🔐 Sign In", key="landing_signin", use_container_width=True):
                go_to('signin')
        
        with col_btn2:
            if st.button("📝 Sign Up", key="landing_signup", use_container_width=True):
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
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">📈 Platform Statistics</h2>
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
    
    # Final CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_cta1, col_cta2 = st.columns(2)
        
        with col_cta1:
            if st.button("🎉 Get Started - Sign Up", key="cta_signup", use_container_width=True):
                go_to('signup')
        
        with col_cta2:
            if st.button("👋 Already a User? Sign In", key="cta_signin", use_container_width=True):
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
    
    # How It Works Section
    st.markdown("## 🔄 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">1️⃣</div>
            <h3>Sign Up</h3>
            <p>Create your account and set up your profile with basic health information.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">2️⃣</div>
            <h3>Add Medicines</h3>
            <p>Input your medications with details like dosage, timing, and special instructions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">3️⃣</div>
            <h3>Stay Healthy</h3>
            <p>Receive timely reminders and track your health journey with detailed analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer Section
    st.markdown("""
    <div class="footer-section">
        <h3>🩺 Smart Medical Reminder</h3>
        <p>Your trusted healthcare companion</p>
        <p style="margin-top: 1rem; opacity: 0.8;">
            © 2024 Smart Medical Reminder. All rights reserved. | 
            Made with ❤️ for better healthcare management
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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
