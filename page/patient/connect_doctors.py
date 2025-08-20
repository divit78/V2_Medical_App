import streamlit as st
from utils.file_ops import load_json, save_json
from config.constants import USERS_FILE, PATIENT_DOCTOR_REQUESTS_FILE, PROFILES_FILE
from utils.id_utils import generate_id
from datetime import datetime

def connect_doctors_page(patient_id):
    st.title("🔗 Search & Connect With Doctors")
    
    try:
        users = load_json(USERS_FILE)
        profiles = load_json(PROFILES_FILE)
        doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
        
        # Debug: Check if data is loaded
        st.write(f"DEBUG: Found {len(users)} users total")
        st.write(f"DEBUG: Found {len(profiles)} profiles total")
        
        # Get all doctors
        all_doctors = {uid: u for uid, u in users.items() if u.get("user_type") == "doctor"}
        st.write(f"DEBUG: Found {len(all_doctors)} doctors")
        
        if not all_doctors:
            st.error("No doctors found in the database. Please run the insert_sample_doctors.py script first.")
            return
            
        doctor_profiles = {}
        for uid in all_doctors.keys():
            profile = profiles.get(uid, {})
            if profile:  # Only add if profile exists
                doctor_profiles[uid] = profile
                
        st.write(f"DEBUG: Found {len(doctor_profiles)} doctor profiles")

        # Get patient's existing requests
        requests = [req for req in doctor_requests.values() if req.get('patient_id') == patient_id]
        requested_doctor_ids = {req.get("doctor_id"): req for req in requests}

        # Filters
        st.subheader("Filter/Search Doctors")
        specializations = []
        for profile in doctor_profiles.values():
            spec = profile.get('specialization')
            if spec and spec not in specializations:
                specializations.append(spec)
        
        selected_spec = st.selectbox("Specialization", ["All"] + sorted(specializations))
        search_name = st.text_input("Search Doctor Name")

        st.markdown("---")
        
        # Display doctors
        displayed_count = 0
        for doc_id, doc_profile in doctor_profiles.items():
            # Apply filters
            if selected_spec != "All" and doc_profile.get("specialization") != selected_spec:
                continue
                
            name = doc_profile.get("full_name", "Unknown Doctor")
            if search_name and search_name.lower() not in name.lower():
                continue

            displayed_count += 1
            
            # Display doctor info
            st.markdown(f"**{name}**")
            st.write(f"👨‍⚕️ **Specialization:** {doc_profile.get('specialization', '-')}")
            st.write(f"📊 **Experience:** {doc_profile.get('experience', '-')} years")
            st.write(f"🏥 **Hospital:** {doc_profile.get('hospital_clinic', '-')}")
            st.write(f"💰 **Consultation Fee:** ₹{doc_profile.get('consultation_fee', '-')}")
            
            # Check if already requested
            already_requested = requested_doctor_ids.get(doc_id)
            if already_requested:
                status = already_requested.get("status", "pending")
                st.info(f"Request Status: {status.capitalize()}")
            else:
                if st.button(f"Send Connection Request", key=f"req_{doc_id}"):
                    req_id = generate_id("PDR")
                    new_request = {
                        "request_id": req_id,
                        "patient_id": patient_id,
                        "doctor_id": doc_id,
                        "status": "pending",
                        "requested_at": datetime.now().isoformat()
                    }
                    doctor_requests[req_id] = new_request
                    save_json(PATIENT_DOCTOR_REQUESTS_FILE, doctor_requests)
                    st.success(f"Connection request sent to {name}")
                  
            
            st.markdown("---")
            
        if displayed_count == 0:
            st.info("No doctors match your search criteria.")

        # Show existing requests
        st.subheader("Your Connection Requests")
        if requests:
            for req in requests:
                docprof = profiles.get(req.get("doctor_id"), {})
                doctor_name = docprof.get('full_name', 'Unknown Doctor')
                specialization = docprof.get('specialization', '-')
                status = req.get('status', 'pending')
                st.write(f"**{doctor_name}** ({specialization}) - Status: {status.capitalize()}")
        else:
            st.info("No connection requests sent yet.")
            
    except Exception as e:
        st.error(f"Error loading doctors: {e}")
        st.write("Please check your database connection and ensure sample doctors are inserted.")
