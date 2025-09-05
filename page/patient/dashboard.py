import streamlit as st
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

from utils.css import load_css
from page.navigation import logout
from config.constants import (
    PROFILES_FILE, MEDICINES_FILE, SCHEDULES_FILE, PRESCRIPTIONS_FILE, 
    MEDICAL_TESTS_FILE, DOCTOR_QUERIES_FILE, GUARDIAN_REQUESTS_FILE, 
    APPOINTMENTS_FILE, PATIENT_DOCTOR_REQUESTS_FILE
)
from utils.file_ops import load_json
from page.patient.medicines import medicine_manager
from page.patient.reminders import medicine_reminder_page
from page.patient.prescriptions import prescriptions_page
from page.patient.medical_tests import medical_tests_page
from page.patient.appointments import ask_questions_and_appointments
from page.patient.adherence import adherence_history
from page.patient.guardians import manage_guardians
from page.update_profile_page import update_profile_page
from page.patient.connect_doctors import connect_doctors_page


@dataclass
class PatientMetrics:
    """Data class for patient dashboard metrics"""
    total_medicines: int
    active_reminders: int
    appointments: int
    profile_completion: int


@dataclass
class NavigationItem:
    """Data class for navigation menu items"""
    icon: str
    label: str
    
    def get_button_text(self) -> str:
        """Get formatted button text"""
        return f"{self.icon} {self.label}"


@dataclass
class QuickActionCard:
    """Data class for quick action cards"""
    icon: str
    title: str
    description: str
    
    def get_html(self) -> str:
        """Get HTML representation of the card"""
        return f"""
        <div style='background:linear-gradient(135deg,#FF8A65,#FF7043);border-radius:15px;padding:20px;color:white;box-shadow:0 10px 20px rgba(255,138,101,0.3);text-align:center;margin:10px 0;'>
            <div style='font-size:3rem;margin-bottom:10px;'>{self.icon}</div>
            <h3 style='margin:10px 0 5px 0;font-size:1.2rem;'>{self.title}</h3>
            <p style='font-size:0.9rem;opacity:0.9;line-height:1.4;'>{self.description}</p>
        </div>
        """


class DateTimeFormatter:
    """Utility class for date formatting"""
    
    @staticmethod
    def safe_date_format(dt: Any) -> str:
        """Safely format date values"""
        if dt is None:
            return 'Unknown'
        if isinstance(dt, str):
            return dt[:10]
        if isinstance(dt, (datetime, date)):
            return dt.strftime('%Y-%m-%d')
        return str(dt)


class BaseRepository:
    """Base repository class"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from file"""
        return load_json(self.file_path)


class ProfileRepository(BaseRepository):
    """Repository for profile operations"""
    
    def __init__(self):
        super().__init__(PROFILES_FILE)
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        profiles = self.load_data()
        return profiles.get(user_id, {})


class MedicineRepository(BaseRepository):
    """Repository for medicine operations"""
    
    def __init__(self):
        super().__init__(MEDICINES_FILE)
    
    def get_patient_medicines(self, patient_id: str) -> Dict[str, Dict[str, Any]]:
        """Get medicines for specific patient"""
        medicines = self.load_data()
        return {k: v for k, v in medicines.items() if v.get("patient_id") == patient_id}


class ScheduleRepository(BaseRepository):
    """Repository for schedule operations"""
    
    def __init__(self):
        super().__init__(SCHEDULES_FILE)
    
    def get_patient_schedules(self, patient_id: str) -> Dict[str, Dict[str, Any]]:
        """Get schedules for specific patient"""
        schedules = self.load_data()
        return {k: v for k, v in schedules.items() if v.get("patient_id") == patient_id}


class AppointmentRepository(BaseRepository):
    """Repository for appointment operations"""
    
    def __init__(self):
        super().__init__(APPOINTMENTS_FILE)
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get appointments for specific patient"""
        appointments = self.load_data()
        return [a for a in appointments.values() if a.get("patient_id") == patient_id]


class ConnectionRepository(BaseRepository):
    """Repository for doctor connection operations"""
    
    def __init__(self):
        super().__init__(PATIENT_DOCTOR_REQUESTS_FILE)
    
    def get_connected_doctors(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get connected doctors for patient"""
        requests = self.load_data()
        return [
            req for req in requests.values() 
            if req.get("patient_id") == patient_id and req.get("status") == "approved"
        ]


class PatientDataService:
    """Service class for patient data operations"""
    
    def __init__(self):
        self.profile_repo = ProfileRepository()
        self.medicine_repo = MedicineRepository()
        self.schedule_repo = ScheduleRepository()
        self.appointment_repo = AppointmentRepository()
        self.connection_repo = ConnectionRepository()
        self.datetime_formatter = DateTimeFormatter()
    
    def get_patient_metrics(self, patient_id: str) -> PatientMetrics:
        """Get comprehensive patient metrics"""
        profile = self.profile_repo.get_profile(patient_id)
        medicines = self.medicine_repo.get_patient_medicines(patient_id)
        schedules = self.schedule_repo.get_patient_schedules(patient_id)
        appointments = self.appointment_repo.get_patient_appointments(patient_id)
        
        return PatientMetrics(
            total_medicines=len(medicines),
            active_reminders=len(schedules),
            appointments=len(appointments),
            profile_completion=profile.get('profile_completion', 0)
        )
    
    def get_recent_activities(self, patient_id: str) -> List[str]:
        """Get recent patient activities"""
        activities = []
        
        try:
            # Recent medicines
            medicines = self.medicine_repo.get_patient_medicines(patient_id)
            sorted_medicines = sorted(
                medicines.items(), 
                key=lambda x: x[1].get('created_at', ''), 
                reverse=True
            )[:3]
            
            for med_id, med in sorted_medicines:
                created_at = self.datetime_formatter.safe_date_format(med.get('created_at'))
                activities.append(f"💊 Added medicine: {med.get('name', 'Unknown')} ({created_at})")
        except Exception:
            pass
        
        try:
            # Recent appointments
            appointments = self.appointment_repo.get_patient_appointments(patient_id)
            sorted_appointments = sorted(
                appointments, 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )[:2]
            
            for apt in sorted_appointments:
                created_at = self.datetime_formatter.safe_date_format(apt.get('created_at'))
                appointment_date = self.datetime_formatter.safe_date_format(apt.get('appointment_date'))
                activities.append(f"📅 Appointment scheduled for {appointment_date} ({created_at})")
        except Exception:
            pass
        
        return activities
    
    def get_latest_appointment_info(self, patient_id: str) -> Optional[str]:
        """Get latest appointment information"""
        appointments = self.appointment_repo.get_patient_appointments(patient_id)
        if not appointments:
            return None
        
        try:
            recent_appointment = max(appointments, key=lambda x: x.get('created_at', ''))
            appointment_date = self.datetime_formatter.safe_date_format(
                recent_appointment.get('appointment_date')
            )
            return f"📅 Latest appointment: {appointment_date}"
        except Exception:
            return None


class UIStyleManager:
    """Manages UI styles and CSS"""
    
    @staticmethod
    def load_dashboard_styles() -> None:
        """Load dashboard-specific CSS styles"""
        load_css()
        
        css_styles = """<style>
        .main .block-container{padding-top:1rem;padding-bottom:1rem;max-width:none;transition:margin-left 0.3s ease,margin-right 0.3s ease,max-width 0.3s ease}
        [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container{margin-left:auto;margin-right:auto;max-width:1400px;padding-left:3rem;padding-right:3rem}
        @media (max-width:768px){.main .block-container,[data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container{padding-left:1rem;padding-right:1rem;max-width:none}}
        .stApp{background:#CFEBAE;animation:none!important}
        .profile-name{color:white;font-weight:700;margin-bottom:10px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
        .nav-container{margin-top:20px}
        .stButton>button{background:linear-gradient(135deg,#FF8C00,#FFA500)!important;color:white!important;border:none!important;border-radius:10px!important;padding:12px 24px!important;font-weight:600!important;transition:all 0.3s ease!important;box-shadow:0 4px 15px rgba(255,140,0,0.2)!important}
        .stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(255,140,0,0.3)!important}
        .dashboard-home-container{background:linear-gradient(135deg,#FFE5B4 0%,#FFCC80 100%);padding:20px;border-radius:15px;margin:-30px -30px 20px -30px}
        .welcome-header{text-align:center;margin-bottom:30px;padding:20px;background:linear-gradient(135deg,#FF8A65,#FF7043);border-radius:15px;color:white;box-shadow:0 10px 30px rgba(255,138,101,0.3)}
        .welcome-header h1{margin:0;font-size:2rem;font-weight:700}
        .welcome-header p{margin:10px 0 0 0;font-size:1.1rem;opacity:0.9}
        </style>"""
        
        st.markdown(css_styles, unsafe_allow_html=True)


class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def render(self) -> None:
        """Render the component"""
        pass


class ProfileSidebarComponent(UIComponent):
    """Component for profile sidebar"""
    
    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile
    
    def render(self) -> None:
        """Render profile sidebar"""
        st.sidebar.markdown('<div class="profile-container">', unsafe_allow_html=True)
        st.sidebar.markdown(
            f'<h3 class="profile-name">Welcome, {self.profile.get("full_name", "Patient")}</h3>', 
            unsafe_allow_html=True
        )
        
        profile_pic = self.profile.get("photo_path")
        if profile_pic and os.path.exists(profile_pic):
            st.sidebar.image(profile_pic, width=120)
        else:
            st.sidebar.info("📷 Upload profile photo in 'Update Profile'")
        
        st.sidebar.markdown('</div>', unsafe_allow_html=True)


class NavigationSidebarComponent(UIComponent):
    """Component for navigation sidebar"""
    
    def __init__(self):
        self.nav_items = [
            NavigationItem("🏠", "Dashboard Home"),
            NavigationItem("💊", "Add Medicine"),
            NavigationItem("⏰", "Medicine Reminder"),
            NavigationItem("📄", "Prescriptions"),
            NavigationItem("🩺", "Medical Tests"),
            NavigationItem("🔗", "Search Doctors"),
            NavigationItem("👥", "Connected Doctors"),
            NavigationItem("💬", "Ask Doctor / Appointments"),
            NavigationItem("📊", "Adherence History"),
            NavigationItem("🛡️", "Guardians"),
            NavigationItem("📝", "Update Profile"),
            NavigationItem("🚪", "Logout")
        ]
    
    def render(self) -> str:
        """Render navigation sidebar and return selected page"""
        if "patient_nav_page" not in st.session_state:
            st.session_state.patient_nav_page = "Dashboard Home"
        
        selected_page = st.session_state.patient_nav_page
        
        st.sidebar.markdown('<div class="nav-container">', unsafe_allow_html=True)
        for nav_item in self.nav_items:
            if st.sidebar.button(nav_item.get_button_text(), key=nav_item.label):
                st.session_state.patient_nav_page = nav_item.label
                st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        return selected_page


class WelcomeHeaderComponent(UIComponent):
    """Component for dashboard welcome header"""
    
    def __init__(self, patient_name: str):
        self.patient_name = patient_name
    
    def render(self) -> None:
        """Render welcome header"""
        header_html = f"""
        <div class="welcome-header">
            <h1>Welcome back, {self.patient_name}! 👋</h1>
            <p>Here's your health summary for today</p>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)


class MetricsCardsComponent(UIComponent):
    """Component for dashboard metrics cards"""
    
    def __init__(self, metrics: PatientMetrics):
        self.metrics = metrics
    
    def render(self) -> None:
        """Render metrics cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_data = [
            ("💊 Total Medicines", self.metrics.total_medicines),
            ("⏰ Active Reminders", self.metrics.active_reminders),
            ("📅 Appointments", self.metrics.appointments),
            ("📊 Profile Complete", f"{self.metrics.profile_completion}%")
        ]
        
        columns = [col1, col2, col3, col4]
        
        for i, (label, value) in enumerate(metrics_data):
            with columns[i]:
                st.metric(label, value)


class QuickActionsComponent(UIComponent):
    """Component for quick actions section"""
    
    def __init__(self):
        self.quick_actions = [
            QuickActionCard("💊", "Medicine Manager", "Add, track, and organize your medications"),
            QuickActionCard("⏰", "Smart Reminders", "Never miss a dose with intelligent alerts"),
            QuickActionCard("👨‍⚕️", "Doctor Connect", "Connect with healthcare professionals")
        ]
    
    def render(self) -> None:
        """Render quick actions"""
        st.subheader("🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        for i, action in enumerate(self.quick_actions):
            with columns[i]:
                st.markdown(action.get_html(), unsafe_allow_html=True)


class RecentActivityComponent(UIComponent):
    """Component for recent activity section"""
    
    def __init__(self, activities: List[str], schedules: Dict[str, Any], 
                 appointments: List[Dict[str, Any]], latest_appointment_info: Optional[str]):
        self.activities = activities
        self.schedules = schedules
        self.appointments = appointments
        self.latest_appointment_info = latest_appointment_info
    
    def render(self) -> None:
        """Render recent activity section"""
        st.subheader("📋 Recent Activity")
        
        if self.activities:
            for activity in self.activities:
                st.write(f"• {activity}")
        else:
            st.info("No recent activities found. Start by adding your first medicine!")
        
        # Status messages
        if self.schedules:
            st.success("✅ You have active medicine reminders set up!")
        else:
            st.warning("⚠️ No medicine reminders set. Click 'Medicine Reminder' to get started.")
        
        if self.latest_appointment_info:
            st.info(self.latest_appointment_info)
        else:
            st.info("📅 No appointments yet. Connect with doctors to schedule appointments!")


class ConnectedDoctorsPage:
    """Page class for connected doctors"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.profile_repo = ProfileRepository()
        self.connection_repo = ConnectionRepository()
    
    def render(self) -> None:
        """Render connected doctors page"""
        st.title("👥 Connected Doctors")
        
        profiles = self.profile_repo.load_data()
        connected_requests = self.connection_repo.get_connected_doctors(self.user_id)
        
        if not connected_requests:
            st.info("No doctors connected yet. Go to 'Search Doctors' to connect with doctors.")
            return
        
        st.write(f"**Total Connected Doctors:** {len(connected_requests)}")
        
        for req in connected_requests:
            doctor_id = req.get("doctor_id")
            doctor_profile = profiles.get(doctor_id, {})
            
            with st.expander(f"Dr. {doctor_profile.get('full_name', 'Unknown Doctor')}"):
                self._render_doctor_info(doctor_profile, doctor_id)
    
    def _render_doctor_info(self, doctor_profile: Dict[str, Any], doctor_id: str) -> None:
        """Render individual doctor information"""
        col1, col2 = st.columns(2)
        
        doctor_info_left = [
            ("Specialization", doctor_profile.get('specialization', 'General')),
            ("Experience", f"{doctor_profile.get('experience', 'N/A')} years"),
            ("Hospital", doctor_profile.get('hospital_clinic', 'Not provided'))
        ]
        
        doctor_info_right = [
            ("Consultation Fee", f"₹{doctor_profile.get('consultation_fee', 'N/A')}"),
            ("Email", doctor_profile.get('email', 'Not provided')),
            ("Mobile", doctor_profile.get('mobile', 'Not provided'))
        ]
        
        with col1:
            for label, value in doctor_info_left:
                st.write(f"**{label}:** {value}")
        
        with col2:
            for label, value in doctor_info_right:
                st.write(f"**{label}:** {value}")
        
        if st.button(f"💬 Message Dr. {doctor_profile.get('full_name', 'Doctor')}", key=f"msg_{doctor_id}"):
            st.session_state.patient_nav_page = "Ask Doctor / Appointments"
            st.rerun()


class DashboardHomePage:
    """Page class for dashboard home"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.data_service = PatientDataService()
    
    def render(self) -> None:
        """Render dashboard home page"""
        profile = self.data_service.profile_repo.get_profile(self.user_id)
        
        # Welcome header
        welcome_header = WelcomeHeaderComponent(profile.get('full_name', 'Patient'))
        welcome_header.render()
        
        # Metrics cards
        metrics = self.data_service.get_patient_metrics(self.user_id)
        metrics_component = MetricsCardsComponent(metrics)
        metrics_component.render()
        
        # Quick actions
        quick_actions = QuickActionsComponent()
        quick_actions.render()
        
        # Recent activity
        activities = self.data_service.get_recent_activities(self.user_id)
        schedules = self.data_service.schedule_repo.get_patient_schedules(self.user_id)
        appointments = self.data_service.appointment_repo.get_patient_appointments(self.user_id)
        latest_appointment_info = self.data_service.get_latest_appointment_info(self.user_id)
        
        activity_component = RecentActivityComponent(
            activities, schedules, appointments, latest_appointment_info
        )
        activity_component.render()


class PatientDashboard:
    """Main patient dashboard class"""
    
    def __init__(self):
        self.profile_repo = ProfileRepository()
        self.ui_style = UIStyleManager()
        self._load_styles()
    
    def _load_styles(self) -> None:
        """Load dashboard styles"""
        self.ui_style.load_dashboard_styles()
    
    def _create_page_factory(self, user_id: str) -> Dict[str, callable]:
        """Factory method to create page instances"""
        return {
            "Dashboard Home": lambda: DashboardHomePage(user_id).render(),
            "Add Medicine": lambda: medicine_manager(user_id),
            "Medicine Reminder": lambda: medicine_reminder_page(user_id),
            "Prescriptions": lambda: prescriptions_page(user_id),
            "Medical Tests": lambda: medical_tests_page(user_id),
            "Search Doctors": lambda: connect_doctors_page(user_id),
            "Connected Doctors": lambda: ConnectedDoctorsPage(user_id).render(),
            "Ask Doctor / Appointments": lambda: ask_questions_and_appointments(user_id),
            "Adherence History": lambda: adherence_history(user_id),
            "Guardians": lambda: manage_guardians(user_id),
            "Update Profile": lambda: update_profile_page(user_id),
            "Logout": logout
        }
    
    def render(self) -> None:
        """Main render method for the dashboard"""
        user_id = st.session_state.user_id
        profile = self.profile_repo.get_profile(user_id)
        
        # Render profile sidebar
        profile_sidebar = ProfileSidebarComponent(profile)
        profile_sidebar.render()
        
        # Render navigation sidebar
        nav_sidebar = NavigationSidebarComponent()
        selected_page = nav_sidebar.render()
        
        # Main content area
        col1, main_content, col3 = st.columns([0.5, 10, 0.5])
        
        with main_content:
            st.markdown('<div class="main-content">', unsafe_allow_html=True)
            
            # Page routing using factory pattern
            pages = self._create_page_factory(user_id)
            
            if selected_page in pages:
                pages[selected_page]()
            
            st.markdown('</div>', unsafe_allow_html=True)


def patient_dashboard():
    """Main entry point for patient dashboard"""
    dashboard = PatientDashboard()
    dashboard.render()
