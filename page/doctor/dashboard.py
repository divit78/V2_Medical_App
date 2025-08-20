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

def doctor_dashboard():
    load_css()
    doctor_id = st.session_state.get("user_id")
    if not doctor_id:
        st.error("You are not logged in.")
        return

    profiles = load_json(PROFILES_FILE)
    doctor_profile = profiles.get(doctor_id, {})
    st.sidebar.markdown(f"### Dr. {doctor_profile.get('full_name', 'Doctor')}")
    profile_pic = doctor_profile.get("photo_path")
    if profile_pic and os.path.exists(profile_pic):
        st.sidebar.image(profile_pic, width=140)
    else:
        st.sidebar.info("No profile photo uploaded.")

    page = st.sidebar.radio("Navigate", [
        "Dashboard Home",
        "Connection Requests",
        "Connected Patients",
        "Appointment Requests", 
        "Patient Queries",
        "Prescriptions",
        "Medical Tests",
        "Update Profile",
        "Logout"
    ])

    if page == "Dashboard Home":
        st.title(f"Welcome, Dr. {doctor_profile.get('full_name', 'Doctor')}!")
        st.subheader("🔍 Overview")
        appointments = load_json(APPOINTMENTS_FILE)
        queries = load_json(DOCTOR_QUERIES_FILE)
        patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
        
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
        
        st.metric("📅 Scheduled Appointments", len(upcoming_appointments))
        st.metric("❓ Pending Queries", len(pending_queries))
        st.metric("👥 Connected Patients", len(connected_patients))
        st.metric("🔔 Pending Connection Requests", len(pending_requests))

    elif page == "Connection Requests":
        st.title("🔗 Patient Connection Requests")
        
        patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
        profiles = load_json(PROFILES_FILE)
        
        st.write(f"**Debug Info:**")
        st.write(f"- Doctor ID: {doctor_id}")
        st.write(f"- Total requests in database: {len(patient_doctor_requests)}")
        
        requests = []
        for req_id, req in patient_doctor_requests.items():
            if req.get("doctor_id") == doctor_id and req.get("status") == "pending":
                requests.append(req)
        
        st.write(f"- Pending requests for this doctor: {len(requests)}")
        
        if not requests:
            st.info("No pending connection requests.")
            all_doctor_requests = [req for req in patient_doctor_requests.values() if req.get("doctor_id") == doctor_id]
            if all_doctor_requests:
                st.write("**All your requests (for debugging):**")
                for req in all_doctor_requests:
                    patient_profile = profiles.get(req.get("patient_id"), {})
                    st.write(f"- Patient: {patient_profile.get('full_name', 'Unknown')} | Status: {req.get('status')}")
        else:
            for req in requests:
                patient_profile = profiles.get(req.get("patient_id"), {})
                st.markdown("---")
                st.write(f"**Patient Name:** {patient_profile.get('full_name', 'Unknown Patient')}")
                st.write(f"**Patient ID:** {req.get('patient_id')}")
                st.write(f"**Request Date:** {req.get('requested_at', 'Unknown')}")
                
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

    elif page == "Connected Patients":
        st.title("👥 Connected Patients")
        
        patient_doctor_requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
        profiles = load_json(PROFILES_FILE)
        
        # Get all approved connections for this doctor
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
                
                st.markdown("---")
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**👤 {patient_profile.get('full_name', 'Unknown Patient')}**")
                    st.write(f"📧 Email: {patient_profile.get('email', 'Not provided')}")
                    st.write(f"📱 Mobile: {patient_profile.get('mobile', 'Not provided')}")
                    st.write(f"🩸 Blood Group: {patient_profile.get('blood_group', 'Not provided')}")
                    st.write(f"🎂 Age: {patient_profile.get('dob', 'Not provided')}")
                    st.write(f"🔗 Connected on: {req.get('requested_at', 'Unknown')}")
                
                with col2:
                    if st.button("📋 View Medical History", key=f"history_{patient_id}"):
                        st.info("Medical history view feature coming soon!")
                    
                    if st.button("💬 Send Message", key=f"message_{patient_id}"):
                        st.info("Messaging feature coming soon!")
                    
                    if st.button("📅 Schedule Appointment", key=f"schedule_{patient_id}"):
                        st.info("Appointment scheduling feature coming soon!")

    elif page == "Appointment Requests":
        appointments = load_json(APPOINTMENTS_FILE)
        profiles = load_json(PROFILES_FILE)
        
        # ADD DEBUG OUTPUT
        st.write("🐛 **DEBUG - Appointments:**")
        st.write(f"- Doctor ID: {doctor_id}")
        st.write(f"- Total appointments in database: {len(appointments)}")
        
        # Show all appointments for debugging
        all_doctor_appointments = [
            appt for appt in appointments.values()
            if appt.get("doctor_id") == doctor_id
        ]
        st.write(f"- All appointments for this doctor: {len(all_doctor_appointments)}")
        
        requests = [
            appt for appt in appointments.values()
            if appt.get("doctor_id") == doctor_id and appt.get("status") == "requested"
        ]
        st.write(f"- Requested appointments: {len(requests)}")
        
        st.title("📅 Appointment Requests")
        
        if not requests:
            st.info("No appointment requests found.")
            
            # Show all appointments for debugging
            if all_doctor_appointments:
                st.write("**All your appointments (for debugging):**")
                for appt in all_doctor_appointments:
                    patient_profile = profiles.get(appt.get("patient_id"), {})
                    st.write(f"- Patient: {patient_profile.get('full_name', 'Unknown')} | Date: {appt.get('appointment_date')} | Time: {appt.get('appointment_time')} | Status: {appt.get('status')}")
        else:
            for appt in requests:
                patient_profile = profiles.get(appt.get("patient_id"), {})
                st.markdown("---")
                st.write(f"**Patient:** {patient_profile.get('full_name', 'Unknown')}")
                st.write(f"**Date:** {appt.get('appointment_date')}")
                st.write(f"**Time:** {appt.get('appointment_time')}")
                st.write(f"**Type:** {appt.get('type')}")
                st.write(f"**Notes:** {appt.get('notes', 'No notes')}")
                
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
                
    elif page == "Patient Queries":
        queries = load_json(DOCTOR_QUERIES_FILE)
        my_queries = {
            qid: q for qid, q in queries.items()
            if q.get("doctor_id") == doctor_id and q.get("status", "") == "pending"
        }
        st.title("💬 Respond to Patient Queries")
        if not my_queries:
            st.info("No pending queries.")
        else:
            for qid, q in my_queries.items():
                st.markdown("----")
                st.markdown(f"**From Patient:** {q.get('patient_id')}")
                st.markdown(f"**Question:** {q.get('question')}")
                response = st.text_area("Your Response:", key=f"resp_{qid}")
                if st.button("Send Response", key=f"submit_{qid}"):
                    q["doctor_response"] = response
                    q["status"] = "answered"
                    queries[qid] = q
                    save_json(DOCTOR_QUERIES_FILE, queries)
                    st.success("✅ Response sent.")
                    st.rerun()
                    
    elif page == "Prescriptions":
        prescriptions = load_json(PRESCRIPTIONS_FILE)
        my_presc = [
            p for p in prescriptions.values()
            if p.get("doctor_id") == doctor_id
        ]
        st.title("🧾 My Prescriptions")
        if not my_presc:
            st.info("No prescriptions found.")
        else:
            for pres in my_presc:
                st.markdown("---")
                st.markdown(f"- **Patient ID:** {pres.get('patient_id')} \n- **Notes:** {pres.get('notes')[:200]}")
                
    elif page == "Medical Tests":
        tests = load_json(MEDICAL_TESTS_FILE)
        my_tests = [
            t for t in tests.values()
            if t.get("doctor_id") == doctor_id
        ]
        st.title("🧪 Ordered Medical Tests")
        if not my_tests:
            st.info("No test orders found.")
        else:
            for test in my_tests:
                st.markdown("-" * 40)
                st.markdown(f"- **Patient ID:** {test.get('patient_id')} \n- **Test Type:** {test.get('test_type')} \n- **Notes:** {test.get('notes', '-')}")
                st.markdown(f"- 📆 Ordered on: {test.get('ordered_at', '-')}")
                
    elif page == "Update Profile":
        update_profile_page(doctor_id)
        
    elif page == "Logout":
        logout()
