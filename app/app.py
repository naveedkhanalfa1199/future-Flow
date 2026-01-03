#
# FuTuRe FLoW - Web Application (Flask) - ADVANCED VERSION
#
# Complete University Management System with Enhanced Security & Professional UI
#

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import json
import re
import requests
import base64
from .university_data import (
    PAKISTANI_UNIVERSITIES, ENGLISH_TESTS, FIELD_NAMES,
    COUNTRIES, COUNTRY_LOCATIONS, STUDY_GAPS, CGPA_RANGES,
    PERCENTAGE_RANGES, INTAKES, DURATIONS, FSC_CUTOFFS,
    MIN_FSC_WITH_BA, MIN_BA_MARKS, MOI_MIN_CGPA,
    MOI_MIN_PERCENTAGE, MOI_MIN_FSC, STAFF_PERCENTAGES,
    STAFF_CGPA_VALUES
)

from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from datetime import timedelta

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=55)

# Email Configuration
# app.config['MAIL_SERVER'] = 'in-v3.mailjet.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('MAILJET_API_KEY')
# app.config['MAIL_PASSWORD'] = os.environ.get('MAILJET_SECRET_KEY')
app.config['MAIL_SUPPRESS_SEND'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'naveed@studyadvisers.com'

mail = Mail(app)

import os
from pathlib import Path

# Database Configuration
current_dir = Path(__file__).parent
db_folder = current_dir / "database_backups"
db_folder.mkdir(exist_ok=True)
db_path = db_folder / "sauk119_advanced.db"

try:
    old_db_path = Path('instance/sauk119.db')
    if old_db_path.exists() and not db_path.exists():
        import shutil
        shutil.copy2(old_db_path, db_path)
    print("✔ Database upgraded to advanced version")
    database_url = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
except Exception as e:
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///./instance/sauk119_advanced.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#
# ENHANCED DATABASE MODELS
#

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Integer, default=0)
    first_login = db.Column(db.Integer, default=1)  # New field for first login detection

class University(db.Model):
    __tablename__ = 'universities'
    id = db.Column(db.Integer, primary_key=True)
    university_name = db.Column(db.String(200))
    country = db.Column(db.String(100))
    location = db.Column(db.Text)

class UniversityField(db.Model):
    __tablename__ = 'university_fields'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'))
    field_name = db.Column(db.String(100))
    course_level = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    intake = db.Column(db.String(50))
    
    # MOI Requirements
    moi_required = db.Column(db.String(10), default='no')
    moi_gap_years = db.Column(db.String(20))
    moi_min_cgpa = db.Column(db.String(20))
    moi_min_percentage = db.Column(db.String(20))
    moi_min_fsc = db.Column(db.String(20))
    moi_two_plus_two = db.Column(db.String(10), default='no')
    moi_university_type = db.Column(db.String(20))
    moi_accepted_universities = db.Column(db.Text)
    
    # General Requirements
    general_min_cgpa = db.Column(db.String(20))
    general_min_percentage = db.Column(db.String(20))
    general_max_study_gap = db.Column(db.String(20))
    
    # Bachelor Entry Requirements
    fsc_cutoff_marks = db.Column(db.String(20))
    ba_required_below_cutoff = db.Column(db.String(10), default='no')
    min_fsc_marks_with_ba = db.Column(db.String(20))
    min_ba_marks = db.Column(db.String(20))
    
    # English Tests
    english_tests = db.Column(db.Text)
    
    # Courses
    courses = db.Column(db.Text)
    
    # Financial
    total_fee = db.Column(db.String(100))
    initial_deposit = db.Column(db.String(100))
    scholarship = db.Column(db.String(200))

class DropdownList(db.Model):
    __tablename__ = 'dropdown_lists'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    value = db.Column(db.String(200))
    parent_value = db.Column(db.String(200))
    display_order = db.Column(db.Integer, default=0)

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    email = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    is_locked = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    first_login = db.Column(db.Integer, default=1)  # New field for first login

class StaffVerification(db.Model):
    __tablename__ = 'staff_verification'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    q1_answer = db.Column(db.String(200))
    q2_answer = db.Column(db.String(200))
    q3_answer = db.Column(db.String(200))
    q4_answer = db.Column(db.String(200))
    q5_answer = db.Column(db.String(200))
    q6_answer = db.Column(db.String(200))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    attempt_time = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Integer, default=0)

#
# ENHANCED HELPER FUNCTIONS
#

def check_password_strength(password):
    """Check password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, "Strong password"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'staff':
            flash('Staff access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_automatic_backup():
    """Automatic backup on server start"""
    try:
        backup_dir = Path(__file__).parent / "database_backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"sauk119_advanced_backup_{timestamp}.db"
        
        main_db_path = db_folder / "sauk119_advanced.db"
        if main_db_path.exists():
            import shutil
            shutil.copy2(main_db_path, backup_file)
            print(f"✔ Automatic backup created: {backup_file.name}")
        else:
            print("▲ Main database not found for backup")
    except Exception as e:
        print(f"▲ Backup failed: {e}")

def get_dropdown_data():
    """Enhanced dropdown data with new categories"""
    return {
        'course_names': DropdownList.query.filter_by(category='course_name').order_by(DropdownList.display_order, DropdownList.value).all(),
        'levels': DropdownList.query.filter_by(category='level').order_by(DropdownList.display_order, DropdownList.value).all(),
    }

def get_hardcoded_values():
    """ALL hardcoded values"""
    return {
        'pakistani_universities': PAKISTANI_UNIVERSITIES,
        'english_tests': ENGLISH_TESTS,
        'field_names': FIELD_NAMES,
        'countries': COUNTRIES,
        'country_locations': COUNTRY_LOCATIONS,
        'study_gaps': STUDY_GAPS,
        'cgpa_ranges': CGPA_RANGES,
        'percentage_ranges': PERCENTAGE_RANGES,
        'intakes': INTAKES,
        'durations': DURATIONS,
        'fsc_cutoffs': FSC_CUTOFFS,
        'min_fsc_with_ba': MIN_FSC_WITH_BA,
        'min_ba_marks': MIN_BA_MARKS,
        'moi_min_cgpa': MOI_MIN_CGPA,
        'moi_min_percentage': MOI_MIN_PERCENTAGE,
        'moi_min_fsc': MOI_MIN_FSC,
        'staff_percentages': STAFF_PERCENTAGES,
        'staff_cgpa_values': STAFF_CGPA_VALUES,
        'cgpas': CGPA_RANGES,
        'study_gaps_simple': [str(i) for i in range(0, 21)],
    }

def check_moi_eligibility(student_fsc, student_cgpa, student_percentage, student_university, student_study_gap, field):
    """Enhanced MOI eligibility check"""
    if field.moi_required != 'yes':
        return False, []
    
    missing_info = []

    # Check FSc marks
    if field.moi_min_fsc:
        if not student_fsc:
            missing_info.append('FSc Marks')
        else:
            try:
                required_fsc = float(field.moi_min_fsc.replace('%', ''))
                student_fsc_float = float(student_fsc.replace('%', ''))
                if student_fsc_float < required_fsc:
                    return False, []
            except:
                pass

    # Check CGPA
    if field.moi_min_cgpa:
        if not student_cgpa:
            missing_info.append('CGPA')
        else:
            try:
                if float(student_cgpa) < float(field.moi_min_cgpa):
                    return False, []
            except:
                pass

    # Check Percentage
    if field.moi_min_percentage:
        if not student_percentage and not student_cgpa:
            missing_info.append('Percentage/CGPA')
        elif student_percentage:
            try:
                required_percentage = float(field.moi_min_percentage.replace('%', ''))
                student_percentage_float = float(student_percentage.replace('%', ''))
                if student_percentage_float < required_percentage:
                    return False, []
            except:
                pass

    # Check Study Gap
    if field.moi_gap_years:
        if not student_study_gap:
            missing_info.append('Study Gap')
        else:
            try:
                max_gap = int(field.moi_gap_years.split()[0])
                student_gap_value = student_study_gap.replace(' Years', '').replace(' Year', '').strip()
                
                if student_gap_value.lower() == 'no gap':
                    student_gap_num = 0
                else:
                    student_gap_num = int(student_gap_value)
                
                if student_gap_num > max_gap:
                    return False, []
            except:
                pass

    # Check University Acceptance
    if field.moi_university_type == 'specific':
        if not student_university:
            missing_info.append('Last University')
        else:
            try:
                accepted_unis = json.loads(field.moi_accepted_universities) if field.moi_accepted_universities else []
                if student_university not in accepted_unis:
                    return False, []
            except:
                pass

    if missing_info:
        return None, missing_info
    return True, []

def check_general_cgpa(student_cgpa, field):
    """Check general CGPA requirement"""
    if not field.general_min_cgpa or not student_cgpa:
        return True
    try:
        return float(student_cgpa) >= float(field.general_min_cgpa)
    except:
        return False

def check_general_study_gap(student_gap, field):
    """Check general study gap requirement"""
    if not field.general_max_study_gap or not student_gap:
        return True
    try:
        if field.general_max_study_gap == "No Gap":
            return student_gap == "No Gap" or student_gap == "0"
        max_gap = field.general_max_study_gap.replace(" Years", "").replace(" Year", "").replace("+", "")
        student_gap_num = student_gap.replace(" Years", "").replace(" Year", "")
        if "+" in field.general_max_study_gap:
            return True
        return int(student_gap_num) <= int(max_gap)
    except:
        return True

def check_bachelor_eligibility(student_fsc, student_ba, field):
    """Check bachelor entry requirements"""
    if not field.fsc_cutoff_marks and not field.min_fsc_marks_with_ba:
        return True, "No specific requirements"

    student_fsc_float = float(student_fsc) if student_fsc else 0
    student_ba_float = float(student_ba) if student_ba else 0

    # Check direct admission via FSc cut-off
    if field.fsc_cutoff_marks:
        cutoff_float = float(field.fsc_cutoff_marks.replace('%', ''))
        if student_fsc_float >= cutoff_float:
            return True, f"Direct admission eligible (FSc ≥ {field.fsc_cutoff_marks})"

    # Check admission with BA
    if (field.ba_required_below_cutoff == 'yes' and
        field.min_fsc_marks_with_ba and
        field.min_ba_marks):
        min_fsc_float = float(field.min_fsc_marks_with_ba.replace('%', ''))
        min_ba_float = float(field.min_ba_marks.replace('%', ''))
        if (student_fsc_float >= min_fsc_float and
            student_ba_float >= min_ba_float):
            return True, f"Eligible with BA (FSc ≥ {field.min_fsc_marks_with_ba}, BA ≥ {field.min_ba_marks})"

    return False, "Entry requirements not met"


def send_email_mailjet_api(to_email, subject, html_content):
    """Send email using Mailjet HTTP API (works on Render)"""
    try:
        api_key = os.environ.get('MAILJET_API_KEY')
        secret_key = os.environ.get('MAILJET_SECRET_KEY')
        
        if not api_key or not secret_key:
            print("ERROR: Mailjet keys not found in environment")
            return False
            
        url = "https://api.mailjet.com/v3.1/send"
        auth = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
        
        data = {
            "Messages": [{
                "From": {"Email": "naveed@studyadvisers.com", "Name": "SAUK Islamabad"},
                "To": [{"Email": to_email}],
                "Subject": subject,
                "HTMLPart": html_content
            }]
        }
        
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ Email sent successfully to {to_email}")
            return True
        else:
            print(f"✗ Mailjet API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Exception in send_email_mailjet_api: {str(e)}")
        return False


#
# ENHANCED ROUTES - AUTHENTICATION
#

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('staff_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # ADMIN LOGIN (Database se check)
        admin_user = User.query.filter_by(username=username, role='admin').first()
        if admin_user and check_password_hash(admin_user.password, password):
            if admin_user.is_locked:
                flash('Account is locked. Contact Administrator.', 'error')
                return redirect(url_for('login'))
            
            session['user_id'] = admin_user.id
            session['username'] = admin_user.username
            session['role'] = 'admin'
            
            # Check first login
            if admin_user.first_login == 1:
                admin_user.first_login = 0
                db.session.commit()
                session['first_login'] = True
            
            attempt = LoginAttempt(username=username, success=1)
            db.session.add(attempt)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))

        # STAFF LOGIN
        staff_user = Staff.query.filter_by(username=username).first()
        if staff_user and check_password_hash(staff_user.password, password):
            if staff_user.status == 'pending':
                flash('Your account is pending approval.', 'error')
                return redirect(url_for('login'))
            if staff_user.status == 'rejected':
                flash('The information provided in the form were incorrect and your account is rejected please try again with different login credentials.', 'error')
                return redirect(url_for('login'))
            if staff_user.is_locked:
                flash('Account is locked. Contact Admin.', 'error')
                return redirect(url_for('login'))
            
            # Staff login successful
            session['user_id'] = staff_user.id
            session['username'] = staff_user.username
            session['role'] = 'staff'
            session['designation'] = staff_user.designation
            
            # Check first login
            if staff_user.first_login == 1:
                staff_user.first_login = 0
                db.session.commit()
                session['first_login'] = True
            else:
                return redirect(url_for('staff_dashboard'))

        attempt = LoginAttempt(username=username, success=0)
        db.session.add(attempt)
        db.session.commit()
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        designation = request.form.get('designation')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Password strength check
        is_strong, message = check_password_strength(password)
        if not is_strong:
            flash(f'Weak password: {message}', 'error')
            return render_template('register.html')

        existing_staff = Staff.query.filter_by(username=username).first()
        existing_admin = User.query.filter_by(username=username).first()

        if existing_staff or existing_admin:
            flash('Username already exists. Please choose another', 'error')
            return render_template('register.html')

        new_staff = Staff(
            username=username,
            designation=designation,
            password=generate_password_hash(password),
            email=email,
            status="pending",
            is_locked=0,
            first_login=1
        )

        db.session.add(new_staff)
        db.session.commit()

        return redirect(url_for('staff_verification', staff_id=new_staff.id))
    
    return render_template('register.html')

@app.route('/staff/verification/<int:staff_id>', methods=['GET', 'POST'])
def staff_verification(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    if request.method == 'POST':
        verification = StaffVerification(
            staff_id=staff_id,
            q1_answer=request.form.get('q1'),
            q2_answer=request.form.get('q2'),
            q3_answer=request.form.get('q3'),
            q4_answer=request.form.get('q4'),
            q5_answer=request.form.get('q5'),
            q6_answer=request.form.get('q6')
        )
        db.session.add(verification)
        db.session.commit()
        return """
        <script>
            alert("Thank you for submitting the form! You will be able to login after admin approval.");
            window.location.href = "/login";
        </script>
        """
    return render_template('staff_verification.html', staff=staff)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

#
# ENHANCED ADMIN ROUTES
#

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html', username=session.get('username'))

@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        admin_user = User.query.get(session['user_id'])
        
        if not check_password_hash(admin_user.password, current_password):
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        # Password strength check
        is_strong, message = check_password_strength(new_password)
        if not is_strong:
            flash(f'Weak password: {message}', 'error')
            return render_template('change_password.html')
        
        admin_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('change_password.html')

@app.route('/admin/universities')
@login_required
@admin_required
def admin_universities():
    universities = University.query.all()
    for uni in universities:
        uni.fields = UniversityField.query.filter_by(university_id=uni.id).all()
        try:
            uni.location_list = json.loads(uni.location) if uni.location else []
        except:
            uni.location_list = [uni.location] if uni.location else []
    return render_template('admin_universities.html', universities=universities)

@app.route('/admin/university/add-detailed', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_university_detailed():
    if request.method == 'POST':
        # 1. Basic University Info
        uni = University(
            university_name=request.form.get('university_name'),
            country=request.form.get('country'),
            location=json.dumps(request.form.getlist('locations')),
        )
        db.session.add(uni)
        db.session.flush()  # ✅ Get uni.id without commit

        # 2. Process ALL Fields with NEW LOGIC
        saved_fields = 0
        
        # Find all field numbers
        for key in request.form.keys():
            if key.startswith('field_name_'):
                field_num = key.split('_')[-1]
                if field_num.isdigit():
                    field_num = int(field_num)
                    
                    # Create field object
                    field = UniversityField(
                        university_id=uni.id,
                        field_name=request.form.get(f'field_name_{field_num}'),
                        course_level=request.form.get(f'course_level_{field_num}'),
                        duration=request.form.get(f'duration_{field_num}'),
                        intake=request.form.get(f'intake_{field_num}'),
                        moi_required=request.form.get(f'moi_required_{field_num}', 'no'),
                        moi_gap_years=request.form.get(f'moi_gap_years_{field_num}'),
                        moi_min_cgpa=request.form.get(f'moi_min_cgpa_{field_num}'),
                        moi_min_percentage=request.form.get(f'moi_min_percentage_{field_num}'),
                        moi_min_fsc=request.form.get(f'moi_min_fsc_{field_num}'),
                        moi_two_plus_two=request.form.get(f'moi_two_plus_two_{field_num}', 'no'),
                        moi_university_type=request.form.get(f'moi_university_type_{field_num}'),
                        general_min_cgpa=request.form.get(f'general_min_cgpa_{field_num}'),
                        general_min_percentage=request.form.get(f'general_min_percentage_{field_num}'),
                        general_max_study_gap=request.form.get(f'general_max_study_gap_{field_num}'),
                        total_fee=request.form.get(f'total_fee_{field_num}'),
                        initial_deposit=request.form.get(f'initial_deposit_{field_num}'),
                        scholarship=request.form.get(f'scholarship_{field_num}')
                    )
                    
                    # Process MOI universities
                    moi_universities = request.form.getlist(f'moi_universities_{field_num}')
                    if moi_universities:
                        field.moi_accepted_universities = json.dumps(moi_universities)
                    
                    # Process Courses
                    courses = []
                    course_idx = 1
                    while f'course_{field_num}_{course_idx}' in request.form:
                        course = request.form.get(f'course_{field_num}_{course_idx}')
                        if course and course.strip():
                            courses.append(course.strip())
                        course_idx += 1
                    if courses:
                        field.courses = json.dumps(courses)
                    
                    # Process English tests
                    english_tests = []
                    selected_tests = request.form.getlist(f'english_tests_{field_num}')
                    for test_name in ['IELTS UKVI', 'PTE UKVI', 'TOEFL', 'Oxford ELLT', 
                                    'ESOL', 'Duolingo', 'IELTS Academic', 'PTE Academic']:
                        if test_name in selected_tests:
                            score = request.form.get(f'score_{test_name}_{field_num}', '')
                            english_tests.append({'test': test_name, 'score': score})
                    if english_tests:
                        field.english_tests = json.dumps(english_tests)
                    
                    db.session.add(field)
                    saved_fields += 1
        
        # FINAL COMMIT
        db.session.commit()
        
        flash(f'University added successfully with {saved_fields} field(s)!', 'success')
        return redirect(url_for('admin_universities'))
    
    dropdown_data = get_dropdown_data()
    hardcoded = get_hardcoded_values()
    return render_template('admin_add_university_detailed.html', **dropdown_data, **hardcoded)

@app.route('/admin/university/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_university(id):
    uni = University.query.get_or_404(id)
    if request.method == 'POST':
        uni.university_name = request.form.get('university_name')
        uni.country = request.form.get('country')
        uni.location = json.dumps(request.form.getlist('locations'))
        db.session.commit()
        flash('University updated successfully', 'success')
        return redirect(url_for('admin_universities'))
    
    dropdown_data = get_dropdown_data()
    hardcoded = get_hardcoded_values()
    return render_template('admin_edit_university.html', uni=uni, **dropdown_data, **hardcoded)

@app.route('/admin/university/delete/<int:id>')
@login_required
@admin_required
def admin_delete_university(id):
    uni = University.query.get_or_404(id)
    UniversityField.query.filter_by(university_id=id).delete()
    db.session.delete(uni)
    db.session.commit()
    flash('University deleted successfully', 'success')
    return redirect(url_for('admin_universities'))

@app.route('/admin/dropdowns')
@login_required
@admin_required
def admin_dropdowns():
    category = request.args.get('category', 'country')
    items = DropdownList.query.filter_by(category=category).order_by(DropdownList.display_order, DropdownList.value).all()
    
    # Ye 2 lines add ho gayi hain
    countries = DropdownList.query.filter_by(category='country').order_by(DropdownList.value).all()
    levels = DropdownList.query.filter_by(category='level').order_by(DropdownList.value).all()
    
    return render_template('admin_dropdowns.html', 
                         items=items, 
                         category=category,
                         countries=countries,
                         levels=levels)

@app.route('/admin/dropdown/add', methods=['POST'])
@login_required
@admin_required
def admin_add_dropdown():
    category = request.form.get('category')
    value = request.form.get('value')
    parent_value = request.form.get('parent_value')
    display_order = int(request.form.get('display_order', 0))
    
    # ✅ VALIDATION: Course name must have parent level
    if category == 'course_name' and not parent_value:
        flash('Error: Course name must be linked to a level (Bachelor, Master, PhD)', 'error')
        return redirect(url_for('admin_dropdowns', category=category))
    
    # ✅ VALIDATION: Value should not be empty
    if not value or not value.strip():
        flash('Error: Value cannot be empty', 'error')
        return redirect(url_for('admin_dropdowns', category=category))
    
    item = DropdownList(category=category, value=value, parent_value=parent_value, display_order=display_order)
    db.session.add(item)
    db.session.commit()
    flash('Item added successfully', 'success')
    return redirect(url_for('admin_dropdowns', category=category))

@app.route('/admin/dropdown/delete/<int:id>')
@login_required
@admin_required
def admin_delete_dropdown(id):
    item = DropdownList.query.get_or_404(id)
    category = item.category
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully', 'success')
    return redirect(url_for('admin_dropdowns', category=category))

@app.route('/admin/staff')
@login_required
@admin_required
def admin_staff():
    staff_members = Staff.query.order_by(Staff.created_at.desc()).all()
    return render_template('admin_staff.html', staff_members=staff_members)

@app.route('/admin/staff/approve/<int:id>')
@login_required
@admin_required
def admin_approve_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.status = 'approved'
    db.session.commit()
    flash('Staff approved successfully', 'success')
    return redirect(url_for('admin_staff'))

@app.route('/admin/staff/reject/<int:id>')
@login_required
@admin_required
def admin_reject_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.status = 'rejected'
    db.session.commit()
    flash('Staff rejected successfully', 'success')
    return redirect(url_for('admin_staff'))

@app.route('/admin/staff/unlock/<int:id>')
@login_required
@admin_required
def admin_unlock_staff(id):
    staff = Staff.query.get_or_404(id)
    staff.is_locked = 0
    db.session.commit()
    flash('Staff unlocked successfully', 'success')
    return redirect(url_for('admin_staff'))

@app.route('/admin/staff/delete/<int:id>')
@login_required
@admin_required
def admin_delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    flash('Staff deleted successfully', 'success')
    return redirect(url_for('admin_staff'))

@app.route('/admin/staff/verification/<int:staff_id>')
@login_required
@admin_required
def admin_view_verification(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    verification = StaffVerification.query.filter_by(staff_id=staff_id).first()
    return render_template('admin_view_verification.html', staff=staff, verification=verification)

@app.route('/admin/university/<int:id>/fields')
@login_required
@admin_required
def admin_view_fields(id):
    university = University.query.get_or_404(id)
    fields = UniversityField.query.filter_by(university_id=id).all()
    return render_template('admin_view_fields.html', university=university, fields=fields)

@app.route('/admin/field/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_field(id):
    field = UniversityField.query.get_or_404(id)
    university = db.session.get(University, field.university_id)
    
    if request.method == 'POST':
        # Basic Info
        field.field_name = request.form.get('field_name')
        field.course_level = request.form.get('course_level')
        field.duration = request.form.get('duration')
        field.intake = request.form.get('intake')
        
        # MOI Requirements
        field.moi_required = request.form.get('moi_required')
        field.moi_gap_years = request.form.get('moi_gap_years')
        field.moi_min_cgpa = request.form.get('moi_min_cgpa')
        field.moi_min_percentage = request.form.get('moi_min_percentage')
        field.moi_min_fsc = request.form.get('moi_min_fsc')
        field.moi_two_plus_two = request.form.get('moi_two_plus_two')
        field.moi_university_type = request.form.get('moi_university_type')
        
        # MOI Universities
        moi_universities = request.form.getlist('moi_universities')
        field.moi_accepted_universities = json.dumps(moi_universities) if moi_universities else '[]'
        
        # General Requirements
        field.general_min_cgpa = request.form.get('general_min_cgpa')
        field.general_min_percentage = request.form.get('general_min_percentage')
        field.general_max_study_gap = request.form.get('general_max_study_gap')
        
        # Bachelor Entry Requirements
        field.fsc_cutoff_marks = request.form.get('fsc_cutoff_marks')
        field.ba_required_below_cutoff = request.form.get('ba_required_below_cutoff')
        field.min_fsc_marks_with_ba = request.form.get('min_fsc_marks_with_ba')
        field.min_ba_marks = request.form.get('min_ba_marks')
        
        # Courses - collect multiple course_1, course_2, etc.
        courses = []
        course_count = 1
        while f'course_{course_count}' in request.form:
            course_name = request.form.get(f'course_{course_count}')
            if course_name and course_name.strip():
                courses.append(course_name.strip())
            course_count += 1
        field.courses = ','.join(courses) if courses else ''
        
        # English Tests
        english_tests = []
        selected_tests = request.form.getlist('english_test')
        
        test_mapping = {
            'IELTS UKVI': 'ielts_ukvi_score',
            'PTE UKVI': 'pte_ukvi_score',
            'Oxford ELLT': 'oxford_ellt_score',
            'ESOL': 'esol_score',
            'TOEFL': 'toefl_score',
            'Duolingo': 'duolingo_score',
            'IELTS Academic': 'ielts_academic_score',
            'PTE Academic': 'pte_academic_score'
        }
        
        for test_name in selected_tests:
            score_field = test_mapping.get(test_name, '')
            score = request.form.get(score_field, '')
            english_tests.append({'test': test_name, 'score': score})
        
        field.english_tests = json.dumps(english_tests) if english_tests else '[]'
        
        # Financial Info
        field.total_fee = request.form.get('total_fee')
        field.initial_deposit = request.form.get('initial_deposit')
        field.scholarship = request.form.get('scholarship')
        
        db.session.commit()
        flash('Field updated successfully!', 'success')
        return redirect(url_for('admin_view_fields', id=field.university_id))
    
    # GET Request - Parse existing data for template
    test_scores = {}
    selected_tests_list = []
    if field.english_tests:
        try:
            tests = json.loads(field.english_tests)
            for test in tests:
                test_name = test.get('test', '')
                if test_name:
                    selected_tests_list.append(test_name)
                    test_scores[test_name] = test.get('score', '')
        except:
            test_scores = {}
            selected_tests_list = []
    
    # Parse MOI universities
    accepted_unis = []
    if field.moi_accepted_universities:
        try:
            accepted_unis = json.loads(field.moi_accepted_universities)
        except:
            accepted_unis = []
    
    # Parse courses for template
    courses_list = []
    if field.courses:
        try:
            # Try JSON format first
            courses_list = json.loads(field.courses)
        except:
            # Fallback for comma-separated format
            courses_list = field.courses.split(',') if field.courses else []
    
    dropdown_data = get_dropdown_data()
    hardcoded = get_hardcoded_values()
    
    return render_template('admin_edit_field.html',
                         field=field,
                         university=university,
                         test_scores=test_scores,
                         selected_tests_list=selected_tests_list,
                         courses_list=courses_list,
                         accepted_unis=accepted_unis,
                         # Explicitly pass dropdown data
                         course_names=dropdown_data['course_names'],
                         levels=dropdown_data['levels'],
                         # Pass hardcoded data
                         **hardcoded)

@app.route('/admin/field/delete/<int:id>')
@login_required
@admin_required
def admin_delete_field(id):
    field = UniversityField.query.get_or_404(id)
    university_id = field.university_id
    db.session.delete(field)
    db.session.commit()
    flash('Field deleted successfully!', 'success')
    return redirect(url_for('admin_view_fields', id=university_id))

@app.route('/admin/login-activity')
@login_required
@admin_required
def admin_login_activity():
    attempts = LoginAttempt.query.order_by(LoginAttempt.attempt_time.desc()).limit(200).all()
    return render_template('admin_login_activity.html', attempts=attempts)

@app.route('/admin/create-backup')
@login_required
@admin_required
def admin_create_backup():
    create_automatic_backup()
    flash('Manual backup created successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

#
# ENHANCED STAFF ROUTES
#

@app.route('/staff/dashboard')
@login_required
@staff_required
def staff_dashboard():
    return render_template('staff_dashboard.html', username=session.get('username'), designation=session.get('designation'))

@app.route('/staff/user-manual')
@login_required
@staff_required
def staff_user_manual():
    return render_template('staff_user_manual.html', username=session.get('username'))

@app.route('/staff/search', methods=['GET', 'POST'])
@login_required
@staff_required
def staff_search():
    results = []
    
    if request.method == 'POST':
        country = request.form.get('country', '')
        location = request.form.get('location', '')
        level = request.form.get('level', '')
        search_course = request.form.get('course', '').strip().lower()
        english_test_type = request.form.get('english_test_type', '')
        english_test_score = request.form.get('english_test_score', '')
        
        # Start with all universities
        results = University.query.all()
        
        # Apply country filter
        if country:
            results = [uni for uni in results if uni.country == country]
        
        # Apply location filter (FIXED - handles JSON format)
        if location:
            filtered = []
            for uni in results:
                try:
                    # Try to parse as JSON array
                    uni_locations = json.loads(uni.location) if uni.location else []
                    if location in uni_locations:
                        filtered.append(uni)
                except:
                    # If not JSON, check as plain string
                    if uni.location == location:
                        filtered.append(uni)
            results = filtered
        
        # If course search is provided, apply advanced filtering
        if search_course:
            filtered_results = []
            for uni in results:
                fields = UniversityField.query.filter_by(university_id=uni.id).all()
                matching_fields = []
                
                for field in fields:
                    # Apply level filter
                    if level and field.course_level != level:
                        continue
                    
                    # Course matching (EXACT or PARTIAL match in courses list)
                    try:
                        courses = json.loads(field.courses) if field.courses else []
                    except:
                        courses = [c.strip() for c in field.courses.split(',')] if field.courses else []
                    
                    course_found = False
                    matched_course_name = None
                    
                    # Check exact or partial match in courses
                    for c in courses:
                        if search_course == c.strip().lower():  # Exact match
                            course_found = True
                            matched_course_name = c
                            break
                        elif search_course in c.lower():  # Partial match
                            course_found = True
                            matched_course_name = c
                            break
                    
                    # FIELD NAME CHECK REMOVED - course must be in courses list
                    # if not course_found:
                    #     course_found = search_course in field.field_name.lower()
                    
                    if course_found:
                        # Store matched course for display
                        field.matched_course = matched_course_name or courses[0] if courses else "Course"
                        matching_fields.append(field)
                    # If course not found in courses list, skip this field
                
                if matching_fields:
                    uni.fields = matching_fields
                    filtered_results.append(uni)
            
            results = filtered_results
        else:
            # If no course search, just get all fields
            for uni in results:
                uni.fields = UniversityField.query.filter_by(university_id=uni.id).all()
        
        # Filter by English Test if provided
        if english_test_type and english_test_score:
            for uni in results:
                if hasattr(uni, 'fields') and uni.fields:
                    filtered_fields = []
                    for field in uni.fields:
                        if field.english_tests:
                            try:
                                tests = json.loads(field.english_tests)
                                test_match = False
                                for test in tests:
                                    test_key = test['test'].lower().replace(' ', '_')
                                    if test_key == english_test_type:
                                        if test.get('score'):
                                            try:
                                                if float(english_test_score) >= float(test['score']):
                                                    test_match = True
                                                    break
                                            except:
                                                pass
                                if test_match:
                                    filtered_fields.append(field)
                            except:
                                pass
                    uni.fields = filtered_fields
            
            # Remove universities with no matching fields
            results = [uni for uni in results if uni.fields]
    
    dropdown_data = get_dropdown_data()
    hardcoded = get_hardcoded_values()
    return render_template('staff_search.html', results=results, **dropdown_data, **hardcoded)

@app.route('/staff/generate-advice', methods=['GET', 'POST'])
@login_required
@staff_required
def staff_generate_advice():
    moi_eligible = []
    regular_results = []  # MOI_POTENTIAL REMOVED
    applied_filters = {}
    profile_warnings = []

    if request.method == 'POST':
        # Get filters
        search_course = request.form.get('course', "").strip().lower()
        country = request.form.get('country', "")
        location = request.form.get('location', "")
        level = request.form.get('level', "")
        intake = request.form.get('intake', "")
        max_fee = request.form.get('max_fee', "")

        # Get student profile
        student_fsc = request.form.get('fsc_marks', "").strip()
        student_ba = request.form.get('ba_marks', "").strip()
        student_cgpa = request.form.get('cgpa', "").strip()
        student_percentage = request.form.get('percentage', "").strip()
        student_study_gap = request.form.get('study_gap', "").strip()
        student_university = request.form.get('last_university', "").strip()
        english_test_type = request.form.get('english_test_type', "")
        english_test_score = request.form.get('english_test_score', "")

        # 🔥 Store in session
        session['student_fsc'] = student_fsc
        session['student_cgpa'] = student_cgpa
        session['student_percentage'] = student_percentage
        session['student_university'] = student_university
        session['student_study_gap'] = student_study_gap
        session['level_filter'] = level

        if search_course:
            all_fields = UniversityField.query.all()
            for field in all_fields:
                uni = University.query.get(field.university_id)
                if not uni:
                    continue

                # Apply location filters
                if country and uni.country != country:
                    continue
                if location:
                    try:
                        uni_locations = json.loads(uni.location) if uni.location else []
                        if location not in uni_locations:
                            continue
                    except:
                        if uni.location != location:
                            continue
                if level and field.course_level != level:
                    continue
                if intake and field.intake != intake:
                    continue
                if max_fee and field.total_fee:
                    try:
                        field_fee = float(field.total_fee.replace('£', '').replace(',', '').replace('$', ''))
                        max_fee_float = float(max_fee)
                        if field_fee > max_fee_float:
                            continue
                    except:
                        pass

                # Enhanced course match
                try:
                    courses = json.loads(field.courses) if field.courses else []
                except:
                    courses = [c.strip() for c in field.courses.split(',')] if field.courses else []
                
                exact_course_match = False
                matched_course = None
                course_match = False               

                for course in courses:
                    if search_course == course.strip().lower():
                        exact_course_match = True
                        matched_course = course
                        break
 
                if not exact_course_match:
                    course_match = any(search_course in course.lower() for course in courses)
                    if not course_match:
                        continue

                # ✅ FIXED: Determine matched_course correctly
                if exact_course_match:
                    # Exact match found (matched_course already set in loop)
                    pass  # matched_course already has the correct value
                elif course_match:
                    # Partial match found
                    matched_course = next((c for c in courses if search_course in c.lower()), None)

                field.matched_course = matched_course

                # Filter by English Test
                if english_test_type and english_test_score:
                    if field.english_tests:
                        try:
                            tests = json.loads(field.english_tests)
                            test_match = False
                            for test in tests:
                                test_key = test['test'].lower().replace(' ', '_')
                                if test_key == english_test_type:
                                    if test.get('score'):
                                        try:
                                            if float(english_test_score) >= float(test['score']):
                                                test_match = True
                                                break
                                        except:
                                            pass
                            if not test_match:
                                continue
                        except:
                            continue

                # Check general study gap
                if not check_general_study_gap(student_study_gap, field):
                    continue

                # Check bachelor entry requirements
                if field.course_level == 'Bachelor' and student_fsc:
                    is_bachelor_eligible, bachelor_reason = check_bachelor_eligibility(student_fsc, student_ba, field)
                    if not is_bachelor_eligible:
                        continue

                # MOI vs REGULAR DECISION LOGIC
                if field.moi_required == 'yes':
                    # University MOI accept karti hai
                    
                    # Check if ALL MOI filters provided hain
                    moi_filters_complete = all([
                        student_fsc,
                        student_cgpa or student_percentage,
                        student_study_gap,
                        student_university
                    ])
                    
                    if moi_filters_complete:
                        # MOI eligibility check
                        is_eligible, missing_info = check_moi_eligibility(
                            student_fsc, student_cgpa, student_percentage,
                            student_university, student_study_gap, field
                        )
                        
                        if is_eligible:
                            # ✅ STUDENT MOI ELIGIBLE HAI
                            if uni not in moi_eligible:
                                uni.matched_field = field
                                moi_eligible.append(uni)
                            # ⚠️ IMPORTANT: MOI eligible ko regular mein NAHI daalna
                            continue
                        else:
                            # ❌ MOI FAIL - Check GENERAL requirements for REGULAR category
                            meets_general = check_general_cgpa(student_cgpa, field)
                            
                            if meets_general:
                                if uni not in regular_results:
                                    uni.matched_field = field
                                    regular_results.append(uni)
                    else:
                        # MOI filters incomplete - Check GENERAL requirements
                        meets_general = check_general_cgpa(student_cgpa, field)
                        
                        if meets_general:
                            if uni not in regular_results:
                                uni.matched_field = field
                                regular_results.append(uni)
                
                else:
                    # NO MOI REQUIRED = REGULAR ONLY
                    meets_general = check_general_cgpa(student_cgpa, field)
                    
                    if meets_general:
                        if uni not in regular_results:
                            uni.matched_field = field
                            regular_results.append(uni)


            # Generate warnings (MOI POTENTIAL WARNINGS REMOVED)
            if not student_fsc:
                profile_warnings.append("✕ FSc English marks not provided - some MOI eligibility checks skipped.")
            if not student_cgpa and not student_percentage:
                profile_warnings.append("✕ CGPA/Percentage not provided - some MOI eligibility checks skipped.")
            if not student_study_gap:
                profile_warnings.append("✕ Study gap not provided - some eligibility checks skipped.")
            if not student_university:
                profile_warnings.append("✕ Last university not provided - some MOI eligibility checks skipped.")

            # Applied filters
            applied_filters["Course"] = search_course.title()
            if country:
                applied_filters["Country"] = country
            if location:
                applied_filters["Location"] = location
            if level:
                applied_filters["Course Level"] = level
            if intake:
                applied_filters["Intake"] = intake
            if max_fee:
                applied_filters["Max Fee"] = f"£{max_fee}"
            if english_test_type and english_test_score:
                applied_filters["English Test"] = f"{english_test_type.replace('_', ' ').title()} - {english_test_score}"
            if student_fsc:
                applied_filters["FSc Marks"] = student_fsc + '%'
            if student_cgpa:
                applied_filters["CGPA"] = student_cgpa
            if student_percentage:
                applied_filters["Percentage"] = student_percentage + '%'
            if student_study_gap:
                applied_filters["Study Gap"] = student_study_gap + ' years'
            if student_university:
                applied_filters["Last University"] = student_university
    
    dropdown_data = get_dropdown_data()
    hardcoded = get_hardcoded_values()

    return render_template('staff_generate_advice.html',
        moi_eligible=moi_eligible,
        regular_results=regular_results,  # MOI_POTENTIAL REMOVED
        applied_filters=applied_filters,
        profile_warnings=profile_warnings,
        **dropdown_data, **hardcoded
    )

@app.route('/staff/download-advice-pdf', methods=['POST'])
@login_required
@staff_required
def staff_download_advice_pdf():
    selected_uni_ids = request.form.getlist('selected_universities')
    
    if not selected_uni_ids:
        flash('Please select at least one university', 'error')
        return redirect(url_for('staff_generate_advice'))
    
    # Get universities
    universities = University.query.filter(University.id.in_(selected_uni_ids)).all()
    
    # Categorize universities like in web view (MOI POTENTIAL REMOVED)
    moi_eligible = []
    regular = []
    
    # Get student profile data from form (if available)
    student_fsc = request.form.get('student_fsc', '')
    student_cgpa = request.form.get('student_cgpa', '')
    student_percentage = request.form.get('student_percentage', '')
    student_university = request.form.get('student_university', '')
    student_study_gap = request.form.get('student_study_gap', '')
    
    level_filter = request.form.get('level', '') or request.form.get('selected_level', '')
    
    for uni in universities:
        matched_course = request.form.get(f'course_{uni.id}', '').lower().strip()
        
        all_fields = UniversityField.query.filter_by(university_id=uni.id).all()
        correct_field = None
        
        for field in all_fields:
            if field.courses:
                try:
                    courses_list = json.loads(field.courses)
                    
                    exact_match = any(
                        matched_course == c.strip().lower()
                        for c in courses_list
                    )
                    if exact_match:
                        correct_field = field
                        break
                    
                    partial_match = any(
                        matched_course in c.lower()
                        for c in courses_list
                    )
                    if partial_match:
                        correct_field = field
                        break
                        
                except:
                    courses_str = field.courses.lower()
                    
                    if matched_course in [c.strip().lower() for c in field.courses.split(',')]:
                        correct_field = field
                        break
                    
                    if matched_course in courses_str:
                        correct_field = field
                        break
        
        if not correct_field:
            continue
        
        field = correct_field
        
        if level_filter and field.course_level != level_filter:
            continue
        
        matched_course_form = request.form.get(f'course_{uni.id}')
        if matched_course_form:
            field.matched_course = matched_course_form
        else:
            field.matched_course = getattr(field, 'matched_course', field.field_name)
        
        if field.moi_required == 'yes':
            is_eligible, missing_info = check_moi_eligibility(
                student_fsc, student_cgpa, student_percentage,
                student_university, student_study_gap, field
            )
            
            if is_eligible:
                uni.matched_field = field
                moi_eligible.append(uni)
            else:
                uni.matched_field = field
                regular.append(uni)
        else:
            uni.matched_field = field
            regular.append(uni)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Professional Header
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FF0000'),
        spaceAfter=20,
        alignment=1
    )
    elements.append(Paragraph("SAUK ISLAMABAD - ADVICE REPORT", header_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student Greeting
    elements.append(Paragraph("Dear Student,", styles["Normal"]))
    elements.append(Spacer(1, 0.1*inch))
    
    intro_text = f"""
    We have shared the following <b>{len(universities)} universities</b> based on the profile
    you have shared with us. Please inform us if you have additional information that may affect this advice.<br/><br/>
    
    Please note, these options are not a comprehensive list of options. We can provide you with 
    additional options based on your updated requirements. 
    """
    elements.append(Paragraph(intro_text, styles["Normal"]))
    elements.append(Spacer(1, 0.3*inch))
    
    # SECTION 1: MOI ELIGIBLE UNIVERSITIES
    if moi_eligible:
        # Green Header
        moi_header_style = ParagraphStyle(
            'MOIHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#228B22'),  # Green color
            spaceAfter=10,
            alignment=0
        )
        elements.append(Paragraph(f"✅ MOI Eligible Universities ({len(moi_eligible)})", moi_header_style))
        elements.append(Paragraph("<font color='#228B22'><b>Student fully qualifies for Medium of Instruction. No English test required!</b></font>", styles["Normal"]))
        elements.append(Spacer(1, 0.1*inch))
        
        for idx, uni in enumerate(moi_eligible, 1):
            field = uni.matched_field
            uni_text = f"""
            <b>{idx}. {uni.university_name}</b><br/>
            <b>Country:</b> {uni.country or 'N/A'}<br/>
            <b>Location:</b> {uni.location or 'N/A'}<br/>
            <b>Course:</b> {field.matched_course or 'N/A'}<br/>
            <b>Level:</b> {field.course_level or 'N/A'}<br/>
            <b>Duration:</b> {field.duration or 'N/A'}<br/>
            <b>Intake:</b> {field.intake or 'N/A'}<br/>
            <b>Fee:</b> {field.total_fee or 'N/A'}<br/>
            <b>Deposit:</b> {field.initial_deposit or 'N/A'}<br/>
            """
            if field.scholarship:
                uni_text += f"<b>Scholarship:</b> {field.scholarship}<br/>"
            
            # Green box for MOI Eligible
            box_table = Table([[Paragraph(uni_text, styles["Normal"])]], colWidths=[6.5*inch])
            box_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#228B22")),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fff0")),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(box_table)
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # SECTION 2: REGULAR UNIVERSITIES
    if regular:
        # Blue Header
        regular_header_style = ParagraphStyle(
            'RegularHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor("#01411C"),  # Dark green/blue
            spaceAfter=10,
            alignment=0
        )
        elements.append(Paragraph(f"📘 Regular Universities ({len(regular)})", regular_header_style))
        elements.append(Paragraph("<font color='#666666'><b>English language test required (IELTS/PTE/TOEFL/etc.)</b></font>", styles["Normal"]))
        elements.append(Spacer(1, 0.1*inch))
        
        for idx, uni in enumerate(regular, 1):
            field = uni.matched_field
            uni_text = f"""
            <b>{idx}. {uni.university_name}</b><br/>
            <b>Country:</b> {uni.country or 'N/A'}<br/>
            <b>Location:</b> {uni.location or 'N/A'}<br/>
            <b>Course:</b> {field.matched_course or 'N/A'}<br/>
            <b>Level:</b> {field.course_level or 'N/A'}<br/>
            <b>Duration:</b> {field.duration or 'N/A'}<br/>
            <b>Intake:</b> {field.intake or 'N/A'}<br/>
            <b>Fee:</b> {field.total_fee or 'N/A'}<br/>
            <b>Deposit:</b> {field.initial_deposit or 'N/A'}<br/>
            """
            
            # MOI Status - sirf tabhi show karein jab MOI required hai aur student eligible nahi hai
            if field.moi_required == 'yes':
                # Check eligibility again to be sure
                is_eligible, _ = check_moi_eligibility(
                    student_fsc, student_cgpa, student_percentage,
                    student_university, student_study_gap, field
                )
                if not is_eligible:
                    uni_text += "<b>MOI Status:</b> <font color='red'>✗ MOI Not Accepted</font><br/>"
            
            # English Tests
            if field.english_tests:
                try:
                    english_tests = json.loads(field.english_tests)
                    if english_tests:
                        uni_text += "<b>English Tests Accepted:</b> "
                        test_list = []
                        for test in english_tests:
                            if test.get('score'):
                                test_list.append(f"{test['test']} (min {test['score']})")
                            else:
                                test_list.append(test['test'])
                        uni_text += ", ".join(test_list) + "<br/>"
                except:
                    pass
            
            if field.scholarship:
                uni_text += f"<b>Scholarship:</b> {field.scholarship}<br/>"
            
            # Regular box
            box_table = Table([[Paragraph(uni_text, styles["Normal"])]], colWidths=[6.5*inch])
            box_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#666666")),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f9f9f9")),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(box_table)
            elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Professional Footer with Pakistan Time
    from datetime import datetime, timezone
    import pytz
    
    # Get Pakistan time
    pakistan_tz = pytz.timezone('Asia/Karachi')
    pakistan_time = datetime.now(pakistan_tz)
    
    footer_text = f"""
    <b>Generated by:</b> {session.get('username', 'Staff')}<br/>
    <b>Date (Pakistan Time):</b> {pakistan_time.strftime("%Y-%m-%d %H:%M")}<br/>
    <font color="#01411C"><b>Thanks for Contacting us, Best Regards: SAUK ISLAMABAD</b></font>
    """
    elements.append(Paragraph(footer_text, styles["Normal"]))
    
    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = 'application/pdf'
    response.headers["Content-Disposition"] = f'attachment; filename=university_advice_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return response

@app.route('/staff/send-email-advice', methods=['POST'])
@login_required
@staff_required
def staff_send_email_advice():
    try:
        # Get data from form
        student_email = request.form.get("student_email")
        selected_uni_ids = request.form.getlist("selected_universities")
        
        if not student_email:
            flash("Please enter student email address", 'error')
            return redirect(url_for("staff_generate_advice"))
        
        if not selected_uni_ids:
            flash("Please select at least one university", 'error')
            return redirect(url_for("staff_generate_advice"))
        
        # Get universities
        universities = University.query.filter(University.id.in_(selected_uni_ids)).all()
        
        # Categorize universities like in web view (MOI POTENTIAL REMOVED)
        moi_eligible = []
        regular = []
        
        # Get student profile data from form (if available)
        student_fsc = request.form.get("student_fsc", "")
        student_cgpa = request.form.get("student_cgpa", "")
        student_percentage = request.form.get("student_percentage", "")
        student_university = request.form.get("student_university", "")
        student_study_gap = request.form.get("student_study_gap", "")
        level_filter = request.form.get('level', "") or request.form.get('selected_level', "")
        
        # 🔥 FIX: PROCESS UNIVERSITIES PROPERLY (LIKE PDF GENERATION)
        for uni in universities:
            matched_course = request.form.get(f'course_{uni.id}', "").lower().strip()
            all_fields = UniversityField.query.filter_by(university_id=uni.id).all()
            
            correct_field = None
            
            for field in all_fields:
                if field.courses:
                    try:
                        courses_list = json.loads(field.courses)
                        # Check for exact match
                        exact_match = any(
                            matched_course == c.strip().lower()
                            for c in courses_list
                        )
                        if exact_match:
                            correct_field = field
                            break
                        
                        # Check for partial match
                        partial_match = any(
                            matched_course in c.lower()
                            for c in courses_list
                        )
                        if partial_match:
                            correct_field = field
                            break
                    except:
                        # Fallback for comma-separated format
                        courses_str = field.courses.lower()
                        if matched_course in [c.strip().lower() for c in field.courses.split(',')]:
                            correct_field = field
                            break
                        if matched_course in courses_str:
                            correct_field = field
                            break
            
            if not correct_field:
                continue
                
            field = correct_field
            
            if level_filter and field.course_level != level_filter:
                continue
            
            # Set matched course
            matched_course_form = request.form.get(f'course_{uni.id}')
            if matched_course_form:
                field.matched_course = matched_course_form
            else:
                field.matched_course = getattr(field, 'matched_course', field.field_name)
            
            # 🔥 CRITICAL: Assign matched_field to university
            uni.matched_field = field
            
            # Parse English tests for display
            if field.english_tests:
                try:
                    tests = json.loads(field.english_tests)
                    field.english_tests_parsed = tests
                except:
                    if ',' in field.english_tests:
                        test_list = field.english_tests.split(',')
                        field.english_tests_parsed = [{'test': t.strip(), 'score': ''} for t in test_list if t.strip()]
                    else:
                        field.english_tests_parsed = []
            else:
                field.english_tests_parsed = []
            
            # Check MOI eligibility for categorization
            if field.moi_required == 'yes':
                is_eligible, missing_info = check_moi_eligibility(
                    student_fsc, student_cgpa, student_percentage,
                    student_university, student_study_gap, field
                )
                if is_eligible:
                    moi_eligible.append(uni)
                else:
                    regular.append(uni)
            else:
                regular.append(uni)
        
        # Create email
        html_content = render_template(
            'email_advice_template.html',
            moi_eligible=moi_eligible,
            regular=regular,
            moi_eligible_count=len(moi_eligible),
            regular_count=len(regular),
            total_universities=len(universities),
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Send email using Mailjet HTTP API
        if send_email_mailjet_api(student_email, f"SAUK University Advice - {len(universities)} Universities", html_content):
            flash(f'Email sent to {student_email}', 'success')
            return redirect(url_for('staff_generate_advice'))
        else:
            flash('Email sending failed. Please try again.', 'error')
            return redirect(url_for('staff_generate_advice'))
        
    except Exception as e:
        flash(f'Email sending failed: {str(e)}', 'error')
        return redirect(url_for('staff_generate_advice'))

#
# ENHANCED API ROUTES
#

@app.route('/api/locations/<country>')
def api_locations(country):
    locations = DropdownList.query.filter_by(category='location', parent_value=country).order_by(DropdownList.value).all()
    return jsonify([{'value': p.value} for p in locations])

@app.route('/api/courses/<level>')
def api_courses(level):
    courses = DropdownList.query.filter_by(category='course_name', parent_value=level).order_by(DropdownList.value).all()
    return jsonify([{'value': c.value} for c in courses])

@app.route('/api/field-courses/<field_name>')
def api_field_courses(field_name):
    # Get courses for specific field
    fields = UniversityField.query.filter_by(field_name=field_name).all()
    courses = []
    for field in fields:
        if field.courses:
            try:
                field_courses = json.loads(field.courses)
                courses.extend(field_courses)
            except:
                pass
    return jsonify([{'value': course} for course in list(set(courses))])

#
# ERROR HANDLING
#

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error="Internal server error"), 500

#
# DATABASE INITIALIZATION
#

def init_database():
    with app.app_context():
        db.create_all()
        
        # Create default admin
        admin = User.query.filter_by(username="adminsauk119").first()
        if not admin:
            admin = User(username="adminsauk119", password="bsf1802507", role="admin", first_login=1)
            db.session.add(admin)
            db.session.commit()
            print("✔ Default admin created (username: adminsauk119, password: bsf1802507)")

        # Update dropdown categories
        existing_categories = ['country', 'location', 'field_name', 'course_name', 'level', 'english_test', 'study_gap', 'percentage']
        
        # Remove old categories
        DropdownList.query.filter(~DropdownList.category.in_(existing_categories)).delete()
        
        # Add sample field names if none exist
        if not DropdownList.query.filter_by(category='field_name').first():
            field_names = ['Business', 'IT & Computer Science', 'Engineering', 'Medical & Health', 'Arts & Humanities', 'Science & Technology']
            for name in field_names:
                db.session.add(DropdownList(category='field_name', value=name, display_order=len(field_names)))
        
        db.session.commit()
        create_automatic_backup()

#
# MAIN APPLICATION
#

if __name__ == '__main__':
    from waitress import serve
    init_database()
    print("="*50)
    print("✔ SAUK119 ADVANCED Server Starting...")
    print("✔ Enhanced Security & Professional Features Enabled")
    print("✔ Server running on: http://0.0.0.0:5000")
    print("="*50)
    serve(app, host='0.0.0.0', port=5000, threads=10)
