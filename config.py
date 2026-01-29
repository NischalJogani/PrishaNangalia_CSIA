"""
Configuration file for the Interior Design Project Management System
Contains database credentials and application settings
"""

import os
import streamlit as st

# =====================================================
# DATABASE CONFIGURATION
# =====================================================
# Try to load from Streamlit secrets first, fallback to environment variables
try:
    DB_CONFIG = {
        'host': st.secrets["database"]["host"],
        'user': st.secrets["database"]["user"],
        'password': st.secrets["database"]["password"],
        'database': st.secrets["database"]["database"],
        'port': st.secrets["database"].get("port", 3306)
    }
except Exception:
    # Fallback to environment variables or defaults for local development
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'interior_designer_app_prisha_csia'),
        'port': int(os.getenv('DB_PORT', 3306))
    }

# =====================================================
# FILE STORAGE PATHS
# =====================================================
# Base directory for all uploads
BASE_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')

# Subdirectories for organized storage
REFERENCE_LIBRARY_DIR = os.path.join(BASE_UPLOAD_DIR, 'projects', '{project_id}', 'reference')
DRAWINGS_DIR = os.path.join(BASE_UPLOAD_DIR, 'projects', '{project_id}', 'drawings')
GALLERY_DIR = os.path.join(BASE_UPLOAD_DIR, 'projects', '{project_id}', 'gallery')
WHITEBOARD_DIR = os.path.join(BASE_UPLOAD_DIR, 'projects', '{project_id}', 'whiteboard')

# =====================================================
# SESSION & COOKIE SETTINGS
# =====================================================
# Try to load from Streamlit secrets first, fallback to defaults
try:
    COOKIE_NAME = st.secrets["session"]["cookie_name"]
    COOKIE_KEY = st.secrets["session"]["cookie_key"]
    COOKIE_EXPIRY_DAYS = st.secrets["session"]["cookie_expiry_days"]
except Exception:
    # Fallback to environment variables or defaults
    COOKIE_NAME = os.getenv('COOKIE_NAME', 'interior_design_session')
    COOKIE_KEY = os.getenv('COOKIE_KEY', 'interior_design_secret_key_change_in_production')
    COOKIE_EXPIRY_DAYS = int(os.getenv('COOKIE_EXPIRY_DAYS', 30))

# =====================================================
# APPLICATION SETTINGS
# =====================================================
APP_TITLE = "Interior Design Project Management System"
PAGE_ICON = "🏠"

# Default task list for new projects
DEFAULT_TASKS = [
    "Site Survey & Measurements",
    "Conceptual Design",
    "3D Modeling & Visualization",
    "Material Selection",
    "Electrical Layout Planning",
    "Plumbing Layout Planning",
    "Furniture Procurement",
    "Painting & Wall Finishing",
    "Flooring Installation",
    "Lighting Installation",
    "Furniture Installation",
    "Final Styling & Accessories",
    "Quality Check & Handover"
]

# Default budget categories
DEFAULT_BUDGET_CATEGORIES = [
    "Design Fees",
    "Furniture",
    "Lighting Fixtures",
    "Wall Paint & Finishes",
    "Flooring Materials",
    "Kitchen & Bathroom Fittings",
    "Curtains & Blinds",
    "Electrical Work",
    "Plumbing Work",
    "Carpentry",
    "Decorative Accessories",
    "Contingency Fund"
]

# =====================================================
# HELPER FUNCTION TO CREATE UPLOAD DIRECTORIES
# =====================================================
def create_upload_directories():
    """
    Create necessary upload directories if they don't exist
    """
    os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)
    print(f"Upload directories initialized at: {BASE_UPLOAD_DIR}")

# =====================================================
# ALLOWED FILE EXTENSIONS
# =====================================================
ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp']
ALLOWED_DRAWING_EXTENSIONS = ['pdf', 'dwg', 'dxf', 'png', 'jpg', 'jpeg']
