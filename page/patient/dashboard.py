import streamlit as st
import os
from datetime import datetime, date
from utils.css import load_css
from page.navigation import logout
from config.constants import (
    PROFILES_FILE, MEDICINES_FILE, SCHEDULES_FILE, PRESCRIPTIONS_FILE,
    MEDICAL_TESTS_FILE, DOCTOR_QUERIES_FILE, GUARDIAN_REQUESTS_FILE,
    APPOINTMENTS_FILE, PATIENT_DOCTOR_REQUESTS_FILE
)
from utils.file_ops import load_json
from page.patient.medicines import medicine_manager
from page.patient.reminders import medicine_reminder_page
from page.patient.prescriptions import prescriptions_page
from page.patient.medical_tests import medical_tests_page
from page.patient.appointments import ask_questions_and_appointments
from page.patient.adherence import adherence_history
from page.patient.guardians import manage_guardians
from page.update_profile_page import update_profile_page
from page.patient.connect_doctors import connect_doctors_page


def safe_date_format(dt):
    """Safely format date values (handles both strings and datetime objects)"""
    if dt is None:
        return 'Unknown'
    if isinstance(dt, str):
        return dt[:10]
    if isinstance(dt, (datetime, date)):
        return dt.strftime('%Y-%m-%d')
    return str(dt)


def connected_doctors_page(user_id):
    """Show connected doctors"""
    st.title("👥 Connected Doctors")
    
    profiles = load_json(PROFILES_FILE)
    patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
    
    connected_requests = [
        req for req in patient_doctor_requests.values()
        if req.get("patient_id") == user_id and req.get("status") == "approved"
    ]
    
    if not connected_requests:
        st.info("No doctors connected yet. Go to 'Search Doctors' to connect with doctors.")
        return
    
    st.write(f"**Total Connected Doctors:** {len(connected_requests)}")
    
    for req in connected_requests:
        doctor_id = req.get("doctor_id")
        doctor_profile = profiles.get(doctor_id, {})
        
        with st.expander(f"Dr. {doctor_profile.get('full_name', 'Unknown Doctor')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Specialization:** {doctor_profile.get('specialization', 'General')}")
                st.write(f"**Experience:** {doctor_profile.get('experience', 'N/A')} years")
                st.write(f"**Hospital:** {doctor_profile.get('hospital_clinic', 'Not provided')}")
            
            with col2:
                st.write(f"**Consultation Fee:** ₹{doctor_profile.get('consultation_fee', 'N/A')}")
                st.write(f"**Email:** {doctor_profile.get('email', 'Not provided')}")
                st.write(f"**Mobile:** {doctor_profile.get('mobile', 'Not provided')}")
            
            if st.button(f"💬 Message Dr. {doctor_profile.get('full_name', 'Doctor')}", key=f"msg_{doctor_id}"):
                st.session_state.patient_nav_page = "Ask Doctor / Appointments"
                st.rerun()


def dashboard_home_page(user_id):
    """Dashboard home page content with light orange background"""
    profiles = load_json(PROFILES_FILE)
    medicines = load_json(MEDICINES_FILE)
    schedules = load_json(SCHEDULES_FILE)
    appointments = load_json(APPOINTMENTS_FILE)
    
    profile = profiles.get(user_id, {})
    
    st.markdown("""
    <style>
    .dashboard-home-container {
        background: linear-gradient(135deg, #FFE5B4 0%, #FFCC80 100%);
        padding: 20px;
        border-radius: 15px;
        margin: -30px -30px 20px -30px;
    }
    
    .welcome-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #FF8A65, #FF7043);
        border-radius: 15px;
        color: white;
        box-shadow: 0 10px 30px rgba(255, 138, 101, 0.3);
    }
    
    .welcome-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .welcome-header p {
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="welcome-header">
        <h1>Welcome back, {profile.get('full_name', 'Patient')}! 👋</h1>
        <p>Here's your health summary for today</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    patient_medicines = {k: v for k, v in medicines.items() if v.get("patient_id") == user_id}
    patient_schedules = {k: v for k, v in schedules.items() if v.get("patient_id") == user_id}
    patient_appointments = [a for a in appointments.values() if a.get("patient_id") == user_id]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💊 Total Medicines", len(patient_medicines))
    col2.metric("⏰ Active Reminders", len(patient_schedules))
    col3.metric("📅 Appointments", len(patient_appointments))
    col4.metric("📊 Profile Complete", f"{profile.get('profile_completion', 0)}%")
    
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FF8A65, #FF7043); border-radius: 15px; padding: 20px; color: white; box-shadow: 0 10px 20px rgba(255, 138, 101, 0.3); text-align: center; margin: 10px 0;'>
            <div style='font-size: 3rem; margin-bottom: 10px;'>💊</div>
            <h3 style='margin: 10px 0 5px 0; font-size: 1.2rem;'>Medicine Manager</h3>
            <p style='font-size: 0.9rem; opacity: 0.9; line-height: 1.4;'>Add, track, and organize your medications</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FF8A65, #FF7043); border-radius: 15px; padding: 20px; color: white; box-shadow: 0 10px 20px rgba(255, 138, 101, 0.3); text-align: center; margin: 10px 0;'>
            <div style='font-size: 3rem; margin-bottom: 10px;'>⏰</div>
            <h3 style='margin: 10px 0 5px 0; font-size: 1.2rem;'>Smart Reminders</h3>
            <p style='font-size: 0.9rem; opacity: 0.9; line-height: 1.4;'>Never miss a dose with intelligent alerts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FF8A65, #FF7043); border-radius: 15px; padding: 20px; color: white; box-shadow: 0 10px 20px rgba(255, 138, 101, 0.3); text-align: center; margin: 10px 0;'>
            <div style='font-size: 3rem; margin-bottom: 10px;'>👨‍⚕️</div>
            <h3 style='margin: 10px 0 5px 0; font-size: 1.2rem;'>Doctor Connect</h3>
            <p style='font-size: 0.9rem; opacity: 0.9; line-height: 1.4;'>Connect with healthcare professionals</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity section
    st.subheader("📋 Recent Activity")
    
    recent_activities = []
    
    # FIXED: Recent medicines with safe date formatting
    try:
        for med_id, med in sorted(patient_medicines.items(), key=lambda x: x[1].get('created_at', ''), reverse=True)[:3]:
            created_at = safe_date_format(med.get('created_at'))
            recent_activities.append(f"💊 Added medicine: {med.get('name', 'Unknown')} ({created_at})")
    except Exception as e:
        pass
    
    # FIXED: Recent appointments with safe date formatting
    try:
        for apt in sorted(patient_appointments, key=lambda x: x.get('created_at', ''), reverse=True)[:2]:
            created_at = safe_date_format(apt.get('created_at'))
            appointment_date = safe_date_format(apt.get('appointment_date'))
            recent_activities.append(f"📅 Appointment scheduled for {appointment_date} ({created_at})")
    except Exception as e:
        pass
    
    if recent_activities:
        for activity in recent_activities:
            st.write(f"• {activity}")
    else:
        st.info("No recent activities found. Start by adding your first medicine!")
    
    if patient_schedules:
        st.success("✅ You have active medicine reminders set up!")
    else:
        st.warning("⚠️ No medicine reminders set. Click 'Medicine Reminder' to get started.")
    
    if patient_appointments:
        recent_appointment = max(patient_appointments, key=lambda x: x.get('created_at', ''))
        appointment_date = safe_date_format(recent_appointment.get('appointment_date'))
        st.info(f"📅 Latest appointment: {appointment_date}")
    else:
        st.info("📅 No appointments yet. Connect with doctors to schedule appointments!")


def patient_dashboard():
    load_css()
    
    custom_css = """
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: none;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container {
        margin-left: auto;
        margin-right: auto;
        max-width: 1400px;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: none;
        }
    }
    
    .main .block-container {
        transition: margin-left 0.3s ease, margin-right 0.3s ease, max-width 0.3s ease;
    }
    
    .stApp {
        background: #CFEBAE;
        animation: none !important;
    }
    
    .profile-name {
        color: white;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .nav-container {
        margin-top: 20px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #FF8C00, #FFA500) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(255, 140, 0, 0.3) !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    profiles = load_json(PROFILES_FILE)
    user_id = st.session_state.user_id
    profile = profiles.get(user_id, {})
    
    st.sidebar.markdown('<div class="profile-container">', unsafe_allow_html=True)
    st.sidebar.markdown(f'<h3 class="profile-name">Welcome, {profile.get("full_name", "Patient")}</h3>', unsafe_allow_html=True)
    
    profile_pic = profile.get("photo_path")
    if profile_pic and os.path.exists(profile_pic):
        st.sidebar.image(profile_pic, width=120)
    else:
        st.sidebar.info("📷 Upload profile photo in 'Update Profile'")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    nav_items = [
        ("🏠", "Dashboard Home"),
        ("💊", "Add Medicine"),
        ("⏰", "Medicine Reminder"),
        ("📄", "Prescriptions"),
        ("🩺", "Medical Tests"),
        ("🔗", "Search Doctors"),
        ("👥", "Connected Doctors"),
        ("💬", "Ask Doctor / Appointments"),
        ("📊", "Adherence History"),
        ("🛡️", "Guardians"),
        ("📝", "Update Profile"),
        ("🚪", "Logout"),
    ]
    
    if "patient_nav_page" not in st.session_state:
        st.session_state.patient_nav_page = "Dashboard Home"
    
    selected_page = st.session_state.patient_nav_page
    
    st.sidebar.markdown('<div class="nav-container">', unsafe_allow_html=True)
    for icon, label in nav_items:
        if st.sidebar.button(f"{icon} {label}", key=label):
            st.session_state.patient_nav_page = label
            st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    page = selected_page
    
    col1, main_content, col3 = st.columns([0.5, 10, 0.5])
    
    with main_content:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        if page == "Dashboard Home":
            dashboard_home_page(user_id)
        elif page == "Add Medicine":
            medicine_manager(user_id)
        elif page == "Medicine Reminder":
            medicine_reminder_page(user_id)
        elif page == "Prescriptions":
            prescriptions_page(user_id)
        elif page == "Medical Tests":
            medical_tests_page(user_id)
        elif page == "Search Doctors":
            connect_doctors_page(user_id)
        elif page == "Connected Doctors":
            connected_doctors_page(user_id)
        elif page == "Ask Doctor / Appointments":
            ask_questions_and_appointments(user_id)
        elif page == "Adherence History":
            adherence_history(user_id)
        elif page == "Guardians":
            manage_guardians(user_id)
        elif page == "Update Profile":
            update_profile_page(user_id)
        elif page == "Logout":
            logout()
        
        st.markdown('</div>', unsafe_allow_html=True)
