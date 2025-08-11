-- Student Info App Database Setup for Supabase
-- Run these SQL commands in your Supabase SQL Editor

-- 1. Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    class VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    last_password_change TIMESTAMP DEFAULT NOW()
);

-- 2. Create students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    class VARCHAR(10) NOT NULL,
    roll INTEGER NOT NULL,
    password VARCHAR(255) NOT NULL,
    math_marks INTEGER,
    science_marks INTEGER,
    history_marks INTEGER,
    english_marks INTEGER,
    added_by VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by VARCHAR(255),
    deleted_at TIMESTAMP
);

-- 3. Create data_log table
CREATE TABLE IF NOT EXISTS data_log (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    who VARCHAR(255) NOT NULL,
    when_timestamp TIMESTAMP DEFAULT NOW()
);

-- 4. Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_roll INTEGER NOT NULL,
    date DATE NOT NULL,
    is_present BOOLEAN DEFAULT FALSE,
    image_data TEXT,
    verified_by VARCHAR(255),
    verified_at TIMESTAMP,
    UNIQUE(student_roll, date)
);

-- 5. Create clear_log table
CREATE TABLE IF NOT EXISTS clear_log (
    id SERIAL PRIMARY KEY,
    cleared_by VARCHAR(255) NOT NULL,
    cleared_at TIMESTAMP DEFAULT NOW()
);

-- 6. Insert default users (teachers and principal)
INSERT INTO users (username, password, role, class) VALUES
('teacher', 'teacher123', 'teacher', NULL),
('teacher_k', 'teacher123', 'teacher', 'K'),
('teacher_1', 'teacher123', 'teacher', '1'),
('teacher_2', 'teacher123', 'teacher', '2'),
('teacher_3', 'teacher123', 'teacher', '3'),
('teacher_4', 'teacher123', 'teacher', '4'),
('teacher_5', 'teacher123', 'teacher', '5'),
('teacher_6', 'teacher123', 'teacher', '6'),
('teacher_7', 'teacher123', 'teacher', '7'),
('teacher_8', 'teacher123', 'teacher', '8'),
('teacher_9', 'teacher123', 'teacher', '9'),
('teacher_10', 'teacher123', 'teacher', '10'),
('teacher_11', 'teacher123', 'teacher', '11'),
('teacher_12', 'teacher123', 'teacher', '12'),
('principal', 'principal123', 'principal', NULL)
ON CONFLICT (username) DO NOTHING;

-- 7. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_students_roll ON students(roll);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class);
CREATE INDEX IF NOT EXISTS idx_students_deleted ON students(is_deleted);
CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_roll, date);
CREATE INDEX IF NOT EXISTS idx_data_log_timestamp ON data_log(when_timestamp);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 8. Enable Row Level Security (RLS) for better security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE clear_log ENABLE ROW LEVEL SECURITY;

-- 9. Create RLS policies (basic policies - you may want to customize these)
-- Users table policies
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = username);

-- Students table policies
CREATE POLICY "All authenticated users can view students" ON students
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Teachers and principals can insert students" ON students
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Teachers and principals can update students" ON students
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Teachers and principals can delete students" ON students
    FOR DELETE USING (auth.role() = 'authenticated');

-- Data log table policies
CREATE POLICY "All authenticated users can view data log" ON data_log
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "All authenticated users can insert data log" ON data_log
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Attendance table policies
CREATE POLICY "All authenticated users can view attendance" ON attendance
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "All authenticated users can insert attendance" ON attendance
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "All authenticated users can update attendance" ON attendance
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Clear log table policies
CREATE POLICY "All authenticated users can view clear log" ON clear_log
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Principals can insert clear log" ON clear_log
    FOR INSERT WITH CHECK (auth.role() = 'authenticated'); 