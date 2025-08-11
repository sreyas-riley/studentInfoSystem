# Student Info App with Supabase Database

A comprehensive student management system with Supabase backend for secure, scalable data storage.

## 🚀 Features

- **Multi-role Authentication**: Principal, Teachers, and Students
- **Student Management**: Add, edit, delete, and recover students
- **Grade Management**: Track marks and calculate grades
- **Attendance Tracking**: Webcam-based attendance with image verification
- **Teacher Management**: Principal can manage teacher accounts
- **Data Logging**: Complete audit trail of all actions
- **Secure Database**: Supabase with Row Level Security (RLS)

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.7+
- Supabase account and project
- Git

### 1. Clone and Navigate

```bash
cd student_info_app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Supabase Database

#### A. Create Supabase Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Note your project URL and anon key

#### B. Set Up Database Tables
1. In your Supabase dashboard, go to **SQL Editor**
2. Copy and paste the contents of `supabase_setup.sql`
3. Run the SQL script
4. Verify the following tables were created:
   - `users` - User accounts and authentication
   - `students` - Student information and marks
   - `data_log` - Audit trail of all actions
   - `attendance` - Student attendance records
   - `clear_log` - Log clearing history

### 4. Configure Environment

#### Option A: Automated Setup (Recommended)
```bash
python setup.py
```
Follow the prompts to enter your Supabase credentials.

#### Option B: Manual Setup
Create a `.env` file in the project root:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_generated_secret_key
FLASK_ENV=development
```

### 5. Run the Application

```bash
python app_supabase.py
```

The application will be available at `http://localhost:5001`

## 🔐 Default Login Credentials

### Principal Access
- **Username**: `principal`
- **Password**: `principal123`
- **Permissions**: Full access to all features

### Teacher Access
- **Username**: `teacher_1` to `teacher_12` (for specific classes)
- **Password**: `teacher123`
- **Permissions**: Manage students in assigned class, view attendance, update marks

### General Teacher
- **Username**: `teacher`
- **Password**: `teacher123`
- **Permissions**: General teacher access

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    class VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    last_password_change TIMESTAMP DEFAULT NOW()
);
```

### Students Table
```sql
CREATE TABLE students (
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
```

### Data Log Table
```sql
CREATE TABLE data_log (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    who VARCHAR(255) NOT NULL,
    when_timestamp TIMESTAMP DEFAULT NOW()
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_roll INTEGER NOT NULL,
    date DATE NOT NULL,
    is_present BOOLEAN DEFAULT FALSE,
    image_data TEXT,
    verified_by VARCHAR(255),
    verified_at TIMESTAMP,
    UNIQUE(student_roll, date)
);
```

## 🔒 Security Features

### Row Level Security (RLS)
- All tables have RLS enabled
- Policies control access based on user roles
- Teachers can only access their assigned class data
- Students can only access their own information

### Environment Variables
- Supabase credentials stored securely in `.env` file
- Flask secret key generated automatically
- No hardcoded credentials in source code

### Data Protection
- Soft delete functionality for students
- Complete audit trail of all actions
- Password hashing (implemented in database layer)

## 🚀 Deployment

### Local Development
```bash
python app_supabase.py
```

### Production Deployment
1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Set up proper SSL certificates
4. Configure environment variables securely

### Environment Variables for Production
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
FLASK_SECRET_KEY=your_secure_secret_key
FLASK_ENV=production
```

## 📁 Project Structure

```
student_info_app/
├── app_supabase.py          # Main Flask application with Supabase
├── database.py              # Supabase database manager
├── requirements.txt         # Python dependencies
├── setup.py                 # Automated setup script
├── supabase_setup.sql      # Database schema and setup
├── env_example.txt         # Environment variables template
├── README_SUPABASE.md      # This file
├── static/
│   └── index.html          # Frontend application
└── .env                     # Environment variables (created during setup)
```

## 🔧 Configuration

### Supabase Settings
- **URL**: Your Supabase project URL
- **Key**: Your Supabase anon key (public key)
- **Database**: PostgreSQL with RLS enabled

### Flask Settings
- **Secret Key**: Automatically generated during setup
- **Environment**: Development/Production
- **Port**: 5001 (configurable)

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify Supabase URL and key in `.env`
   - Check if tables exist in Supabase dashboard
   - Ensure RLS policies are properly configured

2. **Import Errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

3. **Permission Denied Errors**
   - Verify user role and permissions
   - Check RLS policies in Supabase
   - Ensure proper authentication

4. **Environment Variables Not Loading**
   - Verify `.env` file exists in project root
   - Check file permissions
   - Restart the application after changes

### Debug Mode
```bash
export FLASK_ENV=development
python app_supabase.py
```

## 📈 Performance Optimization

### Database Indexes
- Roll number index for fast student lookups
- Class index for teacher queries
- Timestamp index for log queries
- Composite indexes for attendance queries

### Caching Strategy
- Consider implementing Redis for session storage
- Cache frequently accessed data
- Use database connection pooling

## 🔄 Migration from In-Memory Storage

If you're migrating from the original in-memory version:

1. **Backup Data**: Export any existing data
2. **Set Up Supabase**: Follow the setup instructions above
3. **Import Data**: Use the database manager to import existing data
4. **Update Application**: Use `app_supabase.py` instead of `app.py`

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Verify Supabase dashboard for database issues
3. Review Flask logs for application errors
4. Ensure all environment variables are set correctly

## 🔄 Updates and Maintenance

### Regular Maintenance
- Monitor database performance
- Review and update RLS policies
- Backup data regularly
- Update dependencies periodically

### Security Updates
- Keep Supabase client library updated
- Regularly rotate Flask secret key
- Monitor for security vulnerabilities
- Update RLS policies as needed

---

**Note**: This application uses Supabase for data storage, ensuring your data is secure, scalable, and accessible from anywhere. The credentials are kept private through environment variables, making it safe for public deployment. 