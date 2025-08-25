import streamlit as st
from config.constants import PROFILES_FILE
from utils.file_ops import load_json, save_json
import os
from PIL import Image

def save_uploaded_file(uploaded_file, user_id):
    """Save uploaded file and return the saved path"""
    # Create user-specific directory
    upload_dir = os.path.join("profile_photos", user_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create file path
    file_path = os.path.join(upload_dir, f"profile_{user_id}.png")
    
    # Save the uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def update_profile_page(user_id):
    profiles = load_json(PROFILES_FILE)
    profile = profiles.get(user_id, {})
    
    st.title("🔄 Update Profile")
    
    # Profile Photo Upload & Display Section
    st.subheader("📷 Profile Photo")
    
    # Check if user has existing photo
    existing_photo_path = profile.get("photo_path")
    
    # Display current photo if exists
    if existing_photo_path and os.path.exists(existing_photo_path):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(existing_photo_path, width=150, caption="Current Photo")
        with col2:
            st.info("✅ Profile photo uploaded successfully!")
            if st.button("🗑️ Remove Photo"):
                # Remove photo file and update profile
                if os.path.exists(existing_photo_path):
                    os.remove(existing_photo_path)
                profile.pop("photo_path", None)
                profiles[user_id] = profile
                save_json(PROFILES_FILE, profiles)
                st.success("Photo removed successfully!")
                st.rerun()
    else:
        st.info("📷 No profile photo uploaded yet")
    
    # File uploader for new photo
    uploaded_photo = st.file_uploader(
        "Upload New Profile Photo", 
        type=["jpg", "jpeg", "png"],
        help="Choose a JPG, JPEG, or PNG file"
    )
    
    # Handle photo upload
    if uploaded_photo is not None:
        # Display preview
        st.image(uploaded_photo, width=150, caption="Preview")
        
        if st.button("💾 Save Profile Photo"):
            try:
                # Save the uploaded file
                photo_path = save_uploaded_file(uploaded_photo, user_id)
                
                # Update profile with photo path
                profile["photo_path"] = photo_path
                profiles[user_id] = profile
                save_json(PROFILES_FILE, profiles)
                
                st.success("✅ Profile photo uploaded successfully!")
                st.balloons()
                st.rerun()
                
            except Exception as e:
                st.error(f"Error saving photo: {e}")
    
    st.markdown("---")
    
    # Core Details Section
    st.subheader("👤 Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
        gender = st.selectbox(
            "Gender", 
            ["Male", "Female", "Other"],
            index=["Male", "Female", "Other"].index(profile.get("gender", "Male"))
        )
        mobile = st.text_input("Mobile Number", value=profile.get("mobile", ""))
        email = st.text_input("Email", value=profile.get("email", ""))
    
    with col2:
        try:
            from datetime import datetime
            if profile.get("dob"):
                if isinstance(profile.get("dob"), str):
                    dob_value = datetime.fromisoformat(profile.get("dob")).date()
                else:
                    dob_value = profile.get("dob")
            else:
                dob_value = None
        except:
            dob_value = None
            
        dob = st.date_input("Date of Birth", value=dob_value)
        alt_mobile = st.text_input("Alternate Mobile", value=profile.get("alt_mobile", ""))
        emergency_name = st.text_input("Emergency Contact Name", value=profile.get("emergency_name", ""))
        emergency_number = st.text_input("Emergency Contact Number", value=profile.get("emergency_number", ""))
    
    # Address Information
    st.subheader("🏠 Address Information")
    
    col3, col4 = st.columns(2)
    
    with col3:
        address = st.text_area("Address", value=profile.get("address", ""))
        city = st.text_input("City", value=profile.get("city", ""))
    
    with col4:
        pincode = st.text_input("Pin Code", value=profile.get("pincode", ""))
        state = st.text_input("State", value=profile.get("state", ""))
        nationality = st.text_input("Nationality", value=profile.get("nationality", ""))
    
    # User-type specific fields
    user_type = profile.get("user_type") or st.session_state.get("user_type")
    
    if user_type == "patient":
        st.subheader("🩸 Medical Information")
        blood_group = st.selectbox(
            "Blood Group", 
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
            index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(profile.get("blood_group", "Unknown"))
        )
    elif user_type == "doctor":
        st.subheader("👨‍⚕️ Professional Information")
        col5, col6 = st.columns(2)
        with col5:
            specialization = st.text_input("Specialization", value=profile.get("specialization", ""))
            experience = st.number_input("Experience (years)", value=int(profile.get("experience", 0)), min_value=0)
        with col6:
            hospital_clinic = st.text_input("Hospital/Clinic", value=profile.get("hospital_clinic", ""))
            consultation_fee = st.number_input("Consultation Fee (₹)", value=float(profile.get("consultation_fee", 0)), min_value=0.0)
    elif user_type == "guardian":
        st.subheader("👨‍👩‍👧‍👦 Guardian Information")
        relationship = st.text_input("Relationship", value=profile.get("relationship", ""))
    
    # Save Profile Button
    if st.button("💾 Save Profile", type="primary"):
        # Update profile data
        profile["full_name"] = full_name
        profile["gender"] = gender
        profile["dob"] = str(dob)
        profile["mobile"] = mobile
        profile["alt_mobile"] = alt_mobile
        profile["email"] = email
        profile["emergency_name"] = emergency_name
        profile["emergency_number"] = emergency_number
        profile["address"] = address
        profile["city"] = city
        profile["pincode"] = pincode
        profile["state"] = state
        profile["nationality"] = nationality
        
        # Add user-type specific fields
        if user_type == "patient":
            profile["blood_group"] = blood_group
        elif user_type == "doctor":
            profile["specialization"] = specialization
            profile["experience"] = experience
            profile["hospital_clinic"] = hospital_clinic
            profile["consultation_fee"] = consultation_fee
        elif user_type == "guardian":
            profile["relationship"] = relationship
        
        # Save to file
        profiles[user_id] = profile
        save_json(PROFILES_FILE, profiles)
        
        st.success("✅ Profile updated successfully!")
        st.balloons()
