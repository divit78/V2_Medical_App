

import streamlit as st

def load_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        user-select:none;
    }
    .feature-card {
        background: white; padding: 2rem; border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 1rem 0;
        border-left: 5px solid #667eea; transition: all .3s;
    }
    .feature-card:hover {
        transform: translateY(-5px); box-shadow: 0 12px 35px rgba(0,0,0,.15);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    .auth-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 3rem;
        border-radius: 20px;
    }
    .success-message {
        background: #d4edda; color: #155724; padding: 1rem; border-radius: 10px;
    }
    .error-message {
        background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 10px;
    }
    .profile-pic {
        border-radius: 50%; width: 150px; height: 150px; object-fit: cover;
        border: 3px solid #667eea; margin-bottom: 1rem;
    }
    body { font-family: 'Segoe UI', 'sans-serif'; }
    h1, h2 { color: #4051B5; }
    </style>
    """, unsafe_allow_html=True)



