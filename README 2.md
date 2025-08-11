# Student Information System

A comprehensive web-based student management system built with Flask, featuring AI-powered attendance tracking, grade management, and teacher administration tools.

## 🚀 Features

### Core Functionality
- **Student Management**: Add, edit, delete, and recover student records
- **Grade Management**: Track and update student marks with automatic grade calculation
- **Attendance System**: AI-powered facial recognition attendance tracking
- **Teacher Portal**: Dedicated interface for teachers to manage their classes
- **Principal Dashboard**: Administrative access to all system features

### AI-Powered Features
- **Facial Recognition**: Automated attendance verification using face detection
- **Image Processing**: Advanced image analysis for attendance validation
- **Attendance Calendar**: Visual calendar view of student attendance patterns

### Security & Authentication
- **Role-based Access Control**: Different permissions for teachers, principals, and students
- **Session Management**: Secure login/logout functionality
- **Data Protection**: Comprehensive audit logging of all system activities

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: OpenCV, ImageHash, NumPy
- **Authentication**: Flask Sessions
- **Deployment**: Vercel

## 📋 Prerequisites

- Python 3.9+
- Node.js (for Vercel CLI)
- Supabase account
- Modern web browser

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd student_info_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your Supabase credentials
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5001`
   - Use the default credentials:
     - **Principal**: `principal` / `principal123`
     - **Teacher**: `teacher_1` / `teacher123` (for class 1)

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   vercel login
   vercel
   ```

3. **Set environment variables**
   - Go to your Vercel project dashboard
   - Navigate to Settings → Environment Variables
   - Add your Supabase credentials

4. **Redeploy**
   ```bash
   vercel --prod
   ```

## 📁 Project Structure

```
student_info_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment configuration
├── runtime.txt           # Python runtime specification
├── .vercelignore         # Files to exclude from deployment
├── .env                  # Environment variables (not in repo)
├── static/               # Static files (HTML, CSS, JS)
│   ├── index.html        # Main application interface
│   └── profile_setup.html # Profile setup page
├── database.py           # Database operations
├── setup.py              # Initial setup script
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
FLASK_ENV=production
```

### Database Setup

1. **Create Supabase Project**
   - Sign up at [supabase.com](https://supabase.com)
   - Create a new project
   - Get your project URL and anon key

2. **Run Database Setup**
   ```bash
   python setup_database.py
   ```

3. **Insert Default Data**
   ```bash
   python insert_default_users.py
   ```

## 👥 User Roles

### Principal
- Full system access
- Manage all teachers and students
- View system logs and audit trails
- Recover deleted records

### Teacher
- Manage assigned class students
- Mark and verify attendance
- Update student grades
- View attendance reports

### Student
- View personal information
- Submit attendance photos
- Check grades and attendance

## 🔐 Default Credentials

### Principal Access
- **Username**: `principal`
- **Password**: `principal123`

### Teacher Access
- **Username**: `teacher_1` (for class 1)
- **Password**: `teacher123`
- **Available**: `teacher_2` through `teacher_12` for respective classes

## 📊 API Endpoints

### Authentication
- `POST /api/login` - Teacher/Principal login
- `POST /api/student/login` - Student login
- `POST /api/logout` - Logout

### Student Management
- `GET /api/students` - Get all students
- `POST /api/students` - Add new student
- `PUT /api/students/<id>` - Update student
- `DELETE /api/students/<id>` - Delete student

### Attendance
- `POST /api/student/attendance` - Mark attendance
- `GET /api/student/attendance` - Get attendance records
- `POST /api/attendance/verify/<roll>` - Verify attendance

### Grades
- `GET /api/student/grades` - Get student grades
- `PUT /api/teacher/students/<id>` - Update student marks

## 🚨 Important Notes

### Security Considerations
- Change default passwords in production
- Use HTTPS in production environments
- Regularly backup your Supabase database
- Monitor system logs for suspicious activity

### Performance Optimization
- The AI attendance system may take time to process images
- Consider implementing caching for frequently accessed data
- Monitor Vercel function execution times

### Limitations
- File uploads are limited by Vercel's serverless constraints
- Sessions may not persist across serverless function calls
- Large image processing may hit Vercel's timeout limits

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify Supabase credentials in `.env`
   - Check network connectivity
   - Ensure Supabase project is active

2. **Deployment Issues**
   - Check Vercel function logs
   - Verify all environment variables are set
   - Ensure `requirements.txt` is up to date

3. **AI Attendance Not Working**
   - Check if OpenCV is properly installed
   - Verify image format and size
   - Monitor function execution time

### Getting Help

- Check the function logs in Vercel dashboard
- Review the `server.log` file for local development
- Ensure all dependencies are properly installed

## 📈 Future Enhancements

- [ ] Real-time notifications
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Integration with external LMS
- [ ] Multi-language support
- [ ] Advanced reporting features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the project files
- Review the deployment guide (`VERCEL_DEPLOYMENT.md`)

---

**Built with ❤️ using Flask and Vercel**
