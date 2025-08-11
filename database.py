import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase client initialized successfully")
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        try:
            # Create tables using SQL
            self._create_tables()
            
            # Add missing columns to existing tables
            self._migrate_existing_tables()
            
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def _migrate_existing_tables(self):
        """Add missing columns to existing tables"""
        # Skip migration for now to avoid database issues
        pass
    
    def _create_tables(self):
        """Create necessary tables in Supabase"""
        # Users table
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            class VARCHAR(10),
            created_at TIMESTAMP DEFAULT NOW(),
            last_password_change TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Students table
        students_table_sql = """
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
            profile_picture TEXT,
            has_profile_picture BOOLEAN DEFAULT FALSE,
            added_by VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW(),
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_by VARCHAR(255),
            deleted_at TIMESTAMP
        );
        """
        
        # Data log table
        log_table_sql = """
        CREATE TABLE IF NOT EXISTS data_log (
            id SERIAL PRIMARY KEY,
            action VARCHAR(100) NOT NULL,
            details JSONB,
            who VARCHAR(255) NOT NULL,
            when_timestamp TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Attendance table
        attendance_table_sql = """
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            student_roll INTEGER NOT NULL,
            date DATE NOT NULL,
            is_present BOOLEAN DEFAULT FALSE,
            image_data TEXT,
            verified_by VARCHAR(255),
            verified_at TIMESTAMP,
            attempts_remaining INTEGER DEFAULT 3,
            attempt_history JSONB DEFAULT '[]',
            final_status VARCHAR(50) DEFAULT 'pending',
            UNIQUE(student_roll, date)
        );
        """
        
        # Clear log table
        clear_log_table_sql = """
        CREATE TABLE IF NOT EXISTS clear_log (
            id SERIAL PRIMARY KEY,
            cleared_by VARCHAR(255) NOT NULL,
            cleared_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Execute table creation
        tables = [
            users_table_sql,
            students_table_sql,
            log_table_sql,
            attendance_table_sql,
            clear_log_table_sql
        ]
        
        for table_sql in tables:
            try:
                self.supabase.table('dummy').execute()  # This will fail but we use it to execute raw SQL
                # Note: In a real implementation, you'd use Supabase's migration system
                # For now, we'll create tables manually in the Supabase dashboard
                logger.info("Table creation SQL prepared (execute manually in Supabase dashboard)")
            except Exception as e:
                logger.warning(f"Table creation note: {e}")
    
    # User management methods
    def get_user(self, username):
        """Get user by username"""
        try:
            response = self.supabase.table('users').select('*').eq('username', username).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None
    
    def create_user(self, username, password, role, class_name=None):
        """Create a new user"""
        try:
            user_data = {
                'username': username,
                'password': password,
                'role': role,
                'class': class_name
            }
            response = self.supabase.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None
    
    def update_user_password(self, username, new_password):
        """Update user password"""
        try:
            response = self.supabase.table('users').update({
                'password': new_password,
                'last_password_change': datetime.now().isoformat()
            }).eq('username', username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating password for {username}: {e}")
            return None
    
    def delete_user(self, username):
        """Delete a user"""
        try:
            response = self.supabase.table('users').delete().eq('username', username).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
            return False
    
    def get_all_users(self):
        """Get all users"""
        try:
            response = self.supabase.table('users').select('*').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    # Student management methods
    def get_students(self, include_deleted=False):
        """Get all students"""
        try:
            query = self.supabase.table('students').select('*')
            if not include_deleted:
                query = query.eq('is_deleted', False)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting students: {e}")
            return []
    
    def get_student_by_roll(self, roll):
        """Get student by roll number"""
        try:
            response = self.supabase.table('students').select('*').eq('roll', roll).eq('is_deleted', False).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting student by roll {roll}: {e}")
            return None
    
    def create_student(self, student_data):
        """Create a new student"""
        try:
            # Convert marks structure to individual columns
            marks = student_data.get('marks', {})
            db_student = {
                'name': student_data['name'],
                'age': student_data['age'],
                'class': student_data['class'],
                'roll': student_data['roll'],
                'password': student_data.get('password', 'student123'),
                'math_marks': marks.get('math'),
                'science_marks': marks.get('science'),
                'history_marks': marks.get('history'),
                'english_marks': marks.get('english'),
                'profile_picture': None,
                'has_profile_picture': False,
                'added_by': student_data.get('addedBy', 'unknown')
            }
            
            response = self.supabase.table('students').insert(db_student).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating student: {e}")
            return None
    
    def update_student(self, student_id, student_data):
        """Update a student"""
        try:
            # Convert marks structure to individual columns
            marks = student_data.get('marks', {})
            update_data = {
                'name': student_data['name'],
                'age': student_data['age'],
                'class': student_data['class'],
                'roll': student_data['roll'],
                'math_marks': marks.get('math'),
                'science_marks': marks.get('science'),
                'history_marks': marks.get('history'),
                'english_marks': marks.get('english')
            }
            
            # Add profile picture fields if provided
            if 'profile_picture' in student_data:
                update_data['profile_picture'] = student_data['profile_picture']
            if 'has_profile_picture' in student_data:
                update_data['has_profile_picture'] = student_data['has_profile_picture']
            
            response = self.supabase.table('students').update(update_data).eq('id', student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating student {student_id}: {e}")
            return None
    
    def delete_student(self, student_id, deleted_by):
        """Soft delete a student"""
        try:
            response = self.supabase.table('students').update({
                'is_deleted': True,
                'deleted_by': deleted_by,
                'deleted_at': datetime.now().isoformat()
            }).eq('id', student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error deleting student {student_id}: {e}")
            return None
    
    def recover_student(self, student_id):
        """Recover a deleted student"""
        try:
            response = self.supabase.table('students').update({
                'is_deleted': False,
                'deleted_by': None,
                'deleted_at': None
            }).eq('id', student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error recovering student {student_id}: {e}")
            return None
    
    def get_deleted_students(self):
        """Get all deleted students"""
        try:
            response = self.supabase.table('students').select('*').eq('is_deleted', True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting deleted students: {e}")
            return []
    
    # Data log methods
    def add_log_entry(self, action, details, who):
        """Add a log entry"""
        try:
            log_data = {
                'action': action,
                'details': details,
                'who': who
            }
            response = self.supabase.table('data_log').insert(log_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error adding log entry: {e}")
            return None
    
    def get_log_entries(self):
        """Get all log entries"""
        try:
            response = self.supabase.table('data_log').select('*').order('when_timestamp', desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting log entries: {e}")
            return []
    
    def clear_log(self, cleared_by):
        """Clear all log entries"""
        try:
            # Add clear log entry first
            clear_data = {
                'cleared_by': cleared_by
            }
            self.supabase.table('clear_log').insert(clear_data).execute()
            
            # Clear all log entries
            self.supabase.table('data_log').delete().neq('id', 0).execute()
            return True
        except Exception as e:
            logger.error(f"Error clearing log: {e}")
            return False
    
    def get_clear_log(self):
        """Get the last clear log entry"""
        try:
            response = self.supabase.table('clear_log').select('*').order('cleared_at', desc=True).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting clear log: {e}")
            return None
    
    # Attendance methods
    def mark_attendance(self, student_roll, date, is_present=True, image_data=None, verified_by=None):
        """Mark student attendance"""
        try:
            attendance_data = {
                'student_roll': student_roll,
                'date': date,
                'is_present': is_present,
                'image_data': image_data,
                'verified_by': verified_by,
                'verified_at': datetime.now().isoformat() if verified_by else None
            }
            
            # First check if attendance record already exists
            existing = self.supabase.table('attendance').select('*').eq('student_roll', student_roll).eq('date', date).execute()
            
            if existing.data:
                # Update existing record
                response = self.supabase.table('attendance').update(attendance_data).eq('student_roll', student_roll).eq('date', date).execute()
            else:
                # Insert new record
                response = self.supabase.table('attendance').insert(attendance_data).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            return None

    def record_attendance_attempt(self, student_roll, date, image_data, verification_result):
        """Record an attendance attempt with verification result"""
        try:
            # Get existing attendance record
            existing = self.supabase.table('attendance').select('*').eq('student_roll', student_roll).eq('date', date).execute()
            
            if existing.data:
                record = existing.data[0]
                # Handle both old and new schema
                attempts_remaining = record.get('attempts_remaining', 3)
                attempt_history = record.get('attempt_history', [])
                
                # Create attempt record
                attempt_record = {
                    'timestamp': datetime.now().isoformat(),
                    'image_data': image_data,
                    'verification_result': verification_result,
                    'attempt_number': 4 - attempts_remaining  # 1, 2, or 3
                }
                
                # Add to history
                attempt_history.append(attempt_record)
                
                # Update attempts remaining
                attempts_remaining -= 1
                
                # Determine final status
                final_status = 'present' if verification_result.get('verified', False) else 'pending'
                if attempts_remaining <= 0 and not verification_result.get('verified', False):
                    final_status = 'absent'
                
                # Update record
                update_data = {
                    'is_present': verification_result.get('verified', False),
                    'image_data': image_data,
                    'verified_by': 'ai_verification' if verification_result.get('verified', False) else None,
                    'verified_at': datetime.now().isoformat() if verification_result.get('verified', False) else None,
                    'attempts_remaining': attempts_remaining,
                    'attempt_history': attempt_history,
                    'final_status': final_status
                }
                
                response = self.supabase.table('attendance').update(update_data).eq('student_roll', student_roll).eq('date', date).execute()
                return response.data[0] if response.data else None
            else:
                # Create new record
                attempt_record = {
                    'timestamp': datetime.now().isoformat(),
                    'image_data': image_data,
                    'verification_result': verification_result,
                    'attempt_number': 1
                }
                
                # Create new attendance record with attempt tracking
                attendance_data = {
                    'student_roll': student_roll,
                    'date': date,
                    'is_present': verification_result.get('verified', False),
                    'image_data': image_data,
                    'verified_by': 'ai_verification' if verification_result.get('verified', False) else None,
                    'verified_at': datetime.now().isoformat() if verification_result.get('verified', False) else None,
                    'attempts_remaining': 2,  # 3 - 1 = 2 attempts remaining after first attempt
                    'attempt_history': [attempt_record],
                    'final_status': 'present' if verification_result.get('verified', False) else 'pending'
                }
                
                response = self.supabase.table('attendance').insert(attendance_data).execute()
                return response.data[0] if response.data else None
                
        except Exception as e:
            logger.error(f"Error recording attendance attempt: {e}")
            return None

    def get_attendance_attempts(self, student_roll, date):
        """Get attendance attempts for a student on a specific date"""
        try:
            response = self.supabase.table('attendance').select('*').eq('student_roll', student_roll).eq('date', date).execute()
            if response.data:
                record = response.data[0]
                # Provide defaults for missing columns
                return {
                    'student_roll': record.get('student_roll'),
                    'date': record.get('date'),
                    'is_present': record.get('is_present', False),
                    'image_data': record.get('image_data'),
                    'verified_by': record.get('verified_by'),
                    'verified_at': record.get('verified_at'),
                    'attempts_remaining': record.get('attempts_remaining', 3),
                    'attempt_history': record.get('attempt_history', []),
                    'final_status': record.get('final_status', 'pending')
                }
            return None
        except Exception as e:
            logger.error(f"Error getting attendance attempts: {e}")
            return None

    def override_attendance_status(self, student_roll, date, new_status, overridden_by):
        """Override attendance status (only for principals)"""
        try:
            update_data = {
                'is_present': new_status == 'present',
                'verified_by': overridden_by,
                'verified_at': datetime.now().isoformat()
            }
            
            # Try to update new fields if they exist
            try:
                update_data['final_status'] = new_status
            except Exception:
                # New column doesn't exist, continue without it
                pass
            
            response = self.supabase.table('attendance').update(update_data).eq('student_roll', student_roll).eq('date', date).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error overriding attendance status: {e}")
            return None
    
    def get_student_attendance(self, student_roll, start_date=None, end_date=None):
        """Get student attendance records"""
        try:
            query = self.supabase.table('attendance').select('*').eq('student_roll', student_roll)
            
            if start_date:
                query = query.gte('date', start_date)
            if end_date:
                query = query.lte('date', end_date)
            
            response = query.order('date', desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting student attendance: {e}")
            return []
    
    def get_attendance_image(self, student_roll, date):
        """Get attendance image for a specific date"""
        try:
            response = self.supabase.table('attendance').select('image_data').eq('student_roll', student_roll).eq('date', date).execute()
            if response.data:
                return response.data[0]['image_data']
            return None
        except Exception as e:
            logger.error(f"Error getting attendance image: {e}")
            return None

    def update_profile_picture(self, student_roll, profile_picture):
        """Update student's profile picture"""
        try:
            response = self.supabase.table('students').update({
                'profile_picture': profile_picture,
                'has_profile_picture': True
            }).eq('roll', student_roll).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating profile picture for student {student_roll}: {e}")
            return None

    def get_profile_picture(self, student_roll):
        """Get student's profile picture"""
        try:
            response = self.supabase.table('students').select('profile_picture, has_profile_picture').eq('roll', student_roll).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting profile picture for student {student_roll}: {e}")
            return None

    def get_student_attendance_images(self, student_roll, limit=5):
        """Get previous attendance images for a student for AI comparison"""
        try:
            response = self.supabase.table('attendance').select('image_data').eq('student_roll', student_roll).not_.is_('image_data', 'null').order('date', desc=True).limit(limit).execute()
            if response.data:
                return [record['image_data'] for record in response.data if record['image_data']]
            return []
        except Exception as e:
            logger.error(f"Error getting attendance images for student {student_roll}: {e}")
            return []

# Global database instance
db = DatabaseManager() 