import streamlit as st
from datetime import datetime, date, time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from utils.file_ops import load_json, save_json
from config.constants import (
    DOCTOR_QUERIES_FILE, APPOINTMENTS_FILE, PROFILES_FILE, PATIENT_DOCTOR_REQUESTS_FILE
)
from utils.id_utils import generate_id


@dataclass
class DoctorInfo:
    """Data class for doctor information"""
    doctor_id: str
    full_name: str
    specialization: str
    experience: str
    hospital_clinic: str
    consultation_fee: str
    availability: List[str]
    
    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"Dr. {self.full_name} - {self.specialization}"


@dataclass
class AppointmentRequest:
    """Data class for appointment requests"""
    patient_id: str
    doctor_id: str
    question: str
    appointment_type: str
    preferred_date: Optional[date]
    preferred_time: Optional[time]
    action_type: str


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


class ProfileRepository(BaseRepository):
    """Repository for profile operations"""
    
    def __init__(self):
        super().__init__(PROFILES_FILE)
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get profile by user ID"""
        profiles = self.load_data()
        return profiles.get(user_id, {})
    
    def get_doctor_info(self, doctor_id: str) -> DoctorInfo:
        """Get structured doctor information"""
        profile = self.get_profile(doctor_id)
        return DoctorInfo(
            doctor_id=doctor_id,
            full_name=profile.get('full_name', 'Unknown'),
            specialization=profile.get('specialization', 'General'),
            experience=f"{profile.get('experience', 'Not specified')} years",
            hospital_clinic=profile.get('hospital_clinic', 'Not provided'),
            consultation_fee=f"₹{profile.get('consultation_fee', 'Not specified')}",
            availability=profile.get('availability', [])
        )


class PatientDoctorRepository(BaseRepository):
    """Repository for patient-doctor connections"""
    
    def __init__(self):
        super().__init__(PATIENT_DOCTOR_REQUESTS_FILE)
    
    def get_connected_doctors(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get approved doctor connections for patient"""
        requests = self.load_data()
        return [
            req for req in requests.values() 
            if req.get("patient_id") == patient_id and req.get("status") == "approved"
        ]


class DoctorQueryRepository(BaseRepository):
    """Repository for doctor queries"""
    
    def __init__(self):
        super().__init__(DOCTOR_QUERIES_FILE)
    
    def create_query(self, request: AppointmentRequest) -> str:
        """Create a new doctor query"""
        query_id = generate_id("DQ")
        
        new_query = {
            "query_id": query_id,
            "patient_id": request.patient_id,
            "doctor_id": request.doctor_id,
            "question": request.question.strip(),
            "submitted_at": datetime.now().isoformat(),
            "appointment_type": request.appointment_type if request.action_type != "Ask a Question Only" else "No Appointment",
            "preferred_date": request.preferred_date.isoformat() if request.preferred_date else None,
            "preferred_time": request.preferred_time.isoformat() if request.preferred_time else None,
            "status": "pending",
            "doctor_response": None
        }
        
        queries = self.load_data()
        queries[query_id] = new_query
        self.save_data(queries)
        return query_id
    
    def get_patient_queries(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all queries for a patient"""
        queries = self.load_data()
        return [q for q in queries.values() if q.get("patient_id") == patient_id]


class AppointmentRepository(BaseRepository):
    """Repository for appointments"""
    
    def __init__(self):
        super().__init__(APPOINTMENTS_FILE)
    
    def create_appointment(self, request: AppointmentRequest) -> str:
        """Create a new appointment"""
        appointment_id = generate_id("APT")
        
        new_appointment = {
            "appointment_id": appointment_id,
            "patient_id": request.patient_id,
            "doctor_id": request.doctor_id,
            "appointment_date": request.preferred_date.isoformat(),
            "appointment_time": request.preferred_time.isoformat(),
            "type": request.appointment_type,
            "status": "requested",
            "notes": request.question.strip(),
            "created_at": datetime.now().isoformat()
        }
        
        appointments = self.load_data()
        appointments[appointment_id] = new_appointment
        self.save_data(appointments)
        return appointment_id
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all appointments for a patient"""
        appointments = self.load_data()
        return [a for a in appointments.values() if a.get("patient_id") == patient_id]


class AppointmentService:
    """Service class for appointment business logic"""
    
    def __init__(self):
        self.profile_repo = ProfileRepository()
        self.connection_repo = PatientDoctorRepository()
        self.query_repo = DoctorQueryRepository()
        self.appointment_repo = AppointmentRepository()
    
    def get_connected_doctors_info(self, patient_id: str) -> List[DoctorInfo]:
        """Get connected doctors information"""
        connections = self.connection_repo.get_connected_doctors(patient_id)
        doctors_info = []
        
        for connection in connections:
            doctor_id = connection.get("doctor_id")
            doctor_info = self.profile_repo.get_doctor_info(doctor_id)
            doctors_info.append(doctor_info)
        
        return doctors_info
    
    def validate_appointment_request(self, request: AppointmentRequest) -> Optional[str]:
        """Validate appointment request"""
        if not request.question.strip():
            return "Please enter your question or message."
        
        if request.action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
            if not request.preferred_date or not request.preferred_time:
                return "Please select both date and time for your appointment."
        
        return None
    
    def process_appointment_request(self, request: AppointmentRequest) -> Dict[str, str]:
        """Process appointment request"""
        # Always create query
        query_id = self.query_repo.create_query(request)
        
        result = {"query_id": query_id}
        
        # Create appointment if requested
        if request.action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
            appointment_id = self.appointment_repo.create_appointment(request)
            result["appointment_id"] = appointment_id
        
        return result


class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def render(self) -> None:
        """Render the component"""
        pass


class DoctorSelectionComponent(UIComponent):
    """Component for doctor selection"""
    
    def __init__(self, doctors_info: List[DoctorInfo]):
        self.doctors_info = doctors_info
    
    def render(self) -> Optional[DoctorInfo]:
        """Render doctor selection and return selected doctor"""
        if not self.doctors_info:
            st.warning("⚠️ You need to connect with doctors first!")
            st.info("Go to 'Search Doctors' to send connection requests to doctors.")
            return None
        
        st.subheader("👨‍⚕️ Select Doctor")
        
        doctor_options = {doc.get_display_name(): doc for doc in self.doctors_info}
        selected_name = st.selectbox(
            "Choose which doctor you want to contact:",
            options=list(doctor_options.keys()),
            help="Only doctors you're connected with are shown here"
        )
        
        return doctor_options.get(selected_name) if selected_name else None


class DoctorInfoComponent(UIComponent):
    """Component for displaying doctor information"""
    
    def __init__(self, doctor_info: DoctorInfo):
        self.doctor_info = doctor_info
    
    def render(self) -> None:
        """Render doctor information"""
        with st.expander("ℹ️ Doctor Information", expanded=False):
            col1, col2 = st.columns(2)
            
            doctor_details = [
                ("Name", f"Dr. {self.doctor_info.full_name}"),
                ("Specialization", self.doctor_info.specialization),
                ("Experience", self.doctor_info.experience),
                ("Hospital", self.doctor_info.hospital_clinic),
                ("Consultation Fee", self.doctor_info.consultation_fee),
                ("Available Days", ', '.join(self.doctor_info.availability))
            ]
            
            for i, (label, value) in enumerate(doctor_details):
                with col1 if i < 3 else col2:
                    st.write(f"**{label}:** {value}")


class AppointmentFormComponent(UIComponent):
    """Component for appointment form"""
    
    def __init__(self, doctor_info: DoctorInfo):
        self.doctor_info = doctor_info
    
    def render(self) -> AppointmentRequest:
        """Render appointment form and return request data"""
        # Action selection
        st.subheader("💬 What would you like to do?")
        action_type = st.radio(
            "Choose your action:",
            ["Ask a Question Only", "Book an Appointment", "Ask Question + Book Appointment"],
            help="Select what you want to do with this doctor"
        )
        
        # Question section
        st.subheader("💭 Your Question/Message")
        question = st.text_area(
            "Enter Your Question or Message:",
            placeholder="Describe your symptoms, concerns, or questions for the doctor...",
            height=120
        )
        
        # Appointment details
        preferred_date, preferred_time, appointment_type = None, None, "No Appointment"
        
        if action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
            preferred_date, preferred_time, appointment_type = self._render_appointment_details()
        
        # Summary
        self._render_summary(action_type, appointment_type, preferred_date, preferred_time)
        
        return AppointmentRequest(
            patient_id="",  # Will be set by the page
            doctor_id=self.doctor_info.doctor_id,
            question=question,
            appointment_type=appointment_type,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            action_type=action_type
        )
    
    def _render_appointment_details(self) -> tuple:
        """Render appointment details section"""
        st.subheader("📅 Appointment Details")
        appointment_type = st.selectbox(
            "Appointment Type",
            ["Video Call", "In-Person Visit", "Phone Call"],
            help="Choose how you'd like to meet with the doctor"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            preferred_date = st.date_input(
                "Preferred Date",
                min_value=date.today(),
                help="Select your preferred appointment date"
            )
        
        with col2:
            preferred_time = st.time_input(
                "Preferred Time",
                value=time(9, 0),
                help="Select your preferred appointment time"
            )
        
        # Check doctor availability
        self._check_doctor_availability(preferred_date)
        
        return preferred_date, preferred_time, appointment_type
    
    def _check_doctor_availability(self, preferred_date: date) -> None:
        """Check and display doctor availability"""
        if self.doctor_info.availability and preferred_date:
            weekday_name = preferred_date.strftime("%a")
            if weekday_name in self.doctor_info.availability:
                st.success(f"✅ Dr. {self.doctor_info.full_name} is available on {weekday_name}s")
            else:
                st.warning(f"⚠️ Dr. {self.doctor_info.full_name} is typically available on: {', '.join(self.doctor_info.availability)}")
    
    def _render_summary(self, action_type: str, appointment_type: str, preferred_date: date, preferred_time: time) -> None:
        """Render request summary"""
        st.subheader("📋 Summary")
        
        summary_messages = {
            "Ask a Question Only": "You will send a question to the doctor (no appointment will be booked)",
            "Book an Appointment": f"You will book a {appointment_type} appointment for {preferred_date} at {preferred_time}",
            "Ask Question + Book Appointment": f"You will send a question AND book a {appointment_type} appointment for {preferred_date} at {preferred_time}"
        }
        
        st.info(summary_messages.get(action_type, "Unknown action"))


class HistoryComponent(UIComponent):
    """Component for displaying patient history"""
    
    def __init__(self, patient_id: str, appointment_service: AppointmentService):
        self.patient_id = patient_id
        self.appointment_service = appointment_service
    
    def render(self) -> None:
        """Render patient history"""
        st.markdown("---")
        st.subheader("🗂️ Your Previous Queries & Appointments")
        
        queries = self.appointment_service.query_repo.get_patient_queries(self.patient_id)
        appointments = self.appointment_service.appointment_repo.get_patient_appointments(self.patient_id)
        
        if not queries and not appointments:
            st.info("No questions or appointments yet.")
            return
        
        if queries:
            self._render_queries(queries)
        
        if appointments:
            self._render_appointments(appointments)
    
    def _render_queries(self, queries: List[Dict[str, Any]]) -> None:
        """Render patient queries"""
        st.write("**💬 Your Questions:**")
        
        for query in sorted(queries, key=lambda x: x.get("submitted_at", ""), reverse=True):
            doctor_profile = self.appointment_service.profile_repo.get_profile(query.get("doctor_id"))
            doctor_name = doctor_profile.get("full_name", "Unknown Doctor")
            has_appointment = query.get("appointment_type", "No Appointment") != "No Appointment"
            appointment_text = " + Appointment Request" if has_appointment else ""
            
            with st.expander(f"Question to Dr. {doctor_name}{appointment_text} - {query.get('status', 'pending').title()}"):
                query_info = [
                    ("Question", query.get('question', 'No question')),
                    ("Submitted", query.get('submitted_at', 'Unknown')),
                    ("Status", query.get('status', 'pending').title())
                ]
                
                for label, value in query_info:
                    st.write(f"**{label}:** {value}")
                
                if has_appointment:
                    appointment_info = [
                        ("Appointment Type", query.get('appointment_type')),
                        ("Preferred Date", query.get('preferred_date', 'Not specified')),
                        ("Preferred Time", query.get('preferred_time', 'Not specified'))
                    ]
                    for label, value in appointment_info:
                        st.write(f"**{label}:** {value}")
                
                if query.get("doctor_response"):
                    st.write(f"**Doctor's Response:** {query.get('doctor_response')}")
                else:
                    st.info("Waiting for doctor's response...")
    
    def _render_appointments(self, appointments: List[Dict[str, Any]]) -> None:
        """Render patient appointments"""
        st.write("**📅 Your Appointments:**")
        status_colors = {"requested": "🟡", "scheduled": "🟢", "cancelled": "🔴", "completed": "✅"}
        
        for appointment in sorted(appointments, key=lambda x: x.get("appointment_date", ""), reverse=True):
            doctor_profile = self.appointment_service.profile_repo.get_profile(appointment.get("doctor_id"))
            doctor_name = doctor_profile.get("full_name", "Unknown Doctor")
            status_icon = status_colors.get(appointment.get("status", ""), "⚪")
            
            with st.expander(f"{status_icon} Appointment with Dr. {doctor_name} - {appointment.get('status', 'unknown').title()}"):
                appointment_info = [
                    ("Date", appointment.get('appointment_date', 'Not set')),
                    ("Time", appointment.get('appointment_time', 'Not set')),
                    ("Type", appointment.get('type', 'Not specified')),
                    ("Status", appointment.get('status', 'unknown').title())
                ]
                
                for label, value in appointment_info:
                    st.write(f"**{label}:** {value}")
                
                if appointment.get('notes'):
                    st.write(f"**Notes:** {appointment.get('notes')}")


class AppointmentPage:
    """Main appointment page class"""
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.appointment_service = AppointmentService()
    
    def render(self) -> None:
        """Render the main appointment page"""
        st.title("🤝 Ask Doctor / Book Appointment")
        
        # Get connected doctors
        doctors_info = self.appointment_service.get_connected_doctors_info(self.patient_id)
        
        # Doctor selection
        doctor_selection = DoctorSelectionComponent(doctors_info)
        selected_doctor = doctor_selection.render()
        
        if not selected_doctor:
            return
        
        # Doctor information
        doctor_info_component = DoctorInfoComponent(selected_doctor)
        doctor_info_component.render()
        
        st.markdown("---")
        
        # Appointment form
        form_component = AppointmentFormComponent(selected_doctor)
        request = form_component.render()
        request.patient_id = self.patient_id
        
        # Submit button
        if st.button("📤 Submit Request", type="primary"):
            self._handle_submit(request, selected_doctor)
        
        # History
        history_component = HistoryComponent(self.patient_id, self.appointment_service)
        history_component.render()
    
    def _handle_submit(self, request: AppointmentRequest, selected_doctor: DoctorInfo) -> None:
        """Handle form submission"""
        error = self.appointment_service.validate_appointment_request(request)
        if error:
            st.error(error)
            return
        
        try:
            result = self.appointment_service.process_appointment_request(request)
            
            if request.action_type in ["Book an Appointment", "Ask Question + Book Appointment"]:
                st.success(f"✅ Question sent and appointment requested for {request.preferred_date} at {request.preferred_time}!")
                st.balloons()
            else:
                st.success(f"✅ Your question has been sent to Dr. {selected_doctor.full_name}!")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing request: {str(e)}")


def ask_questions_and_appointments(patient_id: str) -> None:
    """Main entry point for appointments page"""
    page = AppointmentPage(patient_id)
    page.render()
