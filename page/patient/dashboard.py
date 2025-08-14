import streamlit as st
import os
from datetime import datetime

from utils.css import load_css
from page.navigation import logout
from config.constants import (
    PROFILES_FILE, MEDICINES_FILE, SCHEDULES_FILE, PRESCRIPTIONS_FILE,
    MEDICAL_TESTS_FILE, DOCTOR_QUERIES_FILE, GUARDIAN_REQUESTS_FILE, APPOINTMENTS_FILE
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

from page.update_profile_page import update_profile_page


def patient_dashboard():
    load_css()

    # Enhanced 4D and animated CSS for sidebar, header, summary cards, lists, buttons, and fade-in effect
    custom_css = """
    <style>
    /* Body and fonts */
    body {
        background: #f9fafc;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        color: #284363;
    }
    /* Fade-in animation wrapper */
    .page-content {
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Sidebar container */
    [data-testid="stSidebar"] {
        background: #fff;
        box-shadow: 2px 0 12px 0 rgba(0,0,0,0.08);
        padding: 32px 22px;
        border-top-right-radius: 32px;
        border-bottom-right-radius: 32px;
        min-width: 310px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    /* Sidebar Profile Section */
    .sidebar-profile {
        text-align: center;
        margin-bottom: 35px;
        width: 100%;
    }
    .sidebar-profile img {
        border-radius: 50%;
        outline: 3px solid #eaf0fb;
        border: 2px solid #a0aec0;
        width: 110px !important;
        height: 110px !important;
        object-fit: cover;
        box-shadow:
          6px 6px 10px rgba(100, 76, 255, 0.15),
          -6px -6px 10px rgba(255, 255, 255, 0.8);
        margin: 0 auto 14px auto;
        display: block;
        transition: box-shadow 0.3s ease;
    }
    .sidebar-profile img:hover {
        box-shadow:
          8px 8px 16px rgba(100, 76, 255, 0.35),
          -8px -8px 16px rgba(255, 255, 255, 1);
        cursor: pointer;
    }
    .sidebar-profile-name {
        font-weight: 700;
        font-size: 1.20rem;
        color: #644cff;
        margin-bottom: 0;
        transition: color 0.3s ease;
    }
    .sidebar-profile-name:hover {
        color: #3a2fcc;
        cursor: default;
    }

    /* Sidebar buttons container */
    .sidebar-btn-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 14px;
    }

    /* 4D Buttons */
    .sidebar-button > button {
        width: 100% !important;
        padding: 14px 0 !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 16px !important;
        border: none !important;
        cursor: pointer !important;
        background: linear-gradient(145deg, #d9e0ec, #f0f4ff);
        box-shadow:
          6px 6px 10px rgba(163,177,198,0.6),
          -6px -6px 10px rgba(255,255,255,0.9);
        color: #222 !important;
        transition: all 0.3s ease;
        user-select: none;
        outline-offset: 4px !important;
        outline: none !important;
        display: flex;
        align-items: center;
        gap: 10px;
        justify-content: center;
        position: relative;
    }
    .sidebar-button > button:hover {
        background: linear-gradient(145deg, #c1c9e2, #e9edff);
        box-shadow:
          8px 8px 15px rgba(143,157,178,0.8),
          -8px -8px 15px rgba(255,255,255,0.95);
        color: #4a4a4a !important;
    }
    .sidebar-button > button:active {
        background: linear-gradient(145deg, #bac2db, #d7dcf3);
        box-shadow: inset 4px 4px 6px rgba(163,177,198,0.6),
                    inset -4px -4px 6px rgba(255,255,255,0.9);
        color: #3d3d3d !important;
    }
    /* Selected button highlight */
    .sidebar-button > button[selected="true"] {
        background: linear-gradient(145deg, #8e9de3, #a8b2ff);
        box-shadow:
          4px 4px 20px #7b89ff,
          -4px -4px 20px #b1c1ff,
          inset 2px 2px 4px #6478ff,
          inset -2px -2px 4px #aec1ff;
        color: white !important;
        font-weight: 800 !important;
    }
    .sidebar-button > button[selected="true"]:hover {
        background: linear-gradient(145deg, #7d8ce0, #95a2ff);
        box-shadow:
          6px 6px 25px #6a7aff,
          -6px -6px 25px #a4b3ff,
          inset 3px 3px 6px #566aff,
          inset -3px -3px 6px #a5b8ff;
        color: white !important;
    }
    .sidebar-button > button:focus {
        outline: 3px solid #7e8aff !important;
        outline-offset: 2px !important;
    }

    /* Sidebar Button Emoji styling */
    .sidebar-button > button span.emoji {
        font-size: 1.4rem;
        line-height: 1;
    }

    /* Main header with animation */
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        color: #000000;
        text-align: center;
        margin-bottom: 0.7em;
        text-shadow: 2px 2px 6px rgba(100, 76, 255, 0.35);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        animation: fadeIn 1s ease forwards;
    }
    .main-header span.name-highlight {
        color: #000000;
    }
    .main-subheader {
        text-align: center;
        font-size: 1.25rem;
        color: #55597b;
        font-weight: 600;
        margin-bottom: 2em;
        animation: fadeIn 1.5s ease forwards;
    }

    /* Summary cards container */
    .summary-cards {
        display: flex;
        gap: 24px;
        margin-bottom: 36px;
        flex-wrap: wrap;
        user-select: none;
        justify-content: center;
    }
    .summary-card {
        background: white;
        flex: 1 1 280px;
        border-radius: 22px;
        padding: 30px 32px;
        box-shadow: 0 20px 42px rgba(127, 88, 255, 0.18);
        transition: 
            box-shadow 0.3s ease, 
            transform 0.3s ease, 
            color 0.3s ease;
        cursor: pointer;
        color: #453a94;
        font-weight: 700;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        text-align: center;
        font-size: 1.1rem;
    }
    .summary-card:hover {
        box-shadow: 0 28px 56px rgba(127, 88, 255, 0.28);
        transform: translateY(-6px) scale(1.03);
        color: #362e7d;
    }
    .summary-card h3 {
        font-size: 1.6rem;
        margin: 0;
    }
    .summary-card p {
        margin: 0;
        color: #5a577a;
        font-weight: 600;
    }

    /* Info box */
    .stInfo {
        background-color: #eaf0fb !important;
        color: #52796f !important;
        font-weight: 700 !important;
        border-left: 5px solid #354f52 !important;
        padding: 18px 25px !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        animation: fadeIn 1s ease forwards;
    }

    /* List item styling with hover */
    div[data-testid="stMarkdownContainer"] li {
        background: #f3ebff;
        border-radius: 0.66em;
        padding: 7px 14px;
        margin-bottom: 6px;
        color: #4e4e8b;
        font-weight: 600;
        font-size: 1.07rem;
        transition: background-color 0.3s ease;
    }
    div[data-testid="stMarkdownContainer"] li:hover {
        background: #d1c4ff;
        cursor: default;
        color: #3f336f;
    }

    /* Main page buttons */
    .stButton > button {
        background-color: #644cff;
        color: #fff;
        border: none;
        padding: 10px 36px;
        border-radius: 15px;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 6px 18px #644cff66;
        transition: background-color 0.25s ease, box-shadow 0.25s ease;
    }
    .stButton > button:hover {
        background-color: #284363;
        box-shadow: 0 8px 22px #284363bb;
        color: #ffe6fb;
    }
    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)

    profiles = load_json(PROFILES_FILE)
    user_id = st.session_state.user_id
    profile = profiles.get(user_id, {})

    # -- Sidebar profile --
    st.sidebar.markdown('<div class="sidebar-profile">', unsafe_allow_html=True)
    profile_pic_path = profile.get("profile_pic")
    if profile_pic_path and os.path.exists(profile_pic_path):
        st.sidebar.image(profile_pic_path, width=110)
    st.sidebar.markdown(f'<div class="sidebar-profile-name">{profile.get("full_name", "Your Profile")}</div>', unsafe_allow_html=True)
    if not (profile_pic_path and os.path.exists(profile_pic_path)):
        st.sidebar.info("No profile photo uploaded.")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # -- Sidebar navigation buttons with emoji spans (for better CSS targeting) --
    nav_items = [
        ("🏠", "Dashboard Home"),
        ("💊", "Add Medicine"),
        ("⏰", "Medicine Reminder"),
        ("📄", "Prescriptions"),
        ("🩺", "Medical Tests"),
        ("💬", "Ask Doctor / Appointments"),
        ("📊", "Adherence History"),
        ("🛡️", "Guardians"),
        ("📝", "Update Profile"),
        ("🚪", "Logout"),
    ]

    if "patient_nav_page" not in st.session_state:
        st.session_state.patient_nav_page = "Dashboard Home"

    selected_page = st.session_state.patient_nav_page

    st.sidebar.markdown('<div class="sidebar-btn-container">', unsafe_allow_html=True)
    for emoji, label_key in nav_items:
        is_selected = (label_key == selected_page)

        # Prepare button label with emoji wrapped in a span for CSS
        button_label = f'<span class="emoji">{emoji}</span> {label_key}'

        # Streamlit buttons cannot render HTML, so use plain text with emoji unicode
        label_text = f"{emoji}  {label_key}"

        btn = st.sidebar.button(label_text, key=f"btn-{label_key}")
        if btn:
            st.session_state.patient_nav_page = label_key
            selected_page = label_key
            st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    page = selected_page

    if page == "Dashboard Home":
        # Animated beautiful header with highlighted name and subheader
        st.markdown(f"""
            <div class="main-header">
                Welcome back, <span class="name-highlight">{profile.get("full_name", "Patient")}</span>! 👋
            </div>
            <div class="main-subheader">
                Your smart health companion awaits.
            </div>
            <div class="page-content">
        """, unsafe_allow_html=True)

        with st.spinner("Loading your dashboard..."):
            medicines = load_json(MEDICINES_FILE)
            schedules = load_json(SCHEDULES_FILE)
            appointments = load_json(APPOINTMENTS_FILE)

            patient_meds = [m for m in medicines.values() if m.get("patient_id") == user_id]
            patient_appointments = [a for a in appointments.values() if a.get("patient_id") == user_id and a.get("status") == "scheduled"]

            reminders = []
            for sched in schedules.values():
                if sched.get("patient_id") == user_id:
                    med_id = sched.get("medicine_id")
                    med_info = medicines.get(med_id, {})
                    next_dose = sched.get("next_dose_time")
                    if next_dose:
                        try:
                            next_dose_dt = datetime.fromisoformat(next_dose)
                            if next_dose_dt.date() == datetime.now().date():
                                reminders.append((next_dose_dt.time().strftime("%H:%M"), med_info.get("name", "Unknown")))
                        except:
                            pass

            # Summary cards clickable to navigate
            cols = st.columns(min(len(nav_items), 3))

            cards_info = [
                ("🩺 Upcoming Appointments", len(patient_appointments), "Ask Doctor / Appointments"),
                ("💊 Your Medicines", len(patient_meds), "Add Medicine"),
                ("⏰ Medicine Reminders", len(reminders), "Medicine Reminder"),
            ]

            for idx, (title, count, target_page) in enumerate(cards_info):
                with cols[idx % len(cols)]:
                    if st.button(f"{title}\n\n{count}", key=f"card-{target_page}"):
                        st.session_state.patient_nav_page = target_page
                        st.rerun()

            # Medicine reminders list
            if reminders:
                st.subheader("Today's Medicine Reminders")
                for time_str, med_name in sorted(reminders):
                    st.write(f"⏰ {time_str} — {med_name}")
            else:
                st.info("No medicine reminders for today.", icon="ℹ️")

            # Upcoming appointments list
            if patient_appointments:
                st.subheader("Upcoming Appointments")
                for app in patient_appointments:
                    doc = profiles.get(app.get("doctor_id"), {})
                    st.write(f"📅 {app.get('date')} with Dr. {doc.get('full_name', 'Doctor')} ({app.get('type')})")

        st.markdown("</div>", unsafe_allow_html=True)

    elif page == "Add Medicine":
        medicine_manager(user_id)
    elif page == "Medicine Reminder":
        medicine_reminder_page(user_id)
    elif page == "Prescriptions":
        prescriptions_page(user_id)
    elif page == "Medical Tests":
        medical_tests_page(user_id)
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
