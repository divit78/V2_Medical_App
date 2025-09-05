import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

from utils.file_ops import load_json, save_json
from config.constants import (PROFILES_FILE, USERS_FILE, PATIENT_DOCTOR_REQUESTS_FILE)
from utils.id_utils import generate_id


@dataclass
class DoctorInfo:
    """Data class for doctor information"""
    doctor_id: str
    full_name: str
    display_name: str
    specialization: str
    experience: int
    hospital_clinic: str
    consultation_fee: float
    initials: str
    
    @classmethod
    def from_profile(cls, doctor_id: str, profile: Dict[str, Any]) -> 'DoctorInfo':
        """Create DoctorInfo from profile data"""
        full_name = profile.get('full_name', 'Unknown Doctor')
        display_name = full_name[4:] if full_name.startswith('Dr. ') else full_name
        
        # Generate initials
        name_parts = display_name.split()
        initials = ''.join([part[0].upper() for part in name_parts[:2]]) if name_parts else 'DR'
        
        return cls(
            doctor_id=doctor_id,
            full_name=full_name,
            display_name=display_name,
            specialization=profile.get('specialization', 'General Medicine'),
            experience=profile.get('experience', 0),
            hospital_clinic=profile.get('hospital_clinic', 'Private Practice'),
            consultation_fee=profile.get('consultation_fee', 0),
            initials=initials
        )


@dataclass
class ConnectionRequest:
    """Data class for connection request"""
    request_id: str
    patient_id: str
    doctor_id: str
    status: str
    requested_at: str
    doctor_info: Optional[DoctorInfo] = None


class BaseRepository:
    """Base repository class"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from file"""
        return load_json(self.file_path)
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """Save data to file"""
        save_json(self.file_path, data)


class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self):
        super().__init__(USERS_FILE)
    
    def get_doctors(self) -> Dict[str, Dict[str, Any]]:
        """Get all doctor users"""
        users = self.load_data()
        return {
            uid: user for uid, user in users.items() 
            if user.get('user_type') == 'doctor'
        }


class ProfileRepository(BaseRepository):
    """Repository for profile operations"""
    
    def __init__(self):
        super().__init__(PROFILES_FILE)
    
    def get_doctor_profiles(self, doctor_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get profiles for specific doctor IDs"""
        profiles = self.load_data()
        return {
            uid: profile for uid, profile in profiles.items() 
            if uid in doctor_ids
        }
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get single profile"""
        profiles = self.load_data()
        return profiles.get(user_id, {})


class ConnectionRequestRepository(BaseRepository):
    """Repository for connection request operations"""
    
    def __init__(self):
        super().__init__(PATIENT_DOCTOR_REQUESTS_FILE)
    
    def get_patient_requests(self, patient_id: str) -> List[ConnectionRequest]:
        """Get all connection requests for a patient"""
        requests = self.load_data()
        patient_requests = []
        
        for req in requests.values():
            if req.get('patient_id') == patient_id:
                connection_req = ConnectionRequest(
                    request_id=req.get('request_id', ''),
                    patient_id=req.get('patient_id', ''),
                    doctor_id=req.get('doctor_id', ''),
                    status=req.get('status', 'pending'),
                    requested_at=req.get('requested_at', '')
                )
                patient_requests.append(connection_req)
        
        return patient_requests
    
    def get_connection_status(self, patient_id: str, doctor_id: str) -> Optional[str]:
        """Get connection status between patient and doctor"""
        requests = self.load_data()
        for req in requests.values():
            if (req.get('patient_id') == patient_id and 
                req.get('doctor_id') == doctor_id):
                return req.get('status')
        return None
    
    def create_connection_request(self, patient_id: str, doctor_id: str) -> bool:
        """Create new connection request"""
        try:
            request_id = generate_id("REQ")
            new_request = {
                "request_id": request_id,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "status": "pending",
                "requested_at": datetime.now().isoformat()
            }
            
            requests = self.load_data()
            requests[request_id] = new_request
            self.save_data(requests)
            return True
            
        except Exception as e:
            st.error(f"Failed to send connection request: {e}")
            return False


class DoctorSearchService:
    """Service class for doctor search functionality"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = ProfileRepository()
        self.connection_repo = ConnectionRequestRepository()
    
    def get_all_doctors(self) -> Dict[str, DoctorInfo]:
        """Get all available doctors"""
        doctors = self.user_repo.get_doctors()
        doctor_profiles = self.profile_repo.get_doctor_profiles(list(doctors.keys()))
        
        doctor_info_dict = {}
        for doc_id, profile in doctor_profiles.items():
            doctor_info = DoctorInfo.from_profile(doc_id, profile)
            doctor_info_dict[doc_id] = doctor_info
        
        return doctor_info_dict
    
    def get_specializations(self, doctors: Dict[str, DoctorInfo]) -> List[str]:
        """Get unique specializations"""
        specializations = set()
        for doctor in doctors.values():
            if doctor.specialization:
                specializations.add(doctor.specialization)
        return ["All"] + sorted(list(specializations))
    
    def filter_doctors(self, doctors: Dict[str, DoctorInfo], 
                      specialization: str, name_search: str) -> Dict[str, DoctorInfo]:
        """Filter doctors based on search criteria"""
        filtered = {}
        
        for doc_id, doctor in doctors.items():
            # Filter by specialization
            if specialization != "All" and doctor.specialization != specialization:
                continue
            
            # Filter by name
            if name_search and name_search.lower() not in doctor.full_name.lower():
                continue
            
            filtered[doc_id] = doctor
        
        return filtered
    
    def get_patient_connection_requests(self, patient_id: str) -> List[ConnectionRequest]:
        """Get patient's connection requests with doctor info"""
        requests = self.connection_repo.get_patient_requests(patient_id)
        
        # Add doctor info to requests
        for req in requests:
            profile = self.profile_repo.get_profile(req.doctor_id)
            if profile:
                req.doctor_info = DoctorInfo.from_profile(req.doctor_id, profile)
        
        return requests


class UIStyleManager:
    """Manages UI styles"""
    
    @staticmethod
    def load_styles() -> None:
        """Load CSS styles"""
        css_styles = """<style>
        .search-section{background:linear-gradient(135deg,#FF8A65,#FF7043);padding:1.5rem;border-radius:10px;margin-bottom:2rem;color:white}
        .doctor-card-header{display:flex;align-items:center;margin-bottom:1rem;padding-bottom:0.5rem;border-bottom:2px solid #f0f0f0}
        .doctor-avatar{width:50px;height:50px;border-radius:50%;background:linear-gradient(135deg,#FF8C00,#FFA500);display:flex;align-items:center;justify-content:center;font-size:1.2rem;color:white;margin-right:1rem;font-weight:bold}
        .doctor-name{font-size:1.3rem;font-weight:700;color:#2c3e50;margin:0}
        .doctor-specialty{color:#FF7043;font-weight:600;font-size:0.9rem;margin:0.2rem 0}
        .connection-section{background:#f8f9fa;padding:1.5rem;border-radius:10px;margin:2rem 0;border-left:4px solid #4CAF50}
        .status-badge{position:absolute;top:1rem;right:1rem;padding:0.3rem 0.8rem;border-radius:15px;font-size:0.75rem;font-weight:600;text-transform:uppercase}
        .fee-highlight{background:linear-gradient(135deg,#4CAF50,#45a049);color:white;padding:0.2rem 0.6rem;border-radius:15px;font-weight:600;font-size:0.85rem}
        </style>"""
        
        st.markdown(css_styles, unsafe_allow_html=True)


class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def render(self) -> None:
        """Render the component"""
        pass


class SearchHeaderComponent(UIComponent):
    """Component for search header"""
    
    def render(self) -> None:
        """Render search header"""
        header_html = """
        <div class="search-section">
            <h3 style="margin-top:0;color:white;">🔍 Find Your Perfect Doctor</h3>
            <p style="margin-bottom:0;opacity:0.9;">Search by specialization or name to connect with qualified healthcare professionals</p>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)


class SearchFiltersComponent(UIComponent):
    """Component for search filters"""
    
    def __init__(self, specializations: List[str]):
        self.specializations = specializations
    
    def render(self) -> Tuple[str, str]:
        """Render search filters and return selected values"""
        col1, col2 = st.columns(2)
        
        with col1:
            selected_specialization = st.selectbox("🩺 Specialization", self.specializations)
        
        with col2:
            search_name = st.text_input("👨‍⚕️ Search Doctor Name", placeholder="Enter doctor's name...")
        
        return selected_specialization, search_name


class DoctorCardComponent(UIComponent):
    """Component for individual doctor card"""
    
    def __init__(self, doctor: DoctorInfo, patient_id: str, connection_status: Optional[str]):
        self.doctor = doctor
        self.patient_id = patient_id
        self.connection_status = connection_status
    
    def render(self) -> bool:
        """Render doctor card and return True if connection request sent"""
        connection_sent = False
        
        with st.container(border=True):
            # Status indicator
            self._render_status_indicator()
            
            # Doctor header
            self._render_doctor_header()
            
            # Doctor information
            self._render_doctor_info()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Connect button
            connection_sent = self._render_connect_button()
        
        return connection_sent
    
    def _render_status_indicator(self) -> None:
        """Render connection status indicator"""
        if self.connection_status == "approved":
            st.success("✅ Connected")
        elif self.connection_status == "pending":
            st.warning("⏳ Request Pending")
    
    def _render_doctor_header(self) -> None:
        """Render doctor header with avatar and name"""
        header_html = f"""
        <div class="doctor-card-header">
            <div class="doctor-avatar">{self.doctor.initials}</div>
            <div>
                <div class="doctor-name">Dr. {self.doctor.display_name}</div>
                <div class="doctor-specialty">{self.doctor.specialization}</div>
            </div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    
    def _render_doctor_info(self) -> None:
        """Render doctor information"""
        col1, col2 = st.columns(2)
        
        # Truncate long hospital names
        hospital_display = self.doctor.hospital_clinic
        if len(hospital_display) > 25:
            hospital_display = hospital_display[:22] + "..."
        
        with col1:
            st.write(f"📊 **Experience:**\n   {self.doctor.experience} years\n🏥 **Hospital:**\n   {hospital_display}")
        
        with col2:
            st.write("💰 **Consultation:**")
            st.markdown(f'   <span class="fee-highlight">₹{self.doctor.consultation_fee:.0f}</span>', unsafe_allow_html=True)
    
    def _render_connect_button(self) -> bool:
        """Render connect button and handle connection request"""
        button_key = f"connect_{self.doctor.doctor_id}"
        
        if self.connection_status == "approved":
            st.button("✅ Already Connected", key=button_key, disabled=True, use_container_width=True)
            return False
        elif self.connection_status == "pending":
            st.button("⏳ Request Sent", key=button_key, disabled=True, type="secondary", use_container_width=True)
            return False
        else:
            if st.button("➕ Send Connection Request", key=button_key, type="primary", use_container_width=True):
                return True
        
        return False


class DoctorGridComponent(UIComponent):
    """Component for displaying doctors in a grid"""
    
    def __init__(self, doctors: Dict[str, DoctorInfo], patient_id: str, search_service: DoctorSearchService):
        self.doctors = doctors
        self.patient_id = patient_id
        self.search_service = search_service
    
    def render(self) -> None:
        """Render doctors grid"""
        if not self.doctors:
            st.warning("🔍 No doctors found matching your search criteria. Try adjusting your filters.")
            return
        
        st.markdown(f"### 👨‍⚕️ Available Doctors ({len(self.doctors)} found)")
        st.info("Click the connect button to send a connection request")
        
        # Display doctors in rows of 2
        doctor_list = list(self.doctors.items())
        
        for i in range(0, len(doctor_list), 2):
            cols = st.columns(2)
            
            for j, col in enumerate(cols):
                if i + j < len(doctor_list):
                    with col:
                        doc_id, doctor = doctor_list[i + j]
                        connection_status = self.search_service.connection_repo.get_connection_status(
                            self.patient_id, doc_id
                        )
                        
                        card = DoctorCardComponent(doctor, self.patient_id, connection_status)
                        connection_sent = card.render()
                        
                        if connection_sent:
                            success = self.search_service.connection_repo.create_connection_request(
                                self.patient_id, doc_id
                            )
                            if success:
                                st.success(f"✅ Connection request sent to Dr. {doctor.display_name}!")
                                st.rerun()


class ConnectionRequestsComponent(UIComponent):
    """Component for displaying connection requests"""
    
    def __init__(self, requests: List[ConnectionRequest]):
        self.requests = requests
    
    def render(self) -> None:
        """Render connection requests"""
        if not self.requests:
            return
        
        st.markdown("### 📋 Your Connection Requests")
        
        with st.container(border=True):
            for i, req in enumerate(self.requests):
                self._render_request_item(req)
                
                # Add divider if not last item
                if i < len(self.requests) - 1:
                    st.divider()
    
    def _render_request_item(self, req: ConnectionRequest) -> None:
        """Render individual request item"""
        if not req.doctor_info:
            return
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Dr. {req.doctor_info.display_name}** ({req.doctor_info.specialization})")
        
        with col2:
            if req.status == "approved":
                st.success("🟢 Approved")
            elif req.status == "pending":
                st.warning("🟡 Pending")
            else:
                st.error("🔴 Denied")


class ConnectDoctorsPage:
    """Main connect doctors page class"""
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.search_service = DoctorSearchService()
        self.ui_style = UIStyleManager()
    
    def render(self) -> None:
        """Render the main page"""
        st.title("🔗 Search & Connect With Doctors")
        
        # Load styles
        self.ui_style.load_styles()
        
        # Get all doctors
        doctors = self.search_service.get_all_doctors()
        
        # Render search header
        header = SearchHeaderComponent()
        header.render()
        
        # Render search filters
        specializations = self.search_service.get_specializations(doctors)
        filters = SearchFiltersComponent(specializations)
        selected_specialization, search_name = filters.render()
        
        # Filter doctors
        filtered_doctors = self.search_service.filter_doctors(
            doctors, selected_specialization, search_name
        )
        
        # Render doctors grid
        grid = DoctorGridComponent(filtered_doctors, self.patient_id, self.search_service)
        grid.render()
        
        # Render connection requests
        requests = self.search_service.get_patient_connection_requests(self.patient_id)
        requests_component = ConnectionRequestsComponent(requests)
        requests_component.render()


def connect_doctors_page(patient_id: str) -> None:
    """Main entry point for connect doctors page"""
    page = ConnectDoctorsPage(patient_id)
    page.render()
