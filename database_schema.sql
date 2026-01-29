-- =====================================================
-- INTERIOR DESIGN PROJECT MANAGEMENT SYSTEM
-- MySQL Database Schema
-- =====================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS timeline;
DROP TABLE IF EXISTS gallery;
DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS budget_items;
DROP TABLE IF EXISTS notes_whiteboard;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS reference_library;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

-- =====================================================
-- USERS TABLE
-- Stores both interior designers and clients
-- =====================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- Only for designers, NULL for clients
    role ENUM('designer', 'client') NOT NULL,
    client_code VARCHAR(20) UNIQUE,  -- Only for clients, auto-generated unique code
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_client_code (client_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- PROJECTS TABLE
-- Each project links a client to a designer
-- =====================================================
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    designer_id INT NOT NULL,
    site_type VARCHAR(100),  -- residential, commercial, etc.
    contact_details TEXT,
    preferred_contact VARCHAR(50),  -- email, phone, whatsapp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (designer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_client (client_id),
    INDEX idx_designer (designer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- REFERENCE LIBRARY TABLE
-- Store reference images organized by room
-- =====================================================
CREATE TABLE reference_library (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    room_name VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,  -- Path to uploaded image
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TASKS TABLE
-- Track project tasks with progress
-- =====================================================
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    progress_percent INT DEFAULT 0,  -- 0-100
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    CHECK (progress_percent >= 0 AND progress_percent <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- NOTES & WHITEBOARD TABLE
-- Save drawings and text notes
-- =====================================================
CREATE TABLE notes_whiteboard (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    drawing_path VARCHAR(500),  -- Path to saved canvas drawing
    text_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- BUDGET ITEMS TABLE
-- Track estimated vs actual costs
-- =====================================================
CREATE TABLE budget_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    estimated_cost DECIMAL(10, 2) DEFAULT 0.00,
    actual_cost DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SUPPLIERS TABLE
-- Store supplier contact information
-- =====================================================
CREATE TABLE suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),  -- furniture, paint, electricals, etc.
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- MEASUREMENTS & DRAWINGS TABLE
-- Store CAD files and measurement drawings
-- =====================================================
CREATE TABLE measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    type ENUM('existing', 'proposed') NOT NULL,
    notes TEXT,
    file_path VARCHAR(500),  -- Path to CAD/drawing file
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- GALLERY TABLE
-- Client inspiration images
-- =====================================================
CREATE TABLE gallery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    uploaded_by ENUM('client', 'designer') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TIMELINE TABLE
-- Project milestones and deadlines
-- =====================================================
CREATE TABLE timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    milestone VARCHAR(255) NOT NULL,
    deadline DATE,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- FEEDBACK & APPROVALS TABLE
-- Client comments and approval status
-- =====================================================
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    item_type ENUM('drawing', 'image') NOT NULL,  -- what they're commenting on
    comment TEXT,
    approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Sample data for testing (OPTIONAL - Comment out in production)
-- =====================================================

-- Sample designer account
-- Password: designer123 (hashed version would be stored in production)
-- INSERT INTO users (name, email, password_hash, role) 
-- VALUES ('Jane Designer', 'designer@example.com', 'hashed_password_here', 'designer');

-- =====================================================
-- END OF SCHEMA
-- =====================================================
