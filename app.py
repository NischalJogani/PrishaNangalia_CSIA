"""
Interior Design Project Management System
Main Streamlit Application Entry Point

This application provides a comprehensive platform for interior designers and their clients
to manage projects, track tasks, budgets, timelines, and collaborate effectively.

Features:
- Role-based authentication (Designer/Client)
- Project management
- Task tracking
- Budget management
- Reference library
- Timeline tracking
- Client feedback system
- And more...

Author: Interior Design Management System
Date: 2026
"""

import streamlit as st
import extra_streamlit_components as stx
from database import test_connection, initialize_database, execute_schema_file, check_tables_exist
from auth import (
    register_designer, login_designer, login_client,
    create_session, save_session_to_cookie, load_session_from_cookie,
    logout, is_logged_in, is_designer, is_client, get_cookie_manager
)
from designer_dashboard import show_designer_dashboard
from client_dashboard import show_client_dashboard
from utils import validate_email, validate_password, show_success, show_error, show_info
import config
import os

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS STYLING
# =====================================================

def load_css():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .success-box {
            padding: 1rem;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

# =====================================================
# INITIALIZATION
# =====================================================

def initialize_app():
    """
    Initialize the application
    - Create upload directories
    - Initialize session state
    - Load cookie manager
    """
    # Create upload directories
    if not os.path.exists(config.BASE_UPLOAD_DIR):
        config.create_upload_directories()
    
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state['initialized'] = True
    
    # Initialize cookie manager
    if 'cookie_manager' not in st.session_state:
        st.session_state['cookie_manager'] = get_cookie_manager()

# =====================================================
# AUTHENTICATION PAGES
# =====================================================

def show_login_page():
    """
    Display login page with options for designer and client login
    """
    st.markdown('<h1 class="main-header">🏠 Interior Design Management System</h1>', unsafe_allow_html=True)
    
    st.write("---")
    
    # Login type selection
    login_type = st.radio("Select Login Type:", ["Interior Designer", "Client"], horizontal=True)
    
    if login_type == "Interior Designer":
        show_designer_login()
    else:
        show_client_login()

def show_designer_login():
    """Designer login form"""
    st.subheader("👨‍🎨 Interior Designer Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("designer_login"):
            email = st.text_input("Email", placeholder="designer@example.com")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me")
            
            submit = st.form_submit_button("Login", type="primary")
            
            if submit:
                if not email or not password:
                    show_error("Please fill in all fields")
                else:
                    success, message, user_data = login_designer(email, password)
                    if success:
                        create_session(user_data)
                        if remember_me:
                            save_session_to_cookie(st.session_state['cookie_manager'], user_data)
                        show_success(message)
                        st.rerun()
                    else:
                        show_error(message)
    
    with tab2:
        with st.form("designer_signup"):
            st.write("Create your designer account")
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="designer@example.com")
            password = st.text_input("Password", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
            
            submit = st.form_submit_button("Sign Up", type="primary")
            
            if submit:
                if not all([name, email, password, password_confirm]):
                    show_error("Please fill in all fields")
                elif password != password_confirm:
                    show_error("Passwords do not match")
                elif not validate_email(email):
                    show_error("Invalid email format")
                else:
                    valid, msg = validate_password(password)
                    if not valid:
                        show_error(msg)
                    else:
                        success, message, user_id = register_designer(name, email, password)
                        if success:
                            show_success(message)
                            st.info("Please login with your credentials")
                        else:
                            show_error(message)

def show_client_login():
    """Client login form"""
    st.subheader("👤 Client Login")
    st.info("ℹ️ Your interior designer will provide you with an access code")
    
    with st.form("client_login"):
        email = st.text_input("Email", placeholder="client@example.com")
        client_code = st.text_input("Access Code", placeholder="ABC123")
        remember_me = st.checkbox("Remember me")
        
        submit = st.form_submit_button("Login", type="primary")
        
        if submit:
            if not email or not client_code:
                show_error("Please fill in all fields")
            else:
                success, message, user_data = login_client(email, client_code.upper())
                if success:
                    create_session(user_data)
                    if remember_me:
                        save_session_to_cookie(st.session_state['cookie_manager'], user_data)
                    show_success(message)
                    st.rerun()
                else:
                    show_error(message)

# =====================================================
# MAIN APPLICATION ROUTING
# =====================================================

def show_main_app():
    """
    Main application logic
    Route to appropriate dashboard based on user role
    """
    # Show logout button in sidebar
    with st.sidebar:
        st.write("---")
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout(st.session_state['cookie_manager'])
            show_success("Logged out successfully!")
            st.rerun()
    
    # Route to appropriate dashboard
    if is_designer():
        show_designer_dashboard()
    elif is_client():
        show_client_dashboard()
    else:
        show_error("Invalid user role")
        logout(st.session_state['cookie_manager'])
        st.rerun()

# =====================================================
# DATABASE SETUP PAGE
# =====================================================

def show_setup_page():
    """
    Show database setup page for first-time setup
    """
    st.title("🔧 Database Setup")
    st.write("Welcome! Let's set up your database.")
    
    with st.expander("📋 Setup Instructions", expanded=True):
        st.markdown("""
        ### Prerequisites:
        1. MySQL server should be running
        2. Credentials should be in `.streamlit/secrets.toml` file
        3. Click the button below to initialize the database
        
        ### Current Configuration:
        """)
        
        # Show current config (without password)
        try:
            st.code(f"""
Host: {config.DB_CONFIG.get('host', 'N/A')}
User: {config.DB_CONFIG.get('user', 'N/A')}
Database: {config.DB_CONFIG.get('database', 'N/A')}
Port: {config.DB_CONFIG.get('port', 'N/A')}
Password: {'***' if config.DB_CONFIG.get('password') else 'NOT SET'}
            """)
        except Exception as e:
            st.error(f"Error reading config: {e}")
        
        st.markdown("""
        ### What this will do:
        - Create the database (if needed)
        - Create all necessary tables
        - Set up the schema
        """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Initialize Database", type="primary", use_container_width=True):
            with st.spinner("Setting up database..."):
                # First check connection
                from database import get_db_connection
                test_conn = get_db_connection()
                if not test_conn:
                    show_error("❌ Cannot connect to MySQL server!")
                    st.error("Please check:")
                    st.markdown("""
                    1. **MySQL is running** - Start your MySQL service
                    2. **Credentials are correct** in `.streamlit/secrets.toml`
                    3. **Database exists** - Create it manually if needed:
                       ```sql
                       CREATE DATABASE interior_designer_app_prisha_csia;
                       ```
                    """)
                    
                    # Show troubleshooting
                    with st.expander("🔍 Troubleshooting"):
                        st.markdown("""
                        **Check MySQL Service:**
                        - Windows: Services → MySQL → Start
                        - Mac: `brew services start mysql`
                        - Linux: `sudo systemctl start mysql`
                        
                        **Test Connection Manually:**
                        ```bash
                        mysql -u root -p
                        ```
                        """)
                    st.stop()
                else:
                    test_conn.close()
                    show_success("✓ MySQL connection successful!")
                
                # Initialize database
                if initialize_database():
                    show_success("✓ Database created/verified!")
                    
                    # Execute schema
                    schema_path = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
                    if execute_schema_file(schema_path):
                        show_success("✓ Database schema created successfully!")
                        st.balloons()
                        
                        # Create upload directories
                        config.create_upload_directories()
                        show_success("✓ Upload directories created!")
                        
                        st.session_state['db_initialized'] = True
                        st.info("✓ Setup complete! Please refresh the page to start using the application.")
                        
                        if st.button("🔄 Refresh Now"):
                            st.rerun()
                    else:
                        show_error("❌ Failed to create database schema")
                else:
                    show_error("❌ Failed to create database. Please check your MySQL connection.")

# =====================================================
# MAIN ENTRY POINT
# =====================================================

def main():
    """
    Main entry point of the application
    """
    # Load custom CSS
    load_css()
    
    # Initialize app
    initialize_app()
    
    # Check if database and tables exist
    if not st.session_state.get('db_initialized', False):
        # Test connection first
        if not test_connection():
            show_setup_page()
            return
        
        # Check if tables exist
        if not check_tables_exist():
            st.warning("⚠️ Database tables not found. Initializing database...")
            st.info("Please wait while we create the necessary tables...")
            
            # Auto-initialize database
            schema_path = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
            
            # Create a placeholder for progress
            progress_placeholder = st.empty()
            
            with progress_placeholder:
                with st.spinner("Creating database tables... This may take a moment..."):
                    if execute_schema_file(schema_path):
                        st.session_state['db_initialized'] = True
                        show_success("✓ Database tables created successfully!")
                        config.create_upload_directories()
                        show_success("✓ Upload directories created!")
                        st.info("🎉 Setup complete! Please refresh the page to continue.")
                        st.balloons()
                        st.button("🔄 Refresh Page", on_click=lambda: st.rerun())
                        st.stop()
                    else:
                        show_error("❌ Failed to create database tables.")
                        st.error("Please check that:")
                        st.markdown("""
                        1. MySQL server is running
                        2. Database credentials in config.py are correct
                        3. The database exists (you may need to create it manually first)
                        """)
                        
                        # Show manual setup option
                        if st.button("🔧 Try Manual Setup"):
                            show_setup_page()
                        st.stop()
        else:
            st.session_state['db_initialized'] = True
    
    # Try to load session from cookie
    if not is_logged_in():
        load_session_from_cookie(st.session_state['cookie_manager'])
    
    # Route to appropriate page
    if is_logged_in():
        show_main_app()
    else:
        show_login_page()

# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    main()
