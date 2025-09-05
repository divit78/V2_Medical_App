import streamlit as st
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from utils.db_helper import db
from utils.file_ops import load_json
from config.constants import (
    PROFILES_FILE, MEDICINES_FILE, SCHEDULES_FILE, APPOINTMENTS_FILE
)


@dataclass
class PatientMetrics:
    """Data class for patient metrics"""
    total_medicines: int
    active_reminders: int
    total_appointments: int
    low_stock_medicines: int


@dataclass
class NavigationMenuItem:
    """Data class for navigation menu items"""
    icon: str
    label: str
    page_key: str


class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def get_connection_status(guardian_id: str) -> str:
        """Check if guardian request is approved"""
        try:
            db.connect()
            result = db.execute_query(
                "SELECT status FROM guardian_requests WHERE guardian_id = %s ORDER BY requested_at DESC LIMIT 1", 
                (guardian_id,)
            )
            return result[0]['status'] if result else "pending"
        except Exception as e:
            print(f"Database query error: {e}")
            return "pending"


class DateTimeFormatter:
    """Utility class for date formatting"""
    
    @staticmethod
    def safe_date_format(date_value: Any) -> str:
        """Safely format date values - handles both string and datetime objects"""
        if not date_value:
            return 'Unknown'
        try:
            if isinstance(date_value, str):
                if 'T' in date_value:
                    return date_value.split('T')[0]
                return date_value[:10]
            return date_value.strftime('%Y-%m-%d')
        except Exception:
            return 'Unknown'


class BaseRepository:
    """Base repository class for data operations"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        return load_json(self.file_path)
    
    def get_patient_data(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get data for specific patient - to be implemented by subclasses"""
        data = self.load_data()
        return [item for item in data.values() if item.get('patient_id') == patient_id]


class MedicineRepository(BaseRepository):
    """Repository for medicine operations"""
    
    def __init__(self):
        super().__init__(MEDICINES_FILE)
    
    def get_patient_medicines(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get medicines for specific patient"""
        return self.get_patient_data(patient_id)
    
    def get_low_stock_medicines(self, patient_id: str, threshold: int = 5) -> List[Dict[str, Any]]:
        """Get medicines with low stock"""
        medicines = self.get_patient_medicines(patient_id)
        return [m for m in medicines if m.get('quantity', 0) <= threshold]
    
    def get_recent_medicines(self, patient_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get recently added medicines"""
        medicines = self.get_patient_medicines(patient_id)
        return sorted(medicines, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]


class ScheduleRepository(BaseRepository):
    """Repository for schedule operations"""
    
    def __init__(self):
        super().__init__(SCHEDULES_FILE)
    
    def get_patient_schedules(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get schedules for specific patient"""
        return self.get_patient_data(patient_id)
    
    def get_active_reminders(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get active reminders for patient"""
        schedules = self.get_patient_schedules(patient_id)
        return [s for s in schedules if s.get('status') == 'active']


class AppointmentRepository(BaseRepository):
    """Repository for appointment operations"""
    
    def __init__(self):
        super().__init__(APPOINTMENTS_FILE)
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get appointments for specific patient"""
        return self.get_patient_data(patient_id)


class ProfileRepository(BaseRepository):
    """Repository for profile operations"""
    
    def __init__(self):
        super().__init__(PROFILES_FILE)
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        profiles = self.load_data()
        return profiles.get(user_id, {})
    
    def get_connected_patient_id(self, guardian_id: str) -> Optional[str]:
        """Get connected patient ID for guardian"""
        profile = self.get_profile(guardian_id)
        return profile.get("connected_patient")


class PatientMetricsService:
    """Service class for calculating patient metrics"""
    
    def __init__(self):
        self.medicine_repo = MedicineRepository()
        self.schedule_repo = ScheduleRepository()
        self.appointment_repo = AppointmentRepository()
    
    def get_patient_metrics(self, patient_id: str) -> PatientMetrics:
        """Get comprehensive patient metrics"""
        try:
            if not patient_id:
                return PatientMetrics(0, 0, 0, 0)
            
            medicines = self.medicine_repo.get_patient_medicines(patient_id)
            active_reminders = self.schedule_repo.get_active_reminders(patient_id)
            appointments = self.appointment_repo.get_patient_appointments(patient_id)
            low_stock_medicines = self.medicine_repo.get_low_stock_medicines(patient_id)
            
            return PatientMetrics(
                total_medicines=len(medicines),
                active_reminders=len(active_reminders),
                total_appointments=len(appointments),
                low_stock_medicines=len(low_stock_medicines)
            )
        except Exception as e:
            print(f"Error getting patient metrics: {e}")
            return PatientMetrics(0, 0, 0, 0)


class UIStyleManager:
    """Manages UI styles and CSS"""
    
    @staticmethod
    def load_css() -> None:
        """Load enhanced CSS styles"""
        css_styles = """<style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        .stApp{background:linear-gradient(135deg,#e8f5e8 0%,#f0fff0 50%,#e0f2e1 100%);font-family:'Inter','Segoe UI',sans-serif}
        .main-header{background:linear-gradient(135deg,#4CAF50,#66BB6A);padding:2.5rem;border-radius:20px;margin-bottom:2rem;text-align:center;color:white;box-shadow:0 10px 30px rgba(76,175,80,0.3);animation:fadeInDown 1s ease-out}
        .main-header h1{font-size:2.8rem;font-weight:700;margin:0;text-shadow:2px 2px 4px rgba(0,0,0,0.2)}
        .main-header h3{font-size:1.5rem;margin:1rem 0 0.5rem 0;opacity:0.95}
        .main-header p{font-size:1.1rem;margin:10px 0 0 0;opacity:0.9}
        .status-pending{background:linear-gradient(135deg,#fff8e1,#ffecb3);color:#e65100;padding:2rem;border-radius:15px;border-left:5px solid #FFA726;margin:2rem 0;box-shadow:0 5px 20px rgba(255,167,38,0.2);animation:slideInLeft 0.8s ease-out}
        .status-approved{background:linear-gradient(135deg,#e8f5e8,#c8e6c9);color:#1b5e20;padding:2rem;border-radius:15px;border-left:5px solid #4CAF50;margin:2rem 0;box-shadow:0 5px 20px rgba(76,175,80,0.2);animation:slideInLeft 0.8s ease-out}
        .status-pending h3,.status-approved h3{font-size:1.5rem;margin:0 0 1rem 0;font-weight:700}
        .status-pending p,.status-approved p{font-size:1rem;line-height:1.6;margin:0}
        .patient-info{background:rgba(255,255,255,0.95);padding:2rem;border-radius:15px;border-left:5px solid #2196F3;margin:2rem 0;box-shadow:0 8px 25px rgba(0,0,0,0.1);animation:slideInRight 0.8s ease-out}
        .patient-info h4{color:#1976D2;font-size:1.5rem;margin:0 0 1rem 0;font-weight:700}
        .patient-info p{margin:0.5rem 0;line-height:1.5}
        .patient-info strong{color:#333;font-weight:600}
        .metric-card{background:white;padding:2rem;border-radius:15px;text-align:center;box-shadow:0 5px 20px rgba(0,0,0,0.08);transition:all 0.3s ease;position:relative;overflow:hidden;animation:fadeInUp 0.6s ease-out;border-top:4px solid #4CAF50}
        .metric-card:hover{transform:translateY(-8px);box-shadow:0 15px 35px rgba(0,0,0,0.15)}
        .metric-card::before{content:'';position:absolute;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg,#4CAF50,#66BB6A)}
        .metric-card h3{font-size:2.5rem;margin-bottom:1rem;color:#4CAF50}
        .metric-card h2{font-size:3rem;font-weight:700;color:#2c3e50;margin:0.5rem 0}
        .metric-card p{font-size:1.1rem;color:#666;font-weight:500;margin:0}
        .sidebar-profile{background:linear-gradient(135deg,#4CAF50,#66BB6A);padding:2rem;border-radius:15px;color:white;text-align:center;margin-bottom:2rem;box-shadow:0 5px 20px rgba(76,175,80,0.3)}
        .sidebar-profile h3{margin:0;font-size:1.5rem;font-weight:700}
        .sidebar-profile p{margin:0.5rem 0 0 0;opacity:0.9;font-size:0.9rem}
        .activity-section{background:rgba(255,255,255,0.95);padding:2rem;border-radius:15px;margin:2rem 0;box-shadow:0 5px 20px rgba(0,0,0,0.08);animation:fadeInUp 0.8s ease-out}
        .activity-item{background:#f8f9fa;padding:1rem 1.5rem;border-radius:10px;margin:0.5rem 0;border-left:4px solid #4CAF50;transition:all 0.3s ease}
        .activity-item:hover{background:#e8f5e8;transform:translateX(5px)}
        .stButton>button{background:linear-gradient(135deg,#4CAF50,#66BB6A)!important;color:white!important;border:none!important;border-radius:10px!important;padding:12px 24px!important;font-weight:600!important;transition:all 0.3s ease!important;box-shadow:0 4px 15px rgba(76,175,80,0.2)!important}
        .stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(76,175,80,0.3)!important}
        .stSelectbox>div>div{background:rgba(255,255,255,0.9)!important;border-radius:10px!important;border:1px solid rgba(76,175,80,0.2)!important}
        .streamlit-expanderHeader{background:rgba(76,175,80,0.1)!important;border-radius:10px!important}
        @keyframes fadeInDown{from{opacity:0;transform:translateY(-30px)}to{opacity:1;transform:translateY(0)}}
        @keyframes slideInLeft{from{opacity:0;transform:translateX(-40px)}to{opacity:1;transform:translateX(0)}}
        @keyframes slideInRight{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:translateX(0)}}
        @keyframes fadeInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
        @media (max-width:768px){.main-header h1{font-size:2rem}.metric-card h2{font-size:2.5rem}.metric-card{padding:1.5rem}}
        </style>"""
        
        st.markdown(css_styles, unsafe_allow_html=True)


class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def render(self) -> None:
        """Render the UI component"""
        pass


class HeaderComponent(UIComponent):
    """Header component for the dashboard"""
    
    def __init__(self, guardian_name: str):
        self.guardian_name = guardian_name
    
    def render(self) -> None:
        """Render the main header"""
        header_html = f"""
        <div class="main-header">
            <h1>👨‍👩‍👧‍👦 Guardian Dashboard</h1>
            <h3>Welcome, {self.guardian_name}!</h3>
            <p>Monitor and support your connected patient's healthcare journey</p>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)


class SidebarComponent(UIComponent):
    """Sidebar navigation component"""
    
    def __init__(self, guardian_profile: Dict[str, Any], user_id: str):
        self.guardian_profile = guardian_profile
        self.user_id = user_id
        self.menu_items = [
            NavigationMenuItem("🏠", "Dashboard Home", "🏠 Dashboard Home"),
            NavigationMenuItem("👤", "Patient Overview", "👤 Patient Overview"),
            NavigationMenuItem("💊", "Patient Medications", "💊 Patient Medications"),
            NavigationMenuItem("⏰", "Medicine Reminders", "⏰ Medicine Reminders"),
            NavigationMenuItem("📅", "Appointments", "📅 Appointments"),
            NavigationMenuItem("📋", "Medical Records", "📋 Medical Records"),
            NavigationMenuItem("⚙️", "Update Profile", "⚙️ Update Profile")
        ]
    
    def render(self) -> str:
        """Render sidebar and return selected page"""
        # Profile section
        profile_html = f"""
        <div class="sidebar-profile">
            <h3>👋 {self.guardian_profile.get('full_name', 'Guardian')}</h3>
            <p>Guardian ID: {self.user_id}</p>
            <p>Role: Healthcare Guardian</p>
        </div>
        """
        st.sidebar.markdown(profile_html, unsafe_allow_html=True)
        
        # Navigation menu
        menu_options = [item.page_key for item in self.menu_items]
        selected_page = st.sidebar.selectbox("Navigate", menu_options)
        
        # Logout button
        if st.sidebar.button("🚪 Logout", type="secondary"):
            from page.navigation import logout
            logout()
        
        return selected_page


class MetricsCardComponent(UIComponent):
    """Metrics cards component"""
    
    def __init__(self, metrics: PatientMetrics):
        self.metrics = metrics
    
    def render(self) -> None:
        """Render metrics cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_data = [
            ("💊", self.metrics.total_medicines, "Total Medicines"),
            ("⏰", self.metrics.active_reminders, "Active Reminders"),
            ("📅", self.metrics.total_appointments, "Upcoming Appointments"),
            ("⚠️", self.metrics.low_stock_medicines, "Low Stock Medicines")
        ]
        
        columns = [col1, col2, col3, col4]
        
        for i, (icon, value, label) in enumerate(metrics_data):
            with columns[i]:
                card_html = f"""
                <div class="metric-card">
                    <h3>{icon}</h3>
                    <h2>{value}</h2>
                    <p>{label}</p>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)


class StatusCardComponent(UIComponent):
    """Status card component for connection status"""
    
    def __init__(self, connection_status: str):
        self.connection_status = connection_status
    
    def render(self) -> None:
        """Render connection status card"""
        if self.connection_status != "approved":
            status_html = """
            <div class="status-pending">
                <h3>⏳ Awaiting Patient Approval</h3>
                <p>Your request to connect with the patient is still pending approval. Please wait for the patient to approve your access request.</p>
            </div>
            """
        else:
            status_html = """
            <div class="status-approved">
                <h3>✅ Connected Successfully</h3>
                <p>You have been approved to access the patient's health information.</p>
            </div>
            """
        
        st.markdown(status_html, unsafe_allow_html=True)


class PatientInfoComponent(UIComponent):
    """Patient information card component"""
    
    def __init__(self, connected_patient: Dict[str, Any], guardian_profile: Dict[str, Any]):
        self.connected_patient = connected_patient
        self.guardian_profile = guardian_profile
    
    def render(self) -> None:
        """Render patient information card"""
        if self.connected_patient:
            patient_html = f"""
            <div class="patient-info">
                <h4>🩺 Connected Patient: {self.connected_patient.get('full_name', 'Unknown')}</h4>
                <p><strong>Patient ID:</strong> {self.connected_patient.get('patient_id', 'N/A')}</p>
                <p><strong>Blood Group:</strong> {self.connected_patient.get('blood_group', 'Not specified')}</p>
                <p><strong>Mobile:</strong> {self.connected_patient.get('mobile', 'Not provided')}</p>
                <p><strong>Relationship:</strong> {self.guardian_profile.get('relationship', 'Not specified')}</p>
            </div>
            """
            st.markdown(patient_html, unsafe_allow_html=True)


class BasePage(ABC):
    """Abstract base class for guardian dashboard pages"""
    
    def __init__(self, connection_status: str):
        self.connection_status = connection_status
        self.datetime_formatter = DateTimeFormatter()
    
    def check_access(self) -> bool:
        """Check if guardian has access to patient data"""
        if self.connection_status != "approved":
            st.warning("⚠️ Please wait for patient approval to access this information.")
            return False
        return True
    
    @abstractmethod
    def render_content(self) -> None:
        """Render the main content of the page"""
        pass
    
    def render(self) -> None:
        """Main render method"""
        if self.check_access():
            self.render_content()


class DashboardHomePage(BasePage):
    """Dashboard home page"""
    
    def __init__(self, guardian_profile: Dict[str, Any], connected_patient: Dict[str, Any], 
                 connected_patient_id: str, connection_status: str):
        super().__init__(connection_status)
        self.guardian_profile = guardian_profile
        self.connected_patient = connected_patient
        self.connected_patient_id = connected_patient_id
        self.metrics_service = PatientMetricsService()
        self.medicine_repo = MedicineRepository()
    
    def render_content(self) -> None:
        """Render dashboard home content"""
        # Patient info component
        if self.connected_patient:
            patient_info = PatientInfoComponent(self.connected_patient, self.guardian_profile)
            patient_info.render()
        
        # Metrics cards
        patient_metrics = self.metrics_service.get_patient_metrics(self.connected_patient_id)
        metrics_component = MetricsCardComponent(patient_metrics)
        metrics_component.render()
        
        # Recent activities
        self._render_recent_activities()
    
    def _render_recent_activities(self) -> None:
        """Render recent patient activities section"""
        st.markdown("---")
        st.markdown('<div class="activity-section">', unsafe_allow_html=True)
        st.subheader("📈 Recent Patient Activities")
        
        recent_medicines = self.medicine_repo.get_recent_medicines(self.connected_patient_id)
        
        if recent_medicines:
            st.write("**Recent Medicines Added:**")
            for med in recent_medicines:
                created_date = self.datetime_formatter.safe_date_format(med.get('created_at'))
                activity_html = f'''
                <div class="activity-item">
                    💊 Added medicine: <strong>{med.get("name", "Unknown")}</strong> ({created_date})
                </div>
                '''
                st.markdown(activity_html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="activity-item">No recent activities found.</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render(self) -> None:
        """Override render to handle non-approved status differently"""
        status_component = StatusCardComponent(self.connection_status)
        status_component.render()
        
        if self.connection_status != "approved":
            st.info("💡 Once approved, you'll be able to monitor the patient's medications, appointments, and health records.")
            return
        
        self.render_content()


class PatientOverviewPage(BasePage):
    """Patient overview page"""
    
    def __init__(self, connected_patient_id: str, connected_patient: Dict[str, Any], connection_status: str):
        super().__init__(connection_status)
        self.connected_patient_id = connected_patient_id
        self.connected_patient = connected_patient
    
    def render_content(self) -> None:
        """Render patient overview content"""
        st.title("👤 Patient Overview")
        
        if not self.connected_patient:
            st.error("❌ No patient connected.")
            return
        
        # Basic information
        with st.expander("📋 Basic Information", expanded=True):
            self._render_basic_info()
        
        # Address information
        with st.expander("🏠 Address Information"):
            self._render_address_info()
    
    def _render_basic_info(self) -> None:
        """Render basic patient information"""
        col1, col2 = st.columns(2)
        basic_info = [
            ("Full Name", "full_name"),
            ("Gender", "gender"),
            ("Blood Group", "blood_group"),
            ("Mobile", "mobile"),
            ("Email", "email"),
            ("Date of Birth", "dob"),
            ("Marital Status", "marital_status"),
            ("Patient ID", "patient_id")
        ]
        
        for i, (label, key) in enumerate(basic_info):
            with col1 if i < 4 else col2:
                default_value = 'Not provided' if key != 'patient_id' else 'N/A'
                st.write(f"**{label}:** {self.connected_patient.get(key, default_value)}")
    
    def _render_address_info(self) -> None:
        """Render address information"""
        address_info = [
            ("Address", "address"),
            ("City", "city"),
            ("State", "state"),
            ("Pincode", "pincode")
        ]
        
        for label, key in address_info:
            st.write(f"**{label}:** {self.connected_patient.get(key, 'Not provided')}")


class PatientMedicationsPage(BasePage):
    """Patient medications page"""
    
    def __init__(self, connected_patient_id: str, connection_status: str):
        super().__init__(connection_status)
        self.connected_patient_id = connected_patient_id
        self.medicine_repo = MedicineRepository()
    
    def render_content(self) -> None:
        """Render patient medications content"""
        st.title("💊 Patient Medications")
        
        if not self.connected_patient_id:
            st.error("❌ No patient connected.")
            return
        
        patient_medicines = self.medicine_repo.get_patient_medicines(self.connected_patient_id)
        
        if patient_medicines:
            st.success(f"Found {len(patient_medicines)} medicines for this patient")
            self._render_medicines(patient_medicines)
        else:
            st.info("📝 Patient hasn't added any medications yet.")
    
    def _render_medicines(self, medicines: List[Dict[str, Any]]) -> None:
        """Render medicines list"""
        for med in medicines:
            with st.expander(f"💊 {med.get('name', 'Unknown Medicine')}"):
                col1, col2 = st.columns(2)
                
                med_info = [
                    ("Contents", "contents"),
                    ("Purpose", "purpose"),
                    ("Category", "category"),
                    ("Quantity", "quantity"),
                    ("Expiry Date", "expiry_date"),
                    ("Take with food", "take_with_food")
                ]
                
                for i, (label, key) in enumerate(med_info):
                    with col1 if i < 3 else col2:
                        value = med.get(key, 'Not specified' if key != 'quantity' else 0)
                        if key == 'quantity':
                            value = f"{value} units"
                        st.write(f"**{label}:** {value}")


class MedicineRemindersPage(BasePage):
    """Medicine reminders page"""
    
    def __init__(self, connected_patient_id: str, connection_status: str):
        super().__init__(connection_status)
        self.connected_patient_id = connected_patient_id
        self.schedule_repo = ScheduleRepository()
    
    def render_content(self) -> None:
        """Render medicine reminders content"""
        st.title("⏰ Medicine Reminders")
        
        if not self.connected_patient_id:
            st.error("❌ No patient connected.")
            return
        
        patient_schedules = self.schedule_repo.get_patient_schedules(self.connected_patient_id)
        
        if patient_schedules:
            st.success(f"Found {len(patient_schedules)} medicine reminders for this patient")
            self._render_schedules(patient_schedules)
        else:
            st.info("⏰ Patient hasn't set any medication reminders yet.")
    
    def _render_schedules(self, schedules: List[Dict[str, Any]]) -> None:
        """Render schedules list"""
        for schedule in schedules:
            with st.expander(f"⏰ {schedule.get('medicine_name', 'Unknown Medicine')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Doses per day:** {schedule.get('doses_per_day', 0)}")
                    st.write(f"**Times:** {', '.join(schedule.get('times', []))}")
                
                with col2:
                    st.write(f"**Take:** {schedule.get('before_after_food', 'Not specified')}")
                    st.write(f"**Status:** {schedule.get('status', 'Unknown')}")
                
                if schedule.get('precaution'):
                    st.write(f"**Precautions:** {schedule.get('precaution')}")


class PatientAppointmentsPage(BasePage):
    """Patient appointments page"""
    
    def __init__(self, connected_patient_id: str, connection_status: str):
        super().__init__(connection_status)
        self.connected_patient_id = connected_patient_id
        self.appointment_repo = AppointmentRepository()
    
    def render_content(self) -> None:
        """Render patient appointments content"""
        st.title("📅 Patient Appointments")
        
        patient_appointments = self.appointment_repo.get_patient_appointments(self.connected_patient_id)
        
        if patient_appointments:
            st.success(f"Found {len(patient_appointments)} appointments for this patient")
            self._render_appointments(patient_appointments)
        else:
            st.info("📅 No appointments scheduled yet.")
    
    def _render_appointments(self, appointments: List[Dict[str, Any]]) -> None:
        """Render appointments list"""
        for apt in appointments:
            with st.expander(f"📅 Appointment - {apt.get('appointment_date', 'Unknown Date')}"):
                apt_info = [
                    ("Date", "appointment_date"),
                    ("Time", "appointment_time"),
                    ("Type", "type"),
                    ("Status", "status")
                ]
                
                for label, key in apt_info:
                    default_value = 'Not specified' if key != 'status' else 'Unknown'
                    st.write(f"**{label}:** {apt.get(key, default_value)}")
                
                if apt.get('notes'):
                    st.write(f"**Notes:** {apt.get('notes')}")


class MedicalRecordsPage(BasePage):
    """Medical records page"""
    
    def __init__(self, connected_patient_id: str, connection_status: str):
        super().__init__(connection_status)
        self.connected_patient_id = connected_patient_id
    
    def render_content(self) -> None:
        """Render medical records content"""
        st.title("📋 Medical Records")
        st.info("📋 Medical records feature coming soon.")


class GuardianDashboard:
    """Main guardian dashboard class"""
    
    def __init__(self):
        self.profile_repo = ProfileRepository()
        self.db_service = DatabaseService()
        self.ui_style = UIStyleManager()
        self._load_ui_styles()
    
    def _load_ui_styles(self) -> None:
        """Load UI styles"""
        self.ui_style.load_css()
    
    def _create_page_factory(self, guardian_profile: Dict[str, Any], connected_patient: Dict[str, Any], 
                           connected_patient_id: str, connection_status: str) -> Dict[str, BasePage]:
        """Factory method to create page instances"""
        return {
            "🏠 Dashboard Home": DashboardHomePage(
                guardian_profile, connected_patient, connected_patient_id, connection_status
            ),
            "👤 Patient Overview": PatientOverviewPage(
                connected_patient_id, connected_patient, connection_status
            ),
            "💊 Patient Medications": PatientMedicationsPage(
                connected_patient_id, connection_status
            ),
            "⏰ Medicine Reminders": MedicineRemindersPage(
                connected_patient_id, connection_status
            ),
            "📅 Appointments": PatientAppointmentsPage(
                connected_patient_id, connection_status
            ),
            "📋 Medical Records": MedicalRecordsPage(
                connected_patient_id, connection_status
            )
        }
    
    def render(self) -> None:
        """Main render method for the guardian dashboard"""
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("❌ You must be logged in to access the Guardian Dashboard.")
            return
        
        # Load user data
        guardian_profile = self.profile_repo.get_profile(user_id)
        connected_patient_id = self.profile_repo.get_connected_patient_id(user_id)
        connected_patient = self.profile_repo.get_profile(connected_patient_id) if connected_patient_id else {}
        connection_status = self.db_service.get_connection_status(user_id)
        
        # Render header
        header = HeaderComponent(guardian_profile.get('full_name', 'Guardian'))
        header.render()
        
        # Render sidebar navigation
        sidebar = SidebarComponent(guardian_profile, user_id)
        selected_page = sidebar.render()
        
        # Page routing
        pages = self._create_page_factory(guardian_profile, connected_patient, connected_patient_id, connection_status)
        
        if selected_page == "⚙️ Update Profile":
            from page.update_profile_page import update_profile_page
            update_profile_page(user_id)
        elif selected_page in pages:
            pages[selected_page].render()


# Main function to be called from your app
def guardian_dashboard():
    """Main entry point for guardian dashboard"""
    dashboard = GuardianDashboard()
    dashboard.render()
