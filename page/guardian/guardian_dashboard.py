import streamlit as st
import os
from datetime import datetime

from page.navigation import logout
from utils.file_ops import load_json, save_json
from config.constants import (
    USERS_FILE, PROFILES_FILE, GUARDIAN_REQUESTS_FILE,
    MEDICINES_FILE, SCHEDULES_FILE
)
from page.update_profile_page import update_profile_page


def load_css():
    st.markdown(
        """
        <style>
        /* Sidebar header */
        .sidebar .sidebar-content h1.sidebar-header {
            font-size: 2rem;
            font-weight: 900;
            color: #104E8B;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #4a90e2;
            margin-bottom: 1rem;
            user-select: none;
        }

        /* Sidebar profile picture */
        .sidebar .sidebar-content img {
            border-radius: 50%;
            padding: 5px;
            border: 2px solid #4a90e2;
            margin-bottom: 1rem;
        }

        /* Sidebar info alert */
        .sidebar .sidebar-content div[role="alert"] {
            background-color: #e3f2fd;
            color: #1565c0;
            border-radius: 10px;
            padding: 8px;
            margin-top: 1rem;
            font-size: 0.9rem;
        }

        /* Sidebar nav radios container */
        .stRadio > div {
            display: flex;
            flex-direction: column;
        }

        /* Sidebar navigation radio buttons with 3D/neumorphic style */
        .stRadio > div > label {
            background: #f0f0f3;
            border-radius: 12px;
            box-shadow:
                6px 6px 8px #bebebe,
               -6px -6px 8px #ffffff;
            padding: 10px 20px;
            margin-bottom: 12px;
            font-weight: 600;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Hover effect: lighten and shadow lift */
        .stRadio > div > label:hover {
            background: #e0e5ec;
            box-shadow:
                3px 3px 6px #bebebe,
               -3px -3px 6px #ffffff;
            color: #104E8B;
        }

        /* Selected radio (pressed in effect) */
        .stRadio > div > label[aria-checked="true"] {
            background: #d1d9e6;
            box-shadow:
                inset 6px 6px 8px #bebebe,
                inset -6px -6px 8px #ffffff;
            color: #104E8B;
            font-weight: 700;
        }

        /* Hide native radio input circles */
        .stRadio > div > input[type="radio"] {
            display: none;
        }

        /* Buttons hover effect */
        button:hover {
            background-color: #4a90e2 !important;
            color: white !important;
            cursor: pointer;
        }

        /* Subheaders */
        h3 {
            color: #1565c0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Horizontal lines */
        hr {
            border-top: 1px solid #4a90e2;
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def guardian_dashboard():
    # Inject CSS styles early
    load_css()

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("You must be logged in to access the Guardian Dashboard.")
        return

    users = load_json(USERS_FILE)
    profiles = load_json(PROFILES_FILE)
    guardian_profile = profiles.get(user_id, {})
    connected_patient_id = guardian_profile.get("connected_patient")
    connected_patient = profiles.get(connected_patient_id) if connected_patient_id else {}

    # Sidebar header
    st.sidebar.markdown('<h1 class="sidebar-header">Guardian Dashboard</h1>', unsafe_allow_html=True)

    # Sidebar profile name and image
    st.sidebar.markdown(f"## {guardian_profile.get('full_name', 'Guardian')}")
    profile_pic_path = guardian_profile.get("profile_pic")
    if profile_pic_path and os.path.exists(profile_pic_path):
        st.sidebar.image(profile_pic_path, width=150)
    else:
        st.sidebar.info("No profile photo")

    # Navigation menu
    page = st.sidebar.radio("Navigate", [
        "Dashboard Home",
        "View Connected Patient",
        "Missed Dose Alerts",
        "Guardian Requests",
        "Update Profile",
        "Logout"
    ])

    if page == "Dashboard Home":
        st.title(f"Welcome, {guardian_profile.get('full_name', 'Guardian')}!")
        if connected_patient:
            st.subheader("Connected Patient Info")
            st.write(f"Name: {connected_patient.get('full_name', 'N/A')}")
            st.write(f"Mobile: {connected_patient.get('mobile', 'N/A')}")
            st.write(f"Blood Group: {connected_patient.get('blood_group', 'N/A')}")
        else:
            st.warning("No connected patient found.")

    elif page == "View Connected Patient":
        st.title("🔍 Connected Patient - Medicine Schedule")
        if not connected_patient_id:
            st.error("No patient assigned.")
            return

        medicines = load_json(MEDICINES_FILE)
        schedules = load_json(SCHEDULES_FILE)

        # Filter medicines and schedules by connected patient ID
        patient_meds = {mid: m for mid, m in medicines.items() if m.get("patient_id") == connected_patient_id}
        patient_scheds = {sid: s for sid, s in schedules.items() if s.get("patient_id") == connected_patient_id}

        if not patient_meds:
            st.info("No medicines found for the connected patient.")
        else:
            for mid, med in patient_meds.items():
                st.subheader(f"💊 {med.get('name', 'Unknown')}")
                st.write(f"Contents: {med.get('contents', 'N/A')}")
                st.write(f"Quantity Available: {med.get('quantity', 'N/A')}")
                st.write(f"Expiry Date: {med.get('expiry_date', 'N/A')}")
                st.write(f"Purpose: {med.get('purpose', 'N/A')}")
                st.markdown("---")

        if not patient_scheds:
            st.info("No medicine schedules found.")
        else:
            st.subheader("⏰ Scheduled Reminders")
            for sid, sched in patient_scheds.items():
                med_name = patient_meds.get(sched.get('medicine_id'), {}).get('name', 'Unknown')
                st.markdown(f"**{med_name}**")
                times = sched.get('times', [])
                st.write(f"Dose Times: {', '.join(times) if times else 'N/A'}")
                taken_today = 'Yes' if sched.get('last_taken') == datetime.today().strftime('%Y-%m-%d') else 'No'
                st.write(f"Taken Today? {taken_today}")
                st.write(f"Missed Doses: {sched.get('missed_doses', 0)}")
                st.markdown("---")

    elif page == "Missed Dose Alerts":
        st.title("⚠️ Missed Dose Alerts")
        if not connected_patient_id:
            st.error("No connected patient found.")
            return

        schedules = load_json(SCHEDULES_FILE)
        medicines = load_json(MEDICINES_FILE)

        # Filter for missed doses for connected patient
        missed_scheds = [
            s for s in schedules.values()
            if s.get("patient_id") == connected_patient_id and s.get("missed_doses", 0) > 0
        ]

        if not missed_scheds:
            st.success("✅ No missed doses reported!")
        else:
            for sched in missed_scheds:
                med = medicines.get(sched.get('medicine_id'), {})
                st.subheader(med.get('name', 'Unknown Medicine'))
                st.write(f"Missed Doses: {sched.get('missed_doses')}")
                st.write(f"Last Taken: {sched.get('last_taken', 'Not recorded')}")
                st.markdown("---")

    elif page == "Guardian Requests":
        st.title("Pending Guardian Access Requests")
        guardian_requests = load_json(GUARDIAN_REQUESTS_FILE)

        # Collect pending requests made by this guardian
        pending_requests = {}
        for patient_id, requests in guardian_requests.items():
            for req in requests:
                if req.get("guardian_id") == user_id and req.get("status") == "pending":
                    pending_requests[patient_id] = req

        if not pending_requests:
            st.info("No pending guardian access requests.")
        else:
            for patient_id, req in pending_requests.items():
                patient_profile = profiles.get(patient_id, {})
                st.write(f"Requested access to {patient_profile.get('full_name', 'Unknown')} ({patient_id})")
                st.write(f"Relationship: {req.get('relationship', 'N/A')}")
                st.write(f"Requested At: {req.get('requested_at', 'N/A')}")
                st.warning("⚠️ Awaiting Patient Approval")
                st.markdown("---")

    elif page == "Update Profile":
        update_profile_page(user_id)

    elif page == "Logout":
        logout()
