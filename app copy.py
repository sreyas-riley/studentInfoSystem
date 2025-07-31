from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask import render_template
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production
CORS(app, supports_credentials=True)

# In-memory data
students = []
deleted_students = []
data_log = []

# Hardcoded users
USERS = {
    'teacher': {'password': 'teacher123', 'role': 'teacher'},
    'principal': {'password': 'principal123', 'role': 'principal'}
}

# --- Helper functions ---
def nowstr():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
    student = {
        'name': data['name'],
        'age': data['age'],
        'class': data['class'],
        'roll': data['roll'],
        'marks': {
            'math': data.get('marks', {}).get('math', 0),
            'science': data.get('marks', {}).get('science', 0),
            'history': data.get('marks', {}).get('history', 0),
            'english': data.get('marks', {}).get('english', 0)
        },
        'addedBy': role,
        'timestamp': nowstr()
    }
    students.append(student)
    data_log.insert(0, {'action': 'add', 'student': student.copy(), 'who': role, 'when': nowstr()})
    return jsonify({'success': True})

@app.route('/api/students/<int:idx>', methods=['PUT'])
@require_login
def edit_student(idx):
    username = session['user']
    role = session['role']
    if idx < 0 or idx >= len(students):
        return jsonify({'error': 'Not found'}), 404
    student = students[idx]
    # Only principal or teacher who added can edit
    if role != 'principal' and not (role == 'teacher' and student['addedBy'] == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Store original data before updating
    original_student = student.copy()
    
    data = request.json
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
    data_log.insert(0, {
        'action': 'edit', 
        'student': student.copy(), 
        'original_student': original_student,
        'who': role, 
        'when': nowstr()
    })
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

if __name__ == '__main__':
    app.run(debug=True, port=5001) 