import streamlit as st
from datetime import datetime, date, time
from utils.file_ops import load_json, save_json
from config.constants import (
    DOCTOR_QUERIES_FILE, APPOINTMENTS_FILE, PROFILES_FILE, 
    PATIENT_DOCTOR_REQUESTS_FILE
)
from utils.id_utils import generate_id

def ask_questions_and_appointments(patient_id):
    st.title("🤝 Ask Doctor / Book Appointment")
    
    # Load data
    profiles = load_json(PROFILES_FILE)
    doctor_queries = load_json(DOCTOR_QUERIES_FILE)
    appointments = load_json(APPOINTMENTS_FILE)
    patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
    
    # Get connected doctors for this patient
    connected_requests = [
        req for req in patient_doctor_requests.values()
        if req.get("patient_id") == patient_id and req.get("status") == "approved"
    ]
    
    if not connected_requests:
        st.warning("⚠️ You need to connect with doctors first!")
        st.info("Go to 'Search Doctors' to send connection requests to doctors.")
        return
    
    # Create doctor selection options
    doctor_options = {}
    for req in connected_requests:
        doctor_id = req.get("doctor_id")
        doctor_profile = profiles.get(doctor_id, {})
        doctor_name = f"Dr. {doctor_profile.get('full_name', 'Unknown')} - {doctor_profile.get('specialization', 'General')}"
        doctor_options[doctor_name] = doctor_id
    
    # Doctor Selection
    st.subheader("👨‍⚕️ Select Doctor")
    selected_doctor_name = st.selectbox(
        "Choose which doctor you want to contact:",
        options=list(doctor_options.keys()),
        help="Only doctors you're connected with are shown here"
    )
    
    if selected_doctor_name:
        selected_doctor_id = doctor_options[selected_doctor_name]
        selected_doctor_profile = profiles.get(selected_doctor_id, {})
        
        # Show selected doctor info
        with st.expander("ℹ️ Doctor Information", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** Dr. {selected_doctor_profile.get('full_name', 'Unknown')}")
                st.write(f"**Specialization:** {selected_doctor_profile.get('specialization', 'Not specified')}")
                st.write(f"**Experience:** {selected_doctor_profile.get('experience', 'Not specified')} years")
            with col2:
                st.write(f"**Hospital:** {selected_doctor_profile.get('hospital_clinic', 'Not provided')}")
                st.write(f"**Consultation Fee:** ₹{selected_doctor_profile.get('consultation_fee', 'Not specified')}")
                st.write(f"**Available Days:** {', '.join(selected_doctor_profile.get('availability', []))}")
        
        st.markdown("---")
        
        # IMPROVED: Ask what they want to do first
        st.subheader("💬 What would you like to do?")
        
        action_type = st.radio(
            "Choose your action:",
            ["Ask a Question Only", "Book an Appointment", "Ask Question + Book Appointment"],
            help="Select what you want to do with this doctor"
        )
        
        # Question section (always shown)
        st.subheader("💭 Your Question/Message")
        question = st.text_area(
            "Enter Your Question or Message:",
            placeholder="Describe your symptoms, concerns, or questions for the doctor...",
            height=120
        )
        
        # Appointment section (shown based on selection)
        preferred_date = None
        preferred_time = None
        appointment_type = "No Appointment"  # Default
        
        if action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
            st.subheader("📅 Appointment Details")
            
            # Appointment type selection
            appointment_type = st.selectbox(
                "Appointment Type",
                ["Video Call", "In-Person Visit", "Phone Call"],
                help="Choose how you'd like to meet with the doctor"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                preferred_date = st.date_input(
                    "Preferred Date",
                    min_value=date.today(),
                    help="Select your preferred appointment date"
                )
            
            with col2:
                preferred_time = st.time_input(
                    "Preferred Time",
                    value=time(9, 0),
                    help="Select your preferred appointment time"
                )
            
            # Show doctor's availability
            doctor_availability = selected_doctor_profile.get('availability', [])
            if doctor_availability and preferred_date:
                weekday_name = preferred_date.strftime("%a")
                if weekday_name in doctor_availability:
                    st.success(f"✅ Dr. {selected_doctor_profile.get('full_name', 'Doctor')} is available on {weekday_name}s")
                else:
                    st.warning(f"⚠️ Dr. {selected_doctor_profile.get('full_name', 'Doctor')} is typically available on: {', '.join(doctor_availability)}")
        
        # Summary of what will be submitted
        st.subheader("📋 Summary")
        if action_type == "Ask a Question Only":
            st.info("You will send a question to the doctor (no appointment will be booked)")
        elif action_type == "Book an Appointment":
            st.info(f"You will book a {appointment_type} appointment for {preferred_date} at {preferred_time}")
        else:  # Ask Question + Book Appointment
            st.info(f"You will send a question AND book a {appointment_type} appointment for {preferred_date} at {preferred_time}")
        
        # Submit button
        if st.button("📤 Submit Request", type="primary"):
            if not question.strip():
                st.error("Please enter your question or message.")
            elif action_type in ["Book an Appointment", "Ask Question + Book Appointment"] and (not preferred_date or not preferred_time):
                st.error("Please select both date and time for your appointment.")
            else:
                # Save the query (always)
                query_id = generate_id("DQ")
                new_query = {
                    "query_id": query_id,
                    "patient_id": patient_id,
                    "doctor_id": selected_doctor_id,
                    "question": question.strip(),
                    "submitted_at": datetime.now().isoformat(),
                    "appointment_type": appointment_type if action_type != "Ask a Question Only" else "No Appointment",
                    "preferred_date": preferred_date.isoformat() if preferred_date else None,
                    "preferred_time": preferred_time.isoformat() if preferred_time else None,
                    "status": "pending",
                    "doctor_response": None
                }
                
                doctor_queries[query_id] = new_query
                save_json(DOCTOR_QUERIES_FILE, doctor_queries)
                
                # Create appointment if requested
                if action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
                    appointment_id = generate_id("APT")
                    new_appointment = {
                        "appointment_id": appointment_id,
                        "patient_id": patient_id,
                        "doctor_id": selected_doctor_id,
                        "appointment_date": preferred_date.isoformat(),
                        "appointment_time": preferred_time.isoformat(),
                        "type": appointment_type,
                        "status": "requested",
                        "notes": question.strip(),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    appointments = load_json(APPOINTMENTS_FILE)
                    appointments[appointment_id] = new_appointment
                    save_json(APPOINTMENTS_FILE, appointments)
                    
                    st.success(f"✅ Question sent and appointment requested for {preferred_date} at {preferred_time}!")
                    st.balloons()
                else:
                    st.success(f"✅ Your question has been sent to Dr. {selected_doctor_profile.get('full_name', 'Doctor')}!")
                
                st.rerun()
    
    # Previous Queries & Appointments
    st.markdown("---")
    st.subheader("🗂️ Your Previous Queries & Appointments")
    
    # Filter queries for this patient
    patient_queries = [
        q for q in doctor_queries.values() 
        if q.get("patient_id") == patient_id
    ]
    
    # Filter appointments for this patient
    patient_appointments = [
        a for a in appointments.values()
        if a.get("patient_id") == patient_id
    ]
    
    if not patient_queries and not patient_appointments:
        st.info("No questions or appointments yet.")
    else:
        # Show queries
        if patient_queries:
            st.write("**💬 Your Questions:**")
            for query in sorted(patient_queries, key=lambda x: x.get("submitted_at", ""), reverse=True):
                doctor_profile = profiles.get(query.get("doctor_id"), {})
                doctor_name = doctor_profile.get("full_name", "Unknown Doctor")
                
                # Show if this query had an appointment request
                has_appointment = query.get("appointment_type", "No Appointment") != "No Appointment"
                appointment_text = f" + Appointment Request" if has_appointment else ""
                
                with st.expander(f"Question to Dr. {doctor_name}{appointment_text} - {query.get('status', 'pending').title()}"):
                    st.write(f"**Question:** {query.get('question', 'No question')}")
                    st.write(f"**Submitted:** {query.get('submitted_at', 'Unknown')}")
                    st.write(f"**Status:** {query.get('status', 'pending').title()}")
                    
                    if has_appointment:
                        st.write(f"**Appointment Type:** {query.get('appointment_type')}")
                        st.write(f"**Preferred Date:** {query.get('preferred_date', 'Not specified')}")
                        st.write(f"**Preferred Time:** {query.get('preferred_time', 'Not specified')}")
                    
                    if query.get("doctor_response"):
                        st.write(f"**Doctor's Response:** {query.get('doctor_response')}")
                    else:
                        st.info("Waiting for doctor's response...")
        
        # Show appointments
        if patient_appointments:
            st.write("**📅 Your Appointments:**")
            for appointment in sorted(patient_appointments, key=lambda x: x.get("appointment_date", ""), reverse=True):
                doctor_profile = profiles.get(appointment.get("doctor_id"), {})
                doctor_name = doctor_profile.get("full_name", "Unknown Doctor")
                
                status_colors = {
                    "requested": "🟡",
                    "scheduled": "🟢", 
                    "cancelled": "🔴",
                    "completed": "✅"
                }
                status_icon = status_colors.get(appointment.get("status", ""), "⚪")
                
                with st.expander(f"{status_icon} Appointment with Dr. {doctor_name} - {appointment.get('status', 'unknown').title()}"):
                    st.write(f"**Date:** {appointment.get('appointment_date', 'Not set')}")
                    st.write(f"**Time:** {appointment.get('appointment_time', 'Not set')}")
                    st.write(f"**Type:** {appointment.get('type', 'Not specified')}")
                    st.write(f"**Status:** {appointment.get('status', 'unknown').title()}")
                    if appointment.get('notes'):
                        st.write(f"**Notes:** {appointment.get('notes')}")
