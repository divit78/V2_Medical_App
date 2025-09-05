import streamlit as st
import traceback
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

from utils.db_helper import db


@dataclass
class GuardianRequest:
    """Data class for guardian request information"""
    request_id: str
    guardian_id: str
    patient_id: str
    guardian_fullname: str
    relationship: str
    mobile: str
    email: str
    status: str
    requested_at: str
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'GuardianRequest':
        """Create GuardianRequest from database row"""
        return cls(
            request_id=row.get('request_id', 'N/A'),
            guardian_id=row.get('guardian_id', 'N/A'),
            patient_id=row.get('patient_id', ''),
            guardian_fullname=row.get('guardian_fullname') or row.get('guardian_name') or 'Unknown Guardian',
            relationship=row.get('relationship', 'Not specified'),
            mobile=row.get('mobile', 'Not provided'),
            email=row.get('email', 'Not provided'),
            status=row.get('status', 'pending'),
            requested_at=row.get('requested_at', 'N/A')
        )


@dataclass
class GuardianStats:
    """Data class for guardian statistics"""
    total_requests: int
    pending_requests: int
    approved_requests: int
    denied_requests: int


@dataclass
class StatusConfig:
    """Data class for status configuration"""
    icon: str
    color: str
    text: str


@dataclass
class ActionButton:
    """Data class for action button configuration"""
    text: str
    button_type: str
    action: str
    message: str
    message_func: Callable
    extra_func: Optional[Callable] = None


class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self):
        self.db = db
    
    def get_guardian_requests(self, patient_id: str) -> List[GuardianRequest]:
        """Get all guardian requests for a patient"""
        try:
            self.db.connect()
            query = """
            SELECT gr.*, p.full_name as guardian_fullname 
            FROM guardian_requests gr 
            LEFT JOIN profiles p ON gr.guardian_id = p.user_id 
            WHERE gr.patient_id = %s 
            ORDER BY gr.requested_at DESC
            """
            
            rows = self.db.execute_query(query, (patient_id,))
            return [GuardianRequest.from_db_row(row) for row in rows] if rows else []
            
        except Exception as e:
            st.error(f"❌ Database query error: {e}")
            return []
    
    def update_request_status(self, request_id: str, status: str) -> bool:
        """Update guardian request status"""
        try:
            query = "UPDATE guardian_requests SET status = %s WHERE request_id = %s"
            result = self.db.execute_query(query, (status, request_id))
            return result is not None
        except Exception as e:
            st.error(f"❌ Database update error: {e}")
            return False
    
    def delete_request(self, request_id: str) -> bool:
        """Delete guardian request"""
        try:
            query = "DELETE FROM guardian_requests WHERE request_id = %s"
            result = self.db.execute_query(query, (request_id,))
            return result is not None
        except Exception as e:
            st.error(f"❌ Database delete error: {e}")
            return False
    
    def close_connection(self) -> None:
        """Close database connection safely"""
        try:
            self.db.close_connection()
        except:
            pass


class GuardianStatsService:
    """Service class for calculating guardian statistics"""
    
    @staticmethod
    def calculate_stats(requests: List[GuardianRequest]) -> GuardianStats:
        """Calculate guardian request statistics"""
        total = len(requests)
        pending = len([r for r in requests if r.status == 'pending'])
        approved = len([r for r in requests if r.status == 'approved'])
        denied = len([r for r in requests if r.status == 'denied'])
        
        return GuardianStats(
            total_requests=total,
            pending_requests=pending,
            approved_requests=approved,
            denied_requests=denied
        )


class StatusConfigService:
    """Service class for status configuration"""
    
    @staticmethod
    def get_status_configs() -> Dict[str, StatusConfig]:
        """Get status configurations"""
        return {
            'approved': StatusConfig('🟢', 'status-approved', 'Approved'),
            'pending': StatusConfig('🟡', 'status-pending', 'Pending'),
            'denied': StatusConfig('🔴', 'status-denied', 'Denied')
        }
    
    @staticmethod
    def get_config_for_status(status: str) -> StatusConfig:
        """Get configuration for specific status"""
        configs = StatusConfigService.get_status_configs()
        return configs.get(status, configs['pending'])


class ActionButtonService:
    """Service class for action button configurations"""
    
    @staticmethod
    def get_pending_actions() -> List[ActionButton]:
        """Get action buttons for pending requests"""
        return [
            ActionButton("✅ Approve Access", "primary", "approved", "✅ Guardian access approved!", st.success, st.balloons),
            ActionButton("❌ Deny Access", "secondary", "denied", "❌ Guardian access denied.", st.warning),
            ActionButton("🗑️ Delete Request", "secondary", "DELETE", "🗑️ Request permanently deleted.", st.info)
        ]
    
    @staticmethod
    def get_approved_actions() -> List[ActionButton]:
        """Get action buttons for approved requests"""
        return [
            ActionButton("🚫 Revoke Access", "secondary", "denied", "🚫 Guardian access has been revoked.", st.warning),
            ActionButton("🗑️ Remove Guardian", "secondary", "DELETE", "Guardian permanently removed from your account.", st.info)
        ]
    
    @staticmethod
    def get_denied_actions() -> List[ActionButton]:
        """Get action buttons for denied requests"""
        return [
            ActionButton("🔄 Re-approve Access", "primary", "approved", "✅ Guardian access re-approved!", st.success),
            ActionButton("🗑️ Delete Request", "secondary", "DELETE", "Request permanently deleted.", st.info)
        ]


class UIStyleManager:
    """Manages UI styles"""
    
    @staticmethod
    def load_styles() -> None:
        """Load CSS styles"""
        css_styles = """<style>
        .status-approved{background:#d4edda;color:#155724;padding:0.5rem;border-radius:5px;margin:0.5rem 0}
        .status-pending{background:#fff3cd;color:#856404;padding:0.5rem;border-radius:5px;margin:0.5rem 0}
        .status-denied{background:#f8d7da;color:#721c24;padding:0.5rem;border-radius:5px;margin:0.5rem 0}
        </style>"""
        
        st.markdown(css_styles, unsafe_allow_html=True)


class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def render(self) -> None:
        """Render the component"""
        pass


class StatsMetricsComponent(UIComponent):
    """Component for displaying guardian statistics"""
    
    def __init__(self, stats: GuardianStats):
        self.stats = stats
    
    def render(self) -> None:
        """Render statistics metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("📊 Total Requests", self.stats.total_requests),
            ("🟡 Pending", self.stats.pending_requests),
            ("🟢 Approved", self.stats.approved_requests),
            ("🔴 Denied", self.stats.denied_requests)
        ]
        
        columns = [col1, col2, col3, col4]
        
        for i, (label, value) in enumerate(metrics):
            with columns[i]:
                st.metric(label, value)


class GuardianInfoComponent(UIComponent):
    """Component for displaying guardian information"""
    
    def __init__(self, request: GuardianRequest):
        self.request = request
    
    def render(self) -> None:
        """Render guardian information"""
        col1, col2 = st.columns(2)
        
        guardian_info_left = [
            ("👤 Guardian Name", self.request.guardian_fullname),
            ("💞 Relationship", self.request.relationship),
            ("📱 Mobile", self.request.mobile),
            ("📧 Email", self.request.email)
        ]
        
        guardian_info_right = [
            ("🆔 Guardian ID", self.request.guardian_id),
            ("📋 Request ID", self.request.request_id),
            ("📅 Requested On", self.request.requested_at),
            ("⭐ Status", self.request.status.title())
        ]
        
        with col1:
            for label, value in guardian_info_left:
                st.markdown(f"**{label}:** {value}")
        
        with col2:
            for label, value in guardian_info_right:
                st.markdown(f"**{label}:** {value}")


class ActionButtonsComponent(UIComponent):
    """Component for action buttons"""
    
    def __init__(self, actions: List[ActionButton], request: GuardianRequest, db_service: DatabaseService):
        self.actions = actions
        self.request = request
        self.db_service = db_service
    
    def render(self) -> None:
        """Render action buttons"""
        if not self.actions:
            return
        
        # Create columns based on number of actions
        if len(self.actions) == 2:
            col1, col2 = st.columns(2)
            columns = [col1, col2]
        else:
            col1, col2, col3 = st.columns(3)
            columns = [col1, col2, col3]
        
        for i, action in enumerate(self.actions):
            if i < len(columns):
                with columns[i]:
                    self._render_action_button(action)
    
    def _render_action_button(self, action: ActionButton) -> None:
        """Render individual action button"""
        button_key = f"{action.action.lower()}_{self.request.request_id}"
        
        if st.button(action.text, key=button_key, type=action.button_type):
            success = self._execute_action(action)
            
            if success:
                action.message_func(action.message)
                if action.extra_func:
                    action.extra_func()
                st.rerun()
    
    def _execute_action(self, action: ActionButton) -> bool:
        """Execute the action"""
        if action.action == "DELETE":
            return self.db_service.delete_request(self.request.request_id)
        else:
            return self.db_service.update_request_status(self.request.request_id, action.action)


class GuardianRequestComponent(UIComponent):
    """Component for individual guardian request"""
    
    def __init__(self, request: GuardianRequest, config: StatusConfig, 
                 is_first_pending: bool, db_service: DatabaseService):
        self.request = request
        self.config = config
        self.is_first_pending = is_first_pending
        self.db_service = db_service
        self.action_service = ActionButtonService()
    
    def render(self) -> None:
        """Render guardian request"""
        with st.expander(
            f"{self.config.icon} {self.request.guardian_fullname} - {self.config.text}", 
            expanded=self.is_first_pending
        ):
            # Guardian information
            info_component = GuardianInfoComponent(self.request)
            info_component.render()
            
            # Status display
            st.markdown(f'<div class="{self.config.color}"><strong>Current Status:</strong> {self.config.text}</div>', unsafe_allow_html=True)
            st.markdown("---")
            
            # Render status-specific content and actions
            self._render_status_content()
    
    def _render_status_content(self) -> None:
        """Render content based on request status"""
        if self.request.status == 'pending':
            self._render_pending_content()
        elif self.request.status == 'approved':
            self._render_approved_content()
        else:  # denied
            self._render_denied_content()
    
    def _render_pending_content(self) -> None:
        """Render content for pending requests"""
        st.markdown("**🔄 Actions Available:**")
        actions = self.action_service.get_pending_actions()
        action_buttons = ActionButtonsComponent(actions, self.request, self.db_service)
        action_buttons.render()
    
    def _render_approved_content(self) -> None:
        """Render content for approved requests"""
        st.success("✅ This guardian currently has access to your health data including:")
        st.markdown("""
        - Your medication list and schedules
        - Appointment history and upcoming appointments
        - Medical test results and prescriptions
        - Health reports and adherence tracking
        """)
        
        actions = self.action_service.get_approved_actions()
        action_buttons = ActionButtonsComponent(actions, self.request, self.db_service)
        action_buttons.render()
    
    def _render_denied_content(self) -> None:
        """Render content for denied requests"""
        st.error("❌ This guardian has been denied access to your health data.")
        
        actions = self.action_service.get_denied_actions()
        action_buttons = ActionButtonsComponent(actions, self.request, self.db_service)
        action_buttons.render()


class InfoSectionComponent(UIComponent):
    """Component for information section"""
    
    def render(self) -> None:
        """Render information section"""
        with st.expander("ℹ️ About Guardian Access"):
            st.markdown("""
            **Guardian Access allows trusted family members or caregivers to:**
            - Monitor your medication schedules and adherence
            - View your appointment history and upcoming visits
            - Access your medical test results and prescriptions
            
            **Your Privacy is Protected:**
            - Guardians can only access data you explicitly approve
            - You can revoke access at any time
            - All guardian activities are logged for your security
            """)


class EmptyStateComponent(UIComponent):
    """Component for empty state when no requests exist"""
    
    def render(self) -> None:
        """Render empty state"""
        st.info("📭 No guardian access requests found.")
        st.markdown("""
        **What are Guardian Requests?**
        - Family members or caregivers can request access to monitor your health data
        - They need your approval before they can see your medications and appointments
        - You can approve or deny these requests at any time
        """)


class GuardianManagementPage:
    """Main guardian management page class"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db_service = DatabaseService()
        self.stats_service = GuardianStatsService()
        self.status_service = StatusConfigService()
        self.ui_style = UIStyleManager()
    
    def render(self) -> None:
        """Render the main guardian management page"""
        st.title("🧑‍🤝‍🧑 Guardian Access")
        st.write(f"***DEBUG: Currently viewing as patient: {self.user_id}***")
        
        # Load styles
        self.ui_style.load_styles()
        
        try:
            # Get guardian requests
            requests = self.db_service.get_guardian_requests(self.user_id)
            
            if not requests:
                empty_state = EmptyStateComponent()
                empty_state.render()
                return
            
            # Display statistics
            stats = self.stats_service.calculate_stats(requests)
            stats_component = StatsMetricsComponent(stats)
            stats_component.render()
            
            st.markdown("---")
            
            # Display requests
            self._render_requests(requests)
            
            # Information section
            info_section = InfoSectionComponent()
            info_section.render()
            
        except Exception as e:
            self._handle_error(e)
        finally:
            self.db_service.close_connection()
    
    def _render_requests(self, requests: List[GuardianRequest]) -> None:
        """Render all guardian requests"""
        for i, request in enumerate(requests):
            config = self.status_service.get_config_for_status(request.status)
            is_first_pending = (i == 0 and request.status == 'pending')
            
            request_component = GuardianRequestComponent(
                request, config, is_first_pending, self.db_service
            )
            request_component.render()
    
    def _handle_error(self, error: Exception) -> None:
        """Handle and display errors"""
        st.error(f"❌ Database connection error: {error}")
        
        with st.expander("🔧 Technical Details"):
            st.code(traceback.format_exc())


def manage_guardians(user_id: str) -> None:
    """Main entry point for guardian management page"""
    page = GuardianManagementPage(user_id)
    page.render()
