import streamlit as st
from datetime import datetime, time
from utils.file_ops import load_json, save_json
from config.constants import MEDICINES_FILE, SCHEDULES_FILE
from utils.id_utils import generate_id


class DateTimeHelper:
    """Helper for datetime operations"""
    
    @staticmethod
    def safe_parse_datetime(iso_str):
        if not iso_str or not isinstance(iso_str, str):
            return None
        try:
            return datetime.fromisoformat(iso_str)
        except (ValueError, TypeError):
            return None


class DataRepository:
    """Handle data loading and saving"""
    
    def __init__(self):
        self.medicines_file = MEDICINES_FILE
        self.schedules_file = SCHEDULES_FILE
    
    def get_patient_medicines(self, patient_id):
        medicines = load_json(self.medicines_file)
        return {k: v for k, v in medicines.items() if v.get("patient_id") == patient_id}
    
    def get_patient_schedules(self, patient_id):
        schedules = load_json(self.schedules_file)
        return {k: v for k, v in schedules.items() if v.get("patient_id") == patient_id}
    
    def save_schedule(self, schedule_id, schedule_data):
        schedules = load_json(self.schedules_file)
        schedules[schedule_id] = schedule_data
        save_json(self.schedules_file, schedules)
    
    def update_schedule(self, schedule_id, updates):
        schedules = load_json(self.schedules_file)
        if schedule_id in schedules:
            schedules[schedule_id].update(updates)
            save_json(self.schedules_file, schedules)
    
    def delete_schedule(self, schedule_id):
        schedules = load_json(self.schedules_file)
        if schedule_id in schedules:
            del schedules[schedule_id]
            save_json(self.schedules_file, schedules)
    
    def update_medicine_quantity(self, medicine_id, new_quantity):
        medicines = load_json(self.medicines_file)
        if medicine_id in medicines:
            medicines[medicine_id]['quantity'] = new_quantity
            save_json(self.medicines_file, medicines)


class ReminderManager:
    """Main reminder management class"""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.repository = DataRepository()
        self.datetime_helper = DateTimeHelper()
    
    def render(self):
        st.title("⏰ Medicine Reminders")
        self._load_styles()
        
        medicines = self.repository.get_patient_medicines(self.patient_id)
        
        if not medicines:
            st.warning("⚠️ No medicines found! Please add medicines first.")
            if st.button("➕ Add Medicine"):
                st.session_state.patient_nav_page = "Add Medicine"
                st.rerun()
            return
        
        # Create new reminder
        self._render_reminder_form(medicines)
        
        # Show existing reminders
        self._render_active_reminders(medicines)
    
    def _load_styles(self):
        st.markdown("""<style>
        .reminder-container{border-radius:15px;padding:20px;margin:15px 0;border-left:6px solid;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
        .active-reminder{border-left-color:#10b981;background:#f0fdf4}
        .low-stock-reminder{border-left-color:#f59e0b;background:#fffbeb}
        .out-stock-reminder{border-left-color:#ef4444;background:#fef2f2}
        .time-badge{background:rgba(99,102,241,0.1);color:#4f46e5;padding:4px 12px;border-radius:20px;margin:2px 4px}
        </style>""", unsafe_allow_html=True)
    
    def _render_reminder_form(self, medicines):
        st.subheader("🔔 Set New Reminder")
        
        with st.form("reminder_form"):
            # Medicine selection
            medicine_options = []
            medicine_mapping = {}
            
            for med_id, medicine in medicines.items():
                quantity = medicine.get("quantity", 0)
                stock_icon = "🟢" if quantity > 5 else "🟡" if quantity > 0 else "🔴"
                option_text = f"{stock_icon} {medicine.get('name', 'Unknown')} (Stock: {quantity})"
                medicine_options.append(option_text)
                medicine_mapping[option_text] = med_id
            
            selected_option = st.selectbox("Select Medicine", medicine_options)
            selected_medicine_id = medicine_mapping.get(selected_option)
            
            if selected_medicine_id:
                selected_medicine = medicines[selected_medicine_id]
                
                # Medicine info
                with st.expander("📋 Medicine Information"):
                    st.write(f"**Contents:** {selected_medicine.get('contents', 'Not specified')}")
                    st.write(f"**Purpose:** {selected_medicine.get('purpose', 'Not specified')}")
                
                # Dosage schedule
                st.subheader("💊 Dosage Schedule")
                doses_per_day = st.selectbox("Doses per day", [1, 2, 3, 4, 5, 6])
                
                # Time inputs
                dose_times = []
                default_times = [time(8, 0), time(14, 0), time(20, 0), time(6, 0), time(12, 0), time(18, 0)]
                cols = st.columns(min(doses_per_day, 3))
                
                for i in range(doses_per_day):
                    with cols[i % 3]:
                        default_time = default_times[i] if i < len(default_times) else time(8, 0)
                        dose_time = st.time_input(f"Dose {i+1} time", value=default_time, key=f"dose_{i}")
                        dose_times.append(dose_time)
                
                # Additional settings
                before_after_food = st.selectbox("When to take?", 
                                               ["Before Eating", "After Eating", "With Food", "Empty Stomach"])
                precautions = st.text_area("Precautions (if any)", 
                                         value=selected_medicine.get('instructions', ''))
                
                # Submit
                if st.form_submit_button("🔔 Set Reminder", type="primary"):
                    self._create_reminder(selected_medicine_id, selected_medicine, doses_per_day, 
                                        dose_times, before_after_food, precautions)
    
    def _create_reminder(self, medicine_id, medicine, doses_per_day, dose_times, 
                        before_after_food, precautions):
        schedule_id = generate_id("SCH")
        time_strings = [t.strftime("%I:%M %p") for t in dose_times]
        
        schedule_data = {
            "schedule_id": schedule_id,
            "patient_id": self.patient_id,
            "medicine_id": medicine_id,
            "medicine_name": medicine.get('name', 'Unknown'),
            "doses_per_day": doses_per_day,
            "times": time_strings,
            "before_after_food": before_after_food,
            "precaution": precautions,
            "remaining_quantity": medicine.get('quantity', 0),
            "last_taken": None,
            "missed_doses": 0,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        self.repository.save_schedule(schedule_id, schedule_data)
        st.success(f"✅ Reminder set for {medicine.get('name')}!")
        st.rerun()
    
    def _render_active_reminders(self, medicines):
        st.markdown("---")
        st.subheader("📋 Active Reminders")
        
        schedules = self.repository.get_patient_schedules(self.patient_id)
        
        if not schedules:
            st.info("No reminders set yet.")
        else:
            for schedule_id, schedule in schedules.items():
                medicine_info = medicines.get(schedule.get("medicine_id"), {})
                self._render_reminder_card(schedule_id, schedule, medicine_info)
    
    def _render_reminder_card(self, schedule_id, schedule, medicine_info):
        medicine_name = schedule.get("medicine_name") or medicine_info.get("name", "Unknown")
        quantity = medicine_info.get("quantity", 0)
        
        # Determine container style
        if quantity > 5:
            container_class = "active-reminder"
            stock_status = "In Stock"
        elif quantity > 0:
            container_class = "low-stock-reminder"
            stock_status = "Low Stock"
        else:
            container_class = "out-stock-reminder"
            stock_status = "Out of Stock"
        
        # Create time badges
        times = schedule.get('times', [])
        time_badges = ''.join([f'<span class="time-badge">{t}</span>' for t in times])
        
        st.markdown(f"""
        <div class="reminder-container {container_class}">
            <h3>💊 {medicine_name}</h3>
            <p><strong>Stock:</strong> {stock_status} ({quantity} remaining)</p>
            <p><strong>Schedule:</strong> {schedule.get('doses_per_day', 0)} times daily</p>
            <p><strong>Times:</strong> {time_badges}</p>
            <p><strong>Instructions:</strong> {schedule.get('before_after_food', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        with st.expander(f"⚙️ Manage {medicine_name} Reminder"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Mark Taken", key=f"taken_{schedule_id}"):
                    self._mark_taken(schedule_id, schedule.get("medicine_id"))
            
            with col2:
                status = schedule.get('status', 'active')
                btn_text = "⏸️ Pause" if status == 'active' else "▶️ Resume"
                if st.button(btn_text, key=f"pause_{schedule_id}"):
                    new_status = 'paused' if status == 'active' else 'active'
                    self._toggle_status(schedule_id, new_status)
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{schedule_id}"):
                    self._delete_reminder(schedule_id, medicine_name)
    
    def _mark_taken(self, schedule_id, medicine_id):
        # Update schedule
        updates = {
            'last_taken': datetime.now().isoformat(),
            'remaining_quantity': max(0, self.repository.get_patient_schedules(self.patient_id)[schedule_id].get('remaining_quantity', 0) - 1)
        }
        self.repository.update_schedule(schedule_id, updates)
        
        # Update medicine quantity
        if medicine_id:
            medicines = self.repository.get_patient_medicines(self.patient_id)
            if medicine_id in medicines:
                current_qty = medicines[medicine_id].get('quantity', 0)
                self.repository.update_medicine_quantity(medicine_id, max(0, current_qty - 1))
        
        st.success("✅ Medicine marked as taken!")
        st.rerun()
    
    def _toggle_status(self, schedule_id, new_status):
        self.repository.update_schedule(schedule_id, {'status': new_status})
        status_text = "paused" if new_status == 'paused' else "resumed"
        st.success(f"✅ Reminder {status_text}!")
        st.rerun()
    
    def _delete_reminder(self, schedule_id, medicine_name):
        self.repository.delete_schedule(schedule_id)
        st.success(f"✅ Reminder for {medicine_name} deleted!")
        st.rerun()


def medicine_reminder_page(patient_id):
    """Main entry point"""
    manager = ReminderManager(patient_id)
    manager.render()
