
import streamlit as st
from config.constants import USERS_FILE, PATIENT_DOCTOR_REQUESTS_FILE
from utils.file_ops import load_json, save_json
from datetime import datetime

def connect_doctors_page(patient_id):
    st.title("🔗 Connect With Doctors")

    users = load_json(USERS_FILE)
    requests = load_json(PATIENT_DOCTOR_REQUESTS_FILE)
    patient_requests = requests.get(patient_id, [])

    all_doctors = {
        uid: u for uid, u in users.items()
        if u.get("user_type") == "doctor"
    }

    specializations = sorted(list({doc.get("specialization", "") for doc in all_doctors.values() if doc.get("specialization")}))
    selected_specialization = st.selectbox("🔬 Filter by Specialization", ["All"] + specializations)
    search_name = st.text_input("🔍 Search Doctor Name")

    st.markdown("---")

    for doc_id, doc in all_doctors.items():
        if selected_specialization != "All" and doc.get("specialization") != selected_specialization:
            continue
        if search_name and search_name.lower() not in doc.get("full_name", "").lower():
            continue

        st.markdown(f"""<div style="background:#f4f6ff;padding:1rem;border-radius:10px;margin-bottom:1rem;">""", unsafe_allow_html=True)
        st.markdown(f"### 👨‍⚕️ Dr. {doc.get('full_name')}")
        st.write(f"📧 {doc.get('email')}")
        st.write(f"🧠 Specialization: {doc.get('specialization', '-')}")
        st.write(f"📊 Experience: {doc.get('experience', '-') or '-'} years")

        existing = [r for r in patient_requests if r["doctor_id"] == doc_id]
        if existing:
            status = existing[0]["status"]
            if status == "pending":
                st.info("⏳ Request Pending")
            elif status == "approved":
                st.success("✅ Connected")
            else:
                st.warning("❌ Rejected")
        else:
            if st.button("Send Connection Request", key=f"req_{doc_id}"):
                new_req = {
                    "doctor_id": doc_id,
                    "requested_at": datetime.now().isoformat(),
                    "status": "pending"
                }
                requests.setdefault(patient_id, []).append(new_req)
                save_json(PATIENT_DOCTOR_REQUESTS_FILE, requests)
                st.success("📨 Request sent to Dr. " + doc["full_name"])
        st.markdown("</div>", unsafe_allow_html=True)