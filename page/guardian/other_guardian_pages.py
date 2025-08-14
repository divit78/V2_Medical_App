# other_guardian_pages.py - generated file


import streamlit as st
from utils.css import load_css

def export_patient_adherence():
    load_css()
    st.title("📊 Export Adherence Report")
    st.info("Here you can download a copy of adherence reports or medicine reminders for your connected patient (feature coming soon).")
    st.warning("📌 This feature is under development.")

def manage_notifications():
    load_css()
    st.title("🔔 Guardian Notification Preferences")
    st.info("Configure how and when you'd like to receive updates about the patient.")
    st.warning("📌 Notification channels like SMS/Email not yet integrated.")

def guardian_extras():
    """
    Entry point for loading all other additional guardian features.
    Add new features in the menu as required.
    """
    load_css()
    option = st.selectbox("Select guardian feature", [
        "📊 Export Patient Adherence Report",
        "🔔 Notification Preferences"
    ])

    if option.startswith("📊"):
        export_patient_adherence()
    elif option.startswith("🔔"):
        manage_notifications()



