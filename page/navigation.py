
import streamlit as st

def go_to(page: str):
    """
    Set the target page in session state and rerun to simulate page routing.
    """
    st.session_state.page = page
    st.rerun()

def logout():
    """
    Clear the user session and return to landing page.
    """
    st.session_state.user_id = None
    st.session_state.user_type = None
    st.session_state.page = 'landing'
    st.rerun()

