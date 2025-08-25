import streamlit as st
from utils.db_helper import db

def manage_guardians(user_id):
    """Complete guardian management page for patients"""
    st.title("🧑‍🤝‍🧑 Guardian Access")
    
    st.write(f"***DEBUG: Currently viewing as patient: {user_id}***")
    
    st.markdown("""
    <style>
    .status-approved {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .status-pending {
        background: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .status-denied {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    try:
        db.connect()
        
        query = """
        SELECT gr.*, p.full_name as guardian_fullname
        FROM guardian_requests gr
        LEFT JOIN profiles p ON gr.guardian_id = p.user_id
        WHERE gr.patient_id = %s
        ORDER BY gr.requested_at DESC
        """
        
        requests = db.execute_query(query, (user_id,))
        
        if not requests:
            st.info("📭 No guardian access requests found.")
            st.markdown("""
            **What are Guardian Requests?**
            - Family members or caregivers can request access to monitor your health data
            - They need your approval before they can see your medications and appointments
            - You can approve or deny these requests at any time
            """)
            return
        
        # Summary statistics
        total_requests = len(requests)
        pending_requests = len([r for r in requests if r.get('status') == 'pending'])
        approved_requests = len([r for r in requests if r.get('status') == 'approved'])
        denied_requests = len([r for r in requests if r.get('status') == 'denied'])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Total Requests", total_requests)
        col2.metric("🟡 Pending", pending_requests)
        col3.metric("🟢 Approved", approved_requests)
        col4.metric("🔴 Denied", denied_requests)
        
        st.markdown("---")
        
        # Display each request
        for i, req in enumerate(requests):
            fullname = req.get('guardian_fullname') or req.get('guardian_name') or 'Unknown Guardian'
            status = req.get('status', 'pending')
            
            status_config = {
                'approved': {'icon': '🟢', 'color': 'status-approved', 'text': 'Approved'},
                'pending': {'icon': '🟡', 'color': 'status-pending', 'text': 'Pending'},
                'denied': {'icon': '🔴', 'color': 'status-denied', 'text': 'Denied'}
            }
            
            config = status_config.get(status, status_config['pending'])
            
            with st.expander(f"{config['icon']} {fullname} - {config['text']}", expanded=(i == 0 and status == 'pending')):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**👤 Guardian Name:** {fullname}")
                    st.markdown(f"**💞 Relationship:** {req.get('relationship', 'Not specified')}")
                    st.markdown(f"**📱 Mobile:** {req.get('mobile', 'Not provided')}")
                    st.markdown(f"**📧 Email:** {req.get('email', 'Not provided')}")
                
                with col2:
                    st.markdown(f"**🆔 Guardian ID:** {req.get('guardian_id', 'N/A')}")
                    st.markdown(f"**📋 Request ID:** {req.get('request_id', 'N/A')}")
                    st.markdown(f"**📅 Requested On:** {req.get('requested_at', 'N/A')}")
                    st.markdown(f"**⭐ Status:** {config['text']}")
                
                st.markdown(f'<div class="{config["color"]}"><strong>Current Status:</strong> {config["text"]}</div>', 
                           unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Action buttons based on status
                if status == 'pending':
                    st.markdown("**🔄 Actions Available:**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Approve Access", key=f"approve_{req['request_id']}", type="primary"):
                            update_query = "UPDATE guardian_requests SET status = 'approved' WHERE request_id = %s"
                            result = db.execute_query(update_query, (req['request_id'],))
                            if result:
                                st.success("✅ Guardian access approved!")
                                st.balloons()
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ Deny Access", key=f"deny_{req['request_id']}"):
                            update_query = "UPDATE guardian_requests SET status = 'denied' WHERE request_id = %s"
                            result = db.execute_query(update_query, (req['request_id'],))
                            if result:
                                st.warning("❌ Guardian access denied.")
                                st.rerun()
                    
                    with col3:
                        if st.button("🗑️ Delete Request", key=f"delete_{req['request_id']}"):
                            delete_query = "DELETE FROM guardian_requests WHERE request_id = %s"
                            result = db.execute_query(delete_query, (req['request_id'],))
                            if result:
                                st.info("🗑️ Request permanently deleted.")
                                st.rerun()
                
                elif status == 'approved':
                    st.success("✅ This guardian currently has access to your health data including:")
                    st.markdown("""
                    - Your medication list and schedules
                    - Appointment history and upcoming appointments  
                    - Medical test results and prescriptions
                    - Health reports and adherence tracking
                    """)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🚫 Revoke Access", key=f"revoke_{req['request_id']}", type="secondary"):
                            update_query = "UPDATE guardian_requests SET status = 'denied' WHERE request_id = %s"
                            result = db.execute_query(update_query, (req['request_id'],))
                            if result:
                                st.warning("🚫 Guardian access has been revoked.")
                                st.rerun()
                    
                    with col2:
                        if st.button("🗑️ Remove Guardian", key=f"remove_{req['request_id']}"):
                            delete_query = "DELETE FROM guardian_requests WHERE request_id = %s"
                            result = db.execute_query(delete_query, (req['request_id'],))
                            if result:
                                st.info("Guardian permanently removed from your account.")
                                st.rerun()
                
                else:  # denied status
                    st.error("❌ This guardian has been denied access to your health data.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Re-approve Access", key=f"reapprove_{req['request_id']}", type="primary"):
                            update_query = "UPDATE guardian_requests SET status = 'approved' WHERE request_id = %s"
                            result = db.execute_query(update_query, (req['request_id'],))
                            if result:
                                st.success("✅ Guardian access re-approved!")
                                st.rerun()
                    
                    with col2:
                        if st.button("🗑️ Delete Request", key=f"delete_denied_{req['request_id']}"):
                            delete_query = "DELETE FROM guardian_requests WHERE request_id = %s"
                            result = db.execute_query(delete_query, (req['request_id'],))
                            if result:
                                st.info("Request permanently deleted.")
                                st.rerun()
        
        # Information section
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
        
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        import traceback
        with st.expander("🔧 Technical Details"):
            st.code(traceback.format_exc())
    
    finally:
        try:
            db.close_connection()
        except:
            pass
