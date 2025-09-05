import streamlit as st
import json
from datetime import datetime
from utils.file_ops import load_json
from config.constants import SCHEDULES_FILE, MEDICINES_FILE


class DateTimeHandler:
    """Simple utility for handling datetime serialization"""
    
    @staticmethod
    def convert_datetime_to_string(obj):
        """Convert datetime objects to strings for JSON serialization"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: DateTimeHandler.convert_datetime_to_string(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DateTimeHandler.convert_datetime_to_string(item) for item in obj]
        return obj


class AdherenceData:
    """Simple data class for adherence information"""
    def __init__(self, schedule_id, medicine_name, last_taken, missed_doses, doses_per_day):
        self.schedule_id = schedule_id
        self.medicine_name = medicine_name
        self.last_taken = last_taken
        self.missed_doses = missed_doses
        self.doses_per_day = doses_per_day
        self.adherence_rate = self._calculate_rate()
    
    def _calculate_rate(self):
        """Calculate adherence rate"""
        if self.doses_per_day <= 0:
            return 0.0
        taken = max(0, self.doses_per_day - self.missed_doses)
        rate = (taken / self.doses_per_day) * 100
        return max(0.0, min(rate, 100.0))


class DataRepository:
    """Simple repository for data operations"""
    
    def __init__(self):
        self.schedules = load_json(SCHEDULES_FILE)
        self.medicines = load_json(MEDICINES_FILE)
    
    def get_patient_adherence_data(self, user_id):
        """Get adherence data for patient"""
        patient_schedules = {
            sid: s for sid, s in self.schedules.items() 
            if s.get("patient_id") == user_id
        }
        
        adherence_list = []
        for sid, sched in patient_schedules.items():
            med_info = self.medicines.get(sched.get("medicine_id"), {})
            
            data = AdherenceData(
                schedule_id=sid,
                medicine_name=med_info.get('name', 'Unknown Medicine'),
                last_taken=sched.get('last_taken', 'N/A'),
                missed_doses=sched.get('missed_doses', 0),
                doses_per_day=sched.get('doses_per_day', 0)
            )
            adherence_list.append(data)
        
        return adherence_list, patient_schedules


class AdherencePage:
    """Main adherence page class"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.repository = DataRepository()
        self.datetime_handler = DateTimeHandler()
    
    def render(self):
        """Render the adherence page"""
        st.title("📈 Adherence History")
        
        adherence_data, raw_schedules = self.repository.get_patient_adherence_data(self.user_id)
        
        if not adherence_data:
            st.info("No adherence history available.")
            return
        
        # Display each medicine's adherence
        for data in adherence_data:
            st.subheader(f"{data.medicine_name}")
            st.write(f"Last Taken: {data.last_taken}")
            st.write(f"Missed Doses: {data.missed_doses}")
            st.write(f"Estimated Adherence: {data.adherence_rate:.1f}%")
            st.markdown("---")
        
        # Export functionality
        self._render_export_button(raw_schedules)
    
    def _render_export_button(self, raw_schedules):
        """Render export functionality"""
        if st.button("📁 Export Adherence Report"):
            try:
                # Convert datetime objects to strings for JSON serialization
                serializable_data = self.datetime_handler.convert_datetime_to_string(raw_schedules)
                download_data = json.dumps(serializable_data, indent=2)
                
                st.download_button(
                    "Download as JSON", 
                    download_data, 
                    "adherence_history.json", 
                    mime="application/json"
                )
                st.success("✅ Export prepared successfully!")
                
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")


def adherence_history(user_id):
    """Main entry point"""
    page = AdherencePage(user_id)
    page.render()
