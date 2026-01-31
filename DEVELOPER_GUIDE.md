# 🔧 Developer Guide

## Interior Design Project Management System - Technical Documentation

---

## 🚀 Quick Commands

### Start Application
```bash
streamlit run app.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Database Operations
```bash
# Auto-initialization on first run
# Manual: Run database_schema.sql in MySQL
```

---

## 📁 File Structure & Responsibilities

### Core Files (7 total)

| File | Lines | Purpose | Key Functions |
|------|-------|---------|---------------|
| `app.py` | ~400 | Entry point, routing, login | `main()`, `show_login_page()`, `show_main_app()` |
| `auth.py` | ~340 | Authentication & sessions | `login_designer()`, `login_client()`, `register_client()`, `generate_client_code()` |
| `database.py` | ~310 | DB operations & CRUD | `get_db_connection()`, `execute_query()`, `insert_record()`, `update_record()` |
| `config.py` | ~60 | Settings & secrets | `DB_CONFIG`, `UPLOAD_FOLDER`, default values |
| `utils.py` | ~280 | Helper functions | `save_uploaded_file()`, formatters, validators, calculations |
| `designer_dashboard.py` | ~1100 | All 9 designer features | Project mgmt, ref library, tasks, whiteboard, budget, suppliers, measurements, timeline, feedback |
| `client_dashboard.py` | ~430 | All 7 client features | View-only dashboards + gallery upload + feedback submission |

### Database
| File | Purpose |
|------|---------|
| `database_schema.sql` | 11-table schema with relationships |

---

## 🗄️ Database Schema

### Tables & Relationships

```
users (id, name, email, password_hash, client_code, role)
  ↓
projects (id, client_id → users, designer_id → users, site_type, created_at)
  ↓
  ├── reference_library (id, project_id, room_name, file_path)
  ├── tasks (id, project_id, title, description, progress_percent, comments)
  ├── notes_whiteboard (id, project_id, text_note, drawing_path)
  ├── budget_items (id, project_id, item_name, estimated_cost, actual_cost)
  ├── measurements (id, project_id, type, file_path, notes)
  ├── gallery (id, project_id, uploaded_by, file_path)
  ├── timeline (id, project_id, milestone, deadline, status)
  └── feedback (id, project_id, item_type, comment, approval_status)

suppliers (id, name, category, phone, email, address)  # Not project-specific
```

### Key Fields

**users table:**
- `role`: 'designer' or 'client'
- `password_hash`: bcrypt (designers only)
- `client_code`: 8-char random (clients only, NULL for designers)

**projects table:**
- `client_id`: Foreign key to users (client)
- `designer_id`: Foreign key to users (designer)

---

## 🔐 Authentication Flow

### Designer Registration
1. User fills signup form → `app.py` (line 160-183)
2. Validates input (email format, password match, strength)
3. `auth.register_designer()` → Hash password with bcrypt
4. Insert into `users` table with role='designer'
5. Return success → User can login

### Designer Login
1. User enters email + password
2. `auth.login_designer()` → Query `users` WHERE email + role='designer'
3. `auth.verify_password()` → Compare bcrypt hash
4. If match: `auth.create_session()` → Store in st.session_state
5. Optional: Save to cookie for persistence
6. Redirect to designer dashboard

### Client Registration (by Designer)
1. Designer creates project → fills client details
2. `auth.register_client()` → Generate 8-digit code
3. `auth.generate_client_code()` → Random uppercase + digits (check uniqueness)
4. Insert into `users` with role='client', client_code=generated
5. Return code to designer → Display prominently

### Client Login
1. User enters email + 8-digit code
2. `auth.login_client()` → Query `users` WHERE email + client_code + role='client'
3. If match: Create session
4. Redirect to client dashboard

---

## 📦 Key Functions

### Database Operations (`database.py`)

```python
# Get connection
conn = get_db_connection()

# Execute query
results = execute_query("SELECT * FROM users WHERE role = %s", ('designer',), fetch_all=True)

# Insert
user_id = insert_record('users', {'name': 'John', 'email': 'john@test.com', 'role': 'designer'})

# Update
update_record('tasks', {'progress_percent': 75}, 'id = %s', (task_id,))

# Delete
delete_record('budget_items', 'id = %s', (item_id,))

# Get records with condition
projects = get_records('projects', 'designer_id = %s', (designer_id,))
```

### File Upload (`utils.py`)

```python
# Save uploaded file
file_path = save_uploaded_file(
    uploaded_file,     # Streamlit UploadedFile object
    project_id,        # Project ID for folder organization
    subfolder          # 'reference', 'drawings', 'gallery', 'whiteboard'
)
# Returns: "uploads/projects/1/reference/image_123456.png"
```

### Calculations (`utils.py`)

```python
# Budget statistics
stats = calculate_budget_statistics(budget_items)
# Returns: {'total_estimated': 50000, 'total_actual': 45000, 'difference': -5000, 'over_budget': False}

# Task completion
completion = calculate_task_completion(tasks)
# Returns: 67.5 (average progress percent)
```

---

## 🎨 UI Components

### Designer Dashboard Structure

```python
def show_designer_dashboard():
    # Sidebar navigation (9 options)
    choice = st.sidebar.radio("Navigate to:", menu_options)
    
    # Route to appropriate function
    if choice == "Project Management":
        show_project_management()
    elif choice == "Reference Library":
        show_reference_library()
    # ... etc
```

### Common Patterns

**Form with validation:**
```python
with st.form("form_key"):
    field1 = st.text_input("Label")
    field2 = st.number_input("Amount")
    submit = st.form_submit_button("Submit")
    
    if submit:
        if not field1:
            show_error("Field required")
        else:
            insert_record('table', {'field': field1})
            show_success("Saved!")
            st.rerun()  # Refresh UI
```

**Expander for items:**
```python
for item in items:
    with st.expander(f"📋 {item['title']}"):
        # Display item details
        # Add edit/delete buttons
```

---

## 🔧 Configuration

### Database Config (`config.py`)
```python
DB_CONFIG = st.secrets["database"] if "database" in st.secrets else {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'interior_designer_app_prisha_csia'),
    'port': int(os.getenv('DB_PORT', 3306))
}
```

### Secrets File (`.streamlit/secrets.toml`)
```toml
[database]
host = "localhost"
user = "root"
password = "your_password"
database = "interior_designer_app_prisha_csia"
port = 3306

[session]
secret_key = "random-secret-key-here"
cookie_name = "interior_designer_session"
```

### Upload Settings (`config.py`)
```python
UPLOAD_FOLDER = "uploads"
ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
ALLOWED_DRAWING_EXTENSIONS = ['dwg', 'dxf', 'pdf', 'png', 'jpg']

DEFAULT_TASKS = ["Site Visit", "Design Concept", "Client Approval", ...]
DEFAULT_BUDGET_CATEGORIES = ["Furniture", "Lighting", "Paint", ...]
```

---

## 🐛 Common Issues & Solutions

### Issue: Database connection fails
**Solution:**
1. Check MySQL is running
2. Verify credentials in `.streamlit/secrets.toml`
3. Check database exists (auto-created on first run)
4. Look for error in terminal output

### Issue: Import errors
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Session state issues
**Solution:**
- Clear browser cookies
- Restart Streamlit
- Check `st.session_state` keys in code

### Issue: File upload fails
**Solution:**
1. Check `uploads/` folder exists
2. Verify permissions (write access)
3. Check file extension is allowed
4. Look at `utils.save_uploaded_file()` error messages

---

## 🔍 Code Navigation Tips

### Find a feature:
- **Project Management:** `designer_dashboard.py` → `show_project_management()`
- **Client Login:** `app.py` → `show_client_login()`
- **Task Update:** `designer_dashboard.py` → `show_task_tracking()`
- **Database Query:** `database.py` → `execute_query()`

### Add a new feature:
1. Add menu option in `show_designer_dashboard()` or `show_client_dashboard()`
2. Create function `def show_new_feature():`
3. Add database queries/CRUD operations
4. Create UI with Streamlit components
5. Add to navigation routing

### Modify database:
1. Update `database_schema.sql`
2. Drop existing tables: `DROP DATABASE interior_designer_app_prisha_csia;`
3. Restart app → Auto-recreates from schema

---

## 📊 Performance Tips

### Database:
- ✅ Use `fetch_all=False` for single records
- ✅ Add indexes to frequently queried columns
- ✅ Use parameterized queries (prevents SQL injection)

### Streamlit:
- ✅ Use `st.cache_data` for expensive computations
- ✅ Minimize `st.rerun()` calls
- ✅ Use forms to batch inputs (reduces reruns)

### Files:
- ✅ Implement file size limits
- ✅ Compress images before storage
- ✅ Clean up unused files periodically

---

## 🧪 Testing

### Manual Testing:
1. Test all features in designer dashboard
2. Test all features in client dashboard
3. Test with multiple projects
4. Test file uploads (various formats)
5. Test edge cases (empty fields, special characters)

### Database Testing:
```python
# Test insert
user_id = insert_record('users', {'name': 'Test', 'email': 'test@test.com', 'role': 'designer'})
assert user_id > 0

# Test query
users = get_records('users', 'role = %s', ('designer',))
assert len(users) > 0
```

---

## 📝 Code Style

### Naming Conventions:
- **Functions:** `snake_case` (e.g., `show_project_management`)
- **Variables:** `snake_case` (e.g., `project_id`)
- **Constants:** `UPPER_CASE` (e.g., `DB_CONFIG`)
- **Classes:** `PascalCase` (not used much in this project)

### Comments:
```python
def function_name():
    """
    Brief description of what the function does
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Description of return value
    """
```

---

## 🚀 Deployment Considerations

### For Production:
1. **Environment variables** for all secrets
2. **HTTPS** for secure connections
3. **Reverse proxy** (nginx) for Streamlit
4. **Database backups** scheduled
5. **File storage** on cloud (S3, etc.) instead of local
6. **Rate limiting** on API endpoints
7. **Monitoring** and logging

### Cloud Deployment Options:
- **Streamlit Cloud** (easiest, free tier available)
- **Heroku** (with MySQL addon)
- **AWS** (EC2 + RDS)
- **Google Cloud** (Compute Engine + Cloud SQL)

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt/)

---

**Happy Coding!** 🎉
