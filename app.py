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
    }
]

# Hardcoded users (including teachers)
USERS = {
    'teacher': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_k': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_1': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_2': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_3': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_4': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_5': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_6': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_7': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_8': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_9': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_10': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_11': {'password': 'teacher123', 'role': 'teacher'},
    'teacher_12': {'password': 'teacher123', 'role': 'teacher'},
    'principal': {'password': 'principal123', 'role': 'principal'}
}

# --- Helper functions ---
def nowstr():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_grade(marks):
    """Calculate grade based on marks (0-100)"""
    if marks >= 97:
        return 'A+'
    elif marks >= 93:
        return 'A'
    elif marks >= 90:
        return 'A-'
    elif marks >= 87:
        return 'B+'
    elif marks >= 83:
        return 'B'
    elif marks >= 80:
        return 'B-'
    elif marks >= 77:
        return 'C+'
    elif marks >= 73:
        return 'C'
    elif marks >= 70:
        return 'C-'
    elif marks >= 67:
        return 'D+'
    elif marks >= 63:
        return 'D'
    elif marks >= 60:
        return 'D-'
    else:
        return 'F'

def get_teacher_class(username):
    """Get the class assigned to a teacher"""
    for teacher in teachers:
        if teacher['username'] == username:
            return teacher.get('class')
    return None


def _strip_data_url_prefix(data_url: str) -> str:
    """Strip data URL prefix from base64 image data"""
    if data_url.startswith('data:image/'):
        return data_url.split('base64,', 1)[1]
    return data_url


def _get_face_encoding_from_b64(b64_data: str):
    """Return one face encoding from a base64 image, or None.
    Tries to import face_recognition lazily.
    """
    try:
        import face_recognition  # type: ignore
    except Exception:
        return None

    try:
        raw = base64.b64decode(_strip_data_url_prefix(b64_data))
        image = face_recognition.load_image_file(io.BytesIO(raw))
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return None
        return encodings[0]
    except Exception:
        return None


def _faces_match(profile_b64: str, capture_b64: str, threshold: float = 0.6):
    """Compare two base64 images via face_recognition when available.

    Returns True/False if computed, or None if AI lib unavailable.
    """
    try:
        import face_recognition  # type: ignore
    except Exception:
        # Try a weak fallback using perceptual hash if PIL+imagehash exist
        try:
            from PIL import Image  # type: ignore
            import imagehash  # type: ignore
            prof_raw = base64.b64decode(_strip_data_url_prefix(profile_b64))
            cap_raw = base64.b64decode(_strip_data_url_prefix(capture_b64))
            prof_img = Image.open(io.BytesIO(prof_raw)).convert('L').resize((256, 256))
            cap_img = Image.open(io.BytesIO(cap_raw)).convert('L').resize((256, 256))
            h1 = imagehash.phash(prof_img)
            h2 = imagehash.phash(cap_img)
            # Smaller distance implies higher similarity; threshold chosen conservatively
            return (h1 - h2) <= 8
        except Exception:
            return None

    enc_profile = _get_face_encoding_from_b64(profile_b64)
    enc_capture = _get_face_encoding_from_b64(capture_b64)
    if enc_profile is None or enc_capture is None:
        return False
    distance = face_recognition.face_distance([enc_profile], enc_capture)[0]
    return bool(distance <= threshold)


def _enhanced_image_verification(image_data: str, roll_number: int):
    """Enhanced image verification using multiple AI techniques when face recognition is unavailable.
    
    Returns a dict with 'verified' (bool), 'method' (str), and 'reason' (str) keys.
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image
        import imagehash
    except ImportError:
        return {
            'verified': False,
            'method': 'none',
            'reason': 'ai_libraries_unavailable'
        }
    
    try:
        # Decode base64 image
        raw_data = base64.b64decode(_strip_data_url_prefix(image_data))
        image = Image.open(io.BytesIO(raw_data))
        
        # Convert to OpenCV format for analysis
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Method 1: Face detection using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Face detected - this is likely a valid attendance photo
            return {
                'verified': True,
                'method': 'opencv_face_detection',
                'reason': 'face_detected'
            }
        
        # Method 2: Image quality and content analysis
        # Check if image has reasonable size and quality
        height, width = gray.shape
        if height < 100 or width < 100:
            return {
                'verified': False,
                'method': 'image_quality_check',
                'reason': 'image_too_small'
            }
        
        # Check image brightness and contrast
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        if mean_brightness < 30 or mean_brightness > 225:
            return {
                'verified': False,
                'method': 'image_quality_check',
                'reason': 'poor_lighting'
            }
        
        if std_brightness < 10:
            return {
                'verified': False,
                'method': 'image_quality_check',
                'reason': 'low_contrast'
            }
        
        # Method 3: Check if image appears to be a selfie/portrait
        # Look for skin tone detection and reasonable aspect ratio
        aspect_ratio = width / height
        if 0.5 <= aspect_ratio <= 2.0:  # Reasonable portrait/selfie ratio
            # Convert to HSV for skin tone detection
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Define skin tone range
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_pixels = cv2.countNonZero(skin_mask)
            total_pixels = height * width
            skin_percentage = (skin_pixels / total_pixels) * 100
            
            if skin_percentage > 5:  # At least 5% of image contains skin tones
                return {
                    'verified': True,
                    'method': 'skin_tone_analysis',
                    'reason': 'likely_human_photo'
                }
        
        # Method 4: Perceptual hash comparison with previous attendance images
        # This is a fallback that checks if the image is similar to previous attendance photos
        try:
            # Get previous attendance images for this student (from in-memory storage)
            previous_images = []
            for date in attendance_images:
                if roll_number in attendance_images[date]:
                    previous_images.append(attendance_images[date][roll_number])
                    if len(previous_images) >= 5:  # Limit to 5 previous images
                        break
            
            if previous_images:
                current_hash = imagehash.phash(image)
                
                for prev_image_data in previous_images:
                    if prev_image_data:
                        prev_raw = base64.b64decode(_strip_data_url_prefix(prev_image_data))
                        prev_image = Image.open(io.BytesIO(prev_raw))
                        prev_hash = imagehash.phash(prev_image)
                        
                        # Check similarity
                        hash_distance = current_hash - prev_hash
                        if hash_distance <= 15:  # Similar image threshold
                            return {
                                'verified': True,
                                'method': 'perceptual_hash_comparison',
                                'reason': 'similar_to_previous_attendance'
                            }
        except Exception:
            pass  # Skip this method if it fails
        
        # If all methods fail, require manual verification
        return {
            'verified': False,
            'method': 'enhanced_verification',
            'reason': 'no_verification_criteria_met'
        }
        
    except Exception as e:
        return {
            'verified': False,
            'method': 'enhanced_verification',
            'reason': f'verification_error: {str(e)}'
        }


def _ai_verify_attendance(image_data: str, roll_number: int):
    """AI-powered attendance verification using multiple techniques.
    
    Returns a dict with 'verified' (bool), 'method' (str), and 'reason' (str) keys.
    """
    # First, try to find student profile picture for face recognition
    student = None
    for s in students:
        if s['roll'] == roll_number:
            student = s
            break
    
    if student and student.get('profile_picture'):
        # Try face recognition first
        match = _faces_match(student['profile_picture'], image_data)
        if match is True:
            return {
                'verified': True,
                'method': 'ai_face_recognition',
                'reason': 'face_match_success'
            }
        elif match is False:
            return {
                'verified': False,
                'method': 'ai_face_recognition',
                'reason': 'face_mismatch'
            }
        # match is None -> AI unavailable: fall through to enhanced verification
    
    # If no profile picture or face recognition failed, try enhanced verification
    if not student or not student.get('profile_picture'):
        return _enhanced_image_verification(image_data, roll_number)
    
    # Fallback to enhanced verification when face recognition is unavailable
    return _enhanced_image_verification(image_data, roll_number)

def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        return f(*args, **kwargs)
    return decorated

# --- Auth endpoints ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in USERS and USERS[username]['password'] == password:
        session['user'] = username
        session['role'] = USERS[username]['role']
        return jsonify({'username': username, 'role': USERS[username]['role']})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
@require_login
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/api/whoami')
@require_login
def whoami():
    return jsonify({'username': session['user'], 'role': session['role']})

@app.route('/api/student/login', methods=['POST'])
def student_login():
    """Student login using first name and password"""
    data = request.get_json()
    first_name = data.get('first_name')
    password = data.get('password')
    
    # Find student by first name (case-insensitive)
    student = None
    for s in students:
        if s['name'].split()[0].lower() == first_name.lower():
            student = s
            break
    
    if student and student.get('password') == password:
        session['user'] = f"student_{student['roll']}"
        session['role'] = 'student'
        session['student_roll'] = student['roll']
        return jsonify({
            'username': f"student_{student['roll']}",
            'role': 'student',
            'student_data': {
                'name': student['name'],
                'roll': student['roll'],
                'class': student['class'],
                'age': student['age']
            }
        })
    else:
        return jsonify({'error': 'Invalid first name or password'}), 401

@app.route('/api/student/attendance', methods=['POST'])
@require_login
def mark_attendance():
    """Upload student attendance image for today with AI-powered automatic verification"""
    if session['role'] != 'student':
        return jsonify({'error': 'Permission denied. Only students can upload attendance.'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check if already uploaded attendance image today
    if today in attendance_images and roll_number in attendance_images[today]:
        return jsonify({'error': 'Attendance image already uploaded for today'}), 400
    
    # Get image data from request
    data = request.get_json()
    image_data = data.get('image_data')  # Base64 encoded image
    
    if not image_data:
        return jsonify({'error': 'Image data is required'}), 400
    
    # AI-powered automatic attendance verification
    verification_result = _ai_verify_attendance(image_data, roll_number)
    
    if verification_result['verified']:
        # AI successfully verified the student - mark as present automatically
        if today not in student_attendance:
            student_attendance[today] = []
        if roll_number not in student_attendance[today]:
            student_attendance[today].append(roll_number)
        
        # Store the image
        if today not in attendance_images:
            attendance_images[today] = {}
        attendance_images[today][roll_number] = image_data
        
        # Log the action
        log_entry = {
            'action': 'verify_attendance_auto',
            'student_roll': roll_number,
            'date': today,
            'who': session['user'],
            'method': verification_result['method'],
            'when': nowstr()
        }
        data_log.insert(0, log_entry)
        
        return jsonify({
            'success': True, 
            'auto_present': True, 
            'message': f'✅ Attendance marked present automatically by {verification_result["method"]}!'
        })
    else:
        # AI verification failed - store image and require manual verification
        if today not in attendance_images:
            attendance_images[today] = {}
        attendance_images[today][roll_number] = image_data
        
        # Log the action
        log_entry = {
            'action': 'upload_attendance_image',
            'student_roll': roll_number,
            'date': today,
            'who': session['user'],
            'note': verification_result.get('reason', 'manual_verification_required'),
            'when': nowstr()
        }
        data_log.insert(0, log_entry)
        
        msg = '📸 Attendance image uploaded. Waiting for teacher verification.'
        if verification_result.get('reason') == 'no_profile_picture':
            msg = '📸 Attendance image saved. Please set a profile picture to enable AI verification.'
        elif verification_result.get('reason') == 'ai_unavailable':
            msg = '📸 Attendance image uploaded. AI verification unavailable, waiting for teacher verification.'
        
        return jsonify({'success': True, 'message': msg})

@app.route('/api/student/attendance', methods=['GET'])
@require_login
def get_student_attendance():
    """Get attendance history for the logged-in student"""
    if session['role'] != 'student':
        return jsonify({'error': 'Permission denied. Only students can view their attendance.'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    # Get attendance for the last 30 days
    attendance_history = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        attended = False
        uploaded = False
        
        if date in student_attendance:
            attended = roll_number in student_attendance[date]
        
        if date in attendance_images:
            uploaded = roll_number in attendance_images[date]
        
        if attended or uploaded:
            attendance_history.append({
                'date': date,
                'attended': attended,
                'uploaded': uploaded
            })
    
    return jsonify(attendance_history)

@app.route('/api/student/grades', methods=['GET'])
@require_login
def get_student_grades():
    """Get grades for the logged-in student"""
    if session['role'] != 'student':
        return jsonify({'error': 'Permission denied. Only students can view their grades.'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    # Find the student
    student = None
    for s in students:
        if s['roll'] == roll_number:
            student = s
            break
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Calculate grades for each subject
    grades = {
        'math': calculate_grade(student['marks']['math']),
        'science': calculate_grade(student['marks']['science']),
        'history': calculate_grade(student['marks']['history']),
        'english': calculate_grade(student['marks']['english'])
    }
    
    # Calculate average marks and overall grade
    avg_marks = sum(student['marks'].values()) / len(student['marks'])
    overall_grade = calculate_grade(avg_marks)
    
    return jsonify({
        'student': {
            'name': student['name'],
            'roll': student['roll'],
            'class': student['class']
        },
        'marks': student['marks'],
        'grades': grades,
        'average_marks': round(avg_marks, 2),
        'overall_grade': overall_grade
    })

@app.route('/api/classes', methods=['GET'])
@require_login
def get_classes():
    return jsonify(AVAILABLE_CLASSES)

@app.route('/api/teacher/students', methods=['GET'])
@require_login
def get_teacher_students():
    """Get students for the logged-in teacher's class"""
    if session['role'] != 'teacher':
        return jsonify({'error': 'Permission denied. Only teachers can access this endpoint.'}), 403
    
    teacher_class = get_teacher_class(session['user'])
    if not teacher_class:
        return jsonify({'error': 'Teacher class not found'}), 404
    
    # Filter students by teacher's class
    class_students = [student for student in students if student['class'] == teacher_class]
    
    # Add grades to each student
    for student in class_students:
        # Handle None marks
        student['grades'] = {
            'math': calculate_grade(student['marks']['math']) if student['marks']['math'] is not None else 'N/A',
            'science': calculate_grade(student['marks']['science']) if student['marks']['science'] is not None else 'N/A',
            'history': calculate_grade(student['marks']['history']) if student['marks']['history'] is not None else 'N/A',
            'english': calculate_grade(student['marks']['english']) if student['marks']['english'] is not None else 'N/A'
        }
        
        # Calculate average marks and overall grade (only for subjects with marks)
        valid_marks = [mark for mark in student['marks'].values() if mark is not None]
        if valid_marks:
            avg_marks = sum(valid_marks) / len(valid_marks)
            student['average_marks'] = round(avg_marks, 2)
            student['overall_grade'] = calculate_grade(avg_marks)
        else:
            student['average_marks'] = None
            student['overall_grade'] = 'N/A'
    
    # Add attendance data for each student
    today = datetime.now().strftime('%Y-%m-%d')
    for student in class_students:
        # Check if student has attendance for today
        if today in student_attendance:
            student['attendance_today'] = student['roll'] in student_attendance[today]
        else:
            student['attendance_today'] = False
        
        # Calculate attendance percentage for last 30 days
        attendance_count = 0
        total_days = 0
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            if date in student_attendance:
                total_days += 1
                if student['roll'] in student_attendance[date]:
                    attendance_count += 1
        
        if total_days > 0:
            student['attendance_percentage'] = round((attendance_count / total_days) * 100, 1)
        else:
            student['attendance_percentage'] = 0
    
    # Add attendance data for each student
    today = datetime.now().strftime('%Y-%m-%d')
    for student in class_students:
        # Check if student has attendance for today
        if today in student_attendance:
            student['attendance_today'] = student['roll'] in student_attendance[today]
        else:
            student['attendance_today'] = False
        
        # Check if student has attendance image for today
        if today in attendance_images and student['roll'] in attendance_images[today]:
            student['has_attendance_image'] = True
            student['attendance_verified'] = student['attendance_today']  # Only verified if marked present
        else:
            student['has_attendance_image'] = False
            student['attendance_verified'] = False
        
        # Calculate attendance percentage for last 30 days
        attendance_count = 0
        total_days = 0
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            if date in student_attendance:
                total_days += 1
                if student['roll'] in student_attendance[date]:
                    attendance_count += 1
        
        if total_days > 0:
            student['attendance_percentage'] = round((attendance_count / total_days) * 100, 1)
        else:
            student['attendance_percentage'] = 0
    
    return jsonify(class_students)

@app.route('/api/attendance/verify/<int:roll_number>', methods=['POST'])
@require_login
def verify_attendance(roll_number):
    """Teacher verifies student attendance"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can verify attendance.'}), 403
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Mark student as present
    if today not in student_attendance:
        student_attendance[today] = []
    
    if roll_number not in student_attendance[today]:
        student_attendance[today].append(roll_number)
    
    # Log the action
    log_entry = {
        'action': 'verify_attendance',
        'student_roll': roll_number,
        'date': today,
        'who': session['user'],
        'when': nowstr()
    }
    data_log.insert(0, log_entry)
    
    return jsonify({'success': True, 'message': 'Attendance verified successfully'})

@app.route('/api/attendance/request-new/<int:roll_number>', methods=['POST'])
@require_login
def request_new_attendance_image(roll_number):
    """Teacher requests new attendance image from student"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can request new images.'}), 403
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Remove existing image and attendance
    if today in attendance_images and roll_number in attendance_images[today]:
        del attendance_images[today][roll_number]
    
    if today in student_attendance and roll_number in student_attendance[today]:
        student_attendance[today].remove(roll_number)
    
    # Log the action
    log_entry = {
        'action': 'request_new_image',
        'student_roll': roll_number,
        'date': today,
        'who': session['user'],
        'when': nowstr()
    }
    data_log.insert(0, log_entry)
    
    return jsonify({'success': True, 'message': 'New image requested successfully'})

@app.route('/api/attendance/image/<date>/<int:roll_number>', methods=['GET'])
@require_login
def get_attendance_image(date, roll_number):
    """Get attendance image for a specific student and date"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can view attendance images.'}), 403
    
    # Check if image exists
    if date in attendance_images and roll_number in attendance_images[date]:
        return jsonify({
            'image_data': attendance_images[date][roll_number],
            'date': date,
            'roll_number': roll_number
        })
    else:
        return jsonify({'error': 'Attendance image not found'}), 404

@app.route('/api/teacher/students/<int:idx>', methods=['PUT'])
@require_login
def update_student_marks(idx):
    """Allow teachers to update marks for students in their class"""
    if session['role'] != 'teacher':
        return jsonify({'error': 'Permission denied. Only teachers can update marks.'}), 403
    
    teacher_class = get_teacher_class(session['user'])
    if not teacher_class:
        return jsonify({'error': 'Teacher class not found'}), 404
    
    if idx < 0 or idx >= len(students):
        return jsonify({'error': 'Student not found'}), 404
    
    student = students[idx]
    
    # Check if student is in teacher's class
    if student['class'] != teacher_class:
        return jsonify({'error': 'Permission denied. You can only update students in your class.'}), 403
    
    data = request.json
    new_marks = data.get('marks', {})
    
    # Validate marks (0-100)
    for subject, mark in new_marks.items():
        if not isinstance(mark, (int, float)) or mark < 0 or mark > 100:
            return jsonify({'error': f'Invalid marks for {subject}. Must be between 0-100.'}), 400
    
    # Store original marks for logging
    original_marks = student['marks'].copy()
    
    # Update marks
    student['marks'].update(new_marks)
    
    # Log the action
    log_entry = {
        'action': 'update_marks',
        'student': student.copy(),
        'original_marks': original_marks,
        'updated_marks': new_marks,
        'who': session['user'],
        'when': nowstr()
    }
    data_log.insert(0, log_entry)
    
    return jsonify({'success': True, 'message': 'Marks updated successfully'})

# --- Teacher Management endpoints ---
@app.route('/api/teachers', methods=['GET'])
@require_login
def get_teachers():
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied. Only principal can view teachers.'}), 403
    return jsonify(teachers)

@app.route('/api/teachers', methods=['POST'])
@require_login
def add_teacher():
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied. Only principal can add teachers.'}), 403
    
    data = request.json
    username = data.get('username')
    teacher_class = data.get('class')
    password = data.get('password')
    
    if not username or not teacher_class or not password:
        return jsonify({'error': 'Username, class, and password are required'}), 400
    
    # Validate class
    if teacher_class not in AVAILABLE_CLASSES:
        return jsonify({'error': f'Class must be one of: {", ".join(AVAILABLE_CLASSES)}'}), 400
    
    # Check if teacher already exists
    if any(t['username'] == username for t in teachers):
        return jsonify({'error': 'Teacher with this username already exists'}), 400
    
    new_teacher = {
        'username': username,
        'password': password,
        'role': 'teacher',
        'class': teacher_class,
        'created_at': nowstr(),
        'last_password_change': nowstr()
    }
    
    teachers.append(new_teacher)
    USERS[username] = {'password': password, 'role': 'teacher'}
    
    # Log the action
    log_entry = {
        'action': 'add_teacher', 
        'teacher': new_teacher.copy(), 
        'who': session['user'], 
        'when': nowstr()
    }
    data_log.insert(0, log_entry)
    
    return jsonify({'success': True, 'teacher': new_teacher})

@app.route('/api/teachers/<username>/change_password', methods=['PUT'])
@require_login
def change_teacher_password(username):
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied. Only principal can change teacher passwords.'}), 403
    
    data = request.json
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify({'error': 'New password is required'}), 400
    
    # Find the teacher
    teacher = None
    for t in teachers:
        if t['username'] == username:
            teacher = t
            break
    
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    
    # Store old password for logging
    old_password = teacher['password']
    
    # Update password
    teacher['password'] = new_password
    teacher['last_password_change'] = nowstr()
    
    # Update USERS dict
    USERS[username]['password'] = new_password
    
    # Log the action
    log_entry = {
        'action': 'change_teacher_password',
        'teacher_username': username,
        'old_password': old_password,
        'new_password': new_password,
        'who': session['user'],
        'when': nowstr()
    }
    data_log.insert(0, log_entry)
    
    return jsonify({'success': True, 'message': f'Password changed for {username}'})

@app.route('/api/teachers/<username>', methods=['DELETE'])
@require_login
def delete_teacher(username):
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied. Only principal can delete teachers.'}), 403
    
    # Find and remove the teacher
    teacher = None
    for i, t in enumerate(teachers):
        if t['username'] == username:
            teacher = teachers.pop(i)
            break
    
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    
    # Remove from USERS dict
    if username in USERS:
        del USERS[username]
    
    # Log the action
    log_entry = {
        'action': 'delete_teacher',
        'teacher': teacher,
        'who': session['user'],
        'when': nowstr()
    }
    data_log.insert(0, log_entry)
    
    return jsonify({'success': True, 'message': f'Teacher {username} deleted'})

# --- Student endpoints ---
@app.route('/api/students', methods=['GET'])
@require_login
def get_students():
    return jsonify(students)

@app.route('/api/students', methods=['POST'])
@require_login
def add_student():
    username = session['user']
    role = session['role']
    data = request.json
    print(f"Adding student: {data}")
    
    # Handle optional marks - use None for empty values
    marks_data = data.get('marks', {})
    profile_picture = data.get('profile_picture')  # Get profile picture if provided
    
    student = {
        'name': data['name'],
        'age': data['age'],
        'class': data['class'],
        'roll': data['roll'],
        'password': data.get('password', 'student123'),  # Default password
        'profile_picture': profile_picture,  # Store profile picture
        'has_profile_picture': bool(profile_picture),  # Flag for profile picture
        'marks': {
            'math': marks_data.get('math') if marks_data.get('math') is not None else None,
            'science': marks_data.get('science') if marks_data.get('science') is not None else None,
            'history': marks_data.get('history') if marks_data.get('history') is not None else None,
            'english': marks_data.get('english') if marks_data.get('english') is not None else None
        },
        'addedBy': role,
        'timestamp': nowstr()
    }
    students.append(student)
    log_entry = {'action': 'add', 'student': student.copy(), 'who': role, 'when': nowstr()}
    data_log.insert(0, log_entry)
    print(f"Added student to students list. Total students: {len(students)}")
    print(f"Added log entry. Total log entries: {len(data_log)}")
    print(f"Log entry: {log_entry}")
    return jsonify({
        'success': True, 
        'has_profile_picture': bool(profile_picture)
    })

@app.route('/api/students/<int:idx>', methods=['PUT'])
@require_login
def edit_student(idx):
    username = session['user']
    role = session['role']
    print(f"Edit student called for index {idx} by {username} ({role})")
    if idx < 0 or idx >= len(students):
        return jsonify({'error': 'Not found'}), 404
    student = students[idx]
    # Only principal or teacher who added can edit
    if role != 'principal' and not (role == 'teacher' and student['addedBy'] == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Store original data before updating
    original_student = student.copy()
    
    data = request.json
    print(f"Edit data received: {data}")
    student.update({
        'name': data['name'],
        'age': data['age'],
        'class': data['class'],
        'roll': data['roll'],
        'marks': {
            'math': data.get('marks', {}).get('math', 0),
            'science': data.get('marks', {}).get('science', 0),
            'history': data.get('marks', {}).get('history', 0),
            'english': data.get('marks', {}).get('english', 0)
        }
    })
    
    # Store both original and updated data in log
    log_entry = {
        'action': 'edit', 
        'student': student.copy(), 
        'original_student': original_student,
        'who': role, 
        'when': nowstr()
    }
    data_log.insert(0, log_entry)
    print(f"Edit log entry created. Total log entries: {len(data_log)}")
    print(f"Log entry: {log_entry}")
    return jsonify({'success': True})

@app.route('/api/students/<int:idx>', methods=['DELETE'])
@require_login
def delete_student(idx):
    username = session['user']
    role = session['role']
    if idx < 0 or idx >= len(students):
        return jsonify({'error': 'Not found'}), 404
    student = students[idx]
    if role != 'principal' and not (role == 'teacher' and student['addedBy'] == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    deleted = students.pop(idx)
    deleted['deletedBy'] = role
    deleted['deletedAt'] = nowstr()
    deleted_students.append(deleted)
    data_log.insert(0, {'action': 'delete', 'student': deleted.copy(), 'who': role, 'when': nowstr()})
    return jsonify({'success': True})

# --- Deleted students endpoints ---
@app.route('/api/deleted_students', methods=['GET'])
@require_login
def get_deleted_students():
    return jsonify(deleted_students)

@app.route('/api/deleted_students/<int:idx>/recover', methods=['POST'])
@require_login
def recover_student(idx):
    username = session['user']
    role = session['role']
    if idx < 0 or idx >= len(deleted_students):
        return jsonify({'error': 'Not found'}), 404
    student = deleted_students[idx]
    # Permission: anyone can recover if deleted by teacher, only principal if deleted by principal
    if student['deletedBy'] == 'principal' and role != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    recovered = deleted_students.pop(idx)
    recovered.pop('deletedBy', None)
    recovered.pop('deletedAt', None)
    students.append(recovered)
    data_log.insert(0, {'action': 'recover', 'student': recovered.copy(), 'who': role, 'when': nowstr()})
    return jsonify({'success': True})

@app.route('/api/deleted_students/<int:idx>', methods=['DELETE'])
@require_login
def permadelete_student(idx):
    username = session['user']
    role = session['role']
    if idx < 0 or idx >= len(deleted_students):
        return jsonify({'error': 'Not found'}), 404
    student = deleted_students[idx]
    # Only principal can permadelete if deleted by principal
    if student['deletedBy'] == 'principal' and role != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    data_log.insert(0, {'action': 'permadelete', 'student': student.copy(), 'who': role, 'when': nowstr()})
    deleted_students.pop(idx)
    return jsonify({'success': True})

# --- Data log endpoint ---
@app.route('/api/log', methods=['GET'])
@require_login
def get_log():
    print(f"Log endpoint called. Total log entries: {len(data_log)}")
    print(f"Log entries: {data_log}")
    return jsonify(data_log)

# --- Clear all / recover all ---
cleared_students = None
clear_log = None

@app.route('/api/clear_all', methods=['POST'])
@require_login
def clear_all():
    global cleared_students, clear_log
    username = session['user']
    role = session['role']
    cleared_students = {
        'students': students.copy(),
        'deleted_students': deleted_students.copy()
    }
    clear_log = {'clearedBy': role, 'clearedAt': nowstr()}
    data_log.insert(0, {'action': 'clear', 'who': role, 'when': nowstr()})
    students.clear()
    deleted_students.clear()
    return jsonify({'success': True})

@app.route('/api/clear_log', methods=['GET'])
def get_clear_log():
    return jsonify(clear_log or {})

@app.route('/api/clear_log', methods=['POST'])
@require_login
def clear_data_log():
    username = session['user']
    role = session['role']
    print(f"Clear data log called by {username} ({role})")
    # Only principal can clear the data log
    if role != 'principal':
        return jsonify({'error': 'Permission denied. Only principal can clear data log.'}), 403
    
    global data_log, clear_log
    # Store the clear log information separately
    clear_log = {'clearedBy': role, 'clearedAt': nowstr()}
    print(f"Clear log set to: {clear_log}")
    
    # Clear the data log
    data_log.clear()
    print(f"Data log cleared, now has {len(data_log)} entries")
    
    return jsonify({'success': True})

@app.route('/api/recover_all', methods=['POST'])
@require_login
def recover_all():
    global cleared_students, clear_log
    username = session['user']
    role = session['role']
    if not cleared_students:
        return jsonify({'error': 'Nothing to recover'}), 400
    if clear_log and clear_log['clearedBy'] == 'principal' and role != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    students.extend(cleared_students['students'])
    deleted_students.extend(cleared_students['deleted_students'])
    data_log.insert(0, {'action': 'recoverall', 'who': role, 'when': nowstr()})
    cleared_students = None
    clear_log = None
    return jsonify({'success': True})

@app.route('/api/undo_edit/<int:log_idx>', methods=['POST'])
@require_login
def undo_edit(log_idx):
    username = session['user']
    role = session['role']
    
    if log_idx < 0 or log_idx >= len(data_log):
        return jsonify({'error': 'Log entry not found'}), 404
    
    log_entry = data_log[log_idx]
    if log_entry['action'] != 'edit':
        return jsonify({'error': 'Not an edit action'}), 400
    
    # Check permissions
    if role != 'principal' and not (role == 'teacher' and log_entry['who'] == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Find the student in the current list and revert to original data
    student_name = log_entry['student']['name']
    student_roll = log_entry['student']['roll']
    
    # Find the student by name and roll number
    student_idx = None
    for i, student in enumerate(students):
        if student['name'] == student_name and student['roll'] == student_roll:
            student_idx = i
            break
    
    if student_idx is None:
        return jsonify({'error': 'Student not found'}), 404
    
    # Revert to original data
    original_data = log_entry['original_student']
    students[student_idx].update({
        'name': original_data['name'],
        'age': original_data['age'],
        'class': original_data['class'],
        'roll': original_data['roll'],
        'marks': original_data['marks']
    })
    
    # Add undo action to log
    data_log.insert(0, {
        'action': 'undo_edit',
        'student': students[student_idx].copy(),
        'who': role,
        'when': nowstr()
    })
    
    return jsonify({'success': True})

@app.route('/api/student/attendance/calendar/<int:roll_number>', methods=['GET'])
@require_login
def get_student_attendance_calendar(roll_number):
    """Get student attendance data for calendar view"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can view attendance calendar.'}), 403
    
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    if year is None or month is None:
        return jsonify({'error': 'Year and month parameters are required'}), 400
    
    # Get all dates in the specified month
    from calendar import monthrange
    _, days_in_month = monthrange(year, month + 1)  # month + 1 because monthrange uses 1-based months
    
    present_dates = []
    uploaded_dates = []
    
    # Check each day of the month
    for day in range(1, days_in_month + 1):
        date_str = f"{year}-{month+1:02d}-{day:02d}"
        
        # Check if student was present on this date
        if date_str in student_attendance and roll_number in student_attendance[date_str]:
            present_dates.append(date_str)
        # Check if student uploaded image on this date
        elif date_str in attendance_images and roll_number in attendance_images[date_str]:
            uploaded_dates.append(date_str)
    
    return jsonify({
        'present_dates': present_dates,
        'uploaded_dates': uploaded_dates,
        'year': year,
        'month': month
    })

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 