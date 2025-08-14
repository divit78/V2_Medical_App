
import streamlit as st
from page.signup.patient import patient_signup
from page.signup.doctor import doctor_signup
from page.signup.guardian import guardian_signup
from utils.css import load_css

def signup_page():
    load_css()
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown("### Select Role & Sign Up")
    user_type = st.selectbox("Account Type", ["Patient", "Doctor", "Guardian"], key="signup_user_type")

    if user_type == "Patient":
        patient_signup()
    elif user_type == "Doctor":
        doctor_signup()
    elif user_type == "Guardian":
        guardian_signup()

    st.markdown('</div>', unsafe_allow_html=True)




