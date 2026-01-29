# 📚 INTERNAL ASSESSMENT (IA) DOCUMENTATION
## Interior Design Project Management System

---

## 📋 PROJECT OVERVIEW

### Title
**Interior Design Project Management System**

### Purpose
A comprehensive web-based platform that enables interior designers to manage multiple client projects while allowing clients to track progress, view designs, and provide feedback - all in one centralized system.

### Problem Statement
Interior designers often struggle with:
- Managing multiple clients and projects simultaneously
- Tracking task progress and deadlines
- Budget management and cost tracking
- Sharing reference images and design files with clients
- Collecting and organizing client feedback
- Maintaining clear communication channels

This system solves these problems by providing a structured, role-based platform.

---

## 🎯 SUCCESS CRITERIA

1. ✅ **User Authentication System**
   - Designers can sign up with email/password (hashed)
   - Clients login with email + unique access code
   - Session persistence with cookies

2. ✅ **Role-Based Access Control**
   - Designers: Full CRUD access to all features
   - Clients: View-only access + feedback submission

3. ✅ **Project Management**
   - Create and manage multiple projects
   - Associate clients with projects
   - Auto-generate unique client access codes

4. ✅ **Task Tracking System**
   - Add/edit/delete tasks
   - Progress tracking (0-100%)
   - Comments per task
   - Overall completion percentage

5. ✅ **Budget Management**
   - Track estimated vs actual costs
   - Multiple budget items per project
   - Automatic difference calculation
   - Visual indicators for over/under budget

6. ✅ **File Management**
   - Upload and organize reference images by room
   - Store CAD files and drawings
   - Client inspiration gallery
   - Organized folder structure

7. ✅ **Timeline Tracking**
   - Add project milestones
   - Set deadlines
   - Status tracking (pending/in progress/completed)

8. ✅ **Feedback System**
   - Clients can comment on designs
   - Approval/rejection workflow
   - History tracking

9. ✅ **Data Persistence**
   - All data stored in MySQL database
   - Files stored in organized local folders
   - Session persistence across browser refreshes

10. ✅ **User-Friendly Interface**
    - Clean, intuitive Streamlit interface
    - Responsive design
    - Clear navigation
    - Helpful feedback messages

---

## 🏗️ SYSTEM ARCHITECTURE

### High-Level Architecture
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────┐
│   Streamlit Frontend (Python)   │
│  - User Interface               │
│  - Session Management           │
│  - Cookie Handling              │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│   Application Layer (Python)    │
│  - Authentication (auth.py)     │
│  - Business Logic               │
│  - File Handling (utils.py)     │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│   Database Layer (database.py)  │
│  - Connection Management        │
│  - CRUD Operations              │
│  - Query Execution              │
└────────────┬────────────────────┘
             │
             ↓
    ┌────────────────┐
    │  MySQL Server  │
    │  (11 Tables)   │
    └────────────────┘
```

### Technology Stack Justification

**1. Streamlit (Frontend + Backend Framework)**
- **Why:** Rapid development, Python-native, perfect for data-driven applications
- **Benefit:** Single language (Python) for entire stack
- **Academic Value:** Demonstrates understanding of modern web frameworks

**2. MySQL (Database)**
- **Why:** Robust relational database, industry standard
- **Benefit:** ACID compliance, complex relationships between tables
- **Academic Value:** Shows proper database design with normalization

**3. bcrypt (Password Hashing)**
- **Why:** Industry-standard password hashing algorithm
- **Benefit:** Security best practices, salt generation
- **Academic Value:** Demonstrates understanding of security

**4. Local File Storage**
- **Why:** Simple, no external dependencies
- **Benefit:** Direct file system control, organized structure
- **Academic Value:** File handling and directory management

---

## 🗄️ DATABASE DESIGN

### Entity-Relationship Model

```
USERS (1) ──────── (*) PROJECTS (*) ──────── (1) USERS
 │                                                    
 │                                                    
 └──────────────────┬──────────────────┬
                    │                  │
                    ↓                  ↓
            REFERENCE_LIBRARY      TASKS
            BUDGET_ITEMS          TIMELINE
            MEASUREMENTS          GALLERY
            NOTES_WHITEBOARD      FEEDBACK
            SUPPLIERS (independent)
```

### Normalization
- **1NF:** All tables have atomic values, no repeating groups
- **2NF:** All non-key attributes fully dependent on primary key
- **3NF:** No transitive dependencies

### Tables Explained

**1. users**
- Stores both designers and clients
- Role field differentiates user types
- Password hash only for designers
- Client code unique for each client

**2. projects**
- Links clients to designers
- Stores project-specific information
- Foreign keys maintain referential integrity

**3. reference_library**
- Stores reference images per project
- Organized by room name
- File path stored as string

**4. tasks**
- Task tracking with progress percentage
- Linked to specific project
- Supports comments

**5. budget_items**
- Estimated vs actual cost tracking
- Multiple items per project
- DECIMAL type for precision

**6. suppliers**
- Shared across all projects
- Searchable by category
- Contact information storage

**7. measurements**
- Stores CAD files and drawings
- Type field: existing vs proposed
- Notes support

**8. gallery**
- Images uploaded by client or designer
- Uploaded_by field for attribution
- Timestamp tracking

**9. timeline**
- Project milestones
- Status tracking (enum)
- Deadline management

**10. notes_whiteboard**
- Stores drawings and text notes
- Linked to specific project
- Optional drawing path

**11. feedback**
- Client comments and approvals
- Status: pending/approved/rejected
- Type: drawing/image

---

## 🔒 SECURITY IMPLEMENTATION

### Password Security
```python
# Hashing (auth.py, line 26-32)
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
```
- Uses bcrypt with automatic salt generation
- Passwords never stored in plain text
- One-way hashing (cannot be reversed)

### Session Management
```python
# Session creation (auth.py, line 147-157)
def create_session(user_data):
    st.session_state['logged_in'] = True
    st.session_state['user_id'] = user_data['id']
    st.session_state['user_role'] = user_data['role']
```
- Server-side session state
- Cookie-based persistence
- Automatic expiry (30 days configurable)

### Access Control
```python
# Role checking (auth.py, line 231-243)
def is_designer():
    return is_logged_in() and st.session_state.get('user_role') == 'designer'
```
- Function-level role verification
- Prevents unauthorized access
- Client code validation for clients

---

## 💻 CODE STRUCTURE

### Modular Design
Each module has a specific responsibility:

**app.py** - Main entry point
- Page configuration
- Routing logic
- Database initialization
- Login/logout flow

**config.py** - Configuration
- Database credentials
- File paths
- Default values
- Application settings

**database.py** - Data layer
- Connection management
- Context managers
- CRUD helpers
- Query execution

**auth.py** - Authentication
- Password hashing
- User registration
- Login validation
- Session management
- Cookie handling

**utils.py** - Utilities
- File upload handling
- Image processing
- Validation functions
- Formatting helpers

**designer_*.py** - Designer features
- Separate file per feature
- Focused functionality
- Reusable components

**client_dashboard.py** - Client features
- All client functions
- View-only implementations
- Feedback submission

---

## 🔄 ALGORITHMS & LOGIC

### 1. Client Code Generation Algorithm
```python
# auth.py, line 45-54
def generate_client_code():
    while True:
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                      for _ in range(6))
        existing = get_records('users', 'client_code = %s', (code,))
        if not existing:
            return code
```
**Purpose:** Generate unique 6-character alphanumeric codes
**Logic:** 
1. Generate random code
2. Check if exists in database
3. If unique, return; else repeat
**Complexity:** O(1) average case

### 2. Budget Statistics Calculation
```python
# utils.py, line 263-277
def calculate_budget_statistics(budget_items):
    total_estimated = sum(item.get('estimated_cost', 0) for item in budget_items)
    total_actual = sum(item.get('actual_cost', 0) for item in budget_items)
    difference = total_actual - total_estimated
    
    return {
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'difference': difference,
        'over_budget': difference > 0
    }
```
**Purpose:** Calculate budget totals and differences
**Logic:** Aggregate costs, compute difference, determine status
**Complexity:** O(n) where n = number of budget items

### 3. Task Completion Percentage
```python
# utils.py, line 279-290
def calculate_task_completion(tasks):
    if not tasks:
        return 0
    total_progress = sum(task.get('progress_percent', 0) for task in tasks)
    return total_progress / len(tasks)
```
**Purpose:** Calculate overall project completion
**Logic:** Average of all task progress percentages
**Complexity:** O(n) where n = number of tasks

---

## 📊 FEATURES BREAKDOWN

### Feature 1: Project Management
**File:** designer_dashboard.py, lines 20-109
**Purpose:** Create and manage client projects
**Key Functions:**
- `show_project_management()` - Main interface
- `initialize_default_tasks()` - Set up task list
- `initialize_default_budget()` - Set up budget categories

**User Flow:**
1. Designer clicks "Project Management"
2. Views existing projects
3. Fills new client form
4. System creates client account with unique code
5. System creates project record
6. System initializes default tasks and budget
7. System creates file directories

### Feature 2: Task Tracking
**File:** designer_dashboard.py, lines 195-264
**Purpose:** Track project tasks with progress
**Key Functions:**
- `show_task_tracking()` - Display and manage tasks
- Progress sliders for each task
- Comment system

**User Flow:**
1. Designer selects project
2. Views task list with progress
3. Updates progress slider
4. Adds comments
5. Saves changes to database
6. Overall completion updates automatically

### Feature 3: Budget Management
**File:** designer_budget.py
**Purpose:** Track costs and budget
**Key Functions:**
- `show_budget_overview()` - Main budget interface
- Real-time difference calculation
- Visual indicators

**User Flow:**
1. Designer enters estimated costs
2. Updates actual costs as spent
3. System calculates difference
4. Shows over/under budget status
5. Displays summary metrics

### Feature 4: Client Feedback
**File:** client_dashboard.py, lines 314-362
**Purpose:** Client feedback and approvals
**Key Functions:**
- `show_client_feedback()` - Feedback submission
- Approval status selection
- History viewing

**User Flow:**
1. Client views designs
2. Writes comment
3. Selects approval status
4. Submits feedback
5. Designer views in their dashboard

---

## 🧪 TESTING

### Test Cases

**Test 1: Designer Registration**
- Input: Name, valid email, 8+ char password
- Expected: Account created, success message
- Result: ✅ Pass

**Test 2: Client Login with Code**
- Input: Client email, 6-char access code
- Expected: Successful login, client dashboard loads
- Result: ✅ Pass

**Test 3: Project Creation**
- Input: Client name, email, site type
- Expected: Client created, project created, directories created
- Result: ✅ Pass

**Test 4: File Upload**
- Input: Image file
- Expected: File saved in correct directory, database record created
- Result: ✅ Pass

**Test 5: Budget Calculation**
- Input: Multiple budget items with costs
- Expected: Correct totals, accurate difference
- Result: ✅ Pass

**Test 6: Task Progress**
- Input: Update task progress to 50%
- Expected: Overall completion updates proportionally
- Result: ✅ Pass

**Test 7: Cookie Persistence**
- Input: Login, close browser, reopen
- Expected: User still logged in
- Result: ✅ Pass

**Test 8: Role-Based Access**
- Input: Client tries to access designer features
- Expected: Access denied or feature hidden
- Result: ✅ Pass

---

## 📈 EXTENSIONS & IMPROVEMENTS

### Implemented Features Beyond Basic Requirements

1. **Cookie-Based Session Persistence**
   - Users stay logged in across sessions
   - Configurable expiry period

2. **Search Functionality**
   - Supplier search across multiple fields
   - Real-time filtering

3. **File Organization**
   - Automatic directory structure
   - Project-specific folders

4. **Default Data Initialization**
   - Pre-filled task lists
   - Standard budget categories

5. **Visual Progress Indicators**
   - Progress bars
   - Metric displays
   - Color-coded status

### Possible Future Enhancements

1. Email notifications
2. PDF report generation
3. Calendar integration
4. Cloud file storage
5. Mobile app version
6. Real-time chat
7. Invoice generation
8. Multi-language support

---

## 🎓 LEARNING OUTCOMES

### Technical Skills Demonstrated

1. **Full-Stack Development**
   - Frontend (Streamlit)
   - Backend (Python)
   - Database (MySQL)

2. **Database Design**
   - Normalization
   - Relationships
   - Indexing
   - Constraints

3. **Security**
   - Password hashing
   - Session management
   - Access control

4. **File Management**
   - Upload handling
   - Directory organization
   - Path management

5. **Software Architecture**
   - Modular design
   - Separation of concerns
   - DRY principles

6. **User Experience**
   - Intuitive navigation
   - Clear feedback
   - Error handling

---

## 📝 CONCLUSION

This Interior Design Project Management System successfully demonstrates:

✅ **Complete CRUD operations** across multiple entities
✅ **Proper database design** with normalization and relationships
✅ **Secure authentication** with role-based access
✅ **File handling** with organized storage
✅ **Clean, documented code** with modular architecture
✅ **User-friendly interface** with clear navigation
✅ **Real-world application** solving actual problems

The system is fully functional, well-documented, and ready for academic evaluation.

---

## 📚 CODE STATISTICS

- **Total Lines of Code:** ~3,500+
- **Number of Files:** 16 Python files + SQL + docs
- **Number of Functions:** 80+
- **Database Tables:** 11
- **Features Implemented:** 10+ major features
- **Comments:** Comprehensive docstrings and inline comments

---

**Developed for IB Computer Science IA**
**Date:** January 2026
**Student:** Prisha Nangalia
