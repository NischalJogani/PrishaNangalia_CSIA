"""
Designer Timeline Module
Manage project milestones and deadlines
"""

import streamlit as st
from database import insert_record, get_records, update_record, delete_record
from utils import format_date, show_success, show_error, show_info
from datetime import date

def show_client_timeline():
    """
    Display timeline management interface
    Add and update project milestones
    """
    st.header("📅 Client Timeline")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_info("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Get all timeline items
    timeline_items = get_records('timeline', 'project_id = %s ORDER BY deadline', (project_id,))
    
    if timeline_items:
        st.subheader("📋 Project Milestones")
        
        # Group by status
        pending = [t for t in timeline_items if t['status'] == 'pending']
        in_progress = [t for t in timeline_items if t['status'] == 'in_progress']
        completed = [t for t in timeline_items if t['status'] == 'completed']
        
        # Display counts
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏳ Pending", len(pending))
        with col2:
            st.metric("🔄 In Progress", len(in_progress))
        with col3:
            st.metric("✅ Completed", len(completed))
        
        st.divider()
        
        # Display all milestones
        for item in timeline_items:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅'
            }
            
            with st.expander(f"{status_emoji[item['status']]} {item['milestone']} - {format_date(item['deadline'])}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_milestone = st.text_input("Milestone", 
                                                 value=item['milestone'],
                                                 key=f"mile_{item['id']}")
                    new_deadline = st.date_input("Deadline", 
                                                value=item['deadline'],
                                                key=f"dead_{item['id']}")
                
                with col2:
                    new_status = st.selectbox("Status",
                                            ['pending', 'in_progress', 'completed'],
                                            index=['pending', 'in_progress', 'completed'].index(item['status']),
                                            key=f"stat_{item['id']}")
                
                col_save, col_delete = st.columns(2)
                
                with col_save:
                    if st.button("💾 Save", key=f"save_time_{item['id']}"):
                        update_data = {
                            'milestone': new_milestone,
                            'deadline': new_deadline,
                            'status': new_status
                        }
                        update_record('timeline', update_data, 'id = %s', (item['id'],))
                        show_success("Milestone updated!")
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"del_time_{item['id']}"):
                        delete_record('timeline', 'id = %s', (item['id'],))
                        show_success("Milestone deleted!")
                        st.rerun()
    else:
        show_info("No milestones added yet")
    
    st.divider()
    
    # Add new milestone
    st.subheader("➕ Add New Milestone")
    
    with st.form("add_milestone"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            milestone = st.text_input("Milestone Name*", placeholder="e.g., Design Approval")
        with col2:
            deadline = st.date_input("Deadline", value=date.today())
        with col3:
            status = st.selectbox("Status", ['pending', 'in_progress', 'completed'])
        
        submit = st.form_submit_button("Add Milestone", type="primary")
        
        if submit:
            if not milestone:
                show_error("Please enter milestone name")
            else:
                timeline_data = {
                    'project_id': project_id,
                    'milestone': milestone,
                    'deadline': deadline,
                    'status': status
                }
                insert_record('timeline', timeline_data)
                show_success("Milestone added successfully!")
                st.rerun()
