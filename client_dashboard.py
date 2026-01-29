"""
Client Dashboard Module
Contains all functionality for the client's dashboard (mostly view-only)
"""

import streamlit as st
from database import get_records, insert_record, execute_query
from utils import (
    display_image, format_currency, format_date, format_datetime,
    show_success, show_error, show_info, calculate_budget_statistics,
    calculate_task_completion, save_uploaded_file
)
import config

# =====================================================
# CLIENT DASHBOARD MAIN
# =====================================================

def show_client_dashboard():
    """
    Main function to display the client dashboard
    Calls appropriate sub-functions based on navigation
    """
    st.sidebar.title("👤 Client Dashboard")
    st.sidebar.write(f"Welcome, {st.session_state.get('user_name', 'Client')}!")
    
    # Get client's project
    client_id = st.session_state.get('user_id')
    project = get_records('projects', 'client_id = %s', (client_id,))
    
    if not project:
        st.error("No project found for your account. Please contact your designer.")
        return
    
    project = project[0]
    project_id = project['id']
    
    # Store project info in session
    st.session_state['client_project_id'] = project_id
    
    # Get designer info
    designer = get_records('users', 'id = %s', (project['designer_id'],))
    if designer:
        st.sidebar.info(f"📧 Your Designer: {designer[0]['name']}\n{designer[0]['email']}")
    
    # Navigation menu
    menu_options = [
        "Reference Library",
        "Task Progress",
        "Budget Overview",
        "Measurements & Drawings",
        "Design Gallery",
        "Timeline Tracker",
        "Feedback & Approval"
    ]
    
    choice = st.sidebar.radio("Navigate to:", menu_options)
    
    # Route to appropriate function
    if choice == "Reference Library":
        show_client_reference_library(project_id)
    elif choice == "Task Progress":
        show_client_task_progress(project_id)
    elif choice == "Budget Overview":
        show_client_budget_overview(project_id)
    elif choice == "Measurements & Drawings":
        show_client_measurements(project_id)
    elif choice == "Design Gallery":
        show_client_gallery(project_id)
    elif choice == "Timeline Tracker":
        show_client_timeline(project_id)
    elif choice == "Feedback & Approval":
        show_client_feedback(project_id)

# =====================================================
# 1. REFERENCE LIBRARY (VIEW ONLY)
# =====================================================

def show_client_reference_library(project_id):
    """
    Display reference library - view only for clients
    """
    st.header("📚 Reference Library")
    st.caption("View reference images organized by room")
    
    references = get_records('reference_library', 'project_id = %s', (project_id,))
    
    if references:
        # Group by room
        rooms = {}
        for ref in references:
            room = ref['room_name']
            if room not in rooms:
                rooms[room] = []
            rooms[room].append(ref)
        
        # Display by room
        for room, images in rooms.items():
            st.subheader(f"🏠 {room}")
            cols = st.columns(3)
            for idx, img in enumerate(images):
                with cols[idx % 3]:
                    display_image(img['file_path'], width=200)
            st.divider()
    else:
        show_info("No reference images available yet. Your designer will upload them soon.")

# =====================================================
# 2. TASK PROGRESS (VIEW ONLY)
# =====================================================

def show_client_task_progress(project_id):
    """
    Display task progress - view only for clients
    """
    st.header("✅ Task Progress")
    st.caption("View project task completion status")
    
    tasks = get_records('tasks', 'project_id = %s', (project_id,))
    
    if tasks:
        # Show overall progress
        overall_progress = calculate_task_completion(tasks)
        st.metric("Overall Project Completion", f"{overall_progress:.1f}%")
        st.progress(overall_progress / 100)
        
        st.divider()
        
        # Group tasks by progress
        completed_tasks = [t for t in tasks if t['progress_percent'] == 100]
        in_progress_tasks = [t for t in tasks if 0 < t['progress_percent'] < 100]
        pending_tasks = [t for t in tasks if t['progress_percent'] == 0]
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Completed", len(completed_tasks))
        with col2:
            st.metric("🔄 In Progress", len(in_progress_tasks))
        with col3:
            st.metric("⏳ Pending", len(pending_tasks))
        
        st.divider()
        
        # Display tasks
        st.subheader("📋 Task List")
        
        for task in tasks:
            status_emoji = '✅' if task['progress_percent'] == 100 else '🔄' if task['progress_percent'] > 0 else '⏳'
            
            with st.expander(f"{status_emoji} {task['title']} - {task['progress_percent']}%"):
                if task['description']:
                    st.write(f"**Description:** {task['description']}")
                
                st.progress(task['progress_percent'] / 100)
                
                if task['comments']:
                    st.write(f"**Designer Notes:** {task['comments']}")
    else:
        show_info("No tasks available yet.")

# =====================================================
# 3. BUDGET OVERVIEW (VIEW ONLY)
# =====================================================

def show_client_budget_overview(project_id):
    """
    Display budget overview - view only for clients
    """
    st.header("💰 Budget Overview")
    st.caption("View project budget and expenses")
    
    budget_items = get_records('budget_items', 'project_id = %s', (project_id,))
    
    if budget_items:
        # Calculate statistics
        stats = calculate_budget_statistics(budget_items)
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Estimated", format_currency(stats['total_estimated']))
        with col2:
            st.metric("Total Actual", format_currency(stats['total_actual']))
        with col3:
            st.metric(
                "Difference", 
                format_currency(abs(stats['difference'])),
                delta=f"{'Over' if stats['over_budget'] else 'Under'} Budget"
            )
        
        st.divider()
        
        # Display budget items
        st.subheader("📊 Budget Breakdown")
        
        for item in budget_items:
            with st.expander(f"💵 {item['item_name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Estimated", format_currency(item['estimated_cost']))
                with col2:
                    st.metric("Actual", format_currency(item['actual_cost']))
    else:
        show_info("Budget details will be available soon.")

# =====================================================
# 4. MEASUREMENTS & DRAWINGS (VIEW ONLY)
# =====================================================

def show_client_measurements(project_id):
    """
    Display measurements and drawings - view only for clients
    """
    st.header("📐 Measurements & Drawings")
    st.caption("View site measurements and design drawings")
    
    tab1, tab2 = st.tabs(["📏 Existing Site Drawings", "🎨 Proposed Design Drawings"])
    
    with tab1:
        show_client_measurement_tab(project_id, 'existing')
    
    with tab2:
        show_client_measurement_tab(project_id, 'proposed')

def show_client_measurement_tab(project_id, measurement_type):
    """Display measurement tab for clients"""
    type_title = "Existing Site" if measurement_type == 'existing' else "Proposed Design"
    
    measurements = get_records('measurements', 
                              'project_id = %s AND type = %s', 
                              (project_id, measurement_type))
    
    if measurements:
        for measurement in measurements:
            with st.expander(f"📄 Drawing - {format_datetime(measurement['uploaded_at'])}"):
                # Display image if it's an image file
                file_ext = measurement['file_path'].split('.')[-1].lower()
                if file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                    display_image(measurement['file_path'])
                else:
                    st.info(f"📎 File: {measurement['file_path'].split('/')[-1]}")
                
                if measurement['notes']:
                    st.write(f"**Notes:** {measurement['notes']}")
    else:
        show_info(f"No {type_title.lower()} drawings available yet.")

# =====================================================
# 5. DESIGN GALLERY (CLIENT CAN UPLOAD)
# =====================================================

def show_client_gallery(project_id):
    """
    Display design gallery - clients can upload inspiration images
    """
    st.header("🎨 Design Gallery")
    st.caption("Upload your inspiration images and view designer's selections")
    
    # Upload section for client
    st.subheader("📤 Upload Your Inspiration Images")
    
    uploaded_files = st.file_uploader(
        "Choose images", 
        type=config.ALLOWED_IMAGE_EXTENSIONS,
        accept_multiple_files=True,
        key="client_gallery_upload"
    )
    
    if st.button("Upload Images", type="primary") and uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = save_uploaded_file(uploaded_file, project_id, 'gallery')
            if file_path:
                gallery_data = {
                    'project_id': project_id,
                    'uploaded_by': 'client',
                    'file_path': file_path
                }
                insert_record('gallery', gallery_data)
        show_success(f"{len(uploaded_files)} image(s) uploaded successfully!")
        st.rerun()
    
    st.divider()
    
    # Display all gallery images
    st.subheader("🖼️ Gallery")
    
    gallery_items = get_records('gallery', 'project_id = %s ORDER BY uploaded_at DESC', (project_id,))
    
    if gallery_items:
        # Separate by uploader
        client_images = [g for g in gallery_items if g['uploaded_by'] == 'client']
        designer_images = [g for g in gallery_items if g['uploaded_by'] == 'designer']
        
        tab1, tab2 = st.tabs([f"Your Uploads ({len(client_images)})", f"Designer's Selections ({len(designer_images)})"])
        
        with tab1:
            if client_images:
                cols = st.columns(3)
                for idx, img in enumerate(client_images):
                    with cols[idx % 3]:
                        display_image(img['file_path'], width=200)
            else:
                show_info("You haven't uploaded any images yet.")
        
        with tab2:
            if designer_images:
                cols = st.columns(3)
                for idx, img in enumerate(designer_images):
                    with cols[idx % 3]:
                        display_image(img['file_path'], width=200)
            else:
                show_info("Designer hasn't uploaded any images yet.")
    else:
        show_info("No gallery images yet. Upload your inspiration above!")

# =====================================================
# 6. TIMELINE TRACKER (VIEW ONLY)
# =====================================================

def show_client_timeline(project_id):
    """
    Display project timeline - view only for clients
    """
    st.header("📅 Timeline Tracker")
    st.caption("View project milestones and deadlines")
    
    timeline_items = get_records('timeline', 'project_id = %s ORDER BY deadline', (project_id,))
    
    if timeline_items:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        pending = len([t for t in timeline_items if t['status'] == 'pending'])
        in_progress = len([t for t in timeline_items if t['status'] == 'in_progress'])
        completed = len([t for t in timeline_items if t['status'] == 'completed'])
        
        with col1:
            st.metric("⏳ Pending", pending)
        with col2:
            st.metric("🔄 In Progress", in_progress)
        with col3:
            st.metric("✅ Completed", completed)
        
        st.divider()
        
        # Display timeline
        st.subheader("📋 Project Milestones")
        
        for item in timeline_items:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅'
            }
            
            status_color = {
                'pending': 'orange',
                'in_progress': 'blue',
                'completed': 'green'
            }
            
            st.markdown(f"### {status_emoji[item['status']]} {item['milestone']}")
            st.markdown(f"**Deadline:** {format_date(item['deadline'])}")
            st.markdown(f"**Status:** :{status_color[item['status']]}[{item['status'].replace('_', ' ').title()}]")
            st.divider()
    else:
        show_info("Timeline will be available soon.")

# =====================================================
# 7. FEEDBACK & APPROVAL
# =====================================================

def show_client_feedback(project_id):
    """
    Feedback and approval interface - clients can provide feedback
    """
    st.header("💬 Feedback & Approval")
    st.caption("Provide feedback and approve/reject design elements")
    
    # Add new feedback
    st.subheader("➕ Submit Feedback")
    
    with st.form("client_feedback"):
        item_type = st.selectbox("Feedback Type", ["drawing", "image"])
        comment = st.text_area("Your Comment/Feedback", 
                              placeholder="Share your thoughts, concerns, or approval...")
        approval_status = st.radio("Approval Status", 
                                  ["pending", "approved", "rejected"],
                                  horizontal=True)
        
        submit = st.form_submit_button("Submit Feedback", type="primary")
        
        if submit:
            if not comment:
                show_error("Please provide a comment")
            else:
                feedback_data = {
                    'project_id': project_id,
                    'item_type': item_type,
                    'comment': comment,
                    'approval_status': approval_status
                }
                insert_record('feedback', feedback_data)
                show_success("Feedback submitted successfully!")
                st.rerun()
    
    st.divider()
    
    # Display previous feedback
    st.subheader("📝 Your Previous Feedback")
    
    feedback_items = get_records('feedback', 
                                'project_id = %s ORDER BY created_at DESC', 
                                (project_id,))
    
    if feedback_items:
        for feedback in feedback_items:
            status_emoji = {
                'approved': '✅',
                'pending': '⏳',
                'rejected': '❌'
            }
            
            with st.expander(f"{status_emoji[feedback['approval_status']]} {feedback['item_type'].title()} - {format_datetime(feedback['created_at'])}"):
                st.markdown(f"**Type:** {feedback['item_type'].title()}")
                st.markdown(f"**Status:** {feedback['approval_status'].title()}")
                st.markdown(f"**Date:** {format_datetime(feedback['created_at'])}")
                st.markdown(f"**Your Comment:**")
                st.info(feedback['comment'])
    else:
        show_info("No feedback submitted yet.")
