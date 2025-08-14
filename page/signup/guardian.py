# guardian.py - generated file

import streamlit as st
from datetime import datetime
from config.constants import USERS_FILE, PROFILES_FILE, GUARDIAN_REQUESTS_FILE
from utils.auth import hash_password
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from page.navigation import go_to

def guardian_signup():
    st.markdown("#### 👨‍👩‍👧 Guardian Registration")
    with st.form("guardian_signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name*", key="gua_full_name")
            username = st.text_input("Username*", key="gua_username")
            mobile = st.text_input("Mobile Number*", key="gua_mobile")
            email = st.text_input("Email", key="gua_email")
            relationship = st.selectbox(
                "Relationship to Patient*",
                ["Parent", "Spouse", "Sibling", "Child", "Friend", "Caregiver", "Relative", "Other"],
                key="gua_relationship"
            )
        with col2:
            patient_id_username = st.text_input("Patient ID or Username to Connect*", key="gua_patient_id")
            emergency_contact = st.text_input("Alternative Contact", key="gua_emergency_contact")
            address = st.text_area("Address", key="gua_address")
            password = st.text_input("Password*", type="password", key="gua_password")
            confirm_password = st.text_input("Confirm Password*", type="password", key="gua_confirm_password")
        terms = st.checkbox("Accept Terms*", key="gua_terms")
        submitted = st.form_submit_button("Sign Up")

    if submitted:
        if not all([full_name, username, mobile, relationship, patient_id_username, password, confirm_password]):
            st.error("Fill all fields marked *")
            return
        if len(password) < 6:
            st.error("Password too short!")
            return
        if password != confirm_password:
            st.error("Passwords do not match!")
            return
        if not terms:
            st.error("Please accept the terms.")
            return

        users = load_json(USERS_FILE)
        profiles = load_json(PROFILES_FILE)
        guardian_requests = load_json(GUARDIAN_REQUESTS_FILE)
        if any(u['username'] == username for u in users.values()):
            st.error("Username exists!")
            return

        connected_patient_id = None
        for uid, prof in profiles.items():
            if (
                prof.get('patient_id') == patient_id_username
                or prof.get('username') == patient_id_username
            ):
                connected_patient_id = uid
                break
        if not connected_patient_id:
            st.error("Patient not found! Check Patient ID or Username.")
        else:
            guardian_id = generate_id("GUA")
            users[guardian_id] = {
                "username": username,
                "password": hash_password(password),
                "user_type": "guardian",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True
            }
            profiles[guardian_id] = {
                "full_name": full_name,
                "username": username,
                "mobile": mobile,
                "email": email,
                "relationship": relationship,
                "guardian_id": guardian_id,
                "connected_patient": connected_patient_id,
                "emergency_contact": emergency_contact,
                "address": address,
                "profile_completion": 85,
                "created_at": datetime.now().isoformat()
            }
            if connected_patient_id not in guardian_requests:
                guardian_requests[connected_patient_id] = []
            guardian_requests[connected_patient_id].append({
                "guardian_id": guardian_id,
                "guardian_name": full_name,
                "relationship": relationship,
                "mobile": mobile,
                "email": email,
                "status": "pending",
                "requested_at": datetime.now().isoformat()
            })
            save_json(USERS_FILE, users)
            save_json(PROFILES_FILE, profiles)
            save_json(GUARDIAN_REQUESTS_FILE, guardian_requests)
            st.success("Guardian account created! Awaiting patient approval.")
            if st.button("Go to Sign In"):
                go_to('signin')

