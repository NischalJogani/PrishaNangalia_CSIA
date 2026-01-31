"""
Designer Dashboard Module
Contains all functionality for the interior designer's dashboard
"""

import streamlit as st
from database import insert_record, get_records, update_record, delete_record, execute_query
from auth import register_client, get_current_user_id
from utils import (
    save_uploaded_file, display_image, format_currency, format_date, format_datetime,
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
    
    designer_id = get_current_user_id()
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 Your Projects", "👥 View Client Codes", "➕ Create New"])
    
    with tab1:
        show_existing_projects_tab(designer_id)
    
    with tab2:
        show_client_codes_tab(designer_id)
    
    with tab3:
        show_create_new_tab(designer_id)

def show_existing_projects_tab(designer_id):
    """Display existing projects in a tab"""
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
    else:
        show_info("No projects yet. Create your first project in the 'Create New' tab!")

def show_client_codes_tab(designer_id):
    """Display all clients with their access codes"""
    st.subheader("👥 Client Access Codes")
    st.caption("View login credentials for all your clients")
    
    # Get all clients for this designer
    clients = execute_query("""
        SELECT DISTINCT u.id, u.name, u.email, u.client_code, u.created_at
        FROM users u
        JOIN projects p ON u.id = p.client_id
        WHERE p.designer_id = %s AND u.role = 'client'
        ORDER BY u.created_at DESC
    """, (designer_id,), fetch_all=True)
    
    if clients:
        st.success(f"**Total Clients:** {len(clients)}")
        st.markdown("---")
        
        for client in clients:
            with st.expander(f"👤 {client['name']}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📧 Email:**")
                    st.code(client['email'], language=None)
                    
                with col2:
                    st.markdown("**🔐 8-Digit Access Code:**")
                    st.code(client['client_code'], language=None)
                
                st.caption(f"Created: {format_datetime(client['created_at'])}")
                
                # Instructions
                st.markdown("---")
                st.info(f"""
**📋 Share these credentials with {client['name']}:**

1. Go to the login page
2. Click the **"Client"** tab
3. Enter:
   - **Email:** `{client['email']}`
   - **Access Code:** `{client['client_code']}`
4. Click Login
                """)
    else:
        show_info("No clients yet. Create your first client in the 'Create New' tab!")

def show_create_new_tab(designer_id):
    """Display create new client form in a tab"""
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
                    
                    show_success(f"✓ Client and project created successfully!")
                    
                    # Display client access code prominently
                    st.markdown("---")
                    st.markdown("### 🔑 Client Login Credentials")
                    st.success("**Share these credentials with your client:**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**📧 Email:**\n\n`{client_email}`")
                    with col2:
                        st.info(f"**🔐 Access Code:**\n\n`{client_code}`")
                    
                    st.markdown("---")
                    st.info("💡 **Instructions for client:** Go to the login page, select 'Client' and enter the email and access code above.")
                    
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
        show_budget_overview()
    elif choice == "Materials & Suppliers":
        show_suppliers_management()
    elif choice == "Measurements & Drawings":
        show_measurements_drawings()
    elif choice == "Client Timeline":
        show_client_timeline()
    elif choice == "Client Feedback":
        show_feedback_approvals()

# =====================================================
# 5. BUDGET OVERVIEW  
# =====================================================
"""
Designer Budget Management Module
Handles budget overview and expense tracking
"""

import streamlit as st
from database import insert_record, get_records, update_record, delete_record
from utils import format_currency, show_success, show_error, show_info, calculate_budget_statistics

def show_budget_overview():
    """
    Display budget overview interface
    Track estimated vs actual costs
    """
    st.header("💰 Budget Overview")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_info("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Get all budget items
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
            difference_color = "red" if stats['over_budget'] else "green"
            st.metric(
                "Difference", 
                format_currency(abs(stats['difference'])),
                delta=f"{'Over' if stats['over_budget'] else 'Under'} Budget",
                delta_color="inverse" if stats['over_budget'] else "normal"
            )
        
        st.divider()
        
        # Display and edit budget items
        st.subheader("📊 Budget Items")
        
        for item in budget_items:
            with st.expander(f"💵 {item['item_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    estimated = st.number_input(
                        "Estimated Cost (₹)",
                        min_value=0.0,
                        value=float(item['estimated_cost']),
                        step=1000.0,
                        key=f"est_{item['id']}"
                    )
                
                with col2:
                    actual = st.number_input(
                        "Actual Cost (₹)",
                        min_value=0.0,
                        value=float(item['actual_cost']),
                        step=1000.0,
                        key=f"act_{item['id']}"
                    )
                
                col_save, col_delete = st.columns(2)
                
                with col_save:
                    if st.button("💾 Save", key=f"save_budget_{item['id']}"):
                        update_data = {
                            'estimated_cost': estimated,
                            'actual_cost': actual
                        }
                        update_record('budget_items', update_data, 'id = %s', (item['id'],))
                        show_success("Budget item updated!")
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"del_budget_{item['id']}"):
                        delete_record('budget_items', 'id = %s', (item['id'],))
                        show_success("Budget item deleted!")
                        st.rerun()
        
        st.divider()
    
    # Add new budget item
    st.subheader("➕ Add New Budget Item")
    
    with st.form("add_budget_item"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            item_name = st.text_input("Item Name", placeholder="e.g., Sofa Set")
        with col2:
            estimated_cost = st.number_input("Estimated Cost (₹)", min_value=0.0, step=1000.0)
        with col3:
            actual_cost = st.number_input("Actual Cost (₹)", min_value=0.0, step=1000.0)
        
        submit = st.form_submit_button("Add Budget Item", type="primary")
        
        if submit and item_name:
            budget_data = {
                'project_id': project_id,
                'item_name': item_name,
                'estimated_cost': estimated_cost,
                'actual_cost': actual_cost
            }
            insert_record('budget_items', budget_data)
            show_success("Budget item added successfully!")
            st.rerun()

# =====================================================
# 6. MATERIALS & SUPPLIERS
# =====================================================
"""
Designer Suppliers Management Module
Handles supplier contact information and search
"""

import streamlit as st
from database import insert_record, get_records, update_record, delete_record
from utils import show_success, show_error, show_info

def show_suppliers_management():
    """
    Display suppliers management interface
    Add, search, and manage supplier contacts
    """
    st.header("📦 Materials & Suppliers")
    
    # Search bar
    st.subheader("🔍 Search Suppliers")
    search_term = st.text_input("Search by name, category, or contact", placeholder="Enter search term...")
    
    # Get all suppliers
    if search_term:
        # Search in name, category, phone, email
        suppliers = get_records('suppliers', 
                               'name LIKE %s OR category LIKE %s OR phone LIKE %s OR email LIKE %s',
                               (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    else:
        suppliers = get_records('suppliers')
    
    # Display suppliers
    if suppliers:
        st.subheader(f"📋 Suppliers ({len(suppliers)} found)")
        
        # Group by category
        categories = {}
        for supplier in suppliers:
            cat = supplier.get('category', 'Uncategorized')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(supplier)
        
        # Display by category
        for category, supplier_list in categories.items():
            with st.expander(f"📁 {category} ({len(supplier_list)} suppliers)"):
                for supplier in supplier_list:
                    st.markdown(f"### {supplier['name']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**📞 Phone:** {supplier['phone'] or 'N/A'}")
                        st.write(f"**📧 Email:** {supplier['email'] or 'N/A'}")
                    with col2:
                        st.write(f"**🏷️ Category:** {supplier['category'] or 'N/A'}")
                        st.write(f"**📍 Address:** {supplier['address'] or 'N/A'}")
                    
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_sup_{supplier['id']}"):
                            st.session_state[f'edit_supplier_{supplier["id"]}'] = True
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️ Delete", key=f"del_sup_{supplier['id']}"):
                            delete_record('suppliers', 'id = %s', (supplier['id'],))
                            show_success("Supplier deleted!")
                            st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f'edit_supplier_{supplier["id"]}'):
                        with st.form(f"edit_supplier_form_{supplier['id']}"):
                            st.write("**Edit Supplier**")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                new_name = st.text_input("Name", value=supplier['name'])
                                new_category = st.text_input("Category", value=supplier['category'] or '')
                                new_phone = st.text_input("Phone", value=supplier['phone'] or '')
                            with col2:
                                new_email = st.text_input("Email", value=supplier['email'] or '')
                                new_address = st.text_area("Address", value=supplier['address'] or '')
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                save = st.form_submit_button("💾 Save Changes")
                            with col_cancel:
                                cancel = st.form_submit_button("❌ Cancel")
                            
                            if save:
                                update_data = {
                                    'name': new_name,
                                    'category': new_category,
                                    'phone': new_phone,
                                    'email': new_email,
                                    'address': new_address
                                }
                                update_record('suppliers', update_data, 'id = %s', (supplier['id'],))
                                del st.session_state[f'edit_supplier_{supplier["id"]}']
                                show_success("Supplier updated!")
                                st.rerun()
                            
                            if cancel:
                                del st.session_state[f'edit_supplier_{supplier["id"]}']
                                st.rerun()
                    
                    st.divider()
    else:
        show_info("No suppliers found. Add some below!")
    
    st.divider()
    
    # Add new supplier
    st.subheader("➕ Add New Supplier")
    
    with st.form("add_supplier"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Supplier Name*", placeholder="ABC Furniture Co.")
            category = st.selectbox("Category", 
                                   ["Furniture", "Lighting", "Paint", "Flooring", 
                                    "Electricals", "Plumbing", "Fabrics", "Accessories", "Other"])
            phone = st.text_input("Phone", placeholder="+91 XXXXXXXXXX")
        
        with col2:
            email = st.text_input("Email", placeholder="supplier@example.com")
            address = st.text_area("Address", placeholder="Full address...")
        
        submit = st.form_submit_button("Add Supplier", type="primary")
        
        if submit:
            if not name:
                show_error("Please enter supplier name")
            else:
                supplier_data = {
                    'name': name,
                    'category': category,
                    'phone': phone,
                    'email': email,
                    'address': address
                }
                insert_record('suppliers', supplier_data)
                show_success("Supplier added successfully!")
                st.rerun()

# =====================================================
# 7. MEASUREMENTS & DRAWINGS
# =====================================================
"""
Designer Measurements & Drawings Module
Handles CAD files and site measurements
"""

import streamlit as st
from database import insert_record, get_records, delete_record, update_record
from utils import save_uploaded_file, display_image, show_success, show_error, show_info, format_datetime
import config

def show_measurements_drawings():
    """
    Display measurements and drawings interface
    Two tabs: Existing Site Drawings and Proposed Design Drawings
    """
    st.header("📐 Measurements & Drawings")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_info("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Two tabs for existing and proposed
    tab1, tab2 = st.tabs(["📏 Existing Site Drawings", "🎨 Proposed Design Drawings"])
    
    with tab1:
        show_measurement_section(project_id, 'existing')
    
    with tab2:
        show_measurement_section(project_id, 'proposed')

def show_measurement_section(project_id, measurement_type):
    """
    Display measurement section for a specific type
    
    Args:
        project_id: Project ID
        measurement_type: 'existing' or 'proposed'
    """
    type_title = "Existing Site" if measurement_type == 'existing' else "Proposed Design"
    
    # Upload new measurement/drawing
    st.subheader(f"📤 Upload {type_title} Drawing")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            f"Choose file (CAD/Image)", 
            type=config.ALLOWED_DRAWING_EXTENSIONS,
            key=f"upload_{measurement_type}"
        )
    with col2:
        notes = st.text_area("Notes", key=f"notes_{measurement_type}", 
                            placeholder="Add any notes about this drawing...")
    
    if st.button(f"Upload Drawing", key=f"btn_upload_{measurement_type}", type="primary") and uploaded_file:
        file_path = save_uploaded_file(uploaded_file, project_id, 'drawing')
        if file_path:
            measurement_data = {
                'project_id': project_id,
                'type': measurement_type,
                'notes': notes,
                'file_path': file_path
            }
            insert_record('measurements', measurement_data)
            show_success(f"{type_title} drawing uploaded successfully!")
            st.rerun()
    
    st.divider()
    
    # Display existing measurements
    st.subheader(f"📁 Existing {type_title} Drawings")
    
    measurements = get_records('measurements', 
                              'project_id = %s AND type = %s', 
                              (project_id, measurement_type))
    
    if measurements:
        for measurement in measurements:
            with st.expander(f"📄 Drawing #{measurement['id']} - {format_datetime(measurement['uploaded_at'])}"):
                # Display image if it's an image file
                file_ext = measurement['file_path'].split('.')[-1].lower()
                if file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                    display_image(measurement['file_path'])
                else:
                    st.info(f"📎 File: {measurement['file_path'].split('/')[-1]}")
                
                if measurement['notes']:
                    st.write(f"**Notes:** {measurement['notes']}")
                
                # Edit notes
                new_notes = st.text_area("Update Notes", 
                                        value=measurement['notes'] or '',
                                        key=f"edit_notes_{measurement['id']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Notes", key=f"save_meas_{measurement['id']}"):
                        update_record('measurements', 
                                    {'notes': new_notes}, 
                                    'id = %s', 
                                    (measurement['id'],))
                        show_success("Notes updated!")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key=f"del_meas_{measurement['id']}"):
                        delete_record('measurements', 'id = %s', (measurement['id'],))
                        show_success("Drawing deleted!")
                        st.rerun()
    else:
        show_info(f"No {type_title.lower()} drawings uploaded yet")

# =====================================================
# 8. CLIENT TIMELINE
# =====================================================
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

# =====================================================
# 9. CLIENT FEEDBACK & APPROVALS
# =====================================================
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

