# doctor.py - generated file


import streamlit as st
from datetime import datetime
import os

from config.constants import USERS_FILE, PROFILES_FILE, UPLOAD_DIR
from utils.auth import hash_password
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from page.navigation import go_to

def save_uploaded_file(uploaded_file, user_id):
    if uploaded_file is not None:
        user_folder = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def doctor_signup():
    st.markdown("#### 🩺 Doctor Registration")
    with st.form("doctor_signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name*", key="doc_full_name")
            username = st.text_input("Username*", key="doc_username")
            mobile = st.text_input("Mobile Number*", key="doc_mobile")
            email = st.text_input("Email*", key="doc_email")
        with col2:
            specialization = st.text_input("Specialization*", key="doc_specialization")
            consultation_fee = st.number_input("Consultation Fee (₹)*", min_value=0, value=500, key="doc_fee")
            experience = st.number_input("Years of Experience*", min_value=0, max_value=50, key="doc_exp")
            password = st.text_input("Password*", type="password", key="doc_password")
            confirm_password = st.text_input("Confirm Password*", type="password", key="doc_confirm_password")
        col3, col4 = st.columns(2)
        with col3:
            hospital = st.text_input("Hospital/Clinic Name*", key="doc_hospital")
            license_num = st.text_input("Medical License Number*", key="doc_license")
            qualification = st.text_area("Qualifications*", key="doc_qualification")
        with col4:
            address = st.text_area("Practice Address*", key="doc_address")
            city = st.text_input("City*", key="doc_city")
            availability = st.multiselect("Available Days*", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], key="doc_availability")
            degree_file = st.file_uploader("Degree Certificate*", type=['pdf','jpg','jpeg','png'], key="doc_degree")
            license_file = st.file_uploader("Medical License (optional)", type=['pdf','jpg','jpeg','png'], key="doc_license_file")
        terms = st.checkbox("Accept Terms*", key="doc_terms")
        verification = st.checkbox("Consent to verification*", key="doc_verification")
        submitted = st.form_submit_button("Sign Up")

    if submitted:
        required = [full_name, username, mobile, email, specialization, hospital, license_num, qualification, address, city, password, confirm_password, degree_file]
        if not all(required) or not terms or not verification:
            st.error("Fill all fields marked * and upload required documents.")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters!")
        else:
            users = load_json(USERS_FILE)
            profiles = load_json(PROFILES_FILE)
            if any(u['username'] == username for u in users.values()):
                st.error("Username exists!")
            else:
                doctor_id = generate_id("DOC")
                cert_path = save_uploaded_file(degree_file, doctor_id)
                license_path = save_uploaded_file(license_file, doctor_id) if license_file else None
                users[doctor_id] = {
                    "username": username,
                    "password": hash_password(password),
                    "user_type": "doctor",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "is_active": True,
                    "verification_status": "pending"
                }
                profiles[doctor_id] = {
                    "full_name": full_name,
                    "username": username,
                    "mobile": mobile,
                    "email": email,
                    "specialization": specialization,
                    "consultation_fee": consultation_fee,
                    "experience": experience,
                    "hospital_clinic": hospital,
                    "license_number": license_num,
                    "qualification": qualification,
                    "address": address,
                    "city": city,
                    "availability": availability,
                    "doctor_id": doctor_id,
                    "certificate_path": cert_path,
                    "license_path": license_path,
                    "profile_completion": 95,
                    "created_at": datetime.now().isoformat()
                }
                save_json(USERS_FILE, users)
                save_json(PROFILES_FILE, profiles)
                st.success(f"Doctor account created! ID: {doctor_id} (Pending Verification)")
                if st.button("Go to Sign In"):
                    go_to('signin')



