"""
Utility Functions Module
Helper functions for file uploads, image handling, and common operations
"""

import os
import shutil
from datetime import datetime
from PIL import Image
import streamlit as st
import config

# =====================================================
# FILE UPLOAD HELPERS
# =====================================================

def save_uploaded_file(uploaded_file, project_id, file_type='reference'):
    """
    Save an uploaded file to the appropriate directory
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        project_id: Project ID for organizing files
        file_type: Type of file ('reference', 'drawing', 'gallery', 'whiteboard')
    
    Returns:
        Relative file path or None if error
    """
    try:
        # Determine directory based on file type
        if file_type == 'reference':
            directory = config.REFERENCE_LIBRARY_DIR.format(project_id=project_id)
        elif file_type == 'drawing':
            directory = config.DRAWINGS_DIR.format(project_id=project_id)
        elif file_type == 'gallery':
            directory = config.GALLERY_DIR.format(project_id=project_id)
        elif file_type == 'whiteboard':
            directory = config.WHITEBOARD_DIR.format(project_id=project_id)
        else:
            directory = os.path.join(config.BASE_UPLOAD_DIR, 'projects', str(project_id), 'misc')
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{uploaded_file.name}"
        filepath = os.path.join(directory, filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Return relative path for database storage
        relative_path = os.path.relpath(filepath, config.BASE_UPLOAD_DIR)
        return relative_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def get_full_file_path(relative_path):
    """
    Convert relative file path to full absolute path
    
    Args:
        relative_path: Relative path stored in database
    
    Returns:
        Full absolute path
    """
    return os.path.join(config.BASE_UPLOAD_DIR, relative_path)

def delete_file(relative_path):
    """
    Delete a file from storage
    
    Args:
        relative_path: Relative path to the file
    
    Returns:
        Boolean indicating success
    """
    try:
        full_path = get_full_file_path(relative_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

# =====================================================
# IMAGE PROCESSING
# =====================================================

def display_image(file_path, caption=None, width=None):
    """
    Display an image from file path
    
    Args:
        file_path: Path to image file
        caption: Optional caption
        width: Optional width for display
    """
    try:
        full_path = get_full_file_path(file_path)
        if os.path.exists(full_path):
            st.image(full_path, caption=caption, width=width)
        else:
            st.warning("Image file not found")
    except Exception as e:
        st.error(f"Error displaying image: {e}")

def get_image_thumbnail(file_path, size=(200, 200)):
    """
    Create and return thumbnail of an image
    
    Args:
        file_path: Path to image file
        size: Tuple of (width, height) for thumbnail
    
    Returns:
        PIL Image object or None
    """
    try:
        full_path = get_full_file_path(file_path)
        img = Image.open(full_path)
        img.thumbnail(size)
        return img
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None

# =====================================================
# VALIDATION HELPERS
# =====================================================

def is_valid_file_extension(filename, allowed_extensions):
    """
    Check if file has an allowed extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (without dots)
    
    Returns:
        Boolean
    """
    extension = filename.split('.')[-1].lower()
    return extension in [ext.lower() for ext in allowed_extensions]

def validate_email(email):
    """
    Basic email validation
    
    Args:
        email: Email string to validate
    
    Returns:
        Boolean
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength
    Requirements: At least 8 characters
    
    Args:
        password: Password string
    
    Returns:
        Tuple (valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, "Password is valid"

# =====================================================
# FORMATTING HELPERS
# =====================================================

def format_currency(amount):
    """
    Format number as currency
    
    Args:
        amount: Numeric amount
    
    Returns:
        Formatted string
    """
    return f"₹{amount:,.2f}"

def format_date(date_obj):
    """
    Format date object to readable string
    
    Args:
        date_obj: datetime object
    
    Returns:
        Formatted date string
    """
    if date_obj:
        return date_obj.strftime('%d %b %Y')
    return 'Not set'

def format_datetime(datetime_obj):
    """
    Format datetime object to readable string
    
    Args:
        datetime_obj: datetime object
    
    Returns:
        Formatted datetime string
    """
    if datetime_obj:
        return datetime_obj.strftime('%d %b %Y, %I:%M %p')
    return 'Not set'

# =====================================================
# PROJECT HELPERS
# =====================================================

def get_project_directory(project_id):
    """
    Get the full directory path for a project
    
    Args:
        project_id: Project ID
    
    Returns:
        Full directory path
    """
    return os.path.join(config.BASE_UPLOAD_DIR, 'projects', str(project_id))

def create_project_directories(project_id):
    """
    Create all necessary directories for a new project
    
    Args:
        project_id: Project ID
    """
    directories = [
        config.REFERENCE_LIBRARY_DIR.format(project_id=project_id),
        config.DRAWINGS_DIR.format(project_id=project_id),
        config.GALLERY_DIR.format(project_id=project_id),
        config.WHITEBOARD_DIR.format(project_id=project_id)
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def delete_project_files(project_id):
    """
    Delete all files for a project
    
    Args:
        project_id: Project ID
    
    Returns:
        Boolean indicating success
    """
    try:
        project_dir = get_project_directory(project_id)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        return True
    except Exception as e:
        print(f"Error deleting project files: {e}")
        return False

# =====================================================
# STREAMLIT UI HELPERS
# =====================================================

def show_success(message):
    """Display success message"""
    st.success(f"✓ {message}")

def show_error(message):
    """Display error message"""
    st.error(f"✗ {message}")

def show_info(message):
    """Display info message"""
    st.info(f"ℹ {message}")

def show_warning(message):
    """Display warning message"""
    st.warning(f"⚠ {message}")

def create_card(title, content, color="lightblue"):
    """
    Create a styled card/box for displaying information
    
    Args:
        title: Card title
        content: Card content (can be HTML)
        color: Background color
    """
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3 style="margin: 0 0 10px 0;">{title}</h3>
            <div>{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# STATISTICS HELPERS
# =====================================================

def calculate_budget_statistics(budget_items):
    """
    Calculate budget statistics from budget items
    
    Args:
        budget_items: List of budget item dictionaries
    
    Returns:
        Dictionary with statistics
    """
    total_estimated = sum(item.get('estimated_cost', 0) for item in budget_items)
    total_actual = sum(item.get('actual_cost', 0) for item in budget_items)
    difference = total_actual - total_estimated
    
    return {
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'difference': difference,
        'over_budget': difference > 0
    }

def calculate_task_completion(tasks):
    """
    Calculate overall task completion percentage
    
    Args:
        tasks: List of task dictionaries
    
    Returns:
        Average completion percentage
    """
    if not tasks:
        return 0
    
    total_progress = sum(task.get('progress_percent', 0) for task in tasks)
    return total_progress / len(tasks)
