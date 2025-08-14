# guardians.py - generated file


import streamlit as st
from utils.file_ops import load_json, save_json
from config.constants import GUARDIAN_REQUESTS_FILE, PROFILES_FILE

def manage_guardians(user_id):
    st.title("🧑‍🤝‍🧑 Guardian Access")

    profiles = load_json(PROFILES_FILE)
    guardian_requests = load_json(GUARDIAN_REQUESTS_FILE)
    requests = guardian_requests.get(user_id, [])

    if not requests:
        st.info("No guardian access requests.")
    else:
        for req in requests:
            st.subheader(f"{req.get('guardian_name')}")
            st.write(f"Relationship: {req.get('relationship')}")
            st.write(f"Mobile: {req.get('mobile')}")
            st.write(f"Email: {req.get('email')}")
            st.write(f"Requested At: {req.get('requested_at')}")
            status = req.get("status", "pending")
            if status == "pending":
                col1, col2 = st.columns(2)
                if col1.button("✅ Approve", key=f"approve_{req['guardian_id']}"):
                    req["status"] = "approved"
                    save_json(GUARDIAN_REQUESTS_FILE, guardian_requests)
                    st.success("Access approved.")
                if col2.button("❌ Deny", key=f"deny_{req['guardian_id']}"):
                    req["status"] = "denied"
                    save_json(GUARDIAN_REQUESTS_FILE, guardian_requests)
                    st.warning("Access denied.")
            else:
                st.info(f"Status: {status.capitalize()}")
            st.markdown("---")


