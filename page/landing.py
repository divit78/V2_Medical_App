import streamlit as st
from utils.css import load_css
from page.navigation import go_to


def landing_page():
    load_css()

    st.markdown("""
    <style>
    /* --- Page Background --- */
    body, .streamlit-container {
        background-color: #f5f5f5;  /* Light gray background */
        min-height: 100vh;
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2f2f2f;  /* Dark text for readability */
    }

    .st-emotion-cache-1r4qj8v {
        position: absolute;
        background: #f5f5f5;  /* Light gray background */
        color: rgb(49, 51, 63);
        inset: 0px;
        color-scheme: light;
        overflow: hidden;
    }

    /* Container styling with white background and subtle shadow */
    .landing-container {
        max-width: 900px;
        margin: 3rem auto 3rem auto;
        background: #ffffffee;  /* White with slight transparency */
        border-radius: 20px;
        padding: 2.5rem 3rem 3rem 3rem;
        box-shadow: 0 12px 30px rgba(100, 130, 190, 0.15);
        color: #323232;
    }

    /* Enhanced Header with Multiple Animations */
    .main-header {
        margin-bottom: 3rem;
        text-align: center;
        user-select: none;
        background: linear-gradient(135deg, #444444, #555555, #444444);
        background-size: 200% 200%;
        border-radius: 20px;
        padding: 3rem 2rem 2.7rem 2rem;
        color: #e0e0e0;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.7);
        position: relative;
        overflow: hidden;
        animation: backgroundShift 8s ease-in-out infinite, headerFloat 6s ease-in-out infinite alternate;
    }

    /* Background gradient animation */
    @keyframes backgroundShift {
        0%, 100% { 
            background-position: 0% 50%; 
        }
        50% { 
            background-position: 100% 50%; 
        }
    }

    /* Floating animation for header container */
    @keyframes headerFloat {
        0% { 
            transform: translateY(0px) scale(1);
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.7);
        }
        50% { 
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
        }
        100% { 
            transform: translateY(0px) scale(1);
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.7);
        }
    }

    /* Animated overlay particles */
    .main-header::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.1) 2px, transparent 2px),
                    radial-gradient(circle at 80% 70%, rgba(255, 255, 255, 0.15) 1px, transparent 1px),
                    radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.08) 3px, transparent 3px);
        animation: particleMove 12s linear infinite;
        pointer-events: none;
        z-index: 1;
    }

    @keyframes particleMove {
        0% { transform: translateX(-100px) translateY(-50px); opacity: 0.3; }
        50% { opacity: 0.8; }
        100% { transform: translateX(100px) translateY(50px); opacity: 0.3; }
    }

    /* Enhanced Header Title with Multiple Animations */
    .main-header h1 {
        font-size: 4.8rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        letter-spacing: 0.1em;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.1;
        cursor: default;
        position: relative;
        z-index: 2;
        background: linear-gradient(45deg, #ffffff, #f0f0f0, #ffffff, #e8e8e8);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: textShimmer 4s ease-in-out infinite, textBounce 3s ease-in-out infinite;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    /* Text shimmer animation */
    @keyframes textShimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    /* Subtle bounce animation for title */
    @keyframes textBounce {
        0%, 100% { transform: translateY(0px); }
        25% { transform: translateY(-2px); }
        75% { transform: translateY(2px); }
    }

    /* Enhanced Animated Underline */
    .main-header h1::after {
        content: "";
        position: absolute;
        width: 0%;
        height: 6px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff6b6b);
        background-size: 300% 100%;
        bottom: -15px;
        left: 50%;
        transform: translateX(-50%);
        border-radius: 3px;
        animation: underlineGrow 3s ease-in-out infinite, colorWave 2s linear infinite;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
    }

    /* Underline grow and shrink animation */
    @keyframes underlineGrow {
        0%, 100% { 
            width: 20%; 
            opacity: 0.6;
        }
        25% { 
            width: 80%; 
            opacity: 1;
        }
        50% { 
            width: 60%; 
            opacity: 0.9;
        }
        75% { 
            width: 90%; 
            opacity: 1;
        }
    }

    /* Color wave animation for underline */
    @keyframes colorWave {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Enhanced Subtitle with Fade Animation */
    .main-header p {
        font-size: 1.6rem;
        max-width: 600px;
        margin: 0 auto 2rem auto;
        color: #cccccc;
        font-weight: 700;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 0.04em;
        user-select: none;
        line-height: 1.3;
        position: relative;
        z-index: 2;
        animation: subtitleFade 5s ease-in-out infinite;
    }

    /* Subtitle fade in/out animation */
    @keyframes subtitleFade {
        0%, 100% { opacity: 0.8; transform: translateY(0px); }
        50% { opacity: 1; transform: translateY(-3px); }
    }

    /* Pulsing glow effect for header */
    .main-header::after {
        content: "";
        position: absolute;
        top: -5px; left: -5px; right: -5px; bottom: -5px;
        border-radius: 25px;
        background: linear-gradient(45deg, rgba(255, 107, 107, 0.3), rgba(78, 205, 196, 0.3), rgba(69, 183, 209, 0.3));
        z-index: -1;
        animation: glowPulse 4s ease-in-out infinite;
        filter: blur(10px);
    }

    @keyframes glowPulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.05); }
    }

    /* Buttons styles */
    button, .st-expander > div:first-child {
        transition: background-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease;
        cursor: pointer;
    }
    button:hover {
        background-color: #6c6cff !important;  /* Light purple blue */
        box-shadow: 0 6px 20px rgba(108, 108, 255, 0.7) !important;
        color: #fff !important;
        transform: translateY(-2px);
    }
    .st-expander > div:first-child:hover {
        background-color: #5757ff33;
        box-shadow: 0 4px 22px rgba(87, 87, 255, 0.25);
        border-radius: 12px;
    }

    .stButton button {
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
        background-color: #5a5aff !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(90, 90, 255, 0.6);
        margin-left: 10px;
    }
    .stButton button:first-child {
        margin-left: 0;
    }
    .stButton button:hover {
        background-color: #3f3fff !important;
        box-shadow: 0 8px 30px rgba(63, 63, 255, 0.8);
        color: #e0e0ff !important;
    }

    /* Video container */
    .video-container {
        position: relative;
        width: 320px;
        height: 180px;
        margin: 4rem auto 2rem auto;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 28px rgba(90, 90, 255, 0.25);
        transition: box-shadow 0.3s ease;
    }
    .video-container iframe,
    .video-container video {
        position: absolute;
        top: 0; 
        left: 0;
        width: 100%; 
        height: 100%;
        border: none;
        border-radius: 16px;
    }
    .video-container:hover {
        box-shadow: 0 12px 36px rgba(90, 90, 255, 0.4);
    }

    /* Footer */
    @keyframes footerGradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .landing-footer {
        text-align: center;
        font-size: 0.9rem;
        color: white;
        padding: 2rem 1rem 3rem 1rem;
        border-top: 1px solid #555555;
        user-select: none;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(270deg, #4b4bc1, #5a5aff, #3f3fff);
        background-size: 400% 400%;
        animation: footerGradientShift 15s ease infinite;
        border-radius: 16px 16px 0 0;
        box-shadow: 0 -4px 8px rgba(74, 74, 255, 0.6);
        position: relative;
    }
    .landing-footer a {
        color: #d6d6ff;
        text-decoration: none;
        font-weight: 600;
        margin: 0 8px;
        position: relative;
        overflow: hidden;
        transition: color 0.25s ease;
    }
    .landing-footer a::after {
        content: '';
        position: absolute;
        width: 100%;
        transform: scaleX(0);
        height: 2px;
        bottom: -3px;
        left: 0;
        background-color: #d6d6ff;
        transform-origin: bottom right;
        transition: transform 0.3s ease-out;
    }
    .landing-footer a:hover::after,
    .landing-footer a:focus::after {
        transform: scaleX(1);
        transform-origin: bottom left;
    }
    .landing-footer a:hover {
        color: #fff;
    }
    .footer-trust-message {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 10px;
        color: #d6d6ffcc;
        font-style: italic;
        letter-spacing: 0.04em;
        user-select: none;
    }

    /* General margin fix for expander text */
    .st-expander > div:nth-child(2) {
        margin-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main container start
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)

    # Top right Sign In and Sign Up buttons placement
    cols = st.columns([4, 1])  # empty space on left; buttons on right
    with cols[1]:
        if st.button("🔐 Sign In"):
            go_to('signin')
        if st.button("📝 Sign Up"):
            go_to('signup')

    # Enhanced Header section with animations
    st.markdown("""
    <div class="main-header">
        <h1>🩺 Smart Medical Reminder</h1>
        <p>Your Health, Our Priority — Never Miss a Dose Again</p>
    </div>
    """, unsafe_allow_html=True)

    # Demo video embed - replace video URL if needed
    video_link = "https://www.youtube.com/embed/0fN7Fxv1e5A"
    video_embed = f"""
    <div class="video-container">
        <iframe src="{video_link}" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
    </div>
    """
    st.markdown(video_embed, unsafe_allow_html=True)

    # Main features section header
    st.markdown("## 🌟 Comprehensive Health Management Features")

    # Expanders for Patients, Doctors, Guardians
    with st.expander("👤 For Patients"):
        st.markdown("""
        - 📱 Smart medicine reminders and scheduling   
        - 📄 Upload and manage medical documents   
        - 💬 Direct communication with doctors   
        - 👨‍👩‍👧 Share access with guardians   
        - ⏰ On-screen medicine alerts   
        - 🔍 Search doctors by name, specialization, and city
        """)

    with st.expander("🩺 For Doctors"):
        st.markdown("""
        - 👥 View patient health data and questions   
        - 📝 Create and manage digital prescriptions   
        - 📈 Monitor medication adherence   
        - 🏥 Professional telemedicine consultations   
        - 📅 Schedule appointments
        """)

    with st.expander("👨‍👩‍👧 For Guardians"):
        st.markdown("""
        - 📊 Monitor patient's medicine intake history   
        - 🚨 Get instant alerts for missed doses   
        - 👪 Manage family health coordination and notifications
        """)

    # Info box for ideal use cases
    st.info("""
    Ideal for:
    - Elderly care
    - Chronic illness tracking
    - Family health coordination
    - Doctor-patient remote assistance
    """, icon="ℹ️")

    # Footer
    st.markdown("""
    <div class="landing-footer">
        <p>&copy; 2025 Smart Medical Reminder. All rights reserved.</p>
        <p>
            <a href="https://yourwebsite.com" target="_blank" rel="noopener">Your Website</a> &bull;
            <a href="https://twitter.com/yourprofile" target="_blank" rel="noopener">Twitter</a> &bull;
            <a href="https://linkedin.com/in/yourprofile" target="_blank" rel="noopener">LinkedIn</a> &bull;
            <a href="mailto:support@yourwebsite.com">Contact</a>
        </p>
        <div class="footer-trust-message">
            Loved by <strong>2 Lakh+</strong> people worldwide — Trusted for your health and wellness.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # End main container
    st.markdown('</div>', unsafe_allow_html=True)
