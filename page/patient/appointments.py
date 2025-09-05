import streamlit as st
from datetime import datetime, date, time
import json
from utils.db_helper import db
from utils.id_utils import generate_id

def ask_questions_and_appointments(patient_id):
    st.title("🤝 Ask Doctor / Book Appointment")
    
    if st.button("🔧 Test Database Connection"):
        try:
            db.connect()
            st.success("✅ Database connected successfully!")
        except Exception as e:
            st.error(f"❌ Database connection failed: {str(e)}")
        return
    
    try:
        db.connect()
        query = """
            SELECT pdr.doctor_id, p.full_name, p.specialization 
            FROM patient_doctor_requests pdr 
            JOIN profiles p ON pdr.doctor_id = p.user_id 
            WHERE pdr.patient_id = %s AND pdr.status = 'approved'
        """
        connected_doctors = db.execute_query(query, (patient_id,))
        
    except Exception as e:
        st.error(f"Error loading doctors: {str(e)}")
        return
    
    if not connected_doctors:
        st.warning("⚠️ You need to connect with doctors first!")
        st.info("Go to 'Search Doctors' to send connection requests to doctors.")
        return
    
    doctor_options = {}
    for doctor in connected_doctors:
        doctor_name = f"Dr. {doctor.get('full_name', 'Unknown')} - {doctor.get('specialization', 'General')}"
        doctor_options[doctor_name] = doctor.get('doctor_id')
    
    st.subheader("👨‍⚕️ Select Doctor")
    selected_doctor_name = st.selectbox(
        "Choose which doctor you want to contact:",
        options=list(doctor_options.keys()),
        help="Only doctors you're connected with are shown here"
    )
    
    if selected_doctor_name:
        selected_doctor_id = doctor_options[selected_doctor_name]
        
        try:
            profile_query = "SELECT * FROM profiles WHERE user_id = %s"
            profile_result = db.execute_query(profile_query, (selected_doctor_id,))
            selected_doctor_profile = profile_result[0] if profile_result else {}
        except Exception as e:
            st.error(f"Error loading doctor profile: {str(e)}")
            selected_doctor_profile = {}
        
        with st.expander("ℹ️ Doctor Information", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** Dr. {selected_doctor_profile.get('full_name', 'Unknown')}")
                st.write(f"**Specialization:** {selected_doctor_profile.get('specialization', 'Not specified')}")
                st.write(f"**Experience:** {selected_doctor_profile.get('experience', 'Not specified')} years")
            with col2:
                st.write(f"**Hospital:** {selected_doctor_profile.get('hospital_clinic', 'Not provided')}")
                st.write(f"**Consultation Fee:** ₹{selected_doctor_profile.get('consultation_fee', 'Not specified')}")
                availability = selected_doctor_profile.get('availability')
                if availability:
                    try:
                        if isinstance(availability, str):
                            availability = json.loads(availability)
                        
                        if isinstance(availability, list):
                            availability_str = ', '.join(str(day) for day in availability) if availability else "Not specified"
                        else:
                            availability_str = str(availability)
                    except:
                        availability_str = str(availability) if availability else "Not specified"
                else:
                    availability_str = "Not specified"
                st.write(f"**Available Days:** {availability_str}")
        
        st.markdown("---")
        
        st.subheader("💬 What would you like to do?")
        action_type = st.radio(
            "Choose your action:",
            ["Ask a Question Only", "Book an Appointment", "Ask Question + Book Appointment"],
            help="Select what you want to do with this doctor"
        )
        
        st.subheader("💭 Your Question/Message")
        question = st.text_area(
            "Enter Your Question or Message:",
            placeholder="Describe your symptoms, concerns, or questions for the doctor...",
            height=120
        )
        
        preferred_date = None
        preferred_time = None
        appointment_type = "No Appointment"
        
        if action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
            st.subheader("📅 Appointment Details")
            
            appointment_type = st.selectbox(
                "Appointment Type",
                ["Video Call", "Clinic Visit"],
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
            
            doctor_availability = selected_doctor_profile.get('availability')
            if doctor_availability and preferred_date:
                weekday_name = preferred_date.strftime("%a")
                
                try:
                    if isinstance(doctor_availability, str):
                        doctor_availability = json.loads(doctor_availability)
                    
                    if isinstance(doctor_availability, list):
                        if weekday_name in doctor_availability:
                            st.success(f"✅ Dr. {selected_doctor_profile.get('full_name', 'Doctor')} is available on {weekday_name}s")
                        else:
                            available_days = ', '.join(str(day) for day in doctor_availability)
                            st.warning(f"⚠️ Dr. {selected_doctor_profile.get('full_name', 'Doctor')} is typically available on: {available_days}")
                except:
                    st.info(f"⚠️ Dr. {selected_doctor_profile.get('full_name', 'Doctor')} availability: {str(doctor_availability)}")
        
        st.subheader("📋 Summary")
        if action_type == "Ask a Question Only":
            st.info("You will send a question to the doctor (no appointment will be booked)")
        elif action_type == "Book an Appointment":
            st.info(f"You will book a {appointment_type} appointment for {preferred_date} at {preferred_time}")
        else:
            st.info(f"You will send a question AND book a {appointment_type} appointment for {preferred_date} at {preferred_time}")
        
        if st.button("📤 Submit Request", type="primary"):
            if not question.strip():
                st.error("Please enter your question or message.")
            elif action_type in ["Book an Appointment", "Ask Question + Book Appointment"] and (not preferred_date or not preferred_time):
                st.error("Please select both date and time for your appointment.")
            else:
                try:
                    db.connect()
                    
                    query_id = generate_id("DQ")
                    
                    db_appointment_type = "No Appointment"
                    if action_type != "Ask a Question Only":
                        if appointment_type == "Video Call":
                            db_appointment_type = "Video Call"
                        elif appointment_type in ["Clinic Visit", "In-Person Visit"]:
                            db_appointment_type = "Clinic Visit"
                    
                    query_data = {
                        'patient_id': patient_id,
                        'doctor_id': selected_doctor_id,
                        'question': question.strip(),
                        'submitted_at': datetime.now(),
                        'appointment_type': db_appointment_type,
                        'preferred_date': preferred_date,
                        'preferred_time': preferred_time,
                        'status': 'pending',
                        'doctor_response': None
                    }
                    
                    if db.save_doctor_query(query_id, query_data):
                        if action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
                            appointment_id = generate_id("APT")
                            
                            db_type = "Video Call" if appointment_type == "Video Call" else "Clinic Visit"
                            
                            appointment_data = {
                                'patient_id': patient_id,
                                'doctor_id': selected_doctor_id,
                                'appointment_date': preferred_date,
                                'appointment_time': preferred_time,
                                'type': db_type,
                                'status': 'requested',  # CHANGED: Start with 'requested' status
                                'notes': question.strip(),
                                'created_at': datetime.now()
                            }
                            
                            if db.save_appointment(appointment_id, appointment_data):
                                st.success(f"✅ Question sent and appointment requested for {preferred_date} at {preferred_time}!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to create appointment")
                        else:
                            st.success(f"✅ Your question has been sent to Dr. {selected_doctor_profile.get('full_name', 'Doctor')}!")
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to send question")
                        
                except Exception as e:
                    st.error(f"❌ Error saving to database: {str(e)}")
    
    # UPDATED: Patient History with Status Display
    st.markdown("---")
    st.subheader("🗂️ Your Previous Queries & Appointments")
    
    try:
        db.connect()
        
        queries_query = """
            SELECT dq.*, p.full_name as doctor_name 
            FROM doctor_queries dq 
            LEFT JOIN profiles p ON dq.doctor_id = p.user_id 
            WHERE dq.patient_id = %s 
            ORDER BY dq.submitted_at DESC
        """
        patient_queries = db.execute_query(queries_query, (patient_id,))
        
        # UPDATED: Get ALL appointments regardless of status
        appointments_query = """
            SELECT a.*, p.full_name as doctor_name 
            FROM appointments a 
            LEFT JOIN profiles p ON a.doctor_id = p.user_id 
            WHERE a.patient_id = %s 
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        patient_appointments = db.execute_query(appointments_query, (patient_id,))
        
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")
        patient_queries = []
        patient_appointments = []
    
    if not patient_queries and not patient_appointments:
        st.info("No questions or appointments yet.")
    else:
        if patient_queries:
            st.write("**💬 Your Questions:**")
            for query in patient_queries:
                doctor_name = query.get("doctor_name", "Unknown Doctor")
                
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
        
        # UPDATED: Show appointments with status indicators
        if patient_appointments:
            st.write("**📅 Your Appointments:**")
            for appointment in patient_appointments:
                doctor_name = appointment.get("doctor_name", "Unknown Doctor")
                
                # UPDATED: Status colors and labels
                status_colors = {
                    "requested": "🟡",      # Pending (yellow)
                    "scheduled": "🟢",     # Approved (green) 
                    "completed": "✅",     # Completed (check mark)
                    "cancelled": "🔴"      # Declined/Cancelled (red)
                }
                
                status_labels = {
                    "requested": "Pending Approval",
                    "scheduled": "Approved",
                    "completed": "Completed", 
                    "cancelled": "Declined"
                }
                
                status = appointment.get("status", "unknown")
                status_icon = status_colors.get(status, "⚪")
                status_label = status_labels.get(status, status.title())
                
                with st.expander(f"{status_icon} Appointment with Dr. {doctor_name} - {status_label}"):
                    st.write(f"**Date:** {appointment.get('appointment_date', 'Not set')}")
                    st.write(f"**Time:** {appointment.get('appointment_time', 'Not set')}")
                    st.write(f"**Type:** {appointment.get('type', 'Not specified')}")
                    st.write(f"**Status:** {status_label}")
                    if appointment.get('notes'):
                        st.write(f"**Notes:** {appointment.get('notes')}")
                    
                    # Show appropriate message based on status
                    if status == "requested":
                        st.info("⏳ Waiting for doctor's approval")
                    elif status == "scheduled":
                        st.success("✅ Your appointment has been approved!")
                    elif status == "cancelled":
                        st.error("❌ Your appointment request was declined")
                    elif status == "completed":
                        st.success("✅ Appointment completed")