-- Fix RLS Policies for Student Info App
-- Run this in your Supabase SQL Editor

-- First, let's drop the existing restrictive policies
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "All authenticated users can view students" ON students;
DROP POLICY IF EXISTS "Teachers and principals can insert students" ON students;
DROP POLICY IF EXISTS "Teachers and principals can update students" ON students;
DROP POLICY IF EXISTS "Teachers and principals can delete students" ON students;
DROP POLICY IF EXISTS "All authenticated users can view data log" ON data_log;
DROP POLICY IF EXISTS "All authenticated users can insert data log" ON data_log;
DROP POLICY IF EXISTS "All authenticated users can view attendance" ON attendance;
DROP POLICY IF EXISTS "All authenticated users can insert attendance" ON attendance;
DROP POLICY IF EXISTS "All authenticated users can update attendance" ON attendance;
DROP POLICY IF EXISTS "All authenticated users can view clear log" ON clear_log;
DROP POLICY IF EXISTS "Principals can insert clear log" ON clear_log;

-- Create more permissive policies for development
-- Users table - allow all operations for now
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL USING (true) WITH CHECK (true);

-- Students table - allow all operations for now
CREATE POLICY "Allow all operations on students" ON students
    FOR ALL USING (true) WITH CHECK (true);

-- Data log table - allow all operations for now
CREATE POLICY "Allow all operations on data_log" ON data_log
    FOR ALL USING (true) WITH CHECK (true);

-- Attendance table - allow all operations for now
CREATE POLICY "Allow all operations on attendance" ON attendance
    FOR ALL USING (true) WITH CHECK (true);

-- Clear log table - allow all operations for now
CREATE POLICY "Allow all operations on clear_log" ON clear_log
    FOR ALL USING (true) WITH CHECK (true);

-- Now insert the default users
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

-- Verify the insertion
SELECT username, role, class FROM users ORDER BY username; 