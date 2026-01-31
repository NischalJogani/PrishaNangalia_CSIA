# 🏠 Interior Design Project Management System

> **Academic Project (CSIA)** - A comprehensive web-based platform for interior designers and clients to collaborate on design projects.

---

## 📋 Overview

**Built with:** Streamlit (Python) + MySQL  
**Purpose:** Enable seamless collaboration between interior designers and their clients through project management, task tracking, budget monitoring, and feedback systems.

---

## ✨ Features

### 👨‍🎨 For Interior Designers:
- **Project Management** - Create clients with 8-digit access codes, manage multiple projects
- **Reference Library** - Upload and organize reference images by room
- **Task Tracking** - Track project tasks with progress bars and comments
- **Whiteboard & Notes** - Drawing canvas and text notes for brainstorming
- **Budget Overview** - Track estimated vs actual costs with statistics
- **Materials & Suppliers** - Manage supplier database with search functionality
- **Measurements & Drawings** - Upload CAD files and site drawings (existing + proposed)
- **Timeline Management** - Set project milestones with deadlines
- **Client Feedback** - View client approvals and rejection comments

### 👤 For Clients:
- **View-Only Dashboards** - Access to reference library, tasks, budget, measurements, timeline
- **Design Gallery** - Upload inspiration images for the designer
- **Feedback & Approval** - Comment on designs and approve/reject with status tracking
- **Progress Monitoring** - Real-time view of project completion percentage

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- MySQL Server (running)

### Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure database credentials
# Create .streamlit/secrets.toml:
[database]
host = "localhost"
user = "root"
password = "your_mysql_password"
database = "interior_designer_app_prisha_csia"
port = 3306

# 3. Run the application
streamlit run app.py
```

The app will open at **http://localhost:8501**

### First-Time Setup
1. Database auto-initializes on first run (11 tables created)
2. Create designer account via "Sign Up" tab
3. Login and create your first client + project
4. Share 8-digit access code with client

---

## 🔐 Login Credentials

### Current Test Accounts

**Designer:**
- Tab: "Interior Designer"
- Email: `nischal@test.com`
- Password: [your signup password]

**Clients:**
- Tab: "Client"
- **Timepass:** `testing1@client.com` / Code: `B6EU0DZ2`
- **Test:** `tester@client.com` / Code: `LS1C3K`

⚠️ **Common Mistake:** Don't use client credentials in the Designer tab!

---

## 📂 Project Structure

```
PrishaNangalia_CSIA/
├── app.py                    # Main entry point & routing
├── auth.py                   # Authentication & user management
├── database.py               # Database operations
├── config.py                 # Configuration & secrets
├── utils.py                  # Helper functions
├── designer_dashboard.py     # All 9 designer features
├── client_dashboard.py       # All 7 client features
├── database_schema.sql       # Database structure
├── requirements.txt          # Python dependencies
├── .streamlit/secrets.toml   # Database credentials
└── uploads/                  # Project files
```

**Only 7 core Python files!** Clean and maintainable.

---

## 🗄️ Database Structure

**11 Tables:**
- `users` - Designers + clients (with client_code field)
- `projects` - Links designers to clients
- `reference_library` - Reference images by room
- `tasks` - Project tasks with progress tracking
- `notes_whiteboard` - Text notes + canvas drawings
- `budget_items` - Estimated vs actual costs
- `suppliers` - Supplier contact database
- `measurements` - CAD files & drawings (existing/proposed)
- `gallery` - Client + designer inspiration images
- `timeline` - Project milestones with deadlines
- `feedback` - Client approval/rejection comments

---

## 🎯 How It Works

### Designer Workflow:
1. **Login** → Designer dashboard
2. **Project Management** → Create client (generates 8-digit code)
3. **Select project** → Access all features for that project
4. **Upload references** → Organize by room
5. **Track tasks** → Update progress with sliders
6. **Manage budget** → Add items, track costs
7. **Set timeline** → Add milestones with deadlines
8. **View feedback** → See client approvals/rejections

### Client Workflow:
1. **Login** → Client dashboard (using email + 8-digit code)
2. **View project data** → References, tasks, budget, timeline, measurements
3. **Upload gallery images** → Share inspiration with designer
4. **Submit feedback** → Approve/reject designs with comments

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | Streamlit 1.28.0+ |
| Backend | Python 3.8+ |
| Database | MySQL 8.0+ |
| Authentication | bcrypt (password hashing) |
| Session Management | extra-streamlit-components (cookies) |
| File Upload | Pillow (image processing) |
| Drawing | streamlit-drawable-canvas (whiteboard) |

**Dependencies:**
```txt
streamlit>=1.28.0
mysql-connector-python==8.0.33
bcrypt==4.0.1
extra-streamlit-components==0.1.60
Pillow==10.0.0
streamlit-drawable-canvas==0.9.3
```

---

## 🐛 Troubleshooting

### Database Connection Failed
- ✅ Check MySQL is running
- ✅ Verify credentials in `.streamlit/secrets.toml`
- ✅ Ensure database exists (auto-created on first run)

### Login Issues
- ✅ Designer uses: Email + Password
- ✅ Client uses: Email + 8-Digit Access Code
- ✅ Make sure you're on the correct tab!

### Import Errors
- ✅ Run: `pip install -r requirements.txt`

### File Upload Fails
- ✅ Check `uploads/` folder exists
- ✅ Verify file extension is allowed in config

---

## 📝 Security Features

- ✅ Bcrypt password hashing (10 rounds)
- ✅ 8-character random access codes
- ✅ Session-based authentication with cookies
- ✅ Role-based access control (designer vs client)
- ✅ Secrets management (credentials not in code)
- ✅ SQL injection prevention (parameterized queries)

---

## 🧪 Testing Checklist

### Designer Tests:
- [ ] Create new client → Verify 8-digit code displays
- [ ] Upload reference images → Check they appear by room
- [ ] Update task progress → Verify overall % updates
- [ ] Add budget item → Check statistics calculate correctly
- [ ] Add supplier → Test search functionality
- [ ] Upload measurement → Verify file saves
- [ ] Add timeline milestone → Check status updates
- [ ] View client feedback → Verify approval status displays

### Client Tests:
- [ ] Login with 8-digit code → Access dashboard
- [ ] View all sections → References, tasks, budget, timeline
- [ ] Upload gallery image → Verify upload success
- [ ] Submit feedback → Check approval status saves

---

## 🎓 Academic Context (CSIA)

**Computer Science Internal Assessment**  
This project demonstrates:
- Full-stack web development
- Database design and normalization
- User authentication and authorization
- File handling and organization
- Real-world client-designer collaboration workflow

---

## 🎉 Ready to Use!

1. Start MySQL
2. Run `streamlit run app.py`
3. Create designer account
4. Create first client
5. Share access code with client
6. Start collaborating! ✨

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** ✅ Production Ready
