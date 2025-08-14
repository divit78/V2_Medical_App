# prescriptions.py - generated file

import streamlit as st
import os
import json
from datetime import datetime
from config.constants import PRESCRIPTIONS_FILE, UPLOAD_DIR
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id

def save_uploaded_file(uploaded_file, user_id):
    user_path = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_path, exist_ok=True)
    file_path = os.path.join(user_path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def prescriptions_page(user_id):
    st.title("📑 Prescriptions")

    prescriptions = load_json(PRESCRIPTIONS_FILE)
    my_prescriptions = {pid: p for pid, p in prescriptions.items() if p.get("patient_id") == user_id}

    with st.expander("Upload New Prescription"):
        file = st.file_uploader("Upload", type=['jpg', 'jpeg', 'png', 'pdf'])
        notes = st.text_area("Notes")
        if file:
            path = save_uploaded_file(file, user_id)
            pid = generate_id("PRESC")
            prescriptions[pid] = {
                "patient_id": user_id,
                "file_path": path,
                "notes": notes,
                "uploaded_at": datetime.now().isoformat()
            }
            save_json(PRESCRIPTIONS_FILE, prescriptions)
            st.success("📥 Prescription uploaded")

    if not my_prescriptions:
        st.info("No prescriptions found.")
    else:
        for pid, p in my_prescriptions.items():
            st.markdown(f"**ID:** {pid}")
            st.write(f"Notes: {p.get('notes')}")
            if p.get('file_path') and os.path.exists(p["file_path"]):
                if p["file_path"].lower().endswith(('.jpg', '.jpeg', '.png')):
                    st.image(p["file_path"], width=300)
            st.markdown("---")

    if st.button("📦 Export All Prescriptions"):
        export = json.dumps(my_prescriptions, indent=2)
        st.download_button("Download", export, "prescriptions.json", mime="application/json")




