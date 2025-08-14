import streamlit as st
from config.constants import PROFILES_FILE
from utils.file_ops import load_json, save_json
import os
from PIL import Image  # For image display

def update_profile_page(user_id):
    profiles = load_json(PROFILES_FILE)
    profile = profiles.get(user_id, {})

    st.title("🔄 Update Profile")

    # Profile Photo Upload & Display
    st.sidebar.write("### Profile Photo")
    profile_photo_path = profile.get("photo_path", None)
    if profile_photo_path and os.path.exists(profile_photo_path):
        st.sidebar.image(profile_photo_path, width=120)
    uploaded_photo = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"])
    photo_path = profile_photo_path
    if uploaded_photo is not None:
        photo_dir = "profile_photos"
        os.makedirs(photo_dir, exist_ok=True)
        photo_path = os.path.join(photo_dir, f"{user_id}.png")
        with open(photo_path, "wb") as f:
            f.write(uploaded_photo.read())
        st.image(photo_path, width=120)
    elif profile_photo_path:
        st.image(profile_photo_path, width=120)

    # Core Details
    full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                          index=["Male", "Female", "Other"].index(profile.get("gender", "Male")))
    dob = st.date_input("Date of Birth", value=profile.get("dob", None))
    mobile = st.text_input("Mobile Number", value=profile.get("mobile", ""))
    alt_mobile = st.text_input("Alternate Mobile Number", value=profile.get("alt_mobile", ""))
    email = st.text_input("Email", value=profile.get("email", ""))
    emergency_name = st.text_input("Emergency Contact Name", value=profile.get("emergency_name", ""))
    emergency_number = st.text_input("Emergency Contact Number", value=profile.get("emergency_number", ""))
    address = st.text_area("Address", value=profile.get("address", ""))
    city = st.text_input("City", value=profile.get("city", ""))
    pincode = st.text_input("Pin Code", value=profile.get("pincode", ""))
    state = st.text_input("State", value=profile.get("state", ""))
    nationality = st.text_input("Nationality", value=profile.get("nationality", ""))

    # Extra fields for patient, doctor, guardian
    user_type = profile.get("user_type") or st.session_state.get("user_type")

    # Show relevant fields
    if user_type == "patient":
        blood_group = st.text_input("Blood Group", value=profile.get("blood_group", ""))
    elif user_type == "doctor":
        specialization = st.text_input("Specialization", value=profile.get("specialization", ""))
        experience = st.text_input("Experience (years)", value=str(profile.get("experience", "")))
    elif user_type == "guardian":
        relationship = st.text_input("Relationship", value=profile.get("relationship", ""))

    submitted = st.button("Save Profile")
    if submitted:
        profile["full_name"] = full_name
        profile["gender"] = gender
        profile["dob"] = str(dob)   # Convert to string for JSON
        profile["mobile"] = mobile
        profile["alt_mobile"] = alt_mobile
        profile["city"] = city
        profile["pincode"] = pincode
        profile["state"] = state
        profile["nationality"] = nationality
        profile["address"] = address
        profile["email"] = email
        profile["emergency_name"] = emergency_name
        profile["emergency_number"] = emergency_number
        if photo_path:
            profile["photo_path"] = photo_path
        if user_type == "patient":
            profile["blood_group"] = blood_group
        elif user_type == "doctor":
            profile["specialization"] = specialization
            profile["experience"] = experience
        elif user_type == "guardian":
            profile["relationship"] = relationship
        profiles[user_id] = profile
        save_json(PROFILES_FILE, profiles)
        st.success("Profile updated!")

