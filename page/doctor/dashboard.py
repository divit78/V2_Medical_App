import streamlit as st
import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.css import load_css
from page.navigation import logout
from utils.db_helper import db
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
    """Base repository class for database operations"""
    
    def __init__(self):
        self.db = db
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from database - override in subclasses"""
        return {}
    
    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get single item by ID - override in subclasses"""
        return None
    
    def update_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific item - override in subclasses"""
        return False


class AppointmentRepository(BaseRepository):
    """Repository for appointment operations using MySQL"""
    
    def get_doctor_appointments(self, doctor_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get appointments for a specific doctor"""
        try:
            self.db.connect()
            if status:
                query = "SELECT * FROM appointments WHERE doctor_id = %s AND status = %s ORDER BY appointment_date DESC"
                result = self.db.execute_query(query, (doctor_id, status))
            else:
                query = "SELECT * FROM appointments WHERE doctor_id = %s ORDER BY appointment_date DESC"
                result = self.db.execute_query(query, (doctor_id,))
            return result or []
        except Exception as e:
            st.error(f"Error loading appointments: {str(e)}")
            return []
    
    def approve_appointment(self, appointment_id: str) -> bool:
        """Approve an appointment - changes status to 'scheduled'"""
        try:
            self.db.connect()
            query = "UPDATE appointments SET status = %s WHERE appointment_id = %s"
            result = self.db.execute_query(query, ("scheduled", appointment_id))
            return result is not None
        except Exception as e:
            st.error(f"Error approving appointment: {str(e)}")
            return False
    
    def decline_appointment(self, appointment_id: str) -> bool:
        """Decline an appointment - changes status to 'cancelled'"""
        try:
            self.db.connect()
            query = "UPDATE appointments SET status = %s WHERE appointment_id = %s"
            result = self.db.execute_query(query, ("cancelled", appointment_id))
            return result is not None
        except Exception as e:
            st.error(f"Error declining appointment: {str(e)}")
            return False


class PatientDoctorRequestRepository(BaseRepository):
    """Repository for patient-doctor connection requests using MySQL"""
    
    def get_doctor_requests(self, doctor_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get connection requests for a specific doctor"""
        try:
            self.db.connect()
            if status:
                query = "SELECT * FROM patient_doctor_requests WHERE doctor_id = %s AND status = %s ORDER BY requested_at DESC"
                result = self.db.execute_query(query, (doctor_id, status))
            else:
                query = "SELECT * FROM patient_doctor_requests WHERE doctor_id = %s ORDER BY requested_at DESC"
                result = self.db.execute_query(query, (doctor_id,))
            return result or []
        except Exception as e:
            st.error(f"Error loading requests: {str(e)}")
            return []
    
    def approve_request(self, request_id: str) -> bool:
        """Approve a connection request"""
        try:
            self.db.connect()
            query = "UPDATE patient_doctor_requests SET status = %s WHERE request_id = %s"
            result = self.db.execute_query(query, ("approved", request_id))
            return result is not None
        except Exception as e:
            st.error(f"Error approving request: {str(e)}")
            return False
    
    def deny_request(self, request_id: str) -> bool:
        """Deny a connection request"""
        try:
            self.db.connect()
            query = "UPDATE patient_doctor_requests SET status = %s WHERE request_id = %s"
            result = self.db.execute_query(query, ("denied", request_id))
            return result is not None
        except Exception as e:
            st.error(f"Error denying request: {str(e)}")
            return False


class DoctorQueryRepository(BaseRepository):
    """Repository for doctor query operations using MySQL"""
    
    def get_doctor_queries(self, doctor_id: str, status: str = None) -> Dict[str, Dict[str, Any]]:
        """Get queries for a specific doctor"""
        try:
            self.db.connect()
            if status:
                query = "SELECT * FROM doctor_queries WHERE doctor_id = %s AND status = %s ORDER BY submitted_at DESC"
                result = self.db.execute_query(query, (doctor_id, status))
            else:
                query = "SELECT * FROM doctor_queries WHERE doctor_id = %s ORDER BY submitted_at DESC"
                result = self.db.execute_query(query, (doctor_id,))
            
            # Convert to dict format to match original logic
            return {q['query_id']: q for q in (result or [])}
        except Exception as e:
            st.error(f"Error loading queries: {str(e)}")
            return {}
    
    def respond_to_query(self, query_id: str, response: str) -> bool:
        """Respond to a patient query"""
        try:
            self.db.connect()
            query = """
                UPDATE doctor_queries 
                SET doctor_response = %s, status = %s 
                WHERE query_id = %s
            """
            result = self.db.execute_query(query, (response.strip(), "answered", query_id))
            return result is not None
        except Exception as e:
            st.error(f"Error responding to query: {str(e)}")
            return False
    
    def mark_resolved(self, query_id: str) -> bool:
        """Mark query as resolved"""
        try:
            self.db.connect()
            query = "UPDATE doctor_queries SET status = %s WHERE query_id = %s"
            result = self.db.execute_query(query, ("answered", query_id))
            return result is not None
        except Exception as e:
            st.error(f"Error marking query as resolved: {str(e)}")
            return False


class ProfileRepository(BaseRepository):
    """Repository for profile operations using MySQL"""
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        try:
            self.db.connect()
            query = "SELECT * FROM profiles WHERE user_id = %s"
            result = self.db.execute_query(query, (user_id,))
            return result[0] if result else {}
        except Exception as e:
            st.error(f"Error loading profile: {str(e)}")
            return {}


class PrescriptionRepository(BaseRepository):
    """Repository for prescription operations using MySQL"""
    
    def get_doctor_prescriptions(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get prescriptions for a specific doctor"""
        try:
            self.db.connect()
            query = "SELECT * FROM prescriptions WHERE doctor_id = %s ORDER BY uploaded_at DESC"
            result = self.db.execute_query(query, (doctor_id,))
            return result or []
        except Exception as e:
            st.error(f"Error loading prescriptions: {str(e)}")
            return []


class MedicalTestRepository(BaseRepository):
    """Repository for medical test operations using MySQL"""
    
    def get_doctor_tests(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get medical tests for a specific doctor"""
        try:
            self.db.connect()
            query = "SELECT * FROM medical_tests WHERE doctor_id = %s ORDER BY uploaded_at DESC"
            result = self.db.execute_query(query, (doctor_id,))
            return result or []
        except Exception as e:
            st.error(f"Error loading medical tests: {str(e)}")
            return []


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
    """Appointment requests page - UPDATED to show only pending requests"""
    
    def __init__(self, doctor_id: str):
        super().__init__(doctor_id)
        self.appointment_repo = AppointmentRepository()
    
    def render(self) -> None:
        """Render appointment requests page"""
        st.title("📅 Appointment Requests")
        
        # CHANGED: Only show appointments with 'requested' status (pending approval)
        requests = self.appointment_repo.get_doctor_appointments(self.doctor_id, "requested")
        st.write(f"**Pending appointment requests:** {len(requests)}")
        
        if not requests:
            st.info("No pending appointment requests found.")
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
                    st.success("Appointment approved and scheduled!")
                    st.balloons()
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