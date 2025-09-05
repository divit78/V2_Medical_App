import streamlit as st
import os
import json
from datetime import datetime
from config.constants import PRESCRIPTIONS_FILE, UPLOAD_DIR
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id


class FileHandler:
    """Handle file operations"""
    
    @staticmethod
    def save_uploaded_file(uploaded_file, user_id):
        user_path = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(user_path, exist_ok=True)
        file_path = os.path.join(user_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path


class PrescriptionManager:
    """Main prescription manager"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.file_handler = FileHandler()
    
    def render(self):
        st.title("📑 Prescriptions")
        
        prescriptions = load_json(PRESCRIPTIONS_FILE)
        my_prescriptions = {pid: p for pid, p in prescriptions.items() 
                           if p.get("patient_id") == self.user_id}
        
        # Upload section
        with st.expander("Upload New Prescription"):
            file = st.file_uploader("Upload", type=['jpg', 'jpeg', 'png', 'pdf'])
            notes = st.text_area("Notes")
            
            if file:
                if st.button("📤 Upload"):
                    path = self.file_handler.save_uploaded_file(file, self.user_id)
                    pid = generate_id("PRESC")
                    prescriptions[pid] = {
                        "patient_id": self.user_id,
                        "file_path": path,
                        "notes": notes,
                        "uploaded_at": datetime.now().isoformat()
                    }
                    save_json(PRESCRIPTIONS_FILE, prescriptions)
                    st.success("✅ Prescription uploaded")
                    st.rerun()
        
        # Display prescriptions
        st.subheader("📋 My Prescriptions")
        
        if not my_prescriptions:
            st.info("No prescriptions found.")
        else:
            for pid, p in my_prescriptions.items():
                st.markdown(f"**ID:** {pid}")
                if p.get('notes'):
                    st.write(f"Notes: {p.get('notes')}")
                
                if p.get('file_path') and os.path.exists(p["file_path"]):
                    if p["file_path"].lower().endswith(('.jpg', '.jpeg', '.png')):
                        st.image(p["file_path"], width=300)
                    else:
                        st.info("📄 PDF file uploaded")
                else:
                    st.warning("⚠️ File not found")
                
                st.markdown("---")
        
        # Export section
        if my_prescriptions and st.button("📦 Export All"):
            export = json.dumps(my_prescriptions, indent=2)
            st.download_button("Download", export, "prescriptions.json", mime="application/json")


def prescriptions_page(user_id):
    """Main entry point"""
    manager = PrescriptionManager(user_id)
    manager.render()
