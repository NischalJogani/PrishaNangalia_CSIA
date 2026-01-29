"""
Designer Feedback Module
View client feedback and approval statuses
"""

import streamlit as st
from database import get_records, execute_query
from utils import format_datetime, show_info

def show_feedback_approvals():
    """
    Display client feedback and approval statuses
    Designer can view but not directly edit (clients create feedback)
    """
    st.header("💬 Client Feedback & Approvals")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_info("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Get all feedback items
    feedback_items = get_records('feedback', 
                                'project_id = %s ORDER BY created_at DESC', 
                                (project_id,))
    
    if feedback_items:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        approved = len([f for f in feedback_items if f['approval_status'] == 'approved'])
        pending = len([f for f in feedback_items if f['approval_status'] == 'pending'])
        rejected = len([f for f in feedback_items if f['approval_status'] == 'rejected'])
        
        with col1:
            st.metric("✅ Approved", approved)
        with col2:
            st.metric("⏳ Pending", pending)
        with col3:
            st.metric("❌ Rejected", rejected)
        
        st.divider()
        
        # Display feedback items
        st.subheader("📝 Feedback History")
        
        for feedback in feedback_items:
            status_emoji = {
                'approved': '✅',
                'pending': '⏳',
                'rejected': '❌'
            }
            
            status_color = {
                'approved': 'green',
                'pending': 'orange',
                'rejected': 'red'
            }
            
            with st.expander(f"{status_emoji[feedback['approval_status']]} {feedback['item_type'].title()} Feedback - {format_datetime(feedback['created_at'])}"):
                st.markdown(f"**Type:** {feedback['item_type'].title()}")
                st.markdown(f"**Status:** :{status_color[feedback['approval_status']]}[{feedback['approval_status'].title()}]")
                st.markdown(f"**Date:** {format_datetime(feedback['created_at'])}")
                
                if feedback['comment']:
                    st.markdown("### Client Comment:")
                    st.info(feedback['comment'])
                else:
                    st.markdown("*No comment provided*")
                
                # If rejected, highlight it
                if feedback['approval_status'] == 'rejected':
                    st.error("⚠️ This item requires attention - client has rejected it")
    else:
        show_info("No feedback from client yet. Client can provide feedback from their dashboard.")
    
    st.divider()
    
    # Instructions for designer
    st.subheader("ℹ️ About Feedback")
    st.markdown("""
    - Clients can provide feedback and approval status from their dashboard
    - **Approved** items indicate client satisfaction
    - **Rejected** items need revision or discussion
    - **Pending** items are awaiting client review
    - Use this section to track client satisfaction and address concerns
    """)
