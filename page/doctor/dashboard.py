import streamlit as st
import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.css import load_css
from page.navigation import logout
from config.constants import (
    USERS_FILE, PROFILES_FILE, APPOINTMENTS_FILE, DOCTOR_QUERIES_FILE, 
    PRESCRIPTIONS_FILE, MEDICAL_TESTS_FILE, PATIENT_DOCTOR_REQUESTS_FILE
)
from utils.file_ops import load_json, save_json
from page.update_profile_page import update_profile_page


@dataclass
class DoctorStats:
    """Data class for doctor dashboard statistics"""
    upcoming_appointments: int
    pending_queries: int
    connected_patients: int
    pending_requests: int


@dataclass
class NavigationItem:
    """Data class for navigation menu items"""
    icon: str
    label: str
    key: str = None
    
    def __post_init__(self):
        if self.key is None:
            self.key = self.label.lower().replace(' ', '_')


class BaseRepository:
    """Base repository class for data operations"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        return load_json(self.file_path)
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file"""
        save_json(self.file_path, data)
    
    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get single item by ID"""
        data = self.load_data()
        return data.get(item_id)
    
    def update_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific item"""
        data = self.load_data()
        if item_id in data:
            data[item_id].update(updates)
            self.save_data(data)
            return True
        return False


class AppointmentRepository(BaseRepository):
    """Repository for appointment operations"""
    
    def __init__(self):
        super().__init__(APPOINTMENTS_FILE)
    
    def get_doctor_appointments(self, doctor_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get appointments for a specific doctor"""
        appointments = self.load_data()
        result = [appt for appt in appointments.values() if appt.get("doctor_id") == doctor_id]
        
        if status:
            result = [appt for appt in result if appt.get("status") == status]
        
        return result
    
    def approve_appointment(self, appointment_id: str) -> bool:
        """Approve an appointment"""
        return self.update_item(appointment_id, {"status": "scheduled"})
    
    def decline_appointment(self, appointment_id: str) -> bool:
        """Decline an appointment"""
        return self.update_item(appointment_id, {"status": "cancelled"})


class PatientDoctorRequestRepository(BaseRepository):
    """Repository for patient-doctor connection requests"""
    
    def __init__(self):
        super().__init__(PATIENT_DOCTOR_REQUESTS_FILE)
    
    def get_doctor_requests(self, doctor_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get connection requests for a specific doctor"""
        requests = self.load_data()
        result = [req for req in requests.values() if req.get("doctor_id") == doctor_id]
        
        if status:
            result = [req for req in result if req.get("status") == status]
        
        return result
    
    def approve_request(self, request_id: str) -> bool:
        """Approve a connection request"""
        return self.update_item(request_id, {"status": "approved"})
    
    def deny_request(self, request_id: str) -> bool:
        """Deny a connection request"""
        return self.update_item(request_id, {"status": "denied"})


class DoctorQueryRepository(BaseRepository):
    """Repository for doctor query operations"""
    
    def __init__(self):
        super().__init__(DOCTOR_QUERIES_FILE)
    
    def get_doctor_queries(self, doctor_id: str, status: str = None) -> Dict[str, Dict[str, Any]]:
        """Get queries for a specific doctor"""
        queries = self.load_data()
        result = {qid: q for qid, q in queries.items() if q.get("doctor_id") == doctor_id}
        
        if status:
            result = {qid: q for qid, q in result.items() if q.get("status") == status}
        
        return result
    
    def respond_to_query(self, query_id: str, response: str) -> bool:
        """Respond to a patient query"""
        updates = {
            "doctor_response": response.strip(),
            "status": "answered",
            "responded_at": datetime.now().isoformat()
        }
        return self.update_item(query_id, updates)
    
    def mark_resolved(self, query_id: str) -> bool:
        """Mark query as resolved"""
        updates = {
            "status": "resolved",
            "resolved_at": datetime.now().isoformat()
        }
        return self.update_item(query_id, updates)


class ProfileRepository(BaseRepository):
    """Repository for profile operations"""
    
    def __init__(self):
        super().__init__(PROFILES_FILE)
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        return self.get_by_id(user_id) or {}


class PrescriptionRepository(BaseRepository):
    """Repository for prescription operations"""
    
    def __init__(self):
        super().__init__(PRESCRIPTIONS_FILE)
    
    def get_doctor_prescriptions(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get prescriptions for a specific doctor"""
        prescriptions = self.load_data()
        return [p for p in prescriptions.values() if p.get("doctor_id") == doctor_id]


class MedicalTestRepository(BaseRepository):
    """Repository for medical test operations"""
    
    def __init__(self):
        super().__init__(MEDICAL_TESTS_FILE)
    
    def get_doctor_tests(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get medical tests for a specific doctor"""
        tests = self.load_data()
        return [t for t in tests.values() if t.get("doctor_id") == doctor_id]


class DateTimeFormatter:
    """Utility class for datetime formatting"""
    
    @staticmethod
    def safe_format_datetime(date_val: Any) -> str:
        """Safely format datetime values - handles both string and datetime objects"""
        if not date_val:
            return 'Unknown'
        try:
            if isinstance(date_val, str):
                return date_val[:19]
            return date_val.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return 'Unknown'


class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def render(self) -> None:
        """Render the UI component"""
        pass


class NavigationSidebar(UIComponent):
    """Navigation sidebar component"""
    
    def __init__(self, doctor_profile: Dict[str, Any]):
        self.doctor_profile = doctor_profile
        self.nav_items = [
            NavigationItem("🏠", "Dashboard Home"),
            NavigationItem("🔗", "Connection Requests"),
            NavigationItem("👥", "Connected Patients"),
            NavigationItem("📅", "Appointment Requests"),
            NavigationItem("💬", "Patient Queries"),
            NavigationItem("📄", "Prescriptions"),
            NavigationItem("🧪", "Medical Tests"),
            NavigationItem("📝", "Update Profile"),
            NavigationItem("🚪", "Logout")
        ]
    
    def render(self) -> str:
        """Render sidebar and return selected page"""
        # Profile section
        st.sidebar.markdown('<div class="profile-container">', unsafe_allow_html=True)
        st.sidebar.markdown(
            f'<h3 class="profile-name">Dr. {self.doctor_profile.get("full_name", "Doctor")}</h3>', 
            unsafe_allow_html=True
        )
        
        profile_pic = self.doctor_profile.get("photo_path")
        if profile_pic and os.path.exists(profile_pic):
            st.sidebar.image(profile_pic, width=140)
        else:
            st.sidebar.info("📷 Upload profile photo in 'Update Profile'")
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation menu
        if "doctor_nav_page" not in st.session_state:
            st.session_state.doctor_nav_page = "Dashboard Home"
        
        selected_page = st.session_state.doctor_nav_page
        
        st.sidebar.markdown('<div class="nav-container">', unsafe_allow_html=True)
        for nav_item in self.nav_items:
            button_class = "nav-button-active" if selected_page == nav_item.label else "nav-button"
            if st.sidebar.button(f"{nav_item.icon} {nav_item.label}", key=nav_item.label):
                st.session_state.doctor_nav_page = nav_item.label
                st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        return selected_page


class StatsCardComponent(UIComponent):
    """Statistics cards component"""
    
    def __init__(self, stats: DoctorStats):
        self.stats = stats
    
    def render(self) -> None:
        """Render statistics cards"""
        stats_html = f"""
        <div class="doctor-stats-container">
            <div class="doctor-stat-card">
                <div class="stat-icon">📅</div>
                <div class="stat-number">{self.stats.upcoming_appointments}</div>
                <div class="stat-label">Scheduled Appointments</div>
            </div>
            <div class="doctor-stat-card">
                <div class="stat-icon">❓</div>
                <div class="stat-number">{self.stats.pending_queries}</div>
                <div class="stat-label">Pending Queries</div>
            </div>
            <div class="doctor-stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-number">{self.stats.connected_patients}</div>
                <div class="stat-label">Connected Patients</div>
            </div>
            <div class="doctor-stat-card">
                <div class="stat-icon">🔔</div>
                <div class="stat-number">{self.stats.pending_requests}</div>
                <div class="stat-label">Pending Requests</div>
            </div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)


class RequestCardComponent(UIComponent):
    """Reusable request card component"""
    
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content
    
    def render(self) -> None:
        """Render request card"""
        card_html = f"""
        <div class="request-card">
            <div class="request-header">{self.title}</div>
            <div class="request-details">{self.content}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)


class BasePage(ABC):
    """Abstract base class for dashboard pages"""
    
    def __init__(self, doctor_id: str):
        self.doctor_id = doctor_id
        self.profile_repo = ProfileRepository()
        self.datetime_formatter = DateTimeFormatter()
    
    @abstractmethod
    def render(self) -> None:
        """Render the page content"""
        pass
    
    def get_patient_name(self, patient_id: str) -> str:
        """Get patient name from profile"""
        profile = self.profile_repo.get_profile(patient_id)
        return profile.get('full_name', 'Unknown Patient')


class DashboardHomePage(BasePage):
    """Dashboard home page"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.appointment_repo = AppointmentRepository()
        self.query_repo = DoctorQueryRepository()
        self.request_repo = PatientDoctorRequestRepository()
    
    def _calculate_stats(self) -> DoctorStats:
        """Calculate dashboard statistics"""
        upcoming_appointments = len(self.appointment_repo.get_doctor_appointments(self.doctor_id, "scheduled"))
        pending_queries = len(self.query_repo.get_doctor_queries(self.doctor_id, "pending"))
        connected_patients = len(self.request_repo.get_doctor_requests(self.doctor_id, "approved"))
        pending_requests = len(self.request_repo.get_doctor_requests(self.doctor_id, "pending"))
        
        return DoctorStats(
            upcoming_appointments=upcoming_appointments,
            pending_queries=pending_queries,
            connected_patients=connected_patients,
            pending_requests=pending_requests
        )
    
    def render(self) -> None:
        """Render dashboard home page"""
        doctor_profile = self.profile_repo.get_profile(self.doctor_id)
        
        # Welcome header
        welcome_html = f"""
        <div class="doctor-welcome-header">
            <h1>Welcome, Dr. {doctor_profile.get('full_name', 'Doctor')}! 👨‍⚕️</h1>
            <p>Your medical practice dashboard - manage patients and appointments</p>
        </div>
        """
        st.markdown(welcome_html, unsafe_allow_html=True)
        
        # Statistics cards
        stats = self._calculate_stats()
        stats_component = StatsCardComponent(stats)
        stats_component.render()
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        quick_actions = [
            ("🔗 View Connection Requests", "Connection Requests", "quick_connections"),
            ("💬 Answer Patient Queries", "Patient Queries", "quick_queries"),
            ("📅 Manage Appointments", "Appointment Requests", "quick_appointments")
        ]
        
        for i, (label, page, key) in enumerate(quick_actions):
            with [col1, col2, col3][i]:
                if st.button(label, key=key):
                    st.session_state.doctor_nav_page = page
                    st.rerun()


class ConnectionRequestsPage(BasePage):
    """Connection requests page"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.request_repo = PatientDoctorRequestRepository()
    
    def render(self) -> None:
        """Render connection requests page"""
        st.title("🔗 Patient Connection Requests")
        
        requests = self.request_repo.get_doctor_requests(self.doctor_id, "pending")
        st.write(f"**Pending requests for this doctor:** {len(requests)}")
        
        if not requests:
            st.info("No pending connection requests.")
            return
        
        for req in requests:
            patient_profile = self.profile_repo.get_profile(req.get("patient_id"))
            
            content = f"""
            <strong>Patient ID:</strong> {req.get('patient_id')}<br>
            <strong>Request Date:</strong> {self.datetime_formatter.safe_format_datetime(req.get('requested_at', 'Unknown'))}<br>
            <strong>Blood Group:</strong> {patient_profile.get('blood_group', 'Not specified')}<br>
            <strong>Age:</strong> {patient_profile.get('dob', 'Not specified')}
            """
            
            card = RequestCardComponent(
                f"👤 {patient_profile.get('full_name', 'Unknown Patient')}", 
                content
            )
            card.render()
            
            col1, col2 = st.columns(2)
            if col1.button("✅ Accept", key=f"accept_{req['request_id']}"):
                if self.request_repo.approve_request(req['request_id']):
                    st.success("Connection approved!")
                    st.rerun()
            
            if col2.button("❌ Deny", key=f"deny_{req['request_id']}"):
                if self.request_repo.deny_request(req['request_id']):
                    st.warning("Connection denied.")
                    st.rerun()


class ConnectedPatientsPage(BasePage):
    """Connected patients page"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.request_repo = PatientDoctorRequestRepository()
    
    def render(self) -> None:
        """Render connected patients page"""
        st.title("👥 Connected Patients")
        
        connected_requests = self.request_repo.get_doctor_requests(self.doctor_id, "approved")
        st.write(f"**Total Connected Patients:** {len(connected_requests)}")
        
        if not connected_requests:
            st.info("No patients connected yet. Approve connection requests to see patients here.")
            return
        
        for req in connected_requests:
            patient_profile = self.profile_repo.get_profile(req.get("patient_id"))
            
            content = f"""
            <strong>📧 Email:</strong> {patient_profile.get('email', 'Not provided')}<br>
            <strong>📱 Mobile:</strong> {patient_profile.get('mobile', 'Not provided')}<br>
            <strong>🩸 Blood Group:</strong> {patient_profile.get('blood_group', 'Not provided')}<br>
            <strong>🎂 Age:</strong> {patient_profile.get('dob', 'Not provided')}<br>
            <strong>🔗 Connected on:</strong> {self.datetime_formatter.safe_format_datetime(req.get('requested_at', 'Unknown'))}
            """
            
            card = RequestCardComponent(
                f"👤 {patient_profile.get('full_name', 'Unknown Patient')}", 
                content
            )
            card.render()
            
            col1, col2, col3 = st.columns(3)
            actions = [
                ("📋 View Medical History", f"history_{req.get('patient_id')}"),
                ("💬 Send Message", f"message_{req.get('patient_id')}"),
                ("📅 Schedule Appointment", f"schedule_{req.get('patient_id')}")
            ]
            
            for i, (label, key) in enumerate(actions):
                with [col1, col2, col3][i]:
                    if st.button(label, key=key):
                        st.info(f"{label.split(' ', 1)[1]} feature coming soon!")


class AppointmentRequestsPage(BasePage):
    """Appointment requests page"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.appointment_repo = AppointmentRepository()
    
    def render(self) -> None:
        """Render appointment requests page"""
        st.title("📅 Appointment Requests")
        
        requests = self.appointment_repo.get_doctor_appointments(self.doctor_id, "requested")
        st.write(f"**Requested appointments:** {len(requests)}")
        
        if not requests:
            st.info("No appointment requests found.")
            return
        
        for appt in requests:
            patient_name = self.get_patient_name(appt.get("patient_id"))
            
            content = f"""
            <strong>Patient:</strong> {patient_name}<br>
            <strong>Date:</strong> {appt.get('appointment_date')}<br>
            <strong>Time:</strong> {appt.get('appointment_time')}<br>
            <strong>Type:</strong> {appt.get('type')}<br>
            <strong>Notes:</strong> {appt.get('notes', 'No notes')}
            """
            
            card = RequestCardComponent(
                f"📅 Appointment Request from {patient_name}", 
                content
            )
            card.render()
            
            col1, col2 = st.columns(2)
            if col1.button("✅ Approve", key=f"approve_{appt['appointment_id']}"):
                if self.appointment_repo.approve_appointment(appt['appointment_id']):
                    st.success("Appointment approved!")
                    st.rerun()
            
            if col2.button("❌ Decline", key=f"decline_{appt['appointment_id']}"):
                if self.appointment_repo.decline_appointment(appt['appointment_id']):
                    st.warning("Appointment declined.")
                    st.rerun()


class PatientQueriesPage(BasePage):
    """Patient queries page"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.query_repo = DoctorQueryRepository()
    
    def render(self) -> None:
        """Render patient queries page"""
        st.title("💬 Respond to Patient Queries")
        
        my_queries = self.query_repo.get_doctor_queries(self.doctor_id, "pending")
        
        if not my_queries:
            st.info("📭 No pending patient queries at the moment.")
            return
        
        st.write(f"**📋 You have {len(my_queries)} pending queries**")
        
        for qid, q in my_queries.items():
            patient_profile = self.profile_repo.get_profile(q.get("patient_id"))
            patient_name = patient_profile.get("full_name", "Unknown Patient")
            patient_mobile = patient_profile.get("mobile", "Not provided")
            
            content = f"""
            <strong>From Patient:</strong> {patient_name} ({q.get("patient_id")})<br>
            <strong>Mobile:</strong> {patient_mobile}<br>
            <strong>Question:</strong> {q.get('question')}<br>
            <strong>Submitted:</strong> {self.datetime_formatter.safe_format_datetime(q.get('submitted_at', 'Unknown time'))}
            """
            
            card = RequestCardComponent("💬 Patient Query", content)
            card.render()
            
            # Response form
            with st.form(f"response_form_{qid}"):
                response = st.text_area(
                    f"Your Response to {patient_name}:", 
                    key=f"resp_{qid}", 
                    height=120, 
                    placeholder=f"Type your professional response to {patient_name} here..."
                )
                
                col1, col2 = st.columns(2)
                submitted = col1.form_submit_button("📤 Send Response", type="primary")
                mark_resolved = col2.form_submit_button("✅ Mark as Resolved")
                
                if submitted and response.strip():
                    if self.query_repo.respond_to_query(qid, response):
                        st.success(f"✅ Response sent to {patient_name}!")
                        st.balloons()
                        st.rerun()
                elif submitted and not response.strip():
                    st.error("❌ Please enter a response before submitting.")
                
                if mark_resolved:
                    if self.query_repo.mark_resolved(qid):
                        st.success(f"✅ Query from {patient_name} marked as resolved!")
                        st.rerun()
            
            st.markdown("---")


class PrescriptionsPage(BasePage):
    """Prescriptions page"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.prescription_repo = PrescriptionRepository()
    
    def render(self) -> None:
        """Render prescriptions page"""
        st.title("📄 My Prescriptions")
        
        my_prescriptions = self.prescription_repo.get_doctor_prescriptions(self.doctor_id)
        
        if not my_prescriptions:
            st.info("No prescriptions found.")
            return
        
        for pres in my_prescriptions:
            patient_name = self.get_patient_name(pres.get('patient_id'))
            
            content = f"""
            <strong>Patient:</strong> {patient_name} ({pres.get('patient_id')})<br>
            <strong>Notes:</strong> {pres.get('notes', 'No notes')[:200]}...
            """
            
            card = RequestCardComponent(f"📄 Prescription for {patient_name}", content)
            card.render()


class MedicalTestsPage(BasePage):
    """Medical tests page"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.test_repo = MedicalTestRepository()
    
    def render(self) -> None:
        """Render medical tests page"""
        st.title("🧪 Ordered Medical Tests")
        
        my_tests = self.test_repo.get_doctor_tests(self.doctor_id)
        
        if not my_tests:
            st.info("No test orders found.")
            return
        
        for test in my_tests:
            patient_name = self.get_patient_name(test.get('patient_id'))
            
            content = f"""
            <strong>Patient:</strong> {patient_name} ({test.get('patient_id')})<br>
            <strong>Test Type:</strong> {test.get('test_type')}<br>
            <strong>Notes:</strong> {test.get('notes', 'N/A')}<br>
            <strong>📆 Ordered on:</strong> {self.datetime_formatter.safe_format_datetime(test.get('ordered_at', 'N/A'))}
            """
            
            card = RequestCardComponent(f"🧪 Medical Test for {patient_name}", content)
            card.render()


class DoctorDashboard:
    """Main doctor dashboard class"""
    
    def __init__(self):
        self.profile_repo = ProfileRepository()
        self._load_css()
    
    def _load_css(self) -> None:
        """Load CSS styles"""
        load_css()
        
        # Enhanced CSS with orange theme - compressed
        css_styles = """<style>
        .main .block-container{padding-top:1rem;padding-bottom:1rem;max-width:none;transition:margin-left 0.3s ease,margin-right 0.3s ease,max-width 0.3s ease}
        [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container{margin-left:auto;margin-right:auto;max-width:1400px;padding-left:3rem;padding-right:3rem}
        @media (max-width:768px){.main .block-container,[data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container{padding-left:1rem;padding-right:1rem;max-width:none}}
        .stApp{background:#9AC77D;animation:none!important}
        .profile-name{color:white;font-weight:700;margin-bottom:10px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
        .nav-container{margin-top:20px}
        .nav-button{background:rgba(255,255,255,0.1)!important;color:white!important;border:1px solid rgba(255,255,255,0.2)!important;border-radius:10px!important;margin:5px 0!important;padding:12px 16px!important;width:100%!important;text-align:left!important;transition:all 0.3s ease!important;backdrop-filter:blur(10px)!important}
        .nav-button:hover{background:rgba(255,255,255,0.2)!important;transform:translateX(5px)!important;box-shadow:0 4px 15px rgba(0,0,0,0.2)!important}
        .nav-button-active{background:rgba(255,255,255,0.3)!important;color:white!important;border:1px solid rgba(255,255,255,0.4)!important;transform:translateX(10px)!important;box-shadow:0 6px 20px rgba(0,0,0,0.3)!important}
        .doctor-welcome-header{text-align:center;background:linear-gradient(135deg,#FF8A65,#FF7043);padding:2rem;border-radius:15px;color:white;box-shadow:0 10px 30px rgba(255,138,101,0.3);margin-bottom:2rem;animation:slideInDown 1s ease-out}
        .doctor-welcome-header h1{margin:0;font-size:2.2rem;font-weight:700;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}
        .doctor-welcome-header p{margin:10px 0 0 0;font-size:1.1rem;opacity:0.9}
        .doctor-stats-container{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:2rem 0}
        .doctor-stat-card{background:linear-gradient(135deg,#FF8A65,#FF7043);border-radius:15px;padding:1.5rem;color:white;text-align:center;box-shadow:0 10px 20px rgba(255,138,101,0.2);transition:transform 0.3s ease,box-shadow 0.3s ease;animation:fadeInUp 0.8s ease-out}
        .doctor-stat-card:hover{transform:translateY(-5px) scale(1.02);box-shadow:0 15px 30px rgba(255,138,101,0.3)}
        .stat-icon{font-size:2.5rem;margin-bottom:0.5rem}
        .stat-number{font-size:2rem;font-weight:bold;margin-bottom:0.5rem}
        .stat-label{font-size:0.9rem;opacity:0.9}
        .request-card{background:rgba(255,255,255,0.9);border-radius:15px;padding:1.5rem;margin:1rem 0;box-shadow:0 5px 15px rgba(0,0,0,0.1);border-left:4px solid #FF8C00;transition:all 0.3s ease;animation:slideInLeft 0.8s ease-out}
        .request-card:hover{transform:translateY(-3px);box-shadow:0 8px 25px rgba(0,0,0,0.15)}
        .request-header{font-size:1.2rem;font-weight:bold;color:#FF7043;margin-bottom:1rem}
        .request-details{color:#666;margin-bottom:1rem;line-height:1.5}
        .stButton>button{background:linear-gradient(135deg,#FF8C00,#FFA500)!important;color:white!important;border:none!important;border-radius:10px!important;padding:12px 24px!important;font-weight:600!important;transition:all 0.3s ease!important;box-shadow:0 4px 15px rgba(255,140,0,0.2)!important}
        .stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(255,140,0,0.3)!important}
        .stSelectbox>div>div,.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:rgba(255,255,255,0.9)!important;border-radius:10px!important;border:1px solid rgba(255,140,0,0.2)!important}
        .stExpander>div>div>div{background:rgba(255,255,255,0.95)!important;border-radius:10px!important;border:1px solid rgba(255,140,0,0.1)!important}
        .stAlert{border-radius:10px!important;border-left:4px solid #FF8C00!important}
        .debug-section{background:rgba(255,235,180,0.3);padding:1rem;border-radius:10px;margin:1rem 0;border:1px solid rgba(255,140,0,0.2)}
        .element-container{animation:slideInLeft 0.6s ease-out}
        @keyframes fadeInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
        @keyframes slideInDown{from{opacity:0;transform:translateY(-30px)}to{opacity:1;transform:translateY(0)}}
        @keyframes slideInLeft{from{opacity:0;transform:translateX(-30px)}to{opacity:1;transform:translateX(0)}}
        @media (max-width:768px){.doctor-stats-container{grid-template-columns:1fr}.main-content{margin:10px;padding:20px}.doctor-welcome-header h1{font-size:1.8rem}}
        </style>"""
        
        st.markdown(css_styles, unsafe_allow_html=True)
    
    def _create_page_factory(self, doctor_id: str) -> Dict[str, BasePage]:
        """Factory method to create page instances"""
        return {
            "Dashboard Home": DashboardHomePage(doctor_id),
            "Connection Requests": ConnectionRequestsPage(doctor_id),
            "Connected Patients": ConnectedPatientsPage(doctor_id),
            "Appointment Requests": AppointmentRequestsPage(doctor_id),
            "Patient Queries": PatientQueriesPage(doctor_id),
            "Prescriptions": PrescriptionsPage(doctor_id),
            "Medical Tests": MedicalTestsPage(doctor_id)
        }
    
    def render(self) -> None:
        """Main render method for the dashboard"""
        doctor_id = st.session_state.get("user_id")
        if not doctor_id:
            st.error("You are not logged in.")
            return
        
        doctor_profile = self.profile_repo.get_profile(doctor_id)
        
        # Render sidebar navigation
        sidebar = NavigationSidebar(doctor_profile)
        selected_page = sidebar.render()
        
        # Main content area
        col1, main_content, col3 = st.columns([0.5, 10, 0.5])
        
        with main_content:
            st.markdown('<div class="main-content">', unsafe_allow_html=True)
            
            # Page routing using factory pattern
            pages = self._create_page_factory(doctor_id)
            
            if selected_page == "Update Profile":
                update_profile_page(doctor_id)
            elif selected_page == "Logout":
                logout()
            elif selected_page in pages:
                pages[selected_page].render()
            
            st.markdown('</div>', unsafe_allow_html=True)


# Main function to be called from your app
def doctor_dashboard():
    """Main entry point for doctor dashboard"""
    dashboard = DoctorDashboard()
    dashboard.render()
