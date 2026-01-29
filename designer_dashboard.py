"""
Designer Dashboard Module
Contains all functionality for the interior designer's dashboard
"""

import streamlit as st
from database import insert_record, get_records, update_record, delete_record, execute_query
from auth import register_client, get_current_user_id
from utils import (
    save_uploaded_file, display_image, format_currency, format_date,
    show_success, show_error, show_info, show_warning, create_project_directories,
    is_valid_file_extension, calculate_budget_statistics, calculate_task_completion
)
import config
from datetime import date

# =====================================================
# 1. PROJECT MANAGEMENT
# =====================================================

def show_project_management():
    """
    Display project management interface for designers
    Allows creating new clients and projects
    """
    st.header("📁 Project Management")
    
    # Show existing projects
    designer_id = get_current_user_id()
    projects = execute_query("""
        SELECT p.*, c.name as client_name, c.email as client_email 
        FROM projects p 
        JOIN users c ON p.client_id = c.id 
        WHERE p.designer_id = %s 
        ORDER BY p.created_at DESC
    """, (designer_id,), fetch_all=True)
    
    if projects:
        st.subheader("Your Projects")
        for project in projects:
            with st.expander(f"📋 {project['client_name']} - {project['site_type']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Client:** {project['client_name']}")
                    st.write(f"**Email:** {project['client_email']}")
                    st.write(f"**Site Type:** {project['site_type']}")
                with col2:
                    st.write(f"**Created:** {format_date(project['created_at'])}")
                    st.write(f"**Contact Details:** {project['contact_details']}")
                    st.write(f"**Preferred Contact:** {project['preferred_contact']}")
                
                # Set as active project button
                if st.button(f"Select This Project", key=f"select_{project['id']}"):
                    st.session_state['active_project_id'] = project['id']
                    st.session_state['active_project_name'] = project['client_name']
                    show_success(f"Project '{project['client_name']}' selected!")
                    st.rerun()
    
    st.divider()
    
    # Create new client and project
    st.subheader("➕ Create New Client & Project")
    
    with st.form("new_client_project"):
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("Client Name*", placeholder="John Doe")
            client_email = st.text_input("Client Email*", placeholder="client@example.com")
            site_type = st.selectbox("Site Type*", 
                                    ["Residential", "Commercial", "Office", "Restaurant", "Retail", "Other"])
        
        with col2:
            contact_details = st.text_area("Contact Details", 
                                          placeholder="Phone: +91 XXXXXXXXXX\nAddress: ...")
            preferred_contact = st.selectbox("Preferred Contact Method", 
                                            ["Email", "Phone", "WhatsApp", "Any"])
        
        submit = st.form_submit_button("Create Client & Project", type="primary")
        
        if submit:
            if not client_name or not client_email:
                show_error("Please fill in all required fields marked with *")
            else:
                # Create client account
                success, message, client_code = register_client(client_name, client_email, designer_id)
                
                if success:
                    # Get the newly created client's ID
                    client = get_records('users', 'email = %s', (client_email,))
                    client_id = client[0]['id']
                    
                    # Create project
                    project_data = {
                        'client_id': client_id,
                        'designer_id': designer_id,
                        'site_type': site_type,
                        'contact_details': contact_details,
                        'preferred_contact': preferred_contact
                    }
                    project_id = insert_record('projects', project_data)
                    
                    # Create project directories
                    create_project_directories(project_id)
                    
                    # Initialize default tasks
                    initialize_default_tasks(project_id)
                    
                    # Initialize default budget items
                    initialize_default_budget(project_id)
                    
                    show_success(f"Client and project created successfully!")
                    st.info(f"🔑 **Client Access Code:** `{client_code}` - Share this with your client!")
                    st.balloons()
                    st.rerun()
                else:
                    show_error(message)

def initialize_default_tasks(project_id):
    """Initialize default task list for a new project"""
    for task_title in config.DEFAULT_TASKS:
        task_data = {
            'project_id': project_id,
            'title': task_title,
            'description': '',
            'progress_percent': 0,
            'comments': ''
        }
        insert_record('tasks', task_data)

def initialize_default_budget(project_id):
    """Initialize default budget categories for a new project"""
    for category in config.DEFAULT_BUDGET_CATEGORIES:
        budget_data = {
            'project_id': project_id,
            'item_name': category,
            'estimated_cost': 0,
            'actual_cost': 0
        }
        insert_record('budget_items', budget_data)

# =====================================================
# 2. REFERENCE LIBRARY
# =====================================================

def show_reference_library():
    """
    Display reference library interface
    Upload and organize images by room
    """
    st.header("📚 Reference Library")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_warning("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Upload new reference images
    st.subheader("📤 Upload Reference Images")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Choose images", 
            type=config.ALLOWED_IMAGE_EXTENSIONS,
            accept_multiple_files=True,
            key="ref_library_upload"
        )
    with col2:
        room_name = st.text_input("Room Name", placeholder="Living Room")
    
    if st.button("Upload Images", type="primary") and uploaded_files:
        if not room_name:
            show_error("Please enter a room name")
        else:
            for uploaded_file in uploaded_files:
                file_path = save_uploaded_file(uploaded_file, project_id, 'reference')
                if file_path:
                    ref_data = {
                        'project_id': project_id,
                        'room_name': room_name,
                        'file_path': file_path
                    }
                    insert_record('reference_library', ref_data)
            show_success(f"{len(uploaded_files)} image(s) uploaded successfully!")
            st.rerun()
    
    st.divider()
    
    # Display existing references organized by room
    st.subheader("🖼️ Existing References")
    
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
            with st.expander(f"🏠 {room} ({len(images)} images)"):
                cols = st.columns(3)
                for idx, img in enumerate(images):
                    with cols[idx % 3]:
                        display_image(img['file_path'], width=200)
                        if st.button("🗑️ Delete", key=f"del_ref_{img['id']}"):
                            delete_record('reference_library', 'id = %s', (img['id'],))
                            show_success("Image deleted")
                            st.rerun()
    else:
        show_info("No reference images uploaded yet")

# =====================================================
# 3. TASK TRACKING
# =====================================================

def show_task_tracking():
    """
    Display task tracking interface
    Manage tasks with progress sliders and comments
    """
    st.header("✅ Task Tracking")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_warning("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Add custom task
    with st.expander("➕ Add Custom Task"):
        with st.form("add_task"):
            task_title = st.text_input("Task Title")
            task_description = st.text_area("Description")
            submit = st.form_submit_button("Add Task")
            
            if submit and task_title:
                task_data = {
                    'project_id': project_id,
                    'title': task_title,
                    'description': task_description,
                    'progress_percent': 0,
                    'comments': ''
                }
                insert_record('tasks', task_data)
                show_success("Task added successfully!")
                st.rerun()
    
    st.divider()
    
    # Display and edit tasks
    tasks = get_records('tasks', 'project_id = %s', (project_id,))
    
    if tasks:
        # Show overall progress
        overall_progress = calculate_task_completion(tasks)
        st.metric("Overall Project Completion", f"{overall_progress:.1f}%")
        st.progress(overall_progress / 100)
        
        st.subheader("📋 Task List")
        
        for task in tasks:
            with st.expander(f"{'✓' if task['progress_percent'] == 100 else '○'} {task['title']} ({task['progress_percent']}%)"):
                if task['description']:
                    st.write(f"**Description:** {task['description']}")
                
                # Progress slider
                progress = st.slider(
                    "Progress", 
                    0, 100, 
                    task['progress_percent'],
                    key=f"progress_{task['id']}"
                )
                
                # Comments
                comments = st.text_area(
                    "Comments",
                    task['comments'] or '',
                    key=f"comments_{task['id']}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Changes", key=f"save_task_{task['id']}"):
                        update_data = {
                            'progress_percent': progress,
                            'comments': comments
                        }
                        update_record('tasks', update_data, 'id = %s', (task['id'],))
                        show_success("Task updated!")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete Task", key=f"del_task_{task['id']}"):
                        delete_record('tasks', 'id = %s', (task['id'],))
                        show_success("Task deleted!")
                        st.rerun()
    else:
        show_info("No tasks found. Add some custom tasks above!")

# =====================================================
# 4. WHITEBOARD & NOTES
# =====================================================

def show_whiteboard_notes():
    """
    Display whiteboard and notes interface
    Drawing canvas and text notes
    """
    st.header("📝 Whiteboard & Notes")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_warning("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Text notes section
    st.subheader("📄 Text Notes")
    
    # Get existing notes
    notes = get_records('notes_whiteboard', 'project_id = %s', (project_id,))
    
    # Note input
    note_text = st.text_area("Add/Edit Note", 
                            value=notes[0]['text_note'] if notes else '',
                            height=200)
    
    if st.button("💾 Save Note", type="primary"):
        if notes:
            # Update existing note
            update_record('notes_whiteboard', 
                         {'text_note': note_text}, 
                         'id = %s', 
                         (notes[0]['id'],))
        else:
            # Create new note
            note_data = {
                'project_id': project_id,
                'text_note': note_text
            }
            insert_record('notes_whiteboard', note_data)
        show_success("Note saved successfully!")
        st.rerun()
    
    st.divider()
    
    # Drawing canvas
    st.subheader("🎨 Drawing Canvas")
    st.info("💡 Use streamlit-drawable-canvas for sketching. Install: `pip install streamlit-drawable-canvas`")
    
    try:
        from streamlit_drawable_canvas import st_canvas
        
        # Canvas settings
        drawing_mode = st.selectbox("Drawing tool:", ("freedraw", "line", "rect", "circle", "transform"))
        stroke_width = st.slider("Stroke width:", 1, 25, 3)
        stroke_color = st.color_picker("Stroke color:", "#000000")
        
        # Create canvas
        canvas_result = st_canvas(
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            drawing_mode=drawing_mode,
            height=400,
            width=700,
            key="canvas"
        )
        
        if st.button("💾 Save Drawing"):
            if canvas_result.image_data is not None:
                # Save canvas as image
                from PIL import Image
                import numpy as np
                
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                import io
                
                # Save to file
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Create a mock uploaded file object
                class MockUploadedFile:
                    def __init__(self, bytes_data, name):
                        self.name = name
                        self._bytes = bytes_data
                    
                    def getbuffer(self):
                        return self._bytes.getvalue()
                
                mock_file = MockUploadedFile(img_bytes, f"whiteboard_{project_id}.png")
                file_path = save_uploaded_file(mock_file, project_id, 'whiteboard')
                
                if file_path:
                    # Update or create whiteboard record
                    if notes:
                        update_record('notes_whiteboard',
                                    {'drawing_path': file_path},
                                    'id = %s',
                                    (notes[0]['id'],))
                    else:
                        wb_data = {
                            'project_id': project_id,
                            'drawing_path': file_path,
                            'text_note': ''
                        }
                        insert_record('notes_whiteboard', wb_data)
                    
                    show_success("Drawing saved!")
                    st.rerun()
    
    except ImportError:
        st.error("Please install streamlit-drawable-canvas: `pip install streamlit-drawable-canvas`")
    
    # Display saved drawing
    if notes and notes[0].get('drawing_path'):
        st.subheader("📌 Saved Drawing")
        display_image(notes[0]['drawing_path'])

# =====================================================
# MAIN DESIGNER DASHBOARD FUNCTION
# =====================================================

def show_designer_dashboard():
    """
    Main function to display the designer dashboard
    Calls appropriate sub-functions based on navigation
    """
    st.sidebar.title("👨‍🎨 Designer Dashboard")
    st.sidebar.write(f"Welcome, {st.session_state.get('user_name', 'Designer')}!")
    
    # Show active project info
    if st.session_state.get('active_project_id'):
        st.sidebar.success(f"📁 Active: {st.session_state.get('active_project_name')}")
    else:
        st.sidebar.info("ℹ️ No project selected")
    
    # Navigation menu
    menu_options = [
        "Project Management",
        "Reference Library",
        "Task Tracking",
        "Whiteboard & Notes",
        "Budget Overview",
        "Materials & Suppliers",
        "Measurements & Drawings",
        "Client Timeline",
        "Client Feedback"
    ]
    
    choice = st.sidebar.radio("Navigate to:", menu_options)
    
    # Route to appropriate function
    if choice == "Project Management":
        show_project_management()
    elif choice == "Reference Library":
        show_reference_library()
    elif choice == "Task Tracking":
        show_task_tracking()
    elif choice == "Whiteboard & Notes":
        show_whiteboard_notes()
    elif choice == "Budget Overview":
        from designer_budget import show_budget_overview
        show_budget_overview()
    elif choice == "Materials & Suppliers":
        from designer_suppliers import show_suppliers_management
        show_suppliers_management()
    elif choice == "Measurements & Drawings":
        from designer_measurements import show_measurements_drawings
        show_measurements_drawings()
    elif choice == "Client Timeline":
        from designer_timeline import show_client_timeline
        show_client_timeline()
    elif choice == "Client Feedback":
        from designer_feedback import show_feedback_approvals
        show_feedback_approvals()
