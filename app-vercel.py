from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask import render_template
from datetime import datetime, timedelta
import io
import base64
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production
CORS(app, supports_credentials=True)

# In-memory data
students = []
deleted_students = []
data_log = []
student_attendance = {}  # Track student attendance by date
attendance_images = {}  # Store attendance images by date and roll number

# Available classes (K-12)
AVAILABLE_CLASSES = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

# Teacher management data
teachers = [
    {
        'username': 'teacher_k',
        'password': 'teacher123',
        'role': 'teacher',
        'class': 'K',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_1',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '1',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_2',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '2',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_3',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '3',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_4',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '4',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_5',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '5',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_6',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '6',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_7',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '7',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_8',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '8',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_9',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '9',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_10',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '10',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_11',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '11',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'teacher_12',
        'password': 'teacher123',
        'role': 'teacher',
        'class': '12',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    },
    {
        'username': 'principal',
        'password': 'principal123',
        'role': 'principal',
        'class': 'all',
        'created_at': '2024-01-01 00:00:00',
        'last_password_change': '2024-01-01 00:00:00'
    }
]

def nowstr():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_grade(marks):
    if marks >= 90:
        return 'A+'
    elif marks >= 80:
        return 'A'
    elif marks >= 70:
        return 'B'
    elif marks >= 60:
        return 'C'
    elif marks >= 50:
        return 'D'
    else:
        return 'F'

def get_teacher_class(username):
    for teacher in teachers:
        if teacher['username'] == username:
            return teacher['class']
    return None

def _strip_data_url_prefix(data_url: str) -> str:
    """Remove data URL prefix from base64 image data"""
    if data_url.startswith('data:image/'):
        return data_url.split(',', 1)[1]
    return data_url

def _get_face_encoding_from_b64(b64_data: str):
    """Simplified face encoding - just return a placeholder for now"""
    # This is a placeholder since we're not using OpenCV in this version
    return "placeholder_encoding"

def _faces_match(profile_b64: str, capture_b64: str, threshold: float = 0.6):
    """Simplified face matching - always return True for demo"""
    # This is a placeholder since we're not using OpenCV in this version
    return True

def _enhanced_image_verification(image_data: str, roll_number: int):
    """Simplified image verification without OpenCV"""
    try:
        # Basic validation - just check if image data exists
        if not image_data or len(image_data) < 100:
            return False, "Image data too small or invalid"
        
        # For demo purposes, always return success
        return True, "Image verification successful (demo mode)"
    except Exception as e:
        return False, f"Image verification error: {str(e)}"

def _ai_verify_attendance(image_data: str, roll_number: int):
    """Simplified AI verification without OpenCV"""
    try:
        # Basic validation
        if not image_data:
            return False, "No image data provided"
        
        # For demo purposes, always return success
        return True, "AI verification successful (demo mode)"
    except Exception as e:
        return False, f"AI verification error: {str(e)}"

def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    for teacher in teachers:
        if teacher['username'] == username and teacher['password'] == password:
            session['user'] = username
            session['role'] = teacher['role']
            return jsonify({'success': True, 'role': teacher['role']})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@require_login
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/whoami')
@require_login
def whoami():
    return jsonify({'user': session['user'], 'role': session['role']})

@app.route('/api/student/login', methods=['POST'])
def student_login():
    data = request.get_json()
    roll_number = data.get('roll_number')
    
    # Find student by roll number
    for student in students:
        if student['roll'] == roll_number:
            session['user'] = f"student_{roll_number}"
            session['role'] = 'student'
            session['student_roll'] = roll_number
            return jsonify({'success': True, 'student': student})
    
    return jsonify({'error': 'Student not found'}), 404

@app.route('/api/student/attendance', methods=['POST'])
@require_login
def mark_attendance():
    if session['role'] != 'student':
        return jsonify({'error': 'Only students can mark attendance'}), 403
    
    data = request.get_json()
    image_data = data.get('image')
    roll_number = session.get('student_roll')
    
    if not image_data:
        return jsonify({'error': 'Image data required'}), 400
    
    # Simplified attendance marking without AI verification
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today not in student_attendance:
        student_attendance[today] = {}
    
    student_attendance[today][roll_number] = {
        'timestamp': nowstr(),
        'verified': True,
        'method': 'manual'
    }
    
    # Store image data
    if today not in attendance_images:
        attendance_images[today] = {}
    attendance_images[today][roll_number] = image_data
    
    return jsonify({'success': True, 'message': 'Attendance marked successfully'})

@app.route('/api/student/attendance', methods=['GET'])
@require_login
def get_student_attendance():
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied'}), 403
    
    roll_number = request.args.get('roll_number', type=int)
    if not roll_number:
        return jsonify({'error': 'Roll number required'}), 400
    
    # Get attendance for the student
    attendance_records = []
    for date, attendance_data in student_attendance.items():
        if roll_number in attendance_data:
            attendance_records.append({
                'date': date,
                'timestamp': attendance_data[roll_number]['timestamp'],
                'verified': attendance_data[roll_number]['verified']
            })
    
    return jsonify({'attendance': attendance_records})

@app.route('/api/student/grades', methods=['GET'])
@require_login
def get_student_grades():
    if session['role'] != 'student':
        return jsonify({'error': 'Only students can view their grades'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    # Find student
    student = None
    for s in students:
        if s['roll'] == roll_number:
            student = s
            break
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'student': {
            'name': student['name'],
            'roll': student['roll'],
            'class': student['class'],
            'marks': student['marks'],
            'grade': calculate_grade(student['marks'])
        }
    })

@app.route('/api/classes', methods=['GET'])
@require_login
def get_classes():
    return jsonify({'classes': AVAILABLE_CLASSES})

@app.route('/api/teacher/students', methods=['GET'])
@require_login
def get_teacher_students():
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied'}), 403
    
    teacher_class = get_teacher_class(session['user'])
    if session['role'] == 'teacher' and teacher_class != 'all':
        # Teacher can only see their class students
        class_students = [s for s in students if s['class'] == teacher_class]
        return jsonify({'students': class_students})
    else:
        # Principal can see all students
        return jsonify({'students': students})

@app.route('/api/students', methods=['GET'])
@require_login
def get_students():
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied'}), 403
    
    teacher_class = get_teacher_class(session['user'])
    if session['role'] == 'teacher' and teacher_class != 'all':
        # Teacher can only see their class students
        class_students = [s for s in students if s['class'] == teacher_class]
        return jsonify({'students': class_students})
    else:
        # Principal can see all students
        return jsonify({'students': students})

@app.route('/api/students', methods=['POST'])
@require_login
def add_student():
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    student_class = data.get('class')
    roll = data.get('roll')
    marks = data.get('marks', 0)
    
    if not all([name, age, student_class, roll]):
        return jsonify({'error': 'All fields are required'}), 400
    
    # Check if roll number already exists
    if any(s['roll'] == roll for s in students):
        return jsonify({'error': 'Roll number already exists'}), 400
    
    new_student = {
        'name': name,
        'age': age,
        'class': student_class,
        'roll': roll,
        'marks': marks
    }
    
    students.append(new_student)
    data_log.insert(0, {
        'action': 'add',
        'student': new_student.copy(),
        'who': session['role'],
        'when': nowstr()
    })
    
    return jsonify({'success': True, 'student': new_student})

@app.route('/api/students/<int:idx>', methods=['PUT'])
@require_login
def edit_student(idx):
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied'}), 403
    
    if idx < 0 or idx >= len(students):
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.get_json()
    original_student = students[idx].copy()
    
    # Update student data
    if 'name' in data:
        students[idx]['name'] = data['name']
    if 'age' in data:
        students[idx]['age'] = data['age']
    if 'class' in data:
        students[idx]['class'] = data['class']
    if 'roll' in data:
        students[idx]['roll'] = data['roll']
    if 'marks' in data:
        students[idx]['marks'] = data['marks']
    
    data_log.insert(0, {
        'action': 'edit',
        'student': students[idx].copy(),
        'original_student': original_student,
        'who': session['role'],
        'when': nowstr()
    })
    
    return jsonify({'success': True, 'student': students[idx]})

@app.route('/api/students/<int:idx>', methods=['DELETE'])
@require_login
def delete_student(idx):
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied'}), 403
    
    if idx < 0 or idx >= len(students):
        return jsonify({'error': 'Student not found'}), 404
    
    deleted_student = students.pop(idx)
    deleted_students.append(deleted_student)
    
    data_log.insert(0, {
        'action': 'delete',
        'student': deleted_student,
        'who': session['role'],
        'when': nowstr()
    })
    
    return jsonify({'success': True})

@app.route('/api/deleted_students', methods=['GET'])
@require_login
def get_deleted_students():
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    return jsonify({'deleted_students': deleted_students})

@app.route('/api/deleted_students/<int:idx>/recover', methods=['POST'])
@require_login
def recover_student(idx):
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    
    if idx < 0 or idx >= len(deleted_students):
        return jsonify({'error': 'Student not found'}), 404
    
    recovered_student = deleted_students.pop(idx)
    students.append(recovered_student)
    
    data_log.insert(0, {
        'action': 'recover',
        'student': recovered_student,
        'who': session['role'],
        'when': nowstr()
    })
    
    return jsonify({'success': True})

@app.route('/api/log', methods=['GET'])
@require_login
def get_log():
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    return jsonify({'log': data_log})

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
