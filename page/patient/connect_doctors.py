import streamlit as st
from datetime import datetime
import json
from utils.file_ops import load_json, save_json
from config.constants import (
    PROFILES_FILE, USERS_FILE, PATIENT_DOCTOR_REQUESTS_FILE
)
from utils.id_utils import generate_id

def connect_doctors_page(patient_id):
    st.title("🔗 Search & Connect With Doctors")
    
    # Enhanced styling for cards
    st.markdown("""
    <style>
    .search-section {
        background: linear-gradient(135deg, #FF8A65, #FF7043);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .doctor-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
    .doctor-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FF8C00, #FFA500);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        color: white;
        margin-right: 1rem;
        font-weight: bold;
    }
    .doctor-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
    }
    .doctor-specialty {
        color: #FF7043;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.2rem 0;
    }
    .connection-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        border-left: 4px solid #4CAF50;
    }
    .status-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .fee-highlight {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Load data
    users = load_json(USERS_FILE)
    profiles = load_json(PROFILES_FILE)
    patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)

    # Filter doctors
    doctors = {uid: user for uid, user in users.items() if user.get('user_type') == 'doctor'}
    doctor_profiles = {uid: profile for uid, profile in profiles.items() if uid in doctors}

    # Search section
    st.markdown("""
    <div class="search-section">
        <h3 style="margin-top: 0; color: white;">🔍 Find Your Perfect Doctor</h3>
        <p style="margin-bottom: 0; opacity: 0.9;">Search by specialization or name to connect with qualified healthcare professionals</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get unique specializations
        specializations = ["All"] + sorted(list(set([
            profile.get('specialization', 'General') 
            for profile in doctor_profiles.values() 
            if profile.get('specialization')
        ])))
        selected_specialization = st.selectbox("🩺 Specialization", specializations)

    with col2:
        search_name = st.text_input("👨‍⚕️ Search Doctor Name", placeholder="Enter doctor's name...")

    # Filter doctors based on search criteria
    filtered_doctors = {}
    for doc_id, profile in doctor_profiles.items():
        # Specialization filter
        if selected_specialization != "All":
            if profile.get('specialization') != selected_specialization:
                continue
        
        # Name search filter
        if search_name:
            full_name = profile.get('full_name', '').lower()
            if search_name.lower() not in full_name:
                continue
        
        filtered_doctors[doc_id] = profile

    # Display results
    if filtered_doctors:
        st.markdown(f"### 👨‍⚕️ Available Doctors ({len(filtered_doctors)} found)")
        st.info("Click the connect button to send a connection request")
        
        display_doctors_in_containers(filtered_doctors, patient_id, patient_doctor_requests)
    else:
        st.warning("🔍 No doctors found matching your search criteria. Try adjusting your filters.")

    # Display connection requests
    display_connection_requests_in_container(patient_id, patient_doctor_requests, doctor_profiles)

def display_doctors_in_containers(filtered_doctors, patient_id, patient_doctor_requests):
    """Display doctors using Streamlit containers with borders"""
    
    doctor_list = list(filtered_doctors.items())
    
    # Display doctors in rows of 2
    for i in range(0, len(doctor_list), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(doctor_list):
                doc_id, profile = doctor_list[i + j]
                
                with col:
                    display_doctor_card_in_container(doc_id, profile, patient_id, patient_doctor_requests)

def display_doctor_card_in_container(doc_id, profile, patient_id, patient_doctor_requests):
    """Display individual doctor card using Streamlit container with border"""
    
    # Check connection status
    connection_status = None
    for req in patient_doctor_requests.values():
        if req.get('patient_id') == patient_id and req.get('doctor_id') == doc_id:
            connection_status = req.get('status')
            break

    # Get doctor info and clean up display
    full_name = profile.get('full_name', 'Unknown Doctor')
    # Remove "Dr." prefix if it exists to avoid "Dr. Dr." issue
    if full_name.startswith('Dr. '):
        display_name = full_name[4:]
    else:
        display_name = full_name
    
    specialization = profile.get('specialization', 'General Medicine')
    experience = profile.get('experience', 0)
    hospital = profile.get('hospital_clinic', 'Private Practice')
    consultation_fee = profile.get('consultation_fee', 0)
    
    # Truncate long hospital names
    if len(hospital) > 25:
        hospital_display = hospital[:22] + "..."
    else:
        hospital_display = hospital
    
    # Get initials for avatar
    name_parts = display_name.split()
    initials = ''.join([part[0].upper() for part in name_parts[:2]]) if name_parts else 'DR'
    
    # Create card using bordered container
    with st.container(border=True):
        # Status indicator at the top
        if connection_status == "approved":
            st.success("✅ Connected")
        elif connection_status == "pending":
            st.warning("⏳ Request Pending")
        
        # Doctor header with avatar
        st.markdown(f"""
        <div class="doctor-card-header">
            <div class="doctor-avatar">{initials}</div>
            <div>
                <div class="doctor-name">Dr. {display_name}</div>
                <div class="doctor-specialty">{specialization}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Doctor information
        col1, col2 = st.columns(2)
        with col1:
            st.write("📊 **Experience:**")
            st.write(f"   {experience} years")
            st.write("🏥 **Hospital:**")
            st.write(f"   {hospital_display}")
        
        with col2:
            st.write("💰 **Consultation:**")
            st.markdown(f'   <span class="fee-highlight">₹{consultation_fee:.0f}</span>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Connect button
        if connection_status == "approved":
            st.button("✅ Already Connected", key=f"connect_{doc_id}", disabled=True, use_container_width=True)
        elif connection_status == "pending":
            st.button("⏳ Request Sent", key=f"connect_{doc_id}", disabled=True, use_container_width=True, type="secondary")
        else:
            if st.button("➕ Send Connection Request", key=f"connect_{doc_id}", type="primary", use_container_width=True):
                if send_connection_request(patient_id, doc_id, profile, patient_doctor_requests):
                    st.success(f"✅ Connection request sent to Dr. {display_name}!")
                    st.rerun()

def send_connection_request(patient_id, doctor_id, doctor_profile, patient_doctor_requests):
    """Send connection request to doctor"""
    try:
        request_id = generate_id("REQ")
        new_request = {
            "request_id": request_id,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "status": "pending",
            "requested_at": datetime.now().isoformat()
        }
        
        patient_doctor_requests[request_id] = new_request
        save_json(PATIENT_DOCTOR_REQUESTS_FILE, patient_doctor_requests)
        
        return True
    except Exception as e:
        st.error(f"Failed to send connection request: {e}")
        return False

def display_connection_requests_in_container(patient_id, patient_doctor_requests, doctor_profiles):
    """Display connection requests section using container with border"""
    
    # Get connection requests for this patient
    patient_requests = [
        req for req in patient_doctor_requests.values()
        if req.get('patient_id') == patient_id
    ]
    
    if patient_requests:
        st.markdown("### 📋 Your Connection Requests")
        
        with st.container(border=True):
            for req in patient_requests:
                doctor_id = req.get("doctor_id")
                doctor_profile = doctor_profiles.get(doctor_id, {})
                doctor_name = doctor_profile.get('full_name', 'Unknown Doctor')
                specialization = doctor_profile.get('specialization', 'General')
                status = req.get('status', 'pending')
                
                # Clean up doctor name display
                if doctor_name.startswith('Dr. '):
                    display_name = doctor_name[4:]
                else:
                    display_name = doctor_name
                
                # Display request with status
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Dr. {display_name}** ({specialization})")
                
                with col2:
                    if status == "approved":
                        st.success("🟢 Approved")
                    elif status == "pending":
                        st.warning("🟡 Pending")
                    else:
                        st.error("🔴 Denied")
                
                if req != patient_requests[-1]:  # Add divider if not last item
                    st.divider()

# Alternative version using metric containers for a different look
def display_doctors_as_metrics(filtered_doctors, patient_id, patient_doctor_requests):
    """Alternative display using metric cards"""
    
    doctor_list = list(filtered_doctors.items())
    
    for i in range(0, len(doctor_list), 3):  # 3 per row for metrics
        cols = st.columns(3)
        
        for j, col in enumerate(cols):
            if i + j < len(doctor_list):
                doc_id, profile = doctor_list[i + j]
                
                with col:
                    display_doctor_metric_card(doc_id, profile, patient_id, patient_doctor_requests)

def display_doctor_metric_card(doc_id, profile, patient_id, patient_doctor_requests):
    """Display doctor as a metric card"""
    
    # Get doctor info
    full_name = profile.get('full_name', 'Unknown Doctor')
    if full_name.startswith('Dr. '):
        display_name = full_name[4:]
    else:
        display_name = full_name
    
    specialization = profile.get('specialization', 'General Medicine')
    experience = profile.get('experience', 0)
    consultation_fee = profile.get('consultation_fee', 0)
    
    # Check connection status
    connection_status = None
    for req in patient_doctor_requests.values():
        if req.get('patient_id') == patient_id and req.get('doctor_id') == doc_id:
            connection_status = req.get('status')
            break
    
    with st.container(border=True):
        st.metric(
            label=f"Dr. {display_name}",
            value=f"₹{consultation_fee:.0f}",
            delta=f"{experience} years exp"
        )
        st.caption(f"🩺 {specialization}")
        
        if connection_status == "approved":
            st.button("✅ Connected", key=f"metric_connect_{doc_id}", disabled=True, use_container_width=True)
        elif connection_status == "pending":
            st.button("⏳ Pending", key=f"metric_connect_{doc_id}", disabled=True, use_container_width=True)
        else:
            if st.button("Connect", key=f"metric_connect_{doc_id}", type="primary", use_container_width=True):
                if send_connection_request(patient_id, doc_id, profile, patient_doctor_requests):
                    st.success(f"Request sent!")
                    st.rerun()
