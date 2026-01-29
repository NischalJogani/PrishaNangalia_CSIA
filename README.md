# 🏠 Interior Design Project Management System

A comprehensive web-based platform built with **Streamlit** and **MySQL** for interior designers and their clients to manage design projects, track progress, collaborate, and share feedback.

---

## 📋 Features

### For Interior Designers (Admin):
- ✅ **Project Management** - Create clients, manage multiple projects
- 📚 **Reference Library** - Upload and organize reference images by room
- ✅ **Task Tracking** - Track tasks with progress bars and comments
- 📝 **Whiteboard & Notes** - Drawing canvas and text notes
- 💰 **Budget Overview** - Track estimated vs actual costs
- 📦 **Materials & Suppliers** - Manage supplier contacts with search
- 📐 **Measurements & Drawings** - Upload CAD files and site drawings
- 📅 **Timeline Management** - Set milestones and deadlines
- 💬 **Client Feedback** - View client approvals and comments

### For Clients:
- 👀 **View-Only Access** - View reference library, tasks, budget, timeline
- 🎨 **Design Gallery** - Upload inspiration images
- 💬 **Feedback & Approval** - Comment and approve/reject designs
- 📊 **Progress Tracking** - View overall project completion

---

## 🛠️ Technology Stack

- **Frontend & Framework:** Streamlit (Python)
- **Backend:** Python
- **Database:** MySQL
- **Database Connector:** mysql-connector-python
- **Authentication:** bcrypt + session state + cookies
- **File Storage:** Local file system (organized folders)

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server (running)
- pip (Python package manager)

### Step 1: Clone or Download the Project
```bash
cd PrishaNangalia_CSIA
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Database
Open `config.py` and update your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Your MySQL username
    'password': 'yourpass',  # Your MySQL password
    'database': 'interior_design_db',
    'port': 3306
}
```

### Step 4: Start MySQL Server
Ensure your MySQL server is running on your machine.

---

## 🚀 Running the Application

### Method 1: Run with Streamlit
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Method 2: Run with Python
```bash
python -m streamlit run app.py
```

---

## 🔧 First-Time Setup

When you run the application for the first time:

1. The **Database Setup** page will appear
2. Click **"Initialize Database"** button
3. The system will:
   - Create the MySQL database
   - Create all necessary tables
   - Set up upload directories
4. Refresh the page to start using the application

---

## 👥 User Roles & Authentication

### Interior Designer (Admin)
1. **Sign Up**: Create an account with email and password
2. **Login**: Use email and password
3. **Features**: Full access to all features

### Client
1. **Created by Designer**: Designer creates client accounts
2. **Login**: Use email + unique access code (provided by designer)
3. **Features**: View-only access + feedback submission

---

## 📁 Project Structure

```
PrishaNangalia_CSIA/
│
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Configuration settings
├── database.py                 # Database connection and operations
├── database_schema.sql         # MySQL schema (CREATE TABLE statements)
├── auth.py                     # Authentication system
├── utils.py                    # Utility helper functions
│
├── designer_dashboard.py       # Designer main dashboard
├── designer_budget.py          # Budget management module
├── designer_suppliers.py       # Suppliers management module
├── designer_measurements.py    # Measurements & drawings module
├── designer_timeline.py        # Timeline management module
├── designer_feedback.py        # Feedback viewing module
│
├── client_dashboard.py         # Client dashboard (all features)
│
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
└── uploads/                    # File storage directory (auto-created)
    └── projects/
        └── {project_id}/
            ├── reference/
            ├── drawings/
            ├── gallery/
            └── whiteboard/
```

---

## 🗄️ Database Schema

The system uses **11 tables**:

1. **users** - Both designers and clients
2. **projects** - Project information
3. **reference_library** - Reference images by room
4. **tasks** - Task tracking with progress
5. **notes_whiteboard** - Drawings and text notes
6. **budget_items** - Budget tracking
7. **suppliers** - Supplier contacts
8. **measurements** - CAD files and drawings
9. **gallery** - Inspiration images
10. **timeline** - Project milestones
11. **feedback** - Client feedback and approvals

Schema file: `database_schema.sql`

---

## 🔐 Security Features

- ✅ **Password Hashing**: bcrypt encryption
- ✅ **Session Management**: Streamlit session state
- ✅ **Persistent Login**: Cookie-based authentication
- ✅ **Role-Based Access**: Designer vs Client permissions
- ✅ **Unique Client Codes**: 6-character random codes

---

## 📝 Usage Guide

### For Designers:

1. **Sign up** and log in
2. Go to **Project Management** → Create a new client and project
3. Note the **client access code** - share it with your client
4. Select the project to make it active
5. Navigate through different sections to:
   - Upload reference images
   - Add and track tasks
   - Manage budget
   - Upload drawings
   - Set timeline milestones
   - View client feedback

### For Clients:

1. Get your **email** and **access code** from your designer
2. Login as a **Client**
3. View all project information
4. Upload inspiration images in **Design Gallery**
5. Submit feedback and approvals in **Feedback & Approval**

---

## 🎨 Key Features Explained

### Task Tracking
- Pre-filled default task list
- Progress slider (0-100%)
- Comments section
- Overall project completion metric

### Budget Management
- Pre-filled budget categories
- Estimated vs Actual cost tracking
- Automatic difference calculation
- Over/Under budget indicators

### File Organization
Files are automatically organized in folders:
```
/uploads/projects/{project_id}/reference/
/uploads/projects/{project_id}/drawings/
/uploads/projects/{project_id}/gallery/
/uploads/projects/{project_id}/whiteboard/
```

### Session Persistence
- Users stay logged in even after browser refresh
- Cookie expiry: 30 days (configurable in `config.py`)

---

## 🐛 Troubleshooting

### Database Connection Error
- Ensure MySQL server is running
- Check credentials in `config.py`
- Verify database exists: Run initialization from setup page

### Import Errors
```bash
pip install -r requirements.txt
```

### Whiteboard Not Working
Install the optional dependency:
```bash
pip install streamlit-drawable-canvas
```

### Cookie Issues
Clear browser cookies or use incognito mode for testing.

---

## 🔄 Default Data

### Default Tasks:
- Site Survey & Measurements
- Conceptual Design
- 3D Modeling & Visualization
- Material Selection
- Electrical/Plumbing Layout
- Furniture Procurement
- Painting & Wall Finishing
- And more...

### Default Budget Categories:
- Design Fees
- Furniture
- Lighting Fixtures
- Wall Paint & Finishes
- Flooring Materials
- Kitchen & Bathroom Fittings
- And more...

*(Configurable in `config.py`)*

---

## 📚 For IA Documentation

Each module contains:
- **Detailed comments** explaining functionality
- **Function docstrings** with parameters and return values
- **Clear variable names** for readability
- **Modular structure** for easy maintenance

---

## 🤝 Contributing

This is an academic project for CSIA (Computer Science Internal Assessment).

---

## 📄 License

Educational/Academic Project - 2026

---

## 👨‍💻 Author

Prisha Nangalia - CSIA Project

---

## 📞 Support

For issues or questions about the codebase, refer to:
- Code comments in each module
- Database schema in `database_schema.sql`
- This README file

---

## 🎯 Project Goals

Built as a **comprehensive academic project** demonstrating:
- Full-stack web development with Python
- Database design and management
- User authentication and authorization
- File handling and storage
- Role-based access control
- Clean, modular code architecture
- Real-world application development

---

**Happy Designing! 🎨🏠**
