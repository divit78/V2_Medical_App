import streamlit as st
from config.constants import PROFILES_FILE
from utils.file_ops import load_json, save_json
import os
from datetime import datetime


class FileHandler:
    """Handle file operations"""
    
    @staticmethod
    def save_uploaded_file(uploaded_file, user_id):
        """Save uploaded file and return path"""
        upload_dir = os.path.join("profile_photos", user_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"profile_{user_id}.png")
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path


class ProfileData:
    """Handle profile data operations"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.profiles = load_json(PROFILES_FILE)
        self.profile = self.profiles.get(user_id, {})
    
    def get_value(self, key, default=""):
        """Get profile value with default"""
        return self.profile.get(key, default)
    
    def update_profile(self, updates):
        """Update profile data"""
        self.profile.update(updates)
        self.profiles[self.user_id] = self.profile
        save_json(PROFILES_FILE, self.profiles)
    
    def remove_photo(self):
        """Remove profile photo"""
        photo_path = self.profile.get("photo_path")
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)
        
        self.profile.pop("photo_path", None)
        self.profiles[self.user_id] = self.profile
        save_json(PROFILES_FILE, self.profiles)
    
    def get_dob_value(self):
        """Get date of birth as date object"""
        try:
            dob = self.profile.get("dob")
            if dob:
                if isinstance(dob, str):
                    return datetime.fromisoformat(dob).date()
                return dob
        except:
            pass
        return None


class UpdateProfilePage:
    """Main update profile page class"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.profile_data = ProfileData(user_id)
        self.file_handler = FileHandler()
    
    def render(self):
        """Render the update profile page"""
        st.title("🔄 Update Profile")
        
        # Profile photo section
        self._render_photo_section()
        
        st.markdown("---")
        
        # Personal information
        self._render_personal_info()
        
        # Address information
        self._render_address_info()
        
        # User-type specific fields
        self._render_user_specific_fields()
        
        # Save button
        self._render_save_button()
    
    def _render_photo_section(self):
        """Render profile photo section"""
        st.subheader("📷 Profile Photo")
        
        existing_photo = self.profile_data.get_value("photo_path")
        
        # Display current photo
        if existing_photo and os.path.exists(existing_photo):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(existing_photo, width=150, caption="Current Photo")
            with col2:
                st.info("✅ Profile photo uploaded successfully!")
                if st.button("🗑️ Remove Photo"):
                    self.profile_data.remove_photo()
                    st.success("Photo removed successfully!")
                    st.rerun()
        else:
            st.info("📷 No profile photo uploaded yet")
        
        # Upload new photo
        uploaded_photo = st.file_uploader(
            "Upload New Profile Photo", 
            type=["jpg", "jpeg", "png"],
            help="Choose a JPG, JPEG, or PNG file"
        )
        
        if uploaded_photo:
            st.image(uploaded_photo, width=150, caption="Preview")
            
            if st.button("💾 Save Profile Photo"):
                try:
                    photo_path = self.file_handler.save_uploaded_file(uploaded_photo, self.user_id)
                    self.profile_data.update_profile({"photo_path": photo_path})
                    st.success("✅ Profile photo uploaded successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving photo: {e}")
    
    def _render_personal_info(self):
        """Render personal information section"""
        st.subheader("👤 Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.full_name = st.text_input("Full Name", value=self.profile_data.get_value("full_name"))
            self.gender = st.selectbox(
                "Gender", 
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(self.profile_data.get_value("gender", "Male"))
            )
            self.mobile = st.text_input("Mobile Number", value=self.profile_data.get_value("mobile"))
            self.email = st.text_input("Email", value=self.profile_data.get_value("email"))
        
        with col2:
            self.dob = st.date_input("Date of Birth", value=self.profile_data.get_dob_value())
            self.alt_mobile = st.text_input("Alternate Mobile", value=self.profile_data.get_value("alt_mobile"))
            self.emergency_name = st.text_input("Emergency Contact Name", value=self.profile_data.get_value("emergency_name"))
            self.emergency_number = st.text_input("Emergency Contact Number", value=self.profile_data.get_value("emergency_number"))
    
    def _render_address_info(self):
        """Render address information section"""
        st.subheader("🏠 Address Information")
        
        col3, col4 = st.columns(2)
        
        with col3:
            self.address = st.text_area("Address", value=self.profile_data.get_value("address"))
            self.city = st.text_input("City", value=self.profile_data.get_value("city"))
        
        with col4:
            self.pincode = st.text_input("Pin Code", value=self.profile_data.get_value("pincode"))
            self.state = st.text_input("State", value=self.profile_data.get_value("state"))
            self.nationality = st.text_input("Nationality", value=self.profile_data.get_value("nationality"))
    
    def _render_user_specific_fields(self):
        """Render user-type specific fields"""
        user_type = self.profile_data.get_value("user_type") or st.session_state.get("user_type")
        
        if user_type == "patient":
            st.subheader("🩸 Medical Information")
            self.blood_group = st.selectbox(
                "Blood Group", 
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
                index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(
                    self.profile_data.get_value("blood_group", "Unknown")
                )
            )
        
        elif user_type == "doctor":
            st.subheader("👨‍⚕️ Professional Information")
            col5, col6 = st.columns(2)
            with col5:
                self.specialization = st.text_input("Specialization", value=self.profile_data.get_value("specialization"))
                self.experience = st.number_input("Experience (years)", 
                                                value=int(self.profile_data.get_value("experience", 0)), 
                                                min_value=0)
            with col6:
                self.hospital_clinic = st.text_input("Hospital/Clinic", value=self.profile_data.get_value("hospital_clinic"))
                self.consultation_fee = st.number_input("Consultation Fee (₹)", 
                                                      value=float(self.profile_data.get_value("consultation_fee", 0)), 
                                                      min_value=0.0)
        
        elif user_type == "guardian":
            st.subheader("👨‍👩‍👧‍👦 Guardian Information")
            self.relationship = st.text_input("Relationship", value=self.profile_data.get_value("relationship"))
        
        self.user_type = user_type
    
    def _render_save_button(self):
        """Render save profile button"""
        if st.button("💾 Save Profile", type="primary"):
            # Prepare update data
            updates = {
                "full_name": self.full_name,
                "gender": self.gender,
                "dob": str(self.dob),
                "mobile": self.mobile,
                "alt_mobile": self.alt_mobile,
                "email": self.email,
                "emergency_name": self.emergency_name,
                "emergency_number": self.emergency_number,
                "address": self.address,
                "city": self.city,
                "pincode": self.pincode,
                "state": self.state,
                "nationality": self.nationality
            }
            
            # Add user-type specific fields
            if self.user_type == "patient":
                updates["blood_group"] = self.blood_group
            elif self.user_type == "doctor":
                updates.update({
                    "specialization": self.specialization,
                    "experience": self.experience,
                    "hospital_clinic": self.hospital_clinic,
                    "consultation_fee": self.consultation_fee
                })
            elif self.user_type == "guardian":
                updates["relationship"] = self.relationship
            
            # Save profile
            self.profile_data.update_profile(updates)
            st.success("✅ Profile updated successfully!")
            st.balloons()


def update_profile_page(user_id):
    """Main entry point"""
    page = UpdateProfilePage(user_id)
    page.render()
