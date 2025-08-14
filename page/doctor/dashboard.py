import streamlit as st
import os
from datetime import datetime

from utils.css import load_css
from page.navigation import logout
from config.constants import (
    USERS_FILE,
    PROFILES_FILE,
    APPOINTMENTS_FILE,
    DOCTOR_QUERIES_FILE,
    PRESCRIPTIONS_FILE,
    MEDICAL_TESTS_FILE
)
from utils.file_ops import load_json, save_json

from page.update_profile_page import update_profile_page


def doctor_dashboard():
   

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

        /* Sidebar title style */
        .sidebar .sidebar-content h2 {
            color: #4a90e2;
            font-weight: 700;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Sidebar profile picture styling */
        .sidebar .sidebar-content img {
            border-radius: 50%;
            padding: 5px;
            border: 2px solid #4a90e2;
            margin-bottom: 1rem;
        }

        /* Sidebar info box */
        .sidebar .sidebar-content div[role="alert"] {
            background-color: #e3f2fd;
            color: #1565c0;
            border-radius: 10px;
            padding: 8px;
            margin-top: 1rem;
            font-size: 0.9rem;
        }

        /* Sidebar navigation radio buttons - 3D button look */
        .stRadio > div > label {
            background: linear-gradient(145deg, #f0f0f3, #cacdd1);
            border-radius: 12px;
            box-shadow:  3px 3px 5px #babecc,
                         -3px -3px 5px #ffffff;
            padding: 10px 18px;
            margin-bottom: 10px;
            transition: all 0.2s ease-in-out;
            font-weight: 600;
            color: #333;
            user-select: none;
            display: block;
            cursor: pointer;
        }
        .stRadio > div > label:hover {
            box-shadow:  1px 1px 2px #b4b8bf,
                         -1px -1px 2px #fff;
            color: #104E8B;
            background: linear-gradient(145deg, #d6e4fb, #a7bcf7);
        }

        /* Selected radio button style - pressed 3D effect */
        .stRadio > div > label[aria-checked="true"] {
            background: linear-gradient(145deg, #a7bcf7, #5680e9);
            box-shadow: inset 3px 3px 7px #3d69d1,
                        inset -3px -3px 7px #7aa1f3;
            color: white !important;
            font-weight: 700;
        }

        /* Subheaders */
        h3 {
            color: #1565c0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Buttons hover effect */
        button:hover {
            background-color: #4a90e2 !important;
            color: white !important;
            cursor: pointer;
        }

        /* Horizontal rule */
        hr {
            border-top: 1px solid #4a90e2;
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    doctor_id = st.session_state.get("user_id")
    if not doctor_id:
        st.error("You are not logged in.")
        return

    profiles = load_json(PROFILES_FILE)
    doctor_profile = profiles.get(doctor_id, {})

    st.sidebar.markdown(f"### Dr. {doctor_profile.get('full_name', 'Doctor')}")
    profile_pic = doctor_profile.get("profile_pic")
    if profile_pic and os.path.exists(profile_pic):
        st.sidebar.image(profile_pic, width=140)
    else:
        st.sidebar.info("No profile photo uploaded.")

    # Sidebar Navigation
    page = st.sidebar.radio("Navigate", [
        "Dashboard Home",
        "My Appointments",
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

        upcoming_appointments = [
            appt for appt in appointments.values()
            if appt.get("doctor_id") == doctor_id and appt.get("status") == "scheduled"
        ]

        pending_queries = [
            q for q in queries.values()
            if q.get("doctor_id") == doctor_id and q.get("status") == "pending"
        ]

        st.metric("📅 Scheduled Appointments", len(upcoming_appointments))
        st.metric("❓ Pending Queries", len(pending_queries))

    elif page == "My Appointments":
        st.title("📅 Upcoming Appointments")
        profiles = load_json(PROFILES_FILE)
        appointments = load_json(APPOINTMENTS_FILE)

        upcoming = [
            appt for appt in appointments.values()
            if appt.get("doctor_id") == doctor_id and appt.get("status") == "scheduled"
        ]
        if not upcoming:
            st.info("No upcoming appointments.")
        else:
            for appt in upcoming:
                patient = profiles.get(appt.get("patient_id"), {})
                st.markdown(f"- {appt.get('date')} with {patient.get('full_name', 'Unknown Patient')} ({appt.get('type')})")

    elif page == "Patient Queries":
        st.title("💬 Respond to Patient Queries")
        queries = load_json(DOCTOR_QUERIES_FILE)
        my_queries = {
            qid: q for qid, q in queries.items()
            if q.get("doctor_id") == doctor_id and q.get("status", "") == "pending"
        }

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

    elif page == "Prescriptions":
        st.title("🧾 My Prescriptions")
        prescriptions = load_json(PRESCRIPTIONS_FILE)
        my_presc = [
            p for p in prescriptions.values()
            if p.get("doctor_id") == doctor_id
        ]

        if not my_presc:
            st.info("No prescriptions found.")
        else:
            for pres in my_presc:
                st.markdown("---")
                st.markdown(f"- **Patient ID:** {pres.get('patient_id')}  \n- **Notes:** {pres.get('notes')[:200]}")

    elif page == "Medical Tests":
        st.title("🧪 Ordered Medical Tests")
        tests = load_json(MEDICAL_TESTS_FILE)
        my_tests = [
            t for t in tests.values()
            if t.get("doctor_id") == doctor_id
        ]
        if not my_tests:
            st.info("No test orders found.")
        else:
            for test in my_tests:
                st.markdown("-" * 40)
                st.markdown(f"- **Patient ID:** {test.get('patient_id')}  \n- **Test Type:** {test.get('test_type')}  \n- **Notes:** {test.get('notes', '-')}")
                st.markdown(f"- 📆 Ordered on: {test.get('ordered_at', '-')}")
    
    elif page == "Update Profile":
        update_profile_page(doctor_id)

    elif page == "Logout":
        logout()