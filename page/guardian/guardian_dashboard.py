import streamlit as st
from utils.db_helper import db
from utils.file_ops import load_json
from config.constants import PROFILES_FILE, MEDICINES_FILE, SCHEDULES_FILE, APPOINTMENTS_FILE

def safe_date_format(date_value):
    """Safely format date values - handles both string and datetime objects"""
    if not date_value:
        return 'Unknown'
    
    try:
        if isinstance(date_value, str):
            # If it's already a string, try to get just the date part
            if 'T' in date_value:
                return date_value.split('T')[0]  # ISO format: "2025-08-14T10:30:00"
            else:
                return date_value[:10]  # Already formatted string
        else:
            # It's a datetime object, convert to string
            return date_value.strftime('%Y-%m-%d')
    except Exception:
        return 'Unknown'

def get_connection_status(guardian_id):
    """Check if guardian request is approved"""
    try:
        db.connect()
        query = "SELECT status FROM guardian_requests WHERE guardian_id = %s ORDER BY requested_at DESC LIMIT 1"
        result = db.execute_query(query, (guardian_id,))
        
        if result:
            return result[0]['status']
        else:
            return "pending"
            
    except Exception as e:
        print(f"Database query error: {e}")
        return "pending"

def get_patient_metrics(connected_patient_id):
    """Get patient's actual medicine and reminder counts"""
    try:
        if not connected_patient_id:
            return {'total_medicines': 0, 'active_reminders': 0, 'total_appointments': 0, 'low_stock_medicines': 0}
        
        # Get medicines count
        medicines = load_json(MEDICINES_FILE)
        total_medicines = len([m for m in medicines.values() if m.get('patient_id') == connected_patient_id])
        
        # Get active reminders count
        schedules = load_json(SCHEDULES_FILE)
        active_reminders = len([s for s in schedules.values() 
                               if s.get('patient_id') == connected_patient_id and s.get('status') == 'active'])
        
        # Get appointments count
        appointments = load_json(APPOINTMENTS_FILE)
        total_appointments = len([a for a in appointments.values() if a.get('patient_id') == connected_patient_id])
        
        # Get low stock medicines count
        low_stock_medicines = len([m for m in medicines.values() 
                                  if m.get('patient_id') == connected_patient_id and m.get('quantity', 0) <= 5])
        
        return {
            'total_medicines': total_medicines,
            'active_reminders': active_reminders,
            'total_appointments': total_appointments,
            'low_stock_medicines': low_stock_medicines
        }
    except Exception as e:
        print(f"Error getting patient metrics: {e}")
        return {'total_medicines': 0, 'active_reminders': 0, 'total_appointments': 0, 'low_stock_medicines': 0}

def guardian_dashboard():
    """Main guardian dashboard with enhanced CSS styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Enhanced background and app styling */
    .stApp {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0fff0 50%, #e0f2e1 100%);
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Enhanced main header */
    .main-header {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
        animation: fadeInDown 1s ease-out;
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header h3 {
        font-size: 1.5rem;
        margin: 1rem 0 0.5rem 0;
        opacity: 0.95;
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
    /* Enhanced status cards */
    .status-pending {
        background: linear-gradient(135deg, #fff8e1, #ffecb3);
        color: #e65100;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #FFA726;
        margin: 2rem 0;
        box-shadow: 0 5px 20px rgba(255, 167, 38, 0.2);
        animation: slideInLeft 0.8s ease-out;
    }
    
    .status-approved {
        background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
        color: #1b5e20;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #4CAF50;
        margin: 2rem 0;
        box-shadow: 0 5px 20px rgba(76, 175, 80, 0.2);
        animation: slideInLeft 0.8s ease-out;
    }
    
    .status-pending h3, .status-approved h3 {
        font-size: 1.5rem;
        margin: 0 0 1rem 0;
        font-weight: 700;
    }
    
    .status-pending p, .status-approved p {
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Enhanced patient info card */
    .patient-info {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #2196F3;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.8s ease-out;
    }
    
    .patient-info h4 {
        color: #1976D2;
        font-size: 1.5rem;
        margin: 0 0 1rem 0;
        font-weight: 700;
    }
    
    .patient-info p {
        margin: 0.5rem 0;
        line-height: 1.5;
    }
    
    .patient-info strong {
        color: #333;
        font-weight: 600;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out;
        border-top: 4px solid #4CAF50;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #4CAF50, #66BB6A);
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: #4CAF50;
    }
    
    .metric-card h2 {
        font-size: 3rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    
    .metric-card p {
        font-size: 1.1rem;
        color: #666;
        font-weight: 500;
        margin: 0;
    }
    
    /* Enhanced sidebar styling */
    .sidebar-profile {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 5px 20px rgba(76, 175, 80, 0.3);
    }
    
    .sidebar-profile h3 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .sidebar-profile p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    /* Enhanced activity section */
    .activity-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
        animation: fadeInUp 0.8s ease-out;
    }
    
    .activity-item {
        background: #f8f9fa;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
        transition: all 0.3s ease;
    }
    
    .activity-item:hover {
        background: #e8f5e8;
        transform: translateX(5px);
    }
    
    /* Button enhancements */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50, #66BB6A) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3) !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(76, 175, 80, 0.2) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(76, 175, 80, 0.1) !important;
        border-radius: 10px !important;
    }
    
    /* Animations */
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
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-40px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(40px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
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
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card h2 {
            font-size: 2.5rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("❌ You must be logged in to access the Guardian Dashboard.")
        return
    
    profiles = load_json(PROFILES_FILE)
    guardian_profile = profiles.get(user_id, {})
    connected_patient_id = guardian_profile.get("connected_patient")
    connected_patient = profiles.get(connected_patient_id) if connected_patient_id else {}
    
    st.markdown(f"""
    <div class="main-header">
        <h1>👨‍👩‍👧‍👦 Guardian Dashboard</h1>
        <h3>Welcome, {guardian_profile.get('full_name', 'Guardian')}!</h3>
        <p>Monitor and support your connected patient's healthcare journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar Navigation
    st.sidebar.markdown(f"""
    <div class="sidebar-profile">
        <h3>👋 {guardian_profile.get('full_name', 'Guardian')}</h3>
        <p>Guardian ID: {user_id}</p>
        <p>Role: Healthcare Guardian</p>
    </div>
    """, unsafe_allow_html=True)
    
    menu_options = [
        "🏠 Dashboard Home",
        "👤 Patient Overview", 
        "💊 Patient Medications",
        "⏰ Medicine Reminders",
        "📅 Appointments",
        "📋 Medical Records",
        "⚙️ Update Profile"
    ]
    
    selected_page = st.sidebar.selectbox("Navigate", menu_options)
    
    if st.sidebar.button("🚪 Logout", type="secondary"):
        from page.navigation import logout
        logout()
    
    # Check connection status (same logic)
    connection_status = get_connection_status(user_id)
    
    # Main content based on selected page (same logic)
    if selected_page == "🏠 Dashboard Home":
        dashboard_home(guardian_profile, connected_patient, connected_patient_id, connection_status)
    elif selected_page == "👤 Patient Overview":
        patient_overview(connected_patient_id, connected_patient, connection_status)
    elif selected_page == "💊 Patient Medications":
        patient_medications(connected_patient_id, connection_status)
    elif selected_page == "⏰ Medicine Reminders":
        medicine_reminders(connected_patient_id, connection_status)
    elif selected_page == "📅 Appointments":
        patient_appointments(connected_patient_id, connection_status)
    elif selected_page == "📋 Medical Records":
        medical_records(connected_patient_id, connection_status)
    elif selected_page == "⚙️ Update Profile":
        from page.update_profile_page import update_profile_page
        update_profile_page(user_id)

def dashboard_home(guardian_profile, connected_patient, connected_patient_id, connection_status):
    """Main dashboard home page with enhanced styling"""
    
    if connection_status != "approved":
        st.markdown("""
        <div class="status-pending">
            <h3>⏳ Awaiting Patient Approval</h3>
            <p>Your request to connect with the patient is still pending approval. 
            Please wait for the patient to approve your access request.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 Once approved, you'll be able to monitor the patient's medications, appointments, and health records.")
        return
    
    # Connection approved - show enhanced dashboard
    st.markdown("""
    <div class="status-approved">
        <h3>✅ Connected Successfully</h3>
        <p>You have been approved to access the patient's health information.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if connected_patient:
        st.markdown(f"""
        <div class="patient-info">
            <h4>🩺 Connected Patient: {connected_patient.get('full_name', 'Unknown')}</h4>
            <p><strong>Patient ID:</strong> {connected_patient.get('patient_id', 'N/A')}</p>
            <p><strong>Blood Group:</strong> {connected_patient.get('blood_group', 'Not specified')}</p>
            <p><strong>Mobile:</strong> {connected_patient.get('mobile', 'Not provided')}</p>
            <p><strong>Relationship:</strong> {guardian_profile.get('relationship', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Get patient metrics (same logic)
    patient_metrics = get_patient_metrics(connected_patient_id)
    
    # Enhanced metric cards with same logic
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💊</h3>
            <h2>{patient_metrics['total_medicines']}</h2>
            <p>Total Medicines</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏰</h3>
            <h2>{patient_metrics['active_reminders']}</h2>
            <p>Active Reminders</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅</h3>
            <h2>{patient_metrics['total_appointments']}</h2>
            <p>Upcoming Appointments</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️</h3>
            <h2>{patient_metrics['low_stock_medicines']}</h2>
            <p>Low Stock Medicines</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Recent Patient Activities (same logic)
    st.markdown("---")
    st.markdown('<div class="activity-section">', unsafe_allow_html=True)
    st.subheader("📈 Recent Patient Activities")
    
    # Get recent medicines (same logic)
    medicines = load_json(MEDICINES_FILE)
    patient_medicines = [m for m in medicines.values() if m.get('patient_id') == connected_patient_id]
    recent_medicines = sorted(patient_medicines, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
    
    if recent_medicines:
        st.write("**Recent Medicines Added:**")
        for med in recent_medicines:
            # Use the safe date formatting function (same logic)
            created_date = safe_date_format(med.get('created_at'))
            st.markdown(f'<div class="activity-item">💊 Added medicine: <strong>{med.get("name", "Unknown")}</strong> ({created_date})</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="activity-item">No recent activities found.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def patient_overview(connected_patient_id, connected_patient, connection_status):
    """Patient overview page"""
    st.title("👤 Patient Overview")
    
    if connection_status != "approved":
        st.warning("⚠️ Please wait for patient approval to access this information.")
        return
    
    if not connected_patient:
        st.error("❌ No patient connected.")
        return
    
    with st.expander("📋 Basic Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Full Name:** {connected_patient.get('full_name', 'Not provided')}")
            st.write(f"**Gender:** {connected_patient.get('gender', 'Not specified')}")
            st.write(f"**Blood Group:** {connected_patient.get('blood_group', 'Not specified')}")
            st.write(f"**Mobile:** {connected_patient.get('mobile', 'Not provided')}")
        with col2:
            st.write(f"**Email:** {connected_patient.get('email', 'Not provided')}")
            st.write(f"**Date of Birth:** {connected_patient.get('dob', 'Not provided')}")
            st.write(f"**Marital Status:** {connected_patient.get('marital_status', 'Not specified')}")
            st.write(f"**Patient ID:** {connected_patient.get('patient_id', 'N/A')}")
    
    with st.expander("🏠 Address Information"):
        st.write(f"**Address:** {connected_patient.get('address', 'Not provided')}")
        st.write(f"**City:** {connected_patient.get('city', 'Not provided')}")
        st.write(f"**State:** {connected_patient.get('state', 'Not provided')}")
        st.write(f"**Pincode:** {connected_patient.get('pincode', 'Not provided')}")

def patient_medications(connected_patient_id, connection_status):
    """Patient medications monitoring"""
    st.title("💊 Patient Medications")
    
    if connection_status != "approved":
        st.warning("⚠️ Please wait for patient approval to access this information.")
        return
    
    if not connected_patient_id:
        st.error("❌ No patient connected.")
        return
    
    # Load and display patient's medicines
    medicines = load_json(MEDICINES_FILE)
    patient_medicines = [m for m in medicines.values() if m.get('patient_id') == connected_patient_id]
    
    if patient_medicines:
        st.success(f"Found {len(patient_medicines)} medicines for this patient")
        for med in patient_medicines:
            with st.expander(f"💊 {med.get('name', 'Unknown Medicine')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Contents:** {med.get('contents', 'Not specified')}")
                    st.write(f"**Purpose:** {med.get('purpose', 'Not specified')}")
                    st.write(f"**Category:** {med.get('category', 'General')}")
                with col2:
                    st.write(f"**Quantity:** {med.get('quantity', 0)} units")
                    st.write(f"**Expiry Date:** {med.get('expiry_date', 'Not specified')}")
                    st.write(f"**Take with food:** {med.get('take_with_food', 'Not specified')}")
    else:
        st.info("📝 Patient hasn't added any medications yet.")

def medicine_reminders(connected_patient_id, connection_status):
    """Medicine reminders monitoring"""
    st.title("⏰ Medicine Reminders")
    
    if connection_status != "approved":
        st.warning("⚠️ Please wait for patient approval to access this information.")
        return
    
    if not connected_patient_id:
        st.error("❌ No patient connected.")
        return
    
    # Load and display patient's schedules
    schedules = load_json(SCHEDULES_FILE)
    patient_schedules = [s for s in schedules.values() if s.get('patient_id') == connected_patient_id]
    
    if patient_schedules:
        st.success(f"Found {len(patient_schedules)} medicine reminders for this patient")
        for schedule in patient_schedules:
            with st.expander(f"⏰ {schedule.get('medicine_name', 'Unknown Medicine')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Doses per day:** {schedule.get('doses_per_day', 0)}")
                    st.write(f"**Times:** {', '.join(schedule.get('times', []))}")
                with col2:
                    st.write(f"**Take:** {schedule.get('before_after_food', 'Not specified')}")
                    st.write(f"**Status:** {schedule.get('status', 'Unknown')}")
                if schedule.get('precaution'):
                    st.write(f"**Precautions:** {schedule.get('precaution')}")
    else:
        st.info("⏰ Patient hasn't set any medication reminders yet.")

def patient_appointments(connected_patient_id, connection_status):
    """Patient appointments monitoring"""
    st.title("📅 Patient Appointments")
    
    if connection_status != "approved":
        st.warning("⚠️ Please wait for patient approval to access this information.")
        return
    
    appointments = load_json(APPOINTMENTS_FILE)
    patient_appointments_list = [a for a in appointments.values() if a.get('patient_id') == connected_patient_id]
    
    if patient_appointments_list:
        st.success(f"Found {len(patient_appointments_list)} appointments for this patient")
        for apt in patient_appointments_list:
            with st.expander(f"📅 Appointment - {apt.get('appointment_date', 'Unknown Date')}"):
                st.write(f"**Date:** {apt.get('appointment_date', 'Not specified')}")
                st.write(f"**Time:** {apt.get('appointment_time', 'Not specified')}")
                st.write(f"**Type:** {apt.get('type', 'Not specified')}")
                st.write(f"**Status:** {apt.get('status', 'Unknown')}")
                if apt.get('notes'):
                    st.write(f"**Notes:** {apt.get('notes')}")
    else:
        st.info("📅 No appointments scheduled yet.")

def medical_records(connected_patient_id, connection_status):
    """Patient medical records"""
    st.title("📋 Medical Records")
    
    if connection_status != "approved":
        st.warning("⚠️ Please wait for patient approval to access this information.")
        return
    
    st.info("📋 Medical records feature coming soon.")
