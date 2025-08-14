# medical_tests.py - generated file


import streamlit as st
from datetime import datetime
import os
import json
from config.constants import MEDICAL_TESTS_FILE
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id
from config.constants import UPLOAD_DIR

def save_uploaded_file(file, user_id):
    user_path = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_path, exist_ok=True)
    file_path = os.path.join(user_path, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

def medical_tests_page(user_id):
    st.title("🧪 Medical Tests")

    tests = load_json(MEDICAL_TESTS_FILE)
    my_tests = {tid: t for tid, t in tests.items() if t.get("patient_id") == user_id}

    with st.expander("Upload New Test Report"):
        uploaded_file = st.file_uploader("Upload Test (JPG, PNG, PDF)", type=['jpg', 'jpeg', 'png', 'pdf'])
        test_type = st.text_input("Test Type (e.g. Blood, X-ray, MRI)")
        notes = st.text_area("Notes (optional)")
        if uploaded_file and test_type:
            file_path = save_uploaded_file(uploaded_file, user_id)
            tid = generate_id("TEST")
            tests[tid] = {
                "patient_id": user_id,
                "test_type": test_type,
                "file_path": file_path,
                "notes": notes,
                "uploaded_at": datetime.now().isoformat()
            }
            save_json(MEDICAL_TESTS_FILE, tests)
            st.success("✅ Test uploaded successfully!")

    st.subheader("📋 My Test Reports")
    if not my_tests:
        st.info("No medical test reports uploaded.")
    else:
        for tid, t in my_tests.items():
            st.markdown(f"**Test Type:** {t.get('test_type')}")
            st.markdown(f"**Notes:** {t.get('notes')}")
            if t.get("file_path") and os.path.exists(t["file_path"]):
                st.write(f"🗂️ {os.path.basename(t['file_path'])}")
                if t["file_path"].lower().endswith(('.png', '.jpg', '.jpeg')):
                    st.image(t["file_path"], width=300)
            st.markdown("---")

    if st.button("📥 Export Medical Tests JSON"):
        download = json.dumps(my_tests, indent=2)
        st.download_button("Download Tests", download, "medical_tests.json", mime="application/json")



