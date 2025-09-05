import streamlit as st
from datetime import datetime
import os
import json
from config.constants import MEDICAL_TESTS_FILE, UPLOAD_DIR
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id


class MedicalTest:
    """Simple class for medical test data"""
    def __init__(self, test_id, data):
        self.test_id = test_id
        self.patient_id = data.get('patient_id', '')
        self.test_type = data.get('test_type', '')
        self.file_path = data.get('file_path', '')
        self.notes = data.get('notes', '')
        self.uploaded_at = data.get('uploaded_at', '')
    
    def get_filename(self):
        return os.path.basename(self.file_path) if self.file_path else "Unknown file"
    
    def is_image(self):
        return self.file_path.lower().endswith(('.png', '.jpg', '.jpeg'))
    
    def file_exists(self):
        return self.file_path and os.path.exists(self.file_path)


class FileHandler:
    """Simple class for file operations"""
    
    @staticmethod
    def save_uploaded_file(file, user_id):
        user_path = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(user_path, exist_ok=True)
        file_path = os.path.join(user_path, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        return file_path


class TestRepository:
    """Simple repository for test data"""
    
    def __init__(self):
        self.file_path = MEDICAL_TESTS_FILE
    
    def get_patient_tests(self, patient_id):
        """Get all tests for patient"""
        all_tests = load_json(self.file_path)
        patient_tests = []
        
        for test_id, test_data in all_tests.items():
            if test_data.get("patient_id") == patient_id:
                patient_tests.append(MedicalTest(test_id, test_data))
        
        return patient_tests
    
    def save_test(self, patient_id, test_type, file_path, notes):
        """Save new test"""
        all_tests = load_json(self.file_path)
        test_id = generate_id("TEST")
        
        all_tests[test_id] = {
            "patient_id": patient_id,
            "test_type": test_type,
            "file_path": file_path,
            "notes": notes,
            "uploaded_at": datetime.now().isoformat()
        }
        
        save_json(self.file_path, all_tests)
        return True
    
    def export_patient_tests(self, patient_id):
        """Export tests as JSON"""
        all_tests = load_json(self.file_path)
        patient_tests = {tid: t for tid, t in all_tests.items() if t.get("patient_id") == patient_id}
        return json.dumps(patient_tests, indent=2)


class MedicalTestsPage:
    """Main page class"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.repository = TestRepository()
        self.file_handler = FileHandler()
    
    def render(self):
        """Render the page"""
        st.title("🧪 Medical Tests")
        
        # Upload section
        self._render_upload_section()
        
        # Display tests
        self._render_tests_section()
        
        # Export section
        self._render_export_section()
    
    def _render_upload_section(self):
        """Render upload form"""
        with st.expander("Upload New Test Report"):
            uploaded_file = st.file_uploader("Upload Test (JPG, PNG, PDF)", type=['jpg', 'jpeg', 'png', 'pdf'])
            test_type = st.text_input("Test Type (e.g. Blood, X-ray, MRI)")
            notes = st.text_area("Notes (optional)")
            
            if uploaded_file and test_type:
                if st.button("📤 Upload Test"):
                    try:
                        file_path = self.file_handler.save_uploaded_file(uploaded_file, self.user_id)
                        self.repository.save_test(self.user_id, test_type, file_path, notes)
                        st.success("✅ Test uploaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error uploading test: {str(e)}")
    
    def _render_tests_section(self):
        """Render tests list"""
        st.subheader("📋 My Test Reports")
        tests = self.repository.get_patient_tests(self.user_id)
        
        if not tests:
            st.info("No medical test reports uploaded.")
            return
        
        for test in tests:
            st.markdown(f"**Test Type:** {test.test_type}")
            if test.notes:
                st.markdown(f"**Notes:** {test.notes}")
            
            if test.file_exists():
                st.write(f"🗂️ {test.get_filename()}")
                if test.is_image():
                    st.image(test.file_path, width=300)
            else:
                st.warning("⚠️ File not found")
            
            st.markdown("---")
    
    def _render_export_section(self):
        """Render export functionality"""
        if st.button("📥 Export Medical Tests JSON"):
            download_data = self.repository.export_patient_tests(self.user_id)
            st.download_button("Download Tests", download_data, "medical_tests.json", mime="application/json")


def medical_tests_page(user_id):
    """Main entry point"""
    page = MedicalTestsPage(user_id)
    page.render()
