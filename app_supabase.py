from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask import render_template
from datetime import datetime, timedelta
import os
import base64
import io
from dotenv import load_dotenv
from database import db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')  # Use environment variable
CORS(app, supports_credentials=True)

# Available classes (K-12)
AVAILABLE_CLASSES = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

# Add cache-busting headers to prevent caching issues
@app.after_request
def add_cache_headers(response):
    """Add cache-busting headers to prevent caching issues"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# --- Helper functions ---
def nowstr():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_grade(marks):
    """Calculate grade based on marks (0-100)"""
    if marks is None:
        return 'N/A'
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

# -------- Face matching helpers (optional AI) --------

def _strip_data_url_prefix(data_url: str) -> str:
    """Remove any data URL prefix from a base64 image string."""
    if not data_url:
        return data_url
    prefix_sep = 'base64,'
    if prefix_sep in data_url:
        return data_url.split(prefix_sep, 1)[1]
    return data_url


def _get_face_encoding_from_b64(b64_data: str):
    """Return one face encoding from a base64 image, or None.
    Tries to import face_recognition lazily.
    """
    try:
        import face_recognition  # type: ignore
    except Exception as e:
        print(f"Face recognition library not available: {e}")
        return None

    try:
        raw = base64.b64decode(_strip_data_url_prefix(b64_data))
        image = face_recognition.load_image_file(io.BytesIO(raw))
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            print("No faces detected in image")
            return None
        print(f"Found {len(encodings)} face(s) in image")
        return encodings[0]
    except Exception as e:
        print(f"Error getting face encoding: {e}")
        return None


def _faces_match(profile_b64: str, capture_b64: str, threshold: float = 0.7):
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
            hash_distance = h1 - h2
            print(f"Perceptual hash distance: {hash_distance}")
            return hash_distance <= 20  # Much more lenient threshold
        except Exception as e:
            print(f"Perceptual hash fallback failed: {e}")
            return None

    enc_profile = _get_face_encoding_from_b64(profile_b64)
    enc_capture = _get_face_encoding_from_b64(capture_b64)
    
    if enc_profile is None:
        print("No face detected in profile picture")
        return False
    if enc_capture is None:
        print("No face detected in captured image")
        return False
        
    distance = face_recognition.face_distance([enc_profile], enc_capture)[0]
    print(f"Face recognition distance: {distance}, threshold: {threshold}")
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
            print(f"OpenCV detected {len(faces)} face(s)")
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
        
        print(f"Image brightness: {mean_brightness:.1f}, contrast: {std_brightness:.1f}")
        
        if mean_brightness < 20 or mean_brightness > 235:  # More lenient brightness range
            return {
                'verified': False,
                'method': 'image_quality_check',
                'reason': 'poor_lighting'
            }
        
        if std_brightness < 5:  # More lenient contrast requirement
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
            # Get previous attendance images for this student
            previous_images = db.get_student_attendance_images(roll_number, limit=5)
            
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

def get_teacher_class(username):
    """Get the class assigned to a teacher"""
    user = db.get_user(username)
    return user.get('class') if user else None

def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        return f(*args, **kwargs)
    return decorated

def convert_db_student_to_app_format(db_student):
    """Convert database student format to app format"""
    return {
        'id': db_student['id'],
        'name': db_student['name'],
        'age': db_student['age'],
        'class': db_student['class'],
        'roll': db_student['roll'],
        'password': db_student['password'],
        'marks': {
            'math': db_student['math_marks'],
            'science': db_student['science_marks'],
            'history': db_student['history_marks'],
            'english': db_student['english_marks']
        },
        'profile_picture': db_student.get('profile_picture'),
        'has_profile_picture': db_student.get('has_profile_picture', False),
        'addedBy': db_student['added_by'],
        'timestamp': db_student['timestamp']
    }

def convert_app_student_to_db_format(app_student):
    """Convert app student format to database format"""
    marks = app_student.get('marks', {})
    return {
        'name': app_student['name'],
        'age': app_student['age'],
        'class': app_student['class'],
        'roll': app_student['roll'],
        'password': app_student.get('password', 'student123'),
        'math_marks': marks.get('math'),
        'science_marks': marks.get('science'),
        'history_marks': marks.get('history'),
        'english_marks': marks.get('english'),
        'added_by': app_student.get('addedBy', 'unknown')
    }

# --- Auth endpoints ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = db.get_user(username)
    if user and user['password'] == password:
        session['user'] = username
        session['role'] = user['role']
        return jsonify({'username': username, 'role': user['role']})
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
    
    print(f"Student login attempt: {first_name}")
    
    # Get all students and find by first name (case-insensitive)
    students = db.get_students()
    student = None
    for s in students:
        if s['name'].split()[0].lower() == first_name.lower():
            student = s
            break
    
    if student and student.get('password') == password:
        print(f"Student found: {student['name']} (Roll: {student['roll']})")
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
            },
            'has_profile_picture': student.get('has_profile_picture', False),
            'needs_profile_picture': not student.get('has_profile_picture', False)
        })
    else:
        print(f"Student not found for: {first_name}")
        return jsonify({'error': 'Invalid first name or password'}), 401

@app.route('/api/student/attendance', methods=['POST'])
@require_login
def mark_attendance():
    """Upload student attendance image with AI verification - 3 attempts max"""
    if session['role'] != 'student':
        return jsonify({'error': 'Permission denied. Only students can upload attendance.'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get image data from request
    data = request.get_json()
    image_data = data.get('image_data')  # Base64 encoded image
    
    if not image_data:
        return jsonify({'error': 'Image data is required'}), 400
    
    # Check if student already has attendance for today
    existing_attendance = db.get_student_attendance(roll_number, today, today)
    
    if existing_attendance and existing_attendance[0]['is_present']:
        return jsonify({
            'success': False,
            'reason': 'already_present',
            'message': '✅ You have already been marked present for today!'
        }), 400
    
    # Check attempts remaining
    attempts_info = db.get_attendance_attempts(roll_number, today)
    attempts_remaining = 3
    if attempts_info and attempts_info.get('attempts_remaining') is not None:
        attempts_remaining = attempts_info['attempts_remaining']
    
    if attempts_remaining <= 0:
        return jsonify({
            'success': False,
            'reason': 'no_attempts_left',
            'message': '❌ You have used all 3 attempts for today. Please contact your principal for manual attendance marking.'
        }), 400
    
    # Perform AI verification
    verification_result = _perform_attendance_verification(image_data, roll_number)
    
    # Record the attempt
    attempt_result = db.record_attendance_attempt(roll_number, today, image_data, verification_result)
    
    if not attempt_result:
        return jsonify({'error': 'Failed to record attendance attempt'}), 500
    
    # Get updated attempts info
    updated_attempts = db.get_attendance_attempts(roll_number, today)
    remaining_after_attempt = updated_attempts.get('attempts_remaining', 0) if updated_attempts else 0
    
    # Log the attempt
    db.add_log_entry('attendance_attempt', {
        'student_roll': roll_number,
        'date': today,
        'verification_result': verification_result,
        'attempts_remaining': remaining_after_attempt
    }, session['user'])
    
    if verification_result['verified']:
        # AI verification succeeded
        return jsonify({
            'success': True,
            'auto_present': True,
            'attempts_remaining': remaining_after_attempt,
            'message': f'✅ Attendance verified successfully by {verification_result["method"]}!'
        })
    else:
        # AI verification failed
        if remaining_after_attempt <= 0:
            message = f'❌ Verification failed: {verification_result["reason"]}. You have used all 3 attempts. Please contact your principal.'
        else:
            message = f'❌ Verification failed: {verification_result["reason"]}. {remaining_after_attempt} attempts remaining.'
        
        return jsonify({
            'success': True,
            'auto_present': False,
            'attempts_remaining': remaining_after_attempt,
            'reason': verification_result.get('reason', 'verification_failed'),
            'message': message
        }), 200


def _perform_attendance_verification(image_data, roll_number):
    """Perform comprehensive attendance verification"""
    # Check if student has a saved profile picture for AI verification
    profile_info = db.get_profile_picture(roll_number)
    profile_b64 = None
    if profile_info and profile_info.get('has_profile_picture'):
        profile_b64 = profile_info.get('profile_picture')

    # AI-powered automatic attendance verification
    if profile_b64:
        match = _faces_match(profile_b64, image_data)
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

    # Enhanced verification when AI is unavailable or no profile picture
    return _enhanced_image_verification(image_data, roll_number)

@app.route('/api/student/attendance', methods=['GET'])
@require_login
def get_student_attendance():
    """Get attendance history for the logged-in student"""
    if session['role'] != 'student':
        return jsonify({'error': 'Permission denied. Only students can view their attendance.'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    print(f"Getting attendance for student roll: {roll_number}")
    
    # Get attendance for the last 30 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    attendance_records = db.get_student_attendance(roll_number, start_date, end_date)
    print(f"Found {len(attendance_records)} attendance records for student {roll_number}")
    
    # Convert to the expected format
    attendance_history = []
    for record in attendance_records:
        attendance_history.append({
            'date': record['date'],
            'attended': record['is_present'],
            'uploaded': record['image_data'] is not None
        })
        print(f"Record: {record['date']} - Present: {record['is_present']} - Has Image: {record['image_data'] is not None}")
    
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
    student = db.get_student_by_roll(roll_number)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Convert to app format
    app_student = convert_db_student_to_app_format(student)
    
    # Calculate grades for each subject
    grades = {
        'math': calculate_grade(app_student['marks']['math']),
        'science': calculate_grade(app_student['marks']['science']),
        'history': calculate_grade(app_student['marks']['history']),
        'english': calculate_grade(app_student['marks']['english'])
    }
    
    # Calculate average marks and overall grade
    valid_marks = [mark for mark in app_student['marks'].values() if mark is not None]
    if valid_marks:
        avg_marks = sum(valid_marks) / len(valid_marks)
        overall_grade = calculate_grade(avg_marks)
    else:
        avg_marks = None
        overall_grade = 'N/A'
    
    return jsonify({
        'student': {
            'name': app_student['name'],
            'roll': app_student['roll'],
            'class': app_student['class']
        },
        'marks': app_student['marks'],
        'grades': grades,
        'average_marks': round(avg_marks, 2) if avg_marks else None,
        'overall_grade': overall_grade
    })

@app.route('/api/student/profile-picture', methods=['GET'])
@require_login
def get_profile_picture_status():
    """Check if student has a profile picture"""
    if session['role'] != 'student':
        return jsonify({'error': 'Permission denied. Only students can check profile picture status.'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    profile_data = db.get_profile_picture(roll_number)
    
    if profile_data:
        return jsonify({
            'has_profile_picture': profile_data['has_profile_picture'],
            'profile_picture': profile_data['profile_picture'] if profile_data['has_profile_picture'] else None
        })
    else:
        return jsonify({'error': 'Student not found'}), 404

@app.route('/api/student/profile-picture', methods=['POST'])
@require_login
def upload_profile_picture():
    """Upload student's profile picture"""
    if session['role'] != 'student':
        return jsonify({'error': 'Permission denied. Only students can upload profile pictures.'}), 403
    
    roll_number = session.get('student_roll')
    if not roll_number:
        return jsonify({'error': 'Student roll number not found'}), 400
    
    data = request.json
    
    if not data or 'profile_picture' not in data:
        return jsonify({'error': 'Profile picture data is required'}), 400
    
    profile_picture = data['profile_picture']
    
    # Update profile picture
    result = db.update_profile_picture(roll_number, profile_picture)
    
    if result:
        # Log the action
        db.add_log_entry('upload_profile_picture', {
            'student_roll': roll_number
        }, f'student_{roll_number}')
        
        return jsonify({'success': True, 'message': 'Profile picture uploaded successfully'})
    else:
        return jsonify({'error': 'Failed to upload profile picture'}), 500

@app.route('/api/student/profile-picture/<int:roll_number>', methods=['GET'])
def get_student_profile_picture(roll_number):
    """Get student's profile picture by roll number (for teachers/admins)"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can view profile pictures.'}), 403
    
    profile_data = db.get_profile_picture(roll_number)
    
    if profile_data and profile_data['has_profile_picture']:
        return jsonify({
            'profile_picture': profile_data['profile_picture'],
            'has_profile_picture': True
        })
    else:
        return jsonify({
            'profile_picture': None,
            'has_profile_picture': False
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
    
    # Get all students and filter by teacher's class
    all_students = db.get_students()
    class_students = [s for s in all_students if s['class'] == teacher_class]
    
    # Convert to app format and add grades
    result_students = []
    for student in class_students:
        app_student = convert_db_student_to_app_format(student)
        
        # Add grades
        app_student['grades'] = {
            'math': calculate_grade(app_student['marks']['math']),
            'science': calculate_grade(app_student['marks']['science']),
            'history': calculate_grade(app_student['marks']['history']),
            'english': calculate_grade(app_student['marks']['english'])
        }
        
        # Calculate average marks and overall grade
        valid_marks = [mark for mark in app_student['marks'].values() if mark is not None]
        if valid_marks:
            avg_marks = sum(valid_marks) / len(valid_marks)
            app_student['average_marks'] = round(avg_marks, 2)
            app_student['overall_grade'] = calculate_grade(avg_marks)
        else:
            app_student['average_marks'] = None
            app_student['overall_grade'] = 'N/A'
        
        # Add attendance data
        today = datetime.now().strftime('%Y-%m-%d')
        today_attendance = db.get_student_attendance(student['roll'], today, today)
        
        if today_attendance:
            app_student['attendance_today'] = today_attendance[0]['is_present']
            app_student['has_attendance_image'] = today_attendance[0]['image_data'] is not None
            app_student['attendance_verified'] = today_attendance[0]['verified_by'] is not None
            app_student['attendance_date'] = today_attendance[0]['date']
        else:
            # Check for any unverified attendance images in the last 7 days
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            recent_attendance = db.get_student_attendance(student['roll'], start_date, end_date)
            
            unverified_with_image = [a for a in recent_attendance if a['image_data'] and not a['verified_by']]
            
            if unverified_with_image:
                # Use the most recent unverified attendance
                latest_unverified = unverified_with_image[0]
                app_student['attendance_today'] = False
                app_student['has_attendance_image'] = True
                app_student['attendance_verified'] = False
                app_student['attendance_date'] = latest_unverified['date']
            else:
                app_student['attendance_today'] = False
                app_student['has_attendance_image'] = False
                app_student['attendance_verified'] = False
                app_student['attendance_date'] = None
        
        # Add simplified attendance status for compatibility
        app_student['attendance_attempts'] = 3  # Default for old schema
        app_student['attendance_status'] = 'present' if app_student['attendance_today'] else 'pending'
        
        # Calculate attendance percentage for last 30 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        attendance_records = db.get_student_attendance(student['roll'], start_date, end_date)
        
        present_count = sum(1 for record in attendance_records if record['is_present'])
        total_days = len(attendance_records)
        
        if total_days > 0:
            app_student['attendance_percentage'] = round((present_count / total_days) * 100, 1)
        else:
            app_student['attendance_percentage'] = 0
        
        result_students.append(app_student)
    
    return jsonify(result_students)

@app.route('/api/attendance/verify/<int:roll_number>', methods=['POST'])
@require_login
def verify_attendance(roll_number):
    """Teacher verifies student attendance"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can verify attendance.'}), 403
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Mark student as present
    result = db.mark_attendance(roll_number, today, is_present=True, verified_by=session['user'])
    
    if result:
        # Log the action
        db.add_log_entry('verify_attendance', {
            'student_roll': roll_number,
            'date': today
        }, session['user'])
        
        return jsonify({'success': True, 'message': 'Attendance verified successfully'})
    else:
        return jsonify({'error': 'Failed to verify attendance'}), 500


@app.route('/api/attendance/override/<int:roll_number>', methods=['POST'])
@require_login
def override_attendance(roll_number):
    """Principal overrides attendance status (only for principals)"""
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied. Only principals can override attendance status.'}), 403
    
    data = request.get_json()
    new_status = data.get('status')  # 'present' or 'absent'
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    if new_status not in ['present', 'absent']:
        return jsonify({'error': 'Invalid status. Must be "present" or "absent".'}), 400
    
    # Override attendance status
    result = db.override_attendance_status(roll_number, date, new_status, session['user'])
    
    if result:
        # Log the action
        db.add_log_entry('override_attendance', {
            'student_roll': roll_number,
            'date': date,
            'new_status': new_status,
            'previous_status': result.get('final_status', 'unknown')
        }, session['user'])
        
        return jsonify({
            'success': True, 
            'message': f'Attendance status overridden to {new_status}'
        })
    else:
        return jsonify({'error': 'Failed to override attendance status'}), 500


@app.route('/api/attendance/attempts/<int:roll_number>', methods=['GET'])
@require_login
def get_attendance_attempts(roll_number):
    """Get attendance attempts for a student (for teachers and principals)"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can view attendance attempts.'}), 403
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Get attendance attempts
    attempts = db.get_attendance_attempts(roll_number, date)
    
    if attempts:
        return jsonify(attempts)
    else:
        return jsonify({
            'student_roll': roll_number,
            'date': date,
            'attempts_remaining': 3,
            'final_status': 'pending',
            'attempt_history': []
        })

@app.route('/api/attendance/request-new/<int:roll_number>', methods=['POST'])
@require_login
def request_new_attendance_image(roll_number):
    """Teacher requests new attendance image from student"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can request new images.'}), 403
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Remove existing attendance record
    result = db.mark_attendance(roll_number, today, is_present=False, image_data=None, verified_by=None)
    
    if result:
        # Log the action
        db.add_log_entry('request_new_image', {
            'student_roll': roll_number,
            'date': today
        }, session['user'])
        
        return jsonify({'success': True, 'message': 'New image requested successfully'})
    else:
        return jsonify({'error': 'Failed to request new image'}), 500

@app.route('/api/attendance/image/<date>/<int:roll_number>', methods=['GET'])
@require_login
def get_attendance_image(date, roll_number):
    """Get attendance image for a specific student and date"""
    if session['role'] not in ['teacher', 'principal']:
        return jsonify({'error': 'Permission denied. Only teachers and principals can view attendance images.'}), 403
    
    # Get attendance image
    image_data = db.get_attendance_image(roll_number, date)
    
    if image_data:
        return jsonify({
            'image_data': image_data,
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
    
    # Get all students and find by index
    all_students = db.get_students()
    if idx < 0 or idx >= len(all_students):
        return jsonify({'error': 'Student not found'}), 404
    
    student = all_students[idx]
    
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
    original_marks = {
        'math': student['math_marks'],
        'science': student['science_marks'],
        'history': student['history_marks'],
        'english': student['english_marks']
    }
    
    # Update marks - need to include all student data
    update_data = {
        'name': student['name'],
        'age': student['age'],
        'class': student['class'],
        'roll': student['roll'],
        'math_marks': new_marks.get('math', student['math_marks']),
        'science_marks': new_marks.get('science', student['science_marks']),
        'history_marks': new_marks.get('history', student['history_marks']),
        'english_marks': new_marks.get('english', student['english_marks'])
    }
    
    result = db.update_student(student['id'], update_data)
    
    if result:
        # Log the action
        db.add_log_entry('update_marks', {
            'student': convert_db_student_to_app_format(result),
            'original_marks': original_marks,
            'updated_marks': new_marks
        }, session['user'])
        
        return jsonify({'success': True, 'message': 'Marks updated successfully'})
    else:
        return jsonify({'error': 'Failed to update marks'}), 500

# --- Teacher Management endpoints ---
@app.route('/api/teachers', methods=['GET'])
@require_login
def get_teachers():
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied. Only principal can view teachers.'}), 403
    
    users = db.get_all_users()
    teachers = [user for user in users if user['role'] == 'teacher']
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
    existing_user = db.get_user(username)
    if existing_user:
        return jsonify({'error': 'Teacher with this username already exists'}), 400
    
    # Create new teacher
    result = db.create_user(username, password, 'teacher', teacher_class)
    
    if result:
        # Log the action
        db.add_log_entry('add_teacher', {
            'teacher': result
        }, session['user'])
        
        return jsonify({'success': True, 'teacher': result})
    else:
        return jsonify({'error': 'Failed to create teacher'}), 500

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
    teacher = db.get_user(username)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    
    # Store old password for logging
    old_password = teacher['password']
    
    # Update password
    result = db.update_user_password(username, new_password)
    
    if result:
        # Log the action
        db.add_log_entry('change_teacher_password', {
            'teacher_username': username,
            'old_password': old_password,
            'new_password': new_password
        }, session['user'])
        
        return jsonify({'success': True, 'message': f'Password changed for {username}'})
    else:
        return jsonify({'error': 'Failed to change password'}), 500

@app.route('/api/teachers/<username>', methods=['DELETE'])
@require_login
def delete_teacher(username):
    if session['role'] != 'principal':
        return jsonify({'error': 'Permission denied. Only principal can delete teachers.'}), 403
    
    # Find the teacher
    teacher = db.get_user(username)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    
    # Delete the teacher
    result = db.delete_user(username)
    
    if result:
        # Log the action
        db.add_log_entry('delete_teacher', {
            'teacher': teacher
        }, session['user'])
        
        return jsonify({'success': True, 'message': f'Teacher {username} deleted'})
    else:
        return jsonify({'error': 'Failed to delete teacher'}), 500

# --- Student endpoints ---
@app.route('/api/students', methods=['GET'])
@require_login
def get_students():
    students = db.get_students()
    # Convert to app format
    app_students = [convert_db_student_to_app_format(s) for s in students]
    return jsonify(app_students)

@app.route('/api/students', methods=['POST'])
@require_login
def add_student():
    username = session['user']
    role = session['role']
    data = request.json
    print(f"Adding student: {data}")
    
    # Extract profile picture if provided
    profile_picture = data.get('profile_picture')
    
    # Convert to database format
    db_student = convert_app_student_to_db_format(data)
    db_student['added_by'] = role
    
    # Create student first
    result = db.create_student(db_student)
    
    if result:
        # If profile picture was provided, update it
        if profile_picture:
            roll_number = db_student['roll']
            db.update_profile_picture(roll_number, profile_picture)
            print(f"Profile picture uploaded for student roll {roll_number}")
        
        # Convert back to app format for logging
        app_student = convert_db_student_to_app_format(result)
        
        # Log the action
        db.add_log_entry('add', {
            'student': app_student,
            'has_profile_picture': bool(profile_picture)
        }, role)
        
        print(f"Added student to database. Student ID: {result['id']}")
        return jsonify({'success': True, 'has_profile_picture': bool(profile_picture)})
    else:
        return jsonify({'error': 'Failed to add student'}), 500

@app.route('/api/students/<int:idx>', methods=['PUT'])
@require_login
def edit_student(idx):
    username = session['user']
    role = session['role']
    print(f"Edit student called for index {idx} by {username} ({role})")
    
    # Get all students and find by index
    all_students = db.get_students()
    if idx < 0 or idx >= len(all_students):
        return jsonify({'error': 'Not found'}), 404
    
    student = all_students[idx]
    
    # Only principal or teacher who added can edit
    if role != 'principal' and not (role == 'teacher' and student['added_by'] == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Store original data before updating
    original_student = convert_db_student_to_app_format(student)
    
    data = request.json
    print(f"Edit data received: {data}")
    
    # Convert to database format
    update_data = convert_app_student_to_db_format(data)
    
    result = db.update_student(student['id'], update_data)
    
    if result:
        # Convert back to app format for logging
        updated_student = convert_db_student_to_app_format(result)
        
        # Log the action
        db.add_log_entry('edit', {
            'student': updated_student,
            'original_student': original_student
        }, role)
        
        print(f"Edit successful. Student ID: {result['id']}")
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update student'}), 500

@app.route('/api/students/<int:idx>', methods=['DELETE'])
@require_login
def delete_student(idx):
    username = session['user']
    role = session['role']
    
    # Get all students and find by index
    all_students = db.get_students()
    if idx < 0 or idx >= len(all_students):
        return jsonify({'error': 'Not found'}), 404
    
    student = all_students[idx]
    
    if role != 'principal' and not (role == 'teacher' and student['added_by'] == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Soft delete the student
    result = db.delete_student(student['id'], role)
    
    if result:
        # Convert to app format for logging
        deleted_student = convert_db_student_to_app_format(result)
        deleted_student['deletedBy'] = role
        deleted_student['deletedAt'] = nowstr()
        
        # Log the action
        db.add_log_entry('delete', {
            'student': deleted_student
        }, role)
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to delete student'}), 500

# --- Deleted students endpoints ---
@app.route('/api/deleted_students', methods=['GET'])
@require_login
def get_deleted_students():
    deleted_students = db.get_deleted_students()
    # Convert to app format
    app_students = []
    for s in deleted_students:
        app_student = convert_db_student_to_app_format(s)
        app_student['deletedBy'] = s['deleted_by']
        app_student['deletedAt'] = s['deleted_at']
        app_students.append(app_student)
    return jsonify(app_students)

@app.route('/api/deleted_students/<int:idx>/recover', methods=['POST'])
@require_login
def recover_student(idx):
    username = session['user']
    role = session['role']
    
    # Get all deleted students and find by index
    deleted_students = db.get_deleted_students()
    if idx < 0 or idx >= len(deleted_students):
        return jsonify({'error': 'Not found'}), 404
    
    student = deleted_students[idx]
    
    # Permission: anyone can recover if deleted by teacher, only principal if deleted by principal
    if student['deleted_by'] == 'principal' and role != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    
    # Recover the student
    result = db.recover_student(student['id'])
    
    if result:
        # Convert to app format for logging
        recovered_student = convert_db_student_to_app_format(result)
        
        # Log the action
        db.add_log_entry('recover', {
            'student': recovered_student
        }, role)
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to recover student'}), 500

@app.route('/api/deleted_students/<int:idx>', methods=['DELETE'])
@require_login
def permadelete_student(idx):
    username = session['user']
    role = session['role']
    
    # Get all deleted students and find by index
    deleted_students = db.get_deleted_students()
    if idx < 0 or idx >= len(deleted_students):
        return jsonify({'error': 'Not found'}), 404
    
    student = deleted_students[idx]
    
    # Only principal can permadelete if deleted by principal
    if student['deleted_by'] == 'principal' and role != 'principal':
        return jsonify({'error': 'Permission denied'}), 403
    
    # Convert to app format for logging
    app_student = convert_db_student_to_app_format(student)
    
    # Log the action before permanent deletion
    db.add_log_entry('permadelete', {
        'student': app_student
    }, role)
    
    # Permanently delete (this would require a separate method in the database manager)
    # For now, we'll just mark it as permanently deleted
    result = db.delete_student(student['id'], role)  # This is already a soft delete
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to permanently delete student'}), 500

# --- Data log endpoint ---
@app.route('/api/log', methods=['GET'])
@require_login
def get_log():
    log_entries = db.get_log_entries()
    print(f"Log endpoint called. Total log entries: {len(log_entries)}")
    
    # Convert to the expected format
    app_log_entries = []
    for entry in log_entries:
        app_entry = {
            'action': entry['action'],
            'who': entry['who'],
            'when': entry['when_timestamp']
        }
        
        # Add details based on action type
        details = entry.get('details', {})
        if entry['action'] == 'add' and 'student' in details:
            app_entry['student'] = details['student']
        elif entry['action'] == 'edit' and 'student' in details:
            app_entry['student'] = details['student']
            app_entry['original_student'] = details.get('original_student')
        elif entry['action'] == 'delete' and 'student' in details:
            app_entry['student'] = details['student']
        elif entry['action'] == 'recover' and 'student' in details:
            app_entry['student'] = details['student']
        elif entry['action'] == 'add_teacher' and 'teacher' in details:
            app_entry['teacher'] = details['teacher']
        elif entry['action'] == 'delete_teacher' and 'teacher' in details:
            app_entry['teacher'] = details['teacher']
        elif entry['action'] == 'change_teacher_password':
            app_entry['teacher_username'] = details.get('teacher_username')
        elif entry['action'] == 'update_marks' and 'student' in details:
            app_entry['student'] = details['student']
        
        app_log_entries.append(app_entry)
    
    print(f"Converted log entries: {app_log_entries}")
    return jsonify(app_log_entries)

# --- Clear all / recover all ---
@app.route('/api/clear_all', methods=['POST'])
@require_login
def clear_all():
    username = session['user']
    role = session['role']
    
    # This would require implementing clear_all functionality in the database manager
    # For now, we'll just log the action
    db.add_log_entry('clear', {}, role)
    
    return jsonify({'success': True})

@app.route('/api/clear_log', methods=['GET'])
def get_clear_log():
    clear_log = db.get_clear_log()
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
    
    result = db.clear_log(role)
    
    if result:
        print(f"Data log cleared successfully")
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to clear data log'}), 500

@app.route('/api/recover_all', methods=['POST'])
@require_login
def recover_all():
    username = session['user']
    role = session['role']
    
    # This would require implementing recover_all functionality in the database manager
    # For now, we'll just log the action
    db.add_log_entry('recoverall', {}, role)
    
    return jsonify({'success': True})

@app.route('/api/undo_edit/<int:log_idx>', methods=['POST'])
@require_login
def undo_edit(log_idx):
    username = session['user']
    role = session['role']
    
    # Get log entries
    log_entries = db.get_log_entries()
    if log_idx < 0 or log_idx >= len(log_entries):
        return jsonify({'error': 'Log entry not found'}), 404
    
    log_entry = log_entries[log_idx]
    if log_entry['action'] != 'edit':
        return jsonify({'error': 'Not an edit action'}), 400
    
    # Check permissions
    if role != 'principal' and not (role == 'teacher' and log_entry['who'] == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Get the original student data
    details = log_entry.get('details', {})
    original_student = details.get('original_student')
    
    if not original_student:
        return jsonify({'error': 'Original student data not found'}), 404
    
    # Find the student by name and roll number
    all_students = db.get_students()
    student_id = None
    for student in all_students:
        if student['name'] == original_student['name'] and student['roll'] == original_student['roll']:
            student_id = student['id']
            break
    
    if student_id is None:
        return jsonify({'error': 'Student not found'}), 404
    
    # Revert to original data
    update_data = convert_app_student_to_db_format(original_student)
    result = db.update_student(student_id, update_data)
    
    if result:
        # Add undo action to log
        db.add_log_entry('undo_edit', {
            'student': convert_db_student_to_app_format(result)
        }, role)
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to undo edit'}), 500

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
        
        # Get attendance for this date
        attendance_records = db.get_student_attendance(roll_number, date_str, date_str)
        
        if attendance_records:
            record = attendance_records[0]
            if record['is_present']:
                present_dates.append(date_str)
            elif record['image_data']:
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

@app.route('/profile-setup')
def profile_setup():
    return app.send_static_file('profile_setup.html')

if __name__ == '__main__':
    # Initialize database
    try:
        db.init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Make sure to set up your Supabase database using the SQL script")
    
    app.run(debug=True, port=5001) 