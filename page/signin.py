


import streamlit as st
from utils.auth import verify_password
from utils.file_ops import load_json, save_json
from config.constants import USERS_FILE
from page.navigation import go_to
from utils.css import load_css
from datetime import datetime

def signin_page():
    load_css()
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    st.markdown("### 🔐 Sign In")
    role = st.selectbox("Sign In as", ["Patient", "Doctor", "Guardian"], key="signin_role")
    username_or_id = st.text_input(f"{role} ID or Username", key="signin_userid")
    password = st.text_input("Password", type="password", key="signin_password")

    if st.button("Sign In"):
        users = load_json(USERS_FILE)
        user_found = None

        for uid, info in users.items():
            if (info.get('username') == username_or_id or uid == username_or_id) and info.get('user_type') == role.lower():
                user_found = (uid, info)
                break

        if not user_found:
            st.error("⚠️ Account not found or role mismatch.")
        elif not verify_password(password, user_found[1]['password']):
            st.error("❌ Incorrect password.")
        else:
            st.session_state.user_id = user_found[0]
            st.session_state.user_type = role.lower()
            st.session_state.page = f"{role.lower()}_dashboard"
            user_found[1]["last_login"] = datetime.now().isoformat()
            save_json(USERS_FILE, users)
            st.success("✅ Login successful!")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


