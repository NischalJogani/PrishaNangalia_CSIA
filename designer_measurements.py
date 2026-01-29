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
