"""
Database Connection Module
Handles all MySQL database connections and operations
"""

import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
import config

# =====================================================
# DATABASE CONNECTION FUNCTIONS
# =====================================================

def get_db_connection():
    """
    Establish and return a MySQL database connection
    Returns:
        connection object or None if connection fails
    """
    try:
        print(f"Attempting to connect to database...")
        print(f"Host: {config.DB_CONFIG['host']}")
        print(f"User: {config.DB_CONFIG['user']}")
        print(f"Database: {config.DB_CONFIG['database']}")
        print(f"Password set: {'Yes' if config.DB_CONFIG['password'] else 'No'}")
        
        connection = mysql.connector.connect(**config.DB_CONFIG)
        if connection.is_connected():
            print("✓ Database connection successful!")
            return connection
    except Error as e:
        print(f"❌ Database connection error: {e}")
        print(f"Error Code: {e.errno if hasattr(e, 'errno') else 'N/A'}")
        print(f"SQL State: {e.sqlstate if hasattr(e, 'sqlstate') else 'N/A'}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

@contextmanager
def get_cursor(dictionary=True):
    """
    Context manager for database operations
    Automatically handles connection and cursor lifecycle
    
    Args:
        dictionary: If True, returns results as dictionaries
    
    Usage:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    connection = get_db_connection()
    if connection is None:
        yield None
        return
    
    try:
        cursor = connection.cursor(dictionary=dictionary)
        yield cursor
        connection.commit()
    except Error as e:
        connection.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# =====================================================
# DATABASE INITIALIZATION
# =====================================================

def initialize_database():
    """
    Create database if it doesn't exist
    This should be run once during setup
    """
    try:
        # Connect without specifying database
        temp_config = config.DB_CONFIG.copy()
        db_name = temp_config.pop('database')
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists")
        
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error creating database: {e}")
        return False

def execute_schema_file(schema_file_path):
    """
    Execute SQL schema file to create tables
    
    Args:
        schema_file_path: Path to the SQL schema file
    """
    try:
        with open(schema_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        connection = get_db_connection()
        if connection is None:
            print("Failed to get database connection")
            return False
        
        cursor = connection.cursor()
        
        # Remove comments and split by semicolon
        lines = sql_script.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove single-line comments
            if not line.strip().startswith('--'):
                cleaned_lines.append(line)
        
        cleaned_script = '\n'.join(cleaned_lines)
        
        # Split by semicolon and execute each statement
        statements = cleaned_script.split(';')
        
        for statement in statements:
            statement = statement.strip()
            # Skip empty statements and comments
            if statement and len(statement) > 5:
                try:
                    cursor.execute(statement)
                    connection.commit()
                except Error as e:
                    error_msg = str(e).lower()
                    # Only skip "already exists" errors
                    if 'already exists' not in error_msg and 'duplicate' not in error_msg:
                        print(f"Error executing statement: {e}")
                        print(f"Statement: {statement[:100]}...")
                        cursor.close()
                        connection.close()
                        return False
        
        cursor.close()
        connection.close()
        print("✓ Database schema executed successfully")
        return True
    except Exception as e:
        print(f"Error executing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

# =====================================================
# CRUD HELPER FUNCTIONS
# =====================================================

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a SQL query with parameters
    
    Args:
        query: SQL query string
        params: Tuple of parameters for the query
        fetch_one: Return single row
        fetch_all: Return all rows
    
    Returns:
        Results or last inserted id
    """
    with get_cursor() as cursor:
        if cursor is None:
            return None
        
        cursor.execute(query, params or ())
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            return cursor.lastrowid

def insert_record(table, data):
    """
    Insert a record into a table
    
    Args:
        table: Table name
        data: Dictionary of column:value pairs
    
    Returns:
        Last inserted ID
    """
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    return execute_query(query, tuple(data.values()))

def update_record(table, data, condition, condition_params):
    """
    Update a record in a table
    
    Args:
        table: Table name
        data: Dictionary of column:value pairs to update
        condition: WHERE clause (e.g., "id = %s")
        condition_params: Tuple of parameters for WHERE clause
    
    Returns:
        Success boolean
    """
    set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    params = tuple(data.values()) + condition_params
    
    execute_query(query, params)
    return True

def delete_record(table, condition, condition_params):
    """
    Delete a record from a table
    
    Args:
        table: Table name
        condition: WHERE clause (e.g., "id = %s")
        condition_params: Tuple of parameters for WHERE clause
    
    Returns:
        Success boolean
    """
    query = f"DELETE FROM {table} WHERE {condition}"
    execute_query(query, condition_params)
    return True

def get_records(table, condition=None, condition_params=None, columns="*"):
    """
    Fetch records from a table
    
    Args:
        table: Table name
        condition: Optional WHERE clause
        condition_params: Tuple of parameters for WHERE clause
        columns: Columns to select (default: all)
    
    Returns:
        List of records
    """
    query = f"SELECT {columns} FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    
    return execute_query(query, condition_params, fetch_all=True) or []

# =====================================================
# TEST CONNECTION FUNCTION
# =====================================================

def test_connection():
    """
    Test if database connection works
    Returns True if successful, False otherwise
    """
    connection = get_db_connection()
    if connection:
        print("✓ Database connection successful!")
        connection.close()
        return True
    else:
        print("✗ Database connection failed!")
        return False

def check_tables_exist():
    """
    Check if all required tables exist in the database
    Returns True if all tables exist, False otherwise
    """
    required_tables = [
        'users', 'projects', 'reference_library', 'tasks',
        'notes_whiteboard', 'budget_items', 'suppliers',
        'measurements', 'gallery', 'timeline', 'feedback'
    ]
    
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        # Check if all required tables exist
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"Missing tables: {', '.join(missing_tables)}")
            return False
        
        print("✓ All required tables exist!")
        return True
    except Exception as e:
        print(f"Error checking tables: {e}")
        return False
