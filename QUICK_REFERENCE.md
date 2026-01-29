# 🔧 DEVELOPER QUICK REFERENCE

## Interior Design Project Management System

---

## 🚀 QUICK COMMANDS

### Start Application
```bash
streamlit run app.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create Virtual Environment (Optional)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

---

## 📁 KEY FILES & THEIR PURPOSES

| File | Purpose | Key Functions |
|------|---------|---------------|
| `app.py` | Main entry point | `main()`, `show_login_page()`, `show_main_app()` |
| `config.py` | Settings | `DB_CONFIG`, file paths, defaults |
| `database.py` | Database operations | `get_cursor()`, `execute_query()`, CRUD helpers |
| `auth.py` | Authentication | `login_designer()`, `login_client()`, `register_designer()` |
| `utils.py` | Helper functions | `save_uploaded_file()`, formatters, validators |
| `designer_dashboard.py` | Designer UI | All designer features |
| `client_dashboard.py` | Client UI | All client features |

---

## 🗄️ DATABASE QUICK REFERENCE

### Connection Config
```python
# config.py, line 11-17
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # ← Change this
    'database': 'interior_design_db',
    'port': 3306
}
```

### Quick Queries

**Get all projects for a designer:**
```python
projects = get_records('projects', 'designer_id = %s', (designer_id,))
```

**Get client's project:**
```python
project = get_records('projects', 'client_id = %s', (client_id,))
```

**Insert new task:**
```python
task_data = {'project_id': 1, 'title': 'Paint', 'progress_percent': 0}
insert_record('tasks', task_data)
```

**Update task progress:**
```python
update_record('tasks', {'progress_percent': 50}, 'id = %s', (task_id,))
```

---

## 🔐 AUTHENTICATION FLOW

### Designer Signup
1. User fills form (`app.py`, line 160-183)
2. Validates input
3. Hashes password (`auth.py`, line 26-32)
4. Inserts into database
5. Returns success

### Designer Login
1. User enters credentials
2. `login_designer()` checks database (`auth.py`, line 102-118)
3. Verifies password hash
4. Creates session (`auth.py`, line 147-157)
5. Optional: Saves cookie (`auth.py`, line 159-174)

### Client Login
1. User enters email + code
2. `login_client()` validates (`auth.py`, line 120-136)
3. Creates session
4. Optional: Saves cookie

---

## 📂 FILE UPLOAD FLOW

### Upload Process
```python
# 1. User selects file in Streamlit
uploaded_file = st.file_uploader("Choose file")

# 2. Save file (utils.py, line 18-60)
file_path = save_uploaded_file(uploaded_file, project_id, 'reference')

# 3. Store path in database
data = {'project_id': project_id, 'file_path': file_path}
insert_record('reference_library', data)
```

### File Organization
```
uploads/
└── projects/
    └── {project_id}/
        ├── reference/    # Reference images
        ├── drawings/     # CAD files
        ├── gallery/      # Client uploads
        └── whiteboard/   # Canvas drawings
```

---

## 🎨 ADDING NEW FEATURES

### Example: Add New Feature to Designer Dashboard

**Step 1:** Create new module
```python
# designer_newfeature.py
import streamlit as st
from database import get_records, insert_record
from utils import show_success

def show_new_feature():
    st.header("New Feature")
    project_id = st.session_state.get('active_project_id')
    # Your code here
```

**Step 2:** Import in designer_dashboard.py
```python
from designer_newfeature import show_new_feature
```

**Step 3:** Add to menu
```python
# designer_dashboard.py, line 357-370
menu_options = [
    "Project Management",
    # ... existing options ...
    "New Feature"  # Add here
]
```

**Step 4:** Add routing
```python
# designer_dashboard.py, line 372+
elif choice == "New Feature":
    show_new_feature()
```

---

## 🔍 DEBUGGING TIPS

### Database Connection Issues
```python
# Test connection
from database import test_connection
test_connection()  # Returns True/False
```

### Check Session State
```python
# Add this anywhere in Streamlit
st.write(st.session_state)
```

### View SQL Errors
```python
# database.py uses try-except blocks
# Errors print to console
# Check terminal output
```

### Test Without Database
```python
# Comment out database operations temporarily
# Use mock data for testing UI
test_data = [{'id': 1, 'name': 'Test'}]
```

---

## 📊 COMMON OPERATIONS

### Get Current User
```python
from auth import get_current_user_id, is_designer, is_client

user_id = get_current_user_id()
if is_designer():
    # Designer-specific code
if is_client():
    # Client-specific code
```

### File Path Handling
```python
from utils import save_uploaded_file, get_full_file_path, display_image

# Save file
relative_path = save_uploaded_file(file, project_id, 'reference')

# Get full path
full_path = get_full_file_path(relative_path)

# Display image
display_image(relative_path, caption="My Image")
```

### Currency Formatting
```python
from utils import format_currency

amount = 150000
formatted = format_currency(amount)  # "₹150,000.00"
```

### Date Formatting
```python
from utils import format_date, format_datetime

date_str = format_date(date_obj)      # "29 Jan 2026"
datetime_str = format_datetime(dt)    # "29 Jan 2026, 02:30 PM"
```

---

## 🎯 TESTING CHECKLIST

### Functionality Tests
- [ ] Designer can sign up
- [ ] Designer can login
- [ ] Designer can create project
- [ ] Client code is generated
- [ ] Client can login with code
- [ ] Files upload successfully
- [ ] Database records created
- [ ] Session persists on refresh
- [ ] Budget calculations correct
- [ ] Task progress updates
- [ ] Feedback submission works
- [ ] Role-based access enforced

### Database Tests
- [ ] All tables created
- [ ] Foreign keys working
- [ ] Constraints enforced
- [ ] Queries return correct data
- [ ] Updates successful
- [ ] Deletes cascade properly

### UI Tests
- [ ] Navigation works
- [ ] Forms validate input
- [ ] Error messages display
- [ ] Success messages show
- [ ] Images display correctly
- [ ] Buttons functional

---

## 🛠️ CUSTOMIZATION

### Change Default Tasks
Edit `config.py`, line 39-52:
```python
DEFAULT_TASKS = [
    "Your Task 1",
    "Your Task 2",
    # Add more...
]
```

### Change Default Budget Categories
Edit `config.py`, line 55-68:
```python
DEFAULT_BUDGET_CATEGORIES = [
    "Category 1",
    "Category 2",
    # Add more...
]
```

### Change Cookie Expiry
Edit `config.py`, line 31:
```python
COOKIE_EXPIRY_DAYS = 30  # Change to desired days
```

### Change File Upload Limits
Edit Streamlit config or add validation in `utils.py`.

---

## 🐛 COMMON ERRORS & FIXES

### "No module named 'streamlit'"
```bash
pip install streamlit
```

### "Can't connect to MySQL server"
- Start MySQL service
- Check port 3306 is not blocked
- Verify credentials in config.py

### "Access denied for user"
- Check username in config.py
- Check password in config.py
- Ensure MySQL user has permissions

### "Table doesn't exist"
- Run database initialization from setup page
- Check database_schema.sql executed correctly

### "Session state key error"
- Initialize session state variables
- Check for typos in key names

---

## 📚 USEFUL CODE SNIPPETS

### Create Expander with Form
```python
with st.expander("Add Item"):
    with st.form("form_key"):
        field = st.text_input("Field")
        submit = st.form_submit_button("Submit")
        if submit:
            # Process form
```

### Display Data in Columns
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Label", value)
with col2:
    st.metric("Label", value)
with col3:
    st.metric("Label", value)
```

### File Upload Validation
```python
from utils import is_valid_file_extension
import config

if uploaded_file:
    if is_valid_file_extension(uploaded_file.name, 
                               config.ALLOWED_IMAGE_EXTENSIONS):
        # Process file
    else:
        st.error("Invalid file type")
```

---

## 🔗 HELPFUL LINKS

- **Streamlit Docs:** https://docs.streamlit.io/
- **MySQL Connector:** https://dev.mysql.com/doc/connector-python/
- **bcrypt:** https://github.com/pyca/bcrypt/
- **Pillow:** https://pillow.readthedocs.io/

---

## 💡 BEST PRACTICES

1. **Always use parameterized queries** (prevents SQL injection)
2. **Hash passwords** (never store plain text)
3. **Validate user input** (check before database insertion)
4. **Use context managers** (automatic cleanup)
5. **Add error handling** (try-except blocks)
6. **Comment your code** (explain complex logic)
7. **Keep functions small** (single responsibility)
8. **Use meaningful names** (descriptive variables)

---

## 🎓 FOR IA EXPLANATION

### Key Points to Mention:

1. **Modular Design** - Separate files for each feature
2. **Security** - Password hashing, session management
3. **Database Design** - Normalized tables, relationships
4. **CRUD Operations** - Complete Create, Read, Update, Delete
5. **File Handling** - Organized storage, path management
6. **User Experience** - Intuitive interface, clear feedback
7. **Error Handling** - Validation, try-catch blocks
8. **Code Quality** - Comments, docstrings, clean code

---

**Quick Reference Complete! 🎉**
