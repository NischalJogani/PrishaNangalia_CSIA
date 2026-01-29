"""
Authentication Module
Handles user registration, login, logout, and session management with cookies
"""

import streamlit as st
import bcrypt
import secrets
import string
from datetime import datetime, timedelta
import extra_streamlit_components as stx
from database import insert_record, get_records, execute_query
import config

# =====================================================
# COOKIE MANAGER INITIALIZATION
# =====================================================

def get_cookie_manager():
    """
    Initialize and return the cookie manager
    """
    return stx.CookieManager()

# =====================================================
# PASSWORD HASHING FUNCTIONS
# =====================================================

def hash_password(password):
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        Boolean indicating if password matches
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# =====================================================
# CLIENT CODE GENERATION
# =====================================================

def generate_client_code():
    """
    Generate a unique random client access code
    Format: 6 uppercase letters and digits (e.g., ABC123)
    
    Returns:
        Unique client code string
    """
    while True:
        # Generate random code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        # Check if code already exists
        existing = get_records('users', 'client_code = %s', (code,))
        if not existing:
            return code

# =====================================================
# USER REGISTRATION FUNCTIONS
# =====================================================

def register_designer(name, email, password):
    """
    Register a new interior designer account
    
    Args:
        name: Designer's full name
        email: Designer's email
        password: Plain text password (will be hashed)
    
    Returns:
        Tuple (success: bool, message: str, user_id: int or None)
    """
    # Check if email already exists
    existing_user = get_records('users', 'email = %s', (email,))
    if existing_user:
        return False, "Email already registered", None
    
    # Hash password
    hashed_pwd = hash_password(password)
    
    # Insert designer into database
    try:
        user_data = {
            'name': name,
            'email': email,
            'password_hash': hashed_pwd,
            'role': 'designer'
        }
        user_id = insert_record('users', user_data)
        return True, "Designer account created successfully!", user_id
    except Exception as e:
        return False, f"Error creating account: {str(e)}", None

def register_client(name, email, designer_id):
    """
    Register a new client account (created by designer)
    No password required - uses auto-generated access code
    
    Args:
        name: Client's name
        email: Client's email
        designer_id: ID of the designer creating this client
    
    Returns:
        Tuple (success: bool, message: str, client_code: str or None)
    """
    # Check if email already exists
    existing_user = get_records('users', 'email = %s', (email,))
    if existing_user:
        return False, "Email already registered", None
    
    # Generate unique client code
    client_code = generate_client_code()
    
    try:
        # Insert client into database
        user_data = {
            'name': name,
            'email': email,
            'role': 'client',
            'client_code': client_code
        }
        user_id = insert_record('users', user_data)
        
        return True, f"Client account created! Access code: {client_code}", client_code
    except Exception as e:
        return False, f"Error creating client account: {str(e)}", None

# =====================================================
# LOGIN FUNCTIONS
# =====================================================

def login_designer(email, password):
    """
    Authenticate a designer user
    
    Args:
        email: Designer's email
        password: Plain text password
    
    Returns:
        Tuple (success: bool, message: str, user_data: dict or None)
    """
    # Fetch user from database
    user = get_records('users', 'email = %s AND role = %s', (email, 'designer'))
    
    if not user:
        return False, "Invalid email or password", None
    
    user = user[0]
    
    # Verify password
    if verify_password(password, user['password_hash']):
        return True, "Login successful!", user
    else:
        return False, "Invalid email or password", None

def login_client(email, client_code):
    """
    Authenticate a client user using email and access code
    
    Args:
        email: Client's email
        client_code: Client's unique access code
    
    Returns:
        Tuple (success: bool, message: str, user_data: dict or None)
    """
    # Fetch client from database
    user = get_records('users', 'email = %s AND client_code = %s AND role = %s', 
                      (email, client_code, 'client'))
    
    if not user:
        return False, "Invalid email or access code", None
    
    return True, "Login successful!", user[0]

# =====================================================
# SESSION MANAGEMENT
# =====================================================

def create_session(user_data):
    """
    Create a session for logged-in user
    Store user information in Streamlit session state
    
    Args:
        user_data: Dictionary containing user information
    """
    st.session_state['logged_in'] = True
    st.session_state['user_id'] = user_data['id']
    st.session_state['user_name'] = user_data['name']
    st.session_state['user_email'] = user_data['email']
    st.session_state['user_role'] = user_data['role']
    
    # For clients, store their code
    if user_data['role'] == 'client':
        st.session_state['client_code'] = user_data.get('client_code')

def save_session_to_cookie(cookie_manager, user_data):
    """
    Save session information to browser cookie for persistent login
    
    Args:
        cookie_manager: Cookie manager instance
        user_data: User information to store
    """
    try:
        # Create session token
        session_token = f"{user_data['id']}:{user_data['role']}:{user_data['email']}"
        
        # Set cookie with expiry
        cookie_manager.set(
            config.COOKIE_NAME,
            session_token,
            expires_at=datetime.now() + timedelta(days=config.COOKIE_EXPIRY_DAYS),
            key=config.COOKIE_KEY
        )
    except Exception as e:
        print(f"Error saving cookie: {e}")

def load_session_from_cookie(cookie_manager):
    """
    Load session from cookie if exists
    Auto-login user if valid cookie found
    
    Args:
        cookie_manager: Cookie manager instance
    
    Returns:
        Boolean indicating if session was loaded successfully
    """
    try:
        # Get cookie
        cookies = cookie_manager.get_all()
        session_token = cookies.get(config.COOKIE_NAME)
        
        if not session_token:
            return False
        
        # Parse session token
        user_id, role, email = session_token.split(':')
        
        # Fetch user from database
        user = get_records('users', 'id = %s AND email = %s AND role = %s', 
                          (int(user_id), email, role))
        
        if user:
            create_session(user[0])
            return True
        
        return False
    except Exception as e:
        print(f"Error loading session from cookie: {e}")
        return False

def logout(cookie_manager):
    """
    Logout user and clear session
    
    Args:
        cookie_manager: Cookie manager instance
    """
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Clear cookie
    try:
        cookie_manager.delete(config.COOKIE_NAME)
    except:
        pass

# =====================================================
# SESSION CHECK HELPERS
# =====================================================

def is_logged_in():
    """
    Check if user is logged in
    
    Returns:
        Boolean
    """
    return st.session_state.get('logged_in', False)

def is_designer():
    """
    Check if logged-in user is a designer
    
    Returns:
        Boolean
    """
    return is_logged_in() and st.session_state.get('user_role') == 'designer'

def is_client():
    """
    Check if logged-in user is a client
    
    Returns:
        Boolean
    """
    return is_logged_in() and st.session_state.get('user_role') == 'client'

def require_login():
    """
    Decorator/check to ensure user is logged in
    Redirect to login if not authenticated
    """
    if not is_logged_in():
        st.warning("Please login to access this page")
        st.stop()

def get_current_user_id():
    """
    Get the current logged-in user's ID
    
    Returns:
        User ID or None
    """
    return st.session_state.get('user_id')
