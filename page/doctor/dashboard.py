import streamlit as st
import os
from datetime import datetime
from utils.css import load_css
from page.navigation import logout
from config.constants import (
    USERS_FILE, PROFILES_FILE, APPOINTMENTS_FILE,
    DOCTOR_QUERIES_FILE, PRESCRIPTIONS_FILE, MEDICAL_TESTS_FILE,
    PATIENT_DOCTOR_REQUESTS_FILE
)
from utils.file_ops import load_json, save_json
from page.update_profile_page import update_profile_page

def safe_format_datetime(date_val):
    """Safely format datetime values - handles both string and datetime objects"""
    if not date_val:
        return 'Unknown'
    
    try:
        if isinstance(date_val, str):
            return date_val[:19]  # Already a string, slice first 19 chars
        else:
            # It's a datetime object, convert to string first
            return date_val.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return 'Unknown'

def doctor_dashboard():
    load_css()
    
    # Enhanced CSS with orange theme matching patient dashboard
    custom_css = """
    <style>
    /* Enhanced CSS with centering fix */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: none;
    }
    
    /* CENTERING FIX: Center content when sidebar is collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container {
        margin-left: auto;
        margin-right: auto;
        max-width: 1400px;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* Responsive design */
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
    
    /* Smooth transition */
    .main .block-container {
        transition: margin-left 0.3s ease, margin-right 0.3s ease, max-width 0.3s ease;
    }
    
    /* STATIC ORANGE BACKGROUND - Same as Patient Dashboard */
    .stApp {
        background: #9AC77D;
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
    
    .nav-button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        margin: 5px 0 !important;
        padding: 12px 16px !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .nav-button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateX(5px) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    .nav-button-active {
        background: rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        transform: translateX(10px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
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
    
    /* Doctor Dashboard specific styling */
    .doctor-welcome-header {
        text-align: center;
        background: linear-gradient(135deg, #FF8A65, #FF7043);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 10px 30px rgba(255, 138, 101, 0.3);
        margin-bottom: 2rem;
        animation: slideInDown 1s ease-out;
    }
    
    .doctor-welcome-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .doctor-welcome-header p {
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Stats cards for doctor dashboard */
    .doctor-stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 2rem 0;
    }
    
    .doctor-stat-card {
        background: linear-gradient(135deg, #FF8A65, #FF7043);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 20px rgba(255, 138, 101, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .doctor-stat-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 30px rgba(255, 138, 101, 0.3);
    }
    
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Request cards styling */
    .request-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #FF8C00;
        transition: all 0.3s ease;
        animation: slideInLeft 0.8s ease-out;
    }
    
    .request-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .request-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FF7043;
        margin-bottom: 1rem;
    }
    
    .request-details {
        color: #666;
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    /* Button styling matching patient dashboard */
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
    
    /* Form elements styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 140, 0, 0.2) !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 140, 0, 0.2) !important;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 140, 0, 0.2) !important;
    }
    
    /* Expander styling */
    .stExpander > div > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 140, 0, 0.1) !important;
    }
    
    .stAlert {
        border-radius: 10px !important;
        border-left: 4px solid #FF8C00 !important;
    }
    
    /* Debug section styling */
    .debug-section {
        background: rgba(255, 235, 180, 0.3);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 140, 0, 0.2);
    }
    
    /* Additional animations */
    @keyframes slideInDown {
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
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .element-container {
        animation: slideInLeft 0.6s ease-out;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .doctor-stats-container {
            grid-template-columns: 1fr;
        }
        
        .main-content {
            margin: 10px;
            padding: 20px;
        }
        
        .doctor-welcome-header h1 {
            font-size: 1.8rem;
        }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    doctor_id = st.session_state.get("user_id")
    if not doctor_id:
        st.error("You are not logged in.")
        return

    profiles = load_json(PROFILES_FILE)
    doctor_profile = profiles.get(doctor_id, {})

    # Sidebar with orange theme matching patient dashboard
    st.sidebar.markdown('<div class="profile-container">', unsafe_allow_html=True)
    st.sidebar.markdown(f'<h3 class="profile-name">Dr. {doctor_profile.get("full_name", "Doctor")}</h3>', unsafe_allow_html=True)
    
    profile_pic = doctor_profile.get("photo_path")
    if profile_pic and os.path.exists(profile_pic):
        st.sidebar.image(profile_pic, width=140)
    else:
        st.sidebar.info("📷 Upload profile photo in 'Update Profile'")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Navigation items
    nav_items = [
        ("🏠", "Dashboard Home"),
        ("🔗", "Connection Requests"),
        ("👥", "Connected Patients"),
        ("📅", "Appointment Requests"),
        ("💬", "Patient Queries"),
        ("📄", "Prescriptions"),
        ("🧪", "Medical Tests"),
        ("📝", "Update Profile"),
        ("🚪", "Logout")
    ]
    
    if "doctor_nav_page" not in st.session_state:
        st.session_state.doctor_nav_page = "Dashboard Home"
    
    selected_page = st.session_state.doctor_nav_page

    st.sidebar.markdown('<div class="nav-container">', unsafe_allow_html=True)
    for icon, label in nav_items:
        button_class = "nav-button-active" if selected_page == label else "nav-button"
        if st.sidebar.button(f"{icon} {label}", key=label):
            st.session_state.doctor_nav_page = label
            st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    page = selected_page

    # **MAIN CONTENT AREA - CENTERED LAYOUT FIX**
    col1, main_content, col3 = st.columns([0.5, 10, 0.5])
    
    with main_content:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        if page == "Dashboard Home":
            doctor_dashboard_home(doctor_id, doctor_profile)
        elif page == "Connection Requests":
            connection_requests_page(doctor_id)
        elif page == "Connected Patients":
            connected_patients_page(doctor_id)
        elif page == "Appointment Requests":
            appointment_requests_page(doctor_id)
        elif page == "Patient Queries":
            patient_queries_page(doctor_id)
        elif page == "Prescriptions":
            prescriptions_page(doctor_id)
        elif page == "Medical Tests":
            medical_tests_page(doctor_id)
        elif page == "Update Profile":
            update_profile_page(doctor_id)
        elif page == "Logout":
            logout()
        
        st.markdown('</div>', unsafe_allow_html=True)

def doctor_dashboard_home(doctor_id, doctor_profile):
    """Doctor dashboard home page with orange theme"""
    
    # Welcome header
    st.markdown(f"""
    <div class="doctor-welcome-header">
        <h1>Welcome, Dr. {doctor_profile.get('full_name', 'Doctor')}! 👨‍⚕️</h1>
        <p>Your medical practice dashboard - manage patients and appointments</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data for stats
    appointments = load_json(APPOINTMENTS_FILE)
    queries = load_json(DOCTOR_QUERIES_FILE)
    patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)

    # Calculate stats
    upcoming_appointments = [
        appt for appt in appointments.values()
        if appt.get("doctor_id") == doctor_id and appt.get("status") == "scheduled"
    ]

    pending_queries = [
        q for q in queries.values()
        if q.get("doctor_id") == doctor_id and q.get("status") == "pending"
    ]

    connected_patients = [
        req for req in patient_doctor_requests.values()
        if req.get("doctor_id") == doctor_id and req.get("status") == "approved"
    ]

    pending_requests = [
        req for req in patient_doctor_requests.values()
        if req.get("doctor_id") == doctor_id and req.get("status") == "pending"
    ]
    
    # Stats cards
    st.markdown("""
    <div class="doctor-stats-container">
        <div class="doctor-stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Scheduled Appointments</div>
        </div>
        <div class="doctor-stat-card">
            <div class="stat-icon">❓</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Pending Queries</div>
        </div>
        <div class="doctor-stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Connected Patients</div>
        </div>
        <div class="doctor-stat-card">
            <div class="stat-icon">🔔</div>
            <div class="stat-number">{}</div>
            <div class="stat-label">Pending Requests</div>
        </div>
    </div>
    """.format(
        len(upcoming_appointments),
        len(pending_queries),
        len(connected_patients),
        len(pending_requests)
    ), unsafe_allow_html=True)
    
    # Quick actions section
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔗 View Connection Requests", key="quick_connections"):
            st.session_state.doctor_nav_page = "Connection Requests"
            st.rerun()
    
    with col2:
        if st.button("💬 Answer Patient Queries", key="quick_queries"):
            st.session_state.doctor_nav_page = "Patient Queries"
            st.rerun()
    
    with col3:
        if st.button("📅 Manage Appointments", key="quick_appointments"):
            st.session_state.doctor_nav_page = "Appointment Requests"
            st.rerun()

def connection_requests_page(doctor_id):
    """Handle patient connection requests"""
    st.title("🔗 Patient Connection Requests")
    
    patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
    profiles = load_json(PROFILES_FILE)

    requests = []
    for req_id, req in patient_doctor_requests.items():
        if req.get("doctor_id") == doctor_id and req.get("status") == "pending":
            requests.append(req)

    st.write(f"**Pending requests for this doctor:** {len(requests)}")

    if not requests:
        st.info("No pending connection requests.")
    else:
        for req in requests:
            patient_profile = profiles.get(req.get("patient_id"), {})
            
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">👤 {patient_profile.get('full_name', 'Unknown Patient')}</div>
                <div class="request-details">
                    <strong>Patient ID:</strong> {req.get('patient_id')}<br>
                    <strong>Request Date:</strong> {safe_format_datetime(req.get('requested_at', 'Unknown'))}<br>
                    <strong>Blood Group:</strong> {patient_profile.get('blood_group', 'Not specified')}<br>
                    <strong>Age:</strong> {patient_profile.get('dob', 'Not specified')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            if col1.button("✅ Accept", key=f"accept_{req['request_id']}"):
                patient_doctor_requests[req['request_id']]['status'] = "approved"
                save_json(PATIENT_DOCTOR_REQUESTS_FILE, patient_doctor_requests)
                st.success("Connection approved!")
                st.rerun()

            if col2.button("❌ Deny", key=f"deny_{req['request_id']}"):
                patient_doctor_requests[req['request_id']]['status'] = "denied"
                save_json(PATIENT_DOCTOR_REQUESTS_FILE, patient_doctor_requests)
                st.warning("Connection denied.")
                st.rerun()

def connected_patients_page(doctor_id):
    """Show connected patients"""
    st.title("👥 Connected Patients")

    patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
    profiles = load_json(PROFILES_FILE)

    # Get all approved connections
    connected_requests = [
        req for req in patient_doctor_requests.values()
        if req.get("doctor_id") == doctor_id and req.get("status") == "approved"
    ]

    st.write(f"**Total Connected Patients:** {len(connected_requests)}")

    if not connected_requests:
        st.info("No patients connected yet. Approve connection requests to see patients here.")
    else:
        for req in connected_requests:
            patient_id = req.get("patient_id")
            patient_profile = profiles.get(patient_id, {})
            
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">👤 {patient_profile.get('full_name', 'Unknown Patient')}</div>
                <div class="request-details">
                    <strong>📧 Email:</strong> {patient_profile.get('email', 'Not provided')}<br>
                    <strong>📱 Mobile:</strong> {patient_profile.get('mobile', 'Not provided')}<br>
                    <strong>🩸 Blood Group:</strong> {patient_profile.get('blood_group', 'Not provided')}<br>
                    <strong>🎂 Age:</strong> {patient_profile.get('dob', 'Not provided')}<br>
                    <strong>🔗 Connected on:</strong> {safe_format_datetime(req.get('requested_at', 'Unknown'))}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 View Medical History", key=f"history_{patient_id}"):
                    st.info("Medical history view feature coming soon!")
            
            with col2:
                if st.button("💬 Send Message", key=f"message_{patient_id}"):
                    st.info("Messaging feature coming soon!")
            
            with col3:
                if st.button("📅 Schedule Appointment", key=f"schedule_{patient_id}"):
                    st.info("Appointment scheduling feature coming soon!")

def appointment_requests_page(doctor_id):
    """Handle appointment requests"""
    st.title("📅 Appointment Requests")
    
    appointments = load_json(APPOINTMENTS_FILE)
    profiles = load_json(PROFILES_FILE)

    requests = [
        appt for appt in appointments.values()
        if appt.get("doctor_id") == doctor_id and appt.get("status") == "requested"
    ]
    st.write(f"**Requested appointments:** {len(requests)}")

    if not requests:
        st.info("No appointment requests found.")
    else:
        for appt in requests:
            patient_profile = profiles.get(appt.get("patient_id"), {})
            
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">📅 Appointment Request from {patient_profile.get('full_name', 'Unknown Patient')}</div>
                <div class="request-details">
                    <strong>Patient:</strong> {patient_profile.get('full_name', 'Unknown')}<br>
                    <strong>Date:</strong> {appt.get('appointment_date')}<br>
                    <strong>Time:</strong> {appt.get('appointment_time')}<br>
                    <strong>Type:</strong> {appt.get('type')}<br>
                    <strong>Notes:</strong> {appt.get('notes', 'No notes')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            if col1.button("✅ Approve", key=f"approve_{appt['appointment_id']}"):
                appointments[appt['appointment_id']]['status'] = "scheduled"
                save_json(APPOINTMENTS_FILE, appointments)
                st.success("Appointment approved!")
                st.rerun()

            if col2.button("❌ Decline", key=f"decline_{appt['appointment_id']}"):
                appointments[appt['appointment_id']]['status'] = "cancelled"
                save_json(APPOINTMENTS_FILE, appointments)
                st.warning("Appointment declined.")
                st.rerun()

def patient_queries_page(doctor_id):
    """Handle patient queries with patient names displayed and FIXED datetime handling"""
    st.title("💬 Respond to Patient Queries")
    
    queries = load_json(DOCTOR_QUERIES_FILE)
    profiles = load_json(PROFILES_FILE)  # Load profiles to get patient names
    
    my_queries = {
        qid: q for qid, q in queries.items()
        if q.get("doctor_id") == doctor_id and q.get("status", "") == "pending"
    }

    if not my_queries:
        st.info("📭 No pending patient queries at the moment.")
    else:
        st.write(f"**📋 You have {len(my_queries)} pending queries**")
        
        for qid, q in my_queries.items():
            patient_id = q.get("patient_id")
            patient_profile = profiles.get(patient_id, {})  # Get patient profile
            patient_name = patient_profile.get("full_name", "Unknown Patient")  # Get patient name
            patient_mobile = patient_profile.get("mobile", "Not provided")
            
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">💬 Patient Query</div>
                <div class="request-details">
                    <strong>From Patient:</strong> {patient_name} ({patient_id})<br>
                    <strong>Mobile:</strong> {patient_mobile}<br>
                    <strong>Question:</strong> {q.get('question')}<br>
                    <strong>Submitted:</strong> {safe_format_datetime(q.get('submitted_at', 'Unknown time'))}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Response form
            with st.form(f"response_form_{qid}"):
                response = st.text_area(
                    f"Your Response to {patient_name}:",
                    key=f"resp_{qid}",
                    height=120,
                    placeholder=f"Type your professional response to {patient_name} here..."
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("📤 Send Response", type="primary")
                with col2:
                    mark_resolved = st.form_submit_button("✅ Mark as Resolved")
                
                if submitted and response.strip():
                    q["doctor_response"] = response.strip()
                    q["status"] = "answered"
                    q["responded_at"] = datetime.now().isoformat()
                    queries[qid] = q
                    save_json(DOCTOR_QUERIES_FILE, queries)
                    st.success(f"✅ Response sent to {patient_name}!")
                    st.balloons()
                    st.rerun()
                
                elif submitted and not response.strip():
                    st.error("❌ Please enter a response before submitting.")
                
                if mark_resolved:
                    q["status"] = "resolved"
                    q["resolved_at"] = datetime.now().isoformat()
                    queries[qid] = q
                    save_json(DOCTOR_QUERIES_FILE, queries)
                    st.success(f"✅ Query from {patient_name} marked as resolved!")
                    st.rerun()
            
            st.markdown("---")

def prescriptions_page(doctor_id):
    """Show prescriptions with patient names"""
    st.title("📄 My Prescriptions")
    
    prescriptions = load_json(PRESCRIPTIONS_FILE)
    profiles = load_json(PROFILES_FILE)
    
    my_presc = [
        p for p in prescriptions.values()
        if p.get("doctor_id") == doctor_id
    ]

    if not my_presc:
        st.info("No prescriptions found.")
    else:
        for pres in my_presc:
            patient_id = pres.get('patient_id')
            patient_profile = profiles.get(patient_id, {})
            patient_name = patient_profile.get('full_name', 'Unknown Patient')
            
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">📄 Prescription for {patient_name}</div>
                <div class="request-details">
                    <strong>Patient:</strong> {patient_name} ({patient_id})<br>
                    <strong>Notes:</strong> {pres.get('notes', 'No notes')[:200]}...
                </div>
            </div>
            """, unsafe_allow_html=True)

def medical_tests_page(doctor_id):
    """Show medical tests with patient names"""
    st.title("🧪 Ordered Medical Tests")
    
    tests = load_json(MEDICAL_TESTS_FILE)
    profiles = load_json(PROFILES_FILE)
    
    my_tests = [
        t for t in tests.values()
        if t.get("doctor_id") == doctor_id
    ]

    if not my_tests:
        st.info("No test orders found.")
    else:
        for test in my_tests:
            patient_id = test.get('patient_id')
            patient_profile = profiles.get(patient_id, {})
            patient_name = patient_profile.get('full_name', 'Unknown Patient')
            
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">🧪 Medical Test for {patient_name}</div>
                <div class="request-details">
                    <strong>Patient:</strong> {patient_name} ({patient_id})<br>
                    <strong>Test Type:</strong> {test.get('test_type')}<br>
                    <strong>Notes:</strong> {test.get('notes', 'N/A')}<br>
                    <strong>📆 Ordered on:</strong> {safe_format_datetime(test.get('ordered_at', 'N/A'))}
                </div>
            </div>
            """, unsafe_allow_html=True)
