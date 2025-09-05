import streamlit as st
from page.navigation import go_to
from utils.css import load_css


class FeatureCard:
    """Simple feature card data class"""
    def __init__(self, icon, title, description):
        self.icon = icon
        self.title = title
        self.description = description
    
    def render(self):
        return f"""<div class="feature-card">
            <div class="feature-icon">{self.icon}</div>
            <div class="feature-title">{self.title}</div>
            <div class="feature-description">{self.description}</div>
        </div>"""


class StatItem:
    """Simple stat item data class"""
    def __init__(self, number, label):
        self.number = number
        self.label = label
    
    def render(self):
        return f"""<div class="stat-item">
            <span class="stat-number">{self.number}</span>
            <div class="stat-label">{self.label}</div>
        </div>"""


class LandingPageContent:
    """Manage landing page content and data"""
    
    def __init__(self):
        self.features = [
            FeatureCard("💊", "Medicine Management", "Easily add, track, and manage all your medications with detailed information."),
            FeatureCard("⏰", "Smart Reminders", "Set up personalized medication schedules with intelligent reminders."),
            FeatureCard("👨‍⚕️", "Doctor Consultation", "Connect with healthcare professionals and schedule appointments."),
            FeatureCard("📊", "Health Analytics", "Track your medication adherence and view health trends."),
            FeatureCard("🛡️", "Guardian Support", "Allow family members to monitor your medication schedule."),
            FeatureCard("📱", "User-Friendly", "Intuitive design that's easy to use for all age groups.")
        ]
        
        self.stats = [
            StatItem("1000+", "Active Users"),
            StatItem("5000+", "Medicines Tracked"),
            StatItem("95%", "Adherence Rate"),
            StatItem("24/7", "Support Available")
        ]
        
        self.steps = [
            ("1️⃣", "Sign Up", "Create your account and set up your profile."),
            ("2️⃣", "Add Medicines", "Input your medications with dosage and timing."),
            ("3️⃣", "Stay Healthy", "Receive reminders and track your health journey.")
        ]
        
        self.testimonials = [
            ("This app has transformed how I manage my medications!", "- Sarah M., Patient"),
            ("Great tool for helping patients stay compliant with schedules.", "- Dr. James L., Physician")
        ]


class LandingPage:
    """Main landing page class"""
    
    def __init__(self):
        self.content = LandingPageContent()
    
    def render(self):
        load_css()
        self._load_styles()
        
        # Hero section
        self._render_hero()
        
        # Navigation buttons
        self._render_nav_buttons()
        
        # Features
        self._render_features()
        
        # Stats
        self._render_stats()
        
        # CTA section
        self._render_cta()
        
        # How it works
        self._render_how_it_works()
        
        # Final buttons
        self._render_final_buttons()
        
        # Testimonials
        self._render_testimonials()
        
        # Footer
        self._render_footer()
        
        # Sidebar info
        self._render_sidebar_info()
    
    def _load_styles(self):
        st.markdown("""<style>
        .stApp{background:#847DC7}
        .landing-header{text-align:center;background:linear-gradient(135deg,#FF8A65,#FF7043);padding:3rem 2rem;border-radius:20px;margin-bottom:2rem;color:white;box-shadow:0 10px 30px rgba(255,138,101,0.3)}
        .landing-header h1{font-size:3.5rem;margin-bottom:1rem;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
        .landing-header p{font-size:1.3rem;margin-bottom:0;opacity:0.95}
        .feature-card{background:linear-gradient(135deg,#FF8A65,#FF7043);padding:2rem;border-radius:15px;box-shadow:0 10px 25px rgba(255,138,101,0.2);text-align:center;transition:all 0.4s ease;color:white;margin:1rem 0}
        .feature-card:hover{transform:translateY(-10px) scale(1.02);box-shadow:0 20px 40px rgba(255,138,101,0.4)}
        .feature-icon{font-size:3.5rem;margin-bottom:1rem}
        .feature-title{font-size:1.5rem;font-weight:bold;margin-bottom:1rem}
        .feature-description{line-height:1.6;margin-bottom:1.5rem;opacity:0.9}
        .cta-section{background:linear-gradient(135deg,#FFE5B4 0%,#FFCC80 100%);padding:3rem 2rem;border-radius:20px;text-align:center;margin:3rem 0;color:#FF7043}
        .cta-section h2{font-size:2.5rem;margin-bottom:1rem}
        .cta-section p{font-size:1.2rem;margin-bottom:2rem;opacity:0.9}
        .stButton>button{background:linear-gradient(135deg,#FF8C00,#FFA500)!important;color:white!important;border:none!important;border-radius:25px!important;padding:1rem 2rem!important;font-size:1.1rem!important;font-weight:bold!important;transition:all 0.3s ease!important;box-shadow:0 4px 15px rgba(255,140,0,0.3)!important}
        .stButton>button:hover{transform:translateY(-3px) scale(1.05)!important;box-shadow:0 8px 25px rgba(255,140,0,0.5)!important}
        .stat-item{text-align:center;padding:1rem}
        .stat-number{font-size:2.5rem;font-weight:bold;color:#FF7043;display:block}
        .stat-label{color:#666;font-size:1.1rem;margin-top:0.5rem}
        .how-it-works-step{text-align:center;padding:1.5rem;background:rgba(255,255,255,0.8);border-radius:15px;margin:1rem}
        .step-number{font-size:3rem;margin-bottom:1rem;color:#FF7043}
        .testimonial{background:rgba(255,255,255,0.9);padding:2rem;border-radius:15px;margin:1rem 0;border-left:4px solid #FF7043}
        .testimonial-text{font-style:italic;color:#555;margin-bottom:1rem;font-size:1.1rem}
        .testimonial-author{font-weight:bold;color:#FF7043}
        .footer-section{background:linear-gradient(135deg,#FF7043,#FF5722);color:white;padding:2rem;border-radius:15px;margin-top:3rem;text-align:center}
        </style>""", unsafe_allow_html=True)
    
    def _render_hero(self):
        st.markdown("""<div class="landing-header">
            <h1>🩺 Smart Medical Reminder</h1>
            <p>Your Personal Healthcare Companion - Never Miss a Dose Again!</p>
        </div>""", unsafe_allow_html=True)
    
    def _render_nav_buttons(self):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔐 Sign In", key="landing_signin"):
                    go_to('signin')
            with col_btn2:
                if st.button("📝 Sign Up", key="landing_signup"):
                    go_to('signup')
    
    def _render_features(self):
        st.markdown("## 🌟 Key Features")
        
        # First row
        col1, col2, col3 = st.columns(3)
        for i, feature in enumerate(self.content.features[:3]):
            with [col1, col2, col3][i]:
                st.markdown(feature.render(), unsafe_allow_html=True)
        
        # Second row
        col1, col2, col3 = st.columns(3)
        for i, feature in enumerate(self.content.features[3:]):
            with [col1, col2, col3][i]:
                st.markdown(feature.render(), unsafe_allow_html=True)
    
    def _render_stats(self):
        st.markdown("## 📈 Platform Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        for i, stat in enumerate(self.content.stats):
            with [col1, col2, col3, col4][i]:
                st.markdown(stat.render(), unsafe_allow_html=True)
    
    def _render_cta(self):
        st.markdown("""<div class="cta-section">
            <h2>Ready to Take Control of Your Health? 🚀</h2>
            <p>Join thousands of users who trust Smart Medical Reminder</p>
        </div>""", unsafe_allow_html=True)
    
    def _render_how_it_works(self):
        st.markdown("## 🔄 How It Works")
        
        col1, col2, col3 = st.columns(3)
        for i, (number, title, desc) in enumerate(self.content.steps):
            with [col1, col2, col3][i]:
                st.markdown(f"""<div class="how-it-works-step">
                    <div class="step-number">{number}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>""", unsafe_allow_html=True)
    
    def _render_final_buttons(self):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            col_cta1, col_cta2 = st.columns(2)
            with col_cta1:
                if st.button("🎉 Get Started - Sign Up", key="cta_signup"):
                    go_to('signup')
            with col_cta2:
                if st.button("👋 Already a User? Sign In", key="cta_signin"):
                    go_to('signin')
    
    def _render_testimonials(self):
        st.markdown("## 💬 What Our Users Say")
        
        col1, col2 = st.columns(2)
        for i, (text, author) in enumerate(self.content.testimonials):
            with [col1, col2][i]:
                st.markdown(f"""<div class="testimonial">
                    <div class="testimonial-text">"{text}"</div>
                    <div class="testimonial-author">{author}</div>
                </div>""", unsafe_allow_html=True)
    
    def _render_footer(self):
        st.markdown("""<div class="footer-section">
            <h3>🩺 Smart Medical Reminder</h3>
            <p>Your trusted healthcare companion</p>
            <p>© 2024 Smart Medical Reminder. All rights reserved.</p>
        </div>""", unsafe_allow_html=True)
    
    def _render_sidebar_info(self):
        st.sidebar.markdown("### ℹ️ About")
        st.sidebar.info("""**Smart Medical Reminder** helps you:

• 💊 Manage medications
• ⏰ Set smart reminders  
• 👨‍⚕️ Connect with doctors
• 📊 Track health analytics
• 🛡️ Share with guardians

**Version:** 2.0
**Database:** MySQL""")


def landing_page():
    """Main entry point"""
    page = LandingPage()
    page.render()


def show_app_info():
    """Display app information - kept for compatibility"""
    pass


if __name__ == "__main__":
    landing_page()
