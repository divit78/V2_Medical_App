# appointments.py - generated file


import streamlit as st
from datetime import date, datetime
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from config.constants import DOCTOR_QUERIES_FILE, APPOINTMENTS_FILE, PROFILES_FILE

def ask_questions_and_appointments(user_id):
    st.title("🤝 Ask Doctor / Book Appointment")

    questions = load_json(DOCTOR_QUERIES_FILE)
    appointments = load_json(APPOINTMENTS_FILE)

    with st.form("ask_doc_form"):
        question_text = st.text_area("💬 Enter Your Question:", height=100)
        appointment_type = st.selectbox("Appointment Type", ["No Appointment", "Video Call", "Clinic Visit"])
        preferred_date = st.date_input("Preferred Date", min_value=date.today())
        preferred_time = st.time_input("Preferred Time")
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not question_text.strip():
                st.error("Please enter a question.")
            else:
                qid = generate_id("QRY")
                questions[qid] = {
                    "patient_id": user_id,
                    "question": question_text.strip(),
                    "submitted_at": datetime.now().isoformat(),
                    "appointment_type": appointment_type,
                    "preferred_date": preferred_date.isoformat() if appointment_type != "No Appointment" else None,
                    "preferred_time": preferred_time.strftime("%H:%M") if appointment_type != "No Appointment" else None,
                    "status": "pending",
                    "doctor_response": ""
                }
                save_json(DOCTOR_QUERIES_FILE, questions)
                st.success("✅ Question and appointment request sent!")

    st.subheader("🗂️ Your Previous Queries & Appointments")

    patient_questions = [
        q for q in questions.values() if q.get("patient_id") == user_id
    ]

    if not patient_questions:
        st.info("No questions or appointments yet.")
    else:
        for q in reversed(patient_questions):
            st.markdown(f"- {q.get('submitted_at')} : {q.get('question')}")
            st.markdown(f"  - Status: {q.get('status')}")
            st.markdown(f"  - Type: {q.get('appointment_type')} on {q.get('preferred_date')} at {q.get('preferred_time')}")
            if q.get("doctor_response"):
                st.success(f"🩺 Doctor responded: {q.get('doctor_response')}")
            st.markdown("---")


