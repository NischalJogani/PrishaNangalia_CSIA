# 🚀 QUICK START GUIDE

## Interior Design Project Management System Setup

---

## ⚡ Quick Installation (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install streamlit mysql-connector-python bcrypt extra-streamlit-components Pillow streamlit-drawable-canvas
```

OR use requirements.txt:
```bash
pip install -r requirements.txt
```

---

### Step 2: Start MySQL Server
Make sure MySQL is running on your computer.

**Windows:**
- Open Services → Find MySQL → Start

**Mac:**
```bash
brew services start mysql
```

**Linux:**
```bash
sudo systemctl start mysql
```

---

### Step 3: Configure Database Credentials
Open `config.py` and update these lines (around line 11-17):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',        # ← Change this to your MySQL username
    'password': '',        # ← Change this to your MySQL password
    'database': 'interior_design_db',
    'port': 3306
}
```

---

### Step 4: Run the Application
```bash
streamlit run app.py
```

Your browser will automatically open at: `http://localhost:8501`

---

### Step 5: Initialize Database (First Time Only)
1. Click **"Initialize Database"** button on the setup page
2. Wait for success messages
3. Refresh the page

---

## 🎉 You're Ready!

### Create Your First Designer Account:
1. Select **"Interior Designer"**
2. Click **"Sign Up"** tab
3. Fill in:
   - Name: Test Designer
   - Email: test@example.com
   - Password: password123
4. Click **"Sign Up"**
5. Switch to **"Login"** tab and login

### Create Your First Project:
1. Go to **"Project Management"**
2. Fill in client details
3. Click **"Create Client & Project"**
4. Note the client access code!

---

## 📱 Client Login

Give your client:
- Their email
- The 6-character access code

They can then login as a **Client** user.

---

## 🔍 Troubleshooting

### "Connection refused" error?
→ MySQL is not running. Start MySQL server.

### "Access denied" error?
→ Check username/password in `config.py`

### Module not found errors?
→ Run: `pip install -r requirements.txt`

### Page not loading?
→ Check if port 8501 is free. If not, Streamlit will use 8502, 8503, etc.

---

## 📁 File Structure Summary

```
Your Project/
├── app.py              ← Main file to run
├── config.py           ← Database settings
├── database.py         ← Database functions
├── auth.py             ← Login system
├── designer_*.py       ← Designer features
├── client_dashboard.py ← Client features
└── uploads/            ← Auto-created for files
```

---

## 🎯 Testing Checklist

- [ ] MySQL server is running
- [ ] Dependencies installed
- [ ] config.py updated with correct credentials
- [ ] App starts without errors
- [ ] Database initialized successfully
- [ ] Designer signup works
- [ ] Designer login works
- [ ] Project created successfully
- [ ] Client login works (with access code)

---

## 🆘 Need Help?

1. Check console for error messages
2. Verify MySQL connection: Run `python -c "import mysql.connector; print('OK')"`
3. Check if database exists: Login to MySQL and run `SHOW DATABASES;`

---

## 🎓 Academic Note

This project demonstrates:
- **Database Design** - 11 tables with relationships
- **Authentication** - Hashed passwords + sessions
- **File Management** - Organized upload system
- **Role-based Access** - Designer vs Client permissions
- **Full CRUD Operations** - Create, Read, Update, Delete
- **Clean Architecture** - Modular, well-commented code

Perfect for IA documentation! 📝

---

**Happy Coding! 🚀**
