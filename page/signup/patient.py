
import streamlit as st
from datetime import datetime, date

from config.constants import USERS_FILE, PROFILES_FILE
from utils.auth import hash_password
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from page.navigation import go_to

def patient_signup():
    st.markdown("#### 👤 Patient Registration")
    with st.form("patient_signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name*", key="pat_full_name")
            title = st.selectbox("Title*", ["Mr.", "Mrs.", "Ms.", "Dr.", "Master"], key="pat_title")
            username = st.text_input("Username*", key="pat_username")
            mobile = st.text_input("Mobile Number*", placeholder="+91 9876543210", key="pat_mobile")
            dob = st.date_input("Date of Birth*", max_value=date.today(), key="pat_dob")
        with col2:
            marital_status = st.selectbox("Marital Status*", ["Single","Married","Divorced","Widowed"], key="pat_marital")
            blood_group = st.selectbox("Blood Group*", ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"], key="pat_blood")
            gender = st.selectbox("Gender*", ["Male","Female","Other","Prefer not to say"], key="pat_gender")
            password = st.text_input("Password*", type="password", key="pat_password")
            confirm_password = st.text_input("Confirm Password*", type="password", key="pat_confirm_password")
        terms = st.checkbox("Accept Terms*", key="pat_terms")
        submitted = st.form_submit_button("Sign Up")

    if submitted:
        if not all([full_name, username, mobile, password, confirm_password]):
            st.error("Fill all fields marked *")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters!")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        elif not terms:
            st.error("Please accept the terms.")
        else:
            users = load_json(USERS_FILE)
            profiles = load_json(PROFILES_FILE)
            if any(u['username'] == username for u in users.values()):
                st.error("Username exists!")
            else:
                patient_id = generate_id("PAT")
                users[patient_id] = {
                    "username": username,
                    "password": hash_password(password),
                    "user_type": "patient",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "is_active": True
                }
                profiles[patient_id] = {
                    "full_name": full_name,
                    "title": title,
                    "username": username,
                    "mobile": mobile,
                    "dob": dob.isoformat(),
                    "marital_status": marital_status,
                    "blood_group": blood_group,
                    "gender": gender,
                    "patient_id": patient_id,
                    "profile_completion": 60,
                    "created_at": datetime.now().isoformat(),
                    "city": ""  # For optional search functionality later
                }
                save_json(USERS_FILE, users)
                save_json(PROFILES_FILE, profiles)
                st.success(f"Patient account created! Your ID: {patient_id}")
                if st.button("Go to Sign In"):
                    go_to('signin')


