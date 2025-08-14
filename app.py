import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration - Set this early to avoid conflicts
st.set_page_config(
    page_title="Smart Medical Reminder", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database initialization check - MUST BE FIRST
def ensure_database_exists():
    """Ensure database exists before importing db_helper"""
    try:
        from utils.db_helper import db
        # Try to connect and create database if missing
        db.connect(create_db_if_missing=True)
        
        # Test query to ensure tables exist
        try:
            db.execute_query("SELECT 1 FROM users LIMIT 1")
            return True
        except Exception:
            # Tables don't exist, run setup
            st.info("Setting up database tables for first time...")
            try:
                from database.setup_database import setup_database
                setup_database()
                st.success("Database initialized successfully!")
                st.rerun()
            except Exception as setup_error:
                st.error(f"Database setup failed: {setup_error}")
                return False
                
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        st.info("Please ensure MySQL is running and credentials are correct in config/constants.py")
        st.code("""
        # Update these in config/constants.py:
        DB_CONFIG = {
            'host': 'localhost',
            'user': 'your_mysql_username',
            'password': 'your_mysql_password',
            'database': 'medical_reminder_db'
        }
        """)
        st.stop()
        return False
    
    return True

# Initialize database before any other operations
if not ensure_database_exists():
    st.stop()

# Now safe to import after database is confirmed
from page import landing, signin
from page.guardian import guardian_dashboard
from page.signup import signup_main
from page.patient import dashboard as patient_dashboard
from utils.db_helper import db

# Your existing session state initialization
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Get current page
page = st.session_state.page

# Your existing page routing logic
if page == 'landing':
    landing.landing_page()
elif page == 'signin':
    signin.signin_page()
elif page == 'signup':
    signup_main.signup_page()
elif page == 'patient_dashboard':
    patient_dashboard.patient_dashboard()
elif page == 'doctor_dashboard':
    from page.doctor import dashboard as doctor_dashboard
    doctor_dashboard.doctor_dashboard()
elif page == 'guardian_dashboard':
    guardian_dashboard.guardian_dashboard()
else:
    # Handle unknown pages
    st.error("Page not found")
    if st.button("Go to Home"):
        st.session_state.page = 'landing'
        st.rerun()
