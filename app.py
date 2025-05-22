from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, DateField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from flask_bcrypt import Bcrypt
from datetime import datetime
from models import db, User, Course, Classroom, Lesson, Assignment, Submission, Quiz, Question, QuizSubmission, Project, ProjectSubmission, ExerciseProblem, SampleVideo, Material, Badge, UserBadge, Enrollment, Participant, Timeline, StudentPerformance, TimelineOverview
from config import Config
from sqlalchemy.sql import text
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "Enter your password"})
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()], render_kw={"placeholder": "Enter your full name"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "Enter your password"})
    role = SelectField('Role', choices=[('Student', 'Student'), ('Teacher', 'Teacher')], validators=[DataRequired()])
    roll_no = StringField('Roll Number (for Students)', render_kw={"placeholder": "Enter roll number (if student)"})
    faculty_id = StringField('Faculty ID (for Teachers)', render_kw={"placeholder": "Enter faculty ID (if teacher)"})
    submit = SubmitField('Register')

class CourseForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()], render_kw={"placeholder": "Enter course name"})
    description = TextAreaField('Description', render_kw={"placeholder": "Enter course description", "rows": 3})
    submit = SubmitField('Add Course')

class ClassroomForm(FlaskForm):
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add Classroom')

class LessonForm(FlaskForm):
    classroom_id = SelectField('Classroom', coerce=int, validators=[DataRequired()])
    lesson_name = StringField('Lesson Name', validators=[DataRequired()], render_kw={"placeholder": "Enter lesson name"})
    content = TextAreaField('Content', render_kw={"placeholder": "Enter lesson content", "rows": 3})
    submit = SubmitField('Add Lesson')

class QuizForm(FlaskForm):
    quiz_name = StringField('Quiz Name', validators=[DataRequired()], render_kw={"placeholder": "Enter quiz name"})
    lesson_id = SelectField('Lesson', coerce=int, validators=[DataRequired()])
    total_questions = IntegerField('Total Questions', validators=[DataRequired(), NumberRange(min=1)], render_kw={"min": 1})
    total_marks = IntegerField('Total Marks', validators=[DataRequired(), NumberRange(min=1)], render_kw={"min": 1})
    submit = SubmitField('Add Quiz')

class QuizTakeForm(FlaskForm):
    submit = SubmitField('Submit Quiz')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()], render_kw={"placeholder": "Enter your full name"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    roll_no = StringField('Roll Number (for Students)', render_kw={"placeholder": "Enter roll number (if student)"})
    faculty_id = StringField('Faculty ID (for Teachers)', render_kw={"placeholder": "Enter faculty ID (if teacher)"})
    submit = SubmitField('Update Profile')

# Helper class for recent activities
class Activity:
    def __init__(self, description, timestamp):
        self.description = description
        self.timestamp = timestamp

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Email=form.email.data).first()
        if user:
            try:
                if bcrypt.check_password_hash(user.Password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    user.LastLoginTime = datetime.utcnow()
                    db.session.commit()  # Trigger UpdateLastLogin will handle LastLoginTime
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
            except ValueError:
                logger.warning(f"Invalid hash for user {user.Email}. Attempting plain text comparison.")
                if user.Password == form.password.data:
                    user.Password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                    db.session.commit()
                    login_user(user, remember=form.remember.data)
                    user.LastLoginTime = datetime.utcnow()
                    db.session.commit()
                    flash('Login successful! Your password has been updated for security.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid email or password.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter_by(Email=form.email.data).first()
            if existing_user:
                flash('Email already registered.', 'danger')
                return redirect(url_for('register'))
            if form.role.data == 'Student' and not form.roll_no.data:
                flash('Roll number is required for students.', 'danger')
                return redirect(url_for('register'))
            if form.role.data == 'Teacher' and not form.faculty_id.data:
                flash('Faculty ID is required for teachers.', 'danger')
                return redirect(url_for('register'))
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                Name=form.name.data,
                Email=form.email.data,
                Password=hashed_password,
                Role=form.role.data,
                RollNo=form.roll_no.data if form.role.data == 'Student' else None,
                FacultyID=form.faculty_id.data if form.role.data == 'Teacher' else None
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Fetch recent activities (last 5 submissions or actions)
        recent_activities = []
        if current_user.Role == 'Student':
            # Student submissions
            submissions = Submission.query.filter_by(UserID=current_user.UserID).order_by(Submission.SubmissionDate.desc()).limit(5).all()
            quiz_submissions = QuizSubmission.query.filter_by(UserID=current_user.UserID).order_by(QuizSubmission.SubmissionDate.desc()).limit(5).all()
            project_submissions = ProjectSubmission.query.filter_by(UserID=current_user.UserID).order_by(ProjectSubmission.SubmissionDate.desc()).limit(5).all()

            for submission in submissions:
                try:
                    assignment_name = submission.assignment.AssignmentName if submission.assignment else "Unknown Assignment"
                    recent_activities.append(Activity(
                        f"Submitted Assignment: {assignment_name}",
                        submission.SubmissionDate
                    ))
                except Exception as e:
                    logger.error(f"Error processing submission for user {current_user.UserID}: {str(e)}")
                    continue

            for quiz_submission in quiz_submissions:
                try:
                    quiz_name = quiz_submission.quiz.QuizName if quiz_submission.quiz else "Unknown Quiz"
                    recent_activities.append(Activity(
                        f"Submitted Quiz: {quiz_name}",
                        quiz_submission.SubmissionDate
                    ))
                except Exception as e:
                    logger.error(f"Error processing quiz submission for user {current_user.UserID}: {str(e)}")
                    continue

            for project_submission in project_submissions:
                try:
                    project_name = project_submission.project.ProjectName if project_submission.project else "Unknown Project"
                    recent_activities.append(Activity(
                        f"Submitted Project: {project_name}",
                        project_submission.SubmissionDate
                    ))
                except Exception as e:
                    logger.error(f"Error processing project submission for user {current_user.UserID}: {str(e)}")
                    continue

            recent_activities.sort(key=lambda x: x.timestamp if x.timestamp else datetime.min, reverse=True)
            recent_activities = recent_activities[:5]

            enrolled_courses = Enrollment.query.join(Classroom).join(Course).filter(Enrollment.UserID == current_user.UserID).all()
            # Use the GetPendingTasks function
            pending_tasks_count = db.session.execute(db.text("SELECT GetPendingTasks(:user_id)"), {'user_id': current_user.UserID}).scalar()
            # Fetch pending tasks for display
            pending_tasks = db.session.query(TimelineOverview).filter(
                TimelineOverview.UserID == current_user.UserID,
                TimelineOverview.DueDate >= datetime.utcnow().date()
            ).all()
            badges = UserBadge.query.join(Badge).filter(UserBadge.UserID == current_user.UserID).order_by(UserBadge.AwardedDate.desc()).limit(5).all()
            # Use the GetAvgGrade function
            avg_grade = db.session.execute(db.text("SELECT GetAvgGrade(:user_id)"), {'user_id': current_user.UserID}).scalar()
            # Use the GetBadgeCount function
            badge_count = db.session.execute(db.text("SELECT GetBadgeCount(:user_id)"), {'user_id': current_user.UserID}).scalar()

            return render_template('dashboard.html', enrolled_courses=enrolled_courses, pending_tasks=pending_tasks, pending_tasks_count=pending_tasks_count, badges=badges, avg_grade=avg_grade, badge_count=badge_count, recent_activities=recent_activities)

        elif current_user.Role == 'Teacher':
            quizzes = Quiz.query.join(Lesson).join(Classroom).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').order_by(Quiz.QuizID.desc()).limit(5).all()
            lessons = Lesson.query.join(Classroom).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').order_by(Lesson.LessonID.desc()).limit(5).all()

            for quiz in quizzes:
                recent_activities.append(Activity(
                    f"Added Quiz: {quiz.QuizName}",
                    datetime.utcnow()
                ))
            for lesson in lessons:
                recent_activities.append(Activity(
                    f"Added Lesson: {lesson.LessonName}",
                    datetime.utcnow()
                ))

            recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
            recent_activities = recent_activities[:5]

            managed_courses = Classroom.query.join(Course).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').all()
            student_progress = db.session.query(StudentPerformance).filter(StudentPerformance.ClassroomID.in_(
                [c.ClassroomID for c in managed_courses]
            )).limit(5).all()
            total_students = Enrollment.query.join(Classroom).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').distinct(Enrollment.UserID).count()
            avg_course_progress = db.session.query(db.func.avg(Enrollment.Progress)).join(Classroom).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').scalar() or 0.0
            avg_grade = db.session.query(db.func.avg(db.func.coalesce(Submission.Grade, QuizSubmission.Score, ProjectSubmission.Grade))).select_from(Submission).join(Enrollment, Enrollment.UserID == Submission.UserID).join(Classroom, Classroom.ClassroomID == Enrollment.ClassroomID).join(Participant, Participant.ClassroomID == Classroom.ClassroomID).outerjoin(QuizSubmission, QuizSubmission.UserID == Enrollment.UserID).outerjoin(ProjectSubmission, ProjectSubmission.UserID == Enrollment.UserID).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').scalar() or 0.0

            return render_template('dashboard.html', managed_courses=managed_courses, student_progress=student_progress, total_students=total_students, avg_course_progress=avg_course_progress, avg_grade=avg_grade, recent_activities=recent_activities)
    except Exception as e:
        logger.error(f"Error loading dashboard for user {current_user.UserID} (Role: {current_user.Role}): {str(e)}")
        return render_template('error.html', error_message=f"Error loading dashboard: {str(e)}"), 500

@app.route('/courses')
@login_required
def courses():
    try:
        if current_user.Role == 'Teacher':
            return redirect(url_for('course_management'))
        elif current_user.Role == 'Student':
            enrolled_courses = Enrollment.query.join(Classroom).join(Course).filter(Enrollment.UserID == current_user.UserID).all()
            return render_template('student_courses.html', enrolled_courses=enrolled_courses)
    except Exception as e:
        flash(f'Error loading courses: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/course_resources/<int:course_id>')
@login_required
def course_resources(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        enrollment = Enrollment.query.join(Classroom).filter(
            Enrollment.UserID == current_user.UserID,
            Classroom.CourseID == course_id
        ).first()
        if not enrollment and current_user.Role == 'Student':
            flash('You are not enrolled in this course.', 'danger')
            return redirect(url_for('courses'))

        classrooms = Classroom.query.filter_by(CourseID=course_id).all()
        lessons = Lesson.query.join(Classroom).filter(Classroom.CourseID == course_id).all()
        assignments = Assignment.query.join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id).all()
        materials = Material.query.join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id).all()
        videos = SampleVideo.query.join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id).all()
        quizzes = Quiz.query.join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id).all()

        # Fetch submissions for the current user
        user_submissions = {}
        if current_user.Role == 'Student':
            user_id = current_user.UserID
            for assignment in assignments:
                submission = Submission.query.filter_by(AssignmentID=assignment.AssignmentID, UserID=user_id).first()
                user_submissions[assignment.AssignmentID] = submission
            for quiz in quizzes:
                submission = QuizSubmission.query.filter_by(QuizID=quiz.QuizID, UserID=user_id).first()
                user_submissions[quiz.QuizID] = submission

        if current_user.Role == 'Student':
            return render_template('course_resources.html', course=course, classrooms=classrooms, lessons=lessons, assignments=assignments, materials=materials, videos=videos, quizzes=quizzes, user_submissions=user_submissions)
        elif current_user.Role == 'Teacher':
            classroom_form = ClassroomForm()
            lesson_form = LessonForm()
            lesson_form.classroom_id.choices = [(c.ClassroomID, f"Classroom {c.ClassroomID}") for c in classrooms]
            return render_template('course_detail.html', course=course, classrooms=classrooms, lessons=lessons, classroom_form=classroom_form, lesson_form=lesson_form)
    except Exception as e:
        flash(f'Error loading course resources: {str(e)}', 'danger')
        return redirect(url_for('courses'))


@app.route('/course_management')
@login_required
def course_management():
    if current_user.Role != 'Teacher':
        flash('Only teachers can access course management.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        courses = Course.query.all()
        classrooms = Classroom.query.join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').all()
        lessons = Lesson.query.join(Classroom).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').all()
        course_form = CourseForm()
        classroom_form = ClassroomForm()
        classroom_form.course_id.choices = [(c.CourseID, c.CourseName) for c in courses]
        lesson_form = LessonForm()
        lesson_form.classroom_id.choices = [(c.ClassroomID, f"Classroom {c.ClassroomID} - {c.course.CourseName}") for c in classrooms]
        return render_template('course_management.html', courses=courses, classrooms=classrooms, lessons=lessons, course_form=course_form, classroom_form=classroom_form, lesson_form=lesson_form)
    except Exception as e:
        flash(f'Error loading course management: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/add_course', methods=['POST'])
@login_required
def add_course():
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    form = CourseForm()
    if form.validate_on_submit():
        try:
            course = Course(CourseName=form.course_name.data, Description=form.description.data)
            db.session.add(course)
            db.session.commit()
            classroom = Classroom(CourseID=course.CourseID, StartDate=datetime.utcnow().date(), EndDate=datetime.utcnow().date(), NumberOfEnrollments=0)
            db.session.add(classroom)
            db.session.commit()
            # Use stored procedure to add teacher to classroom
            db.session.execute(db.text("CALL AddUserToClassroom(:user_id, :classroom_id, :role)"),
                              {'user_id': current_user.UserID, 'classroom_id': classroom.ClassroomID, 'role': 'Teacher'})
            db.session.commit()
            flash('Course added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course: {str(e)}', 'danger')
    return redirect(url_for('course_management'))

@app.route('/add_classroom', methods=['POST'])
@login_required
def add_classroom():
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    form = ClassroomForm()
    form.course_id.choices = [(c.CourseID, c.CourseName) for c in Course.query.all()]
    if form.validate_on_submit():
        try:
            classroom = Classroom(CourseID=form.course_id.data, StartDate=form.start_date.data, EndDate=form.end_date.data, NumberOfEnrollments=0)
            db.session.add(classroom)
            db.session.commit()
            # Use stored procedure to add teacher to classroom
            db.session.execute(db.text("CALL AddUserToClassroom(:user_id, :classroom_id, :role)"),
                              {'user_id': current_user.UserID, 'classroom_id': classroom.ClassroomID, 'role': 'Teacher'})
            db.session.commit()
            flash('Classroom added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding classroom: {str(e)}', 'danger')
    return redirect(url_for('course_management'))

@app.route('/add_lesson', methods=['POST'])
@login_required
def add_lesson():
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    form = LessonForm()
    form.classroom_id.choices = [(c.ClassroomID, f"Classroom {c.ClassroomID}") for c in Classroom.query.all()]
    if form.validate_on_submit():
        try:
            lesson = Lesson(ClassroomID=form.classroom_id.data, LessonName=form.lesson_name.data, Content=form.content.data)
            db.session.add(lesson)
            db.session.commit()
            flash('Lesson added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding lesson: {str(e)}', 'danger')
    return redirect(url_for('course_management'))

@app.route('/course_detail/<int:course_id>')
@login_required
def course_detail(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        classrooms = Classroom.query.filter_by(CourseID=course_id).all()
        lessons = Lesson.query.join(Classroom).filter(Classroom.CourseID == course_id).all()
        if current_user.Role == 'Student':
            progress = {
                'overall': Enrollment.query.filter_by(UserID=current_user.UserID, ClassroomID=classrooms[0].ClassroomID).first().Progress if classrooms else 0,
                'assignments_completed': Submission.query.join(Assignment).join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id, Submission.UserID == current_user.UserID).count(),
                'assignments_total': Assignment.query.join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id).count(),
                'quizzes_completed': QuizSubmission.query.join(Quiz).join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id, QuizSubmission.UserID == current_user.UserID).count(),
                'quizzes_total': Quiz.query.join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id).count(),
                'projects_completed': ProjectSubmission.query.join(Project).join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id, ProjectSubmission.UserID == current_user.UserID).count(),
                'projects_total': Project.query.join(Lesson).join(Classroom).filter(Classroom.CourseID == course_id).count(),
                'avg_grade': db.session.execute(db.text("SELECT GetAvgGrade(:user_id)"), {'user_id': current_user.UserID}).scalar()
            }
            for classroom in classrooms:
                enrollment = Enrollment.query.filter_by(UserID=current_user.UserID, ClassroomID=classroom.ClassroomID).first()
                classroom.is_enrolled = enrollment is not None
                classroom.Progress = enrollment.Progress if enrollment else 0
            classroom_form = ClassroomForm()
            lesson_form = LessonForm()
            lesson_form.classroom_id.choices = [(c.ClassroomID, f"Classroom {c.ClassroomID}") for c in classrooms]
            return render_template('course_detail.html', course=course, classrooms=classrooms, lessons=lessons, progress=progress, classroom_form=classroom_form, lesson_form=lesson_form)
        elif current_user.Role == 'Teacher':
            classroom_form = ClassroomForm()
            # Ensure course_id is included in choices
            classroom_form.course_id.choices = [(c.CourseID, c.CourseName) for c in Course.query.all()]
            lesson_form = LessonForm()
            # Safely set classroom choices, handling potential None values
            lesson_form.classroom_id.choices = [
                (c.ClassroomID, f"Classroom {c.ClassroomID} - {c.course.CourseName if c.course else 'Unnamed Course'}")
                for c in classrooms if c.course
            ] if classrooms else []
            return render_template('course_detail.html', course=course, classrooms=classrooms, lessons=lessons, classroom_form=classroom_form, lesson_form=lesson_form)
    except Exception as e:
        logger.error(f"Error in course_detail for course_id {course_id}: {str(e)}")
        flash(f'Error loading course details: {str(e)}', 'danger')
        return redirect(url_for('course_management'))

@app.route('/enroll_classroom/<int:classroom_id>')
@login_required
def enroll_classroom(classroom_id):
    if current_user.Role != 'Student':
        flash('Only students can enroll.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        # Use stored procedure to enroll student
        db.session.execute(db.text("CALL AddUserToClassroom(:user_id, :classroom_id, :role)"),
                          {'user_id': current_user.UserID, 'classroom_id': classroom_id, 'role': 'Student'})
        db.session.commit()
        flash('Successfully enrolled!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error enrolling: {str(e)}', 'danger')
    return redirect(url_for('course_detail', course_id=Classroom.query.get(classroom_id).CourseID))

@app.route('/quiz/<int:course_id>/<int:classroom_id>')
@login_required
def quiz(course_id, classroom_id):
    try:
        course = Course.query.get_or_404(course_id)
        classroom = Classroom.query.get_or_404(classroom_id)
        if current_user.Role == 'Teacher':
            quizzes = Quiz.query.join(Lesson).join(Classroom).filter(Classroom.ClassroomID == classroom_id).all()
            quiz_form = QuizForm()
            quiz_form.lesson_id.choices = [(l.LessonID, l.LessonName) for l in Lesson.query.filter_by(ClassroomID=classroom_id).all()]
            return render_template('quiz.html', course=course, classroom=classroom, quizzes=quizzes, quiz_form=quiz_form)
        elif current_user.Role == 'Student':
            enrollment = Enrollment.query.filter_by(UserID=current_user.UserID, ClassroomID=classroom_id).first()
            if not enrollment:
                flash('You are not enrolled in this classroom.', 'danger')
                return redirect(url_for('course_resources', course_id=course_id))
            quizzes = Quiz.query.join(Lesson).join(Classroom).filter(Classroom.ClassroomID == classroom_id).all()
            return render_template('quiz.html', course=course, classroom=classroom, quizzes=quizzes)
    except Exception as e:
        flash(f'Error loading quiz page: {str(e)}', 'danger')
        return redirect(url_for('course_resources', course_id=course_id))

@app.route('/add_quiz/<int:course_id>/<int:classroom_id>', methods=['POST'])
@login_required
def add_quiz(course_id, classroom_id):
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    form = QuizForm()
    form.lesson_id.choices = [(l.LessonID, l.LessonName) for l in Lesson.query.filter_by(ClassroomID=classroom_id).all()]
    if form.validate_on_submit():
        try:
            quiz = Quiz(
                LessonID=form.lesson_id.data,
                QuizName=form.quiz_name.data,
                TotalQuestions=form.total_questions.data,
                TotalMarks=form.total_marks.data
            )
            db.session.add(quiz)
            db.session.commit()
            students = Enrollment.query.filter_by(ClassroomID=classroom_id).all()
            for student in students:
                timeline = Timeline(
                    UserID=student.UserID,
                    ActivityType='Quiz',
                    ActivityID=quiz.QuizID,
                    DueDate=datetime.utcnow().date()
                )
                db.session.add(timeline)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding quiz: {str(e)}', 'danger')
    return redirect(url_for('quiz', course_id=course_id, classroom_id=classroom_id))

@app.route('/quiz_take/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def quiz_take(quiz_id):
    if current_user.Role != 'Student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(QuizID=quiz_id).all()
        quiz_submitted = QuizSubmission.query.filter_by(UserID=current_user.UserID, QuizID=quiz_id).first() is not None

        if request.method == 'POST' and not quiz_submitted:
            score = 0
            for question in questions:
                answer = request.form.get(f'question_{question.QuestionID}')
                if answer and answer == question.CorrectAnswer:
                    score += (quiz.TotalMarks / quiz.TotalQuestions if quiz.TotalQuestions > 0 else 0)
            submission = QuizSubmission(
                UserID=current_user.UserID,
                QuizID=quiz_id,
                SubmissionDate=datetime.utcnow().date(),
                Score=score
            )
            db.session.add(submission)
            db.session.commit()
            flash('Quiz submitted successfully!', 'success')
            return redirect(url_for('quiz_take', quiz_id=quiz_id))

        if quiz_submitted:
            submission = QuizSubmission.query.filter_by(UserID=current_user.UserID, QuizID=quiz_id).first()
            for question in questions:
                question.user_answer = "Not answered"  # Placeholder, update with actual submission if stored
                question.correct_answer = question.CorrectAnswer
                question.is_correct = question.user_answer == question.correct_answer
            return render_template('quiz_take.html', quiz=quiz, questions=questions, quiz_submitted=quiz_submitted, score=submission.Score)

        return render_template('quiz_take.html', quiz=quiz, questions=questions, quiz_submitted=quiz_submitted, score=None)
    except Exception as e:
        flash(f'Error loading quiz: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/progress')
@login_required
def progress():
    if current_user.Role != 'Student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        stats = {
            'courses_enrolled': Enrollment.query.filter_by(UserID=current_user.UserID).count(),
            'overall_progress': db.session.query(db.func.avg(Enrollment.Progress)).filter_by(
                UserID=current_user.UserID).scalar() or 0.0,
            'assignments_completed': Submission.query.filter_by(UserID=current_user.UserID).count(),
            'assignments_total': Timeline.query.filter_by(UserID=current_user.UserID,
                                                          ActivityType='Assignment').count(),
            'quizzes_completed': QuizSubmission.query.filter_by(UserID=current_user.UserID).count(),
            'quizzes_total': Timeline.query.filter_by(UserID=current_user.UserID, ActivityType='Quiz').count(),
            'projects_completed': ProjectSubmission.query.filter_by(UserID=current_user.UserID).count(),
            'projects_total': Timeline.query.filter_by(UserID=current_user.UserID, ActivityType='Project').count(),
            'avg_grade': db.session.execute(db.text("SELECT GetAvgGrade(:user_id)"),
                                            {'user_id': current_user.UserID}).scalar()
        }
        courses = Enrollment.query.join(Classroom).join(Course).filter(Enrollment.UserID == current_user.UserID).all()
        return render_template('progress.html', stats=stats, courses=courses)
    except Exception as e:
        flash(f'Error loading progress: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/classroom/<int:classroom_id>')
@login_required
def classroom(classroom_id):
    try:
        classroom = Classroom.query.get_or_404(classroom_id)
        # Check if the user is a participant in the classroom
        participant = Participant.query.filter_by(ClassroomID=classroom_id, UserID=current_user.UserID).first()
        if not participant:
            flash('You are not enrolled in this classroom.', 'danger')
            return redirect(url_for('dashboard'))

        lessons = classroom.lessons  # This is an InstrumentedList of Lesson objects
        for lesson in lessons:
            # No need to filter quizzes, assignments, etc., as the relationship already filters them
            # Just add submission status for each resource
            for quiz in lesson.quizzes:
                quiz.is_submitted = QuizSubmission.query.filter_by(UserID=current_user.UserID,
                                                                   QuizID=quiz.QuizID).first() is not None
            for assignment in lesson.assignments:
                assignment.is_submitted = Submission.query.filter_by(UserID=current_user.UserID,
                                                                     AssignmentID=assignment.AssignmentID).first() is not None
            for project in lesson.projects:
                project.is_submitted = ProjectSubmission.query.filter_by(UserID=current_user.UserID,
                                                                         ProjectID=project.ProjectID).first() is not None
            # No need to check submission status for sample_videos, materials, or exercise_problems
            # since they are not submitted by students

        return render_template('classroom.html', classroom=classroom, lessons=lessons)
    except Exception as e:
        return render_template('error.html', error_message=f'Error loading course resources: {str(e)}')

@app.route('/badges')
@login_required
def badges():
    if current_user.Role != 'Student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        badges = UserBadge.query.join(Badge).filter(UserBadge.UserID == current_user.UserID).all()
        badge_count = db.session.execute(db.text("SELECT GetBadgeCount(:user_id)"),
                                         {'user_id': current_user.UserID}).scalar()
        return render_template('badges.html', badges=badges, badge_count=badge_count)
    except Exception as e:
        flash(f'Error loading badges: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/timeline')
@login_required
def timeline():
    if current_user.Role != 'Student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        tasks = db.session.query(TimelineOverview).filter(
            TimelineOverview.UserID == current_user.UserID
        ).all()
        now = datetime.utcnow().date()  # Define 'now' as the current date
        for task in tasks:
            if task.DueDate:
                task.days_left = (task.DueDate - now).days
            else:
                task.days_left = None
            if task.ActivityType == 'Assignment':
                task.is_submitted = Submission.query.filter_by(UserID=current_user.UserID, AssignmentID=task.ActivityID).first() is not None
            elif task.ActivityType == 'Quiz':
                task.is_submitted = QuizSubmission.query.filter_by(UserID=current_user.UserID, QuizID=task.ActivityID).first() is not None
            elif task.ActivityType == 'Project':
                task.is_submitted = ProjectSubmission.query.filter_by(UserID=current_user.UserID, ProjectID=task.ActivityID).first() is not None
        return render_template('timeline.html', tasks=tasks, now=now)
    except Exception as e:
        return render_template('error.html', error_message=f'Error loading timeline: {str(e)}')


@app.route('/analytics_student')
@login_required
def analytics_student():
    if current_user.Role != 'Student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        stats = {
            'courses_enrolled': Enrollment.query.filter_by(UserID=current_user.UserID).count(),
            'overall_progress': db.session.query(db.func.avg(Enrollment.Progress)).filter_by(UserID=current_user.UserID).scalar() or 0.0,
            'assignments_completed': Submission.query.filter_by(UserID=current_user.UserID).count(),
            'assignments_total': Timeline.query.filter_by(UserID=current_user.UserID, ActivityType='Assignment').count(),
            'quizzes_completed': QuizSubmission.query.filter_by(UserID=current_user.UserID).count(),
            'quizzes_total': Timeline.query.filter_by(UserID=current_user.UserID, ActivityType='Quiz').count(),
            'projects_completed': ProjectSubmission.query.filter_by(UserID=current_user.UserID).count(),
            'projects_total': Timeline.query.filter_by(UserID=current_user.UserID, ActivityType='Project').count(),
            'avg_grade': db.session.execute(db.text("SELECT GetAvgGrade(:user_id)"), {'user_id': current_user.UserID}).scalar() or 0.0
        }
        performance = db.session.query(StudentPerformance).filter(StudentPerformance.UserID == current_user.UserID).all()
        return render_template('analytics_student.html', stats=stats, performance=performance)
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/analytics_teacher')
@login_required
def analytics_teacher():
    if current_user.Role != 'Teacher':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        managed_courses = Classroom.query.join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').all()
        stats = {
            'courses_managed': len(managed_courses),
            'total_students': Enrollment.query.join(Classroom).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').distinct(Enrollment.UserID).count(),
            'avg_progress': db.session.query(db.func.avg(Enrollment.Progress)).select_from(Enrollment).join(Classroom).join(Participant).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').scalar() or 0.0,
            'avg_grade': db.session.query(db.func.avg(db.func.coalesce(Submission.Grade, QuizSubmission.Score, ProjectSubmission.Grade))).select_from(Submission).join(Enrollment, Enrollment.UserID == Submission.UserID).join(Classroom, Classroom.ClassroomID == Enrollment.ClassroomID).join(Participant, Participant.ClassroomID == Classroom.ClassroomID).outerjoin(QuizSubmission, QuizSubmission.UserID == Enrollment.UserID).outerjoin(ProjectSubmission, ProjectSubmission.UserID == Enrollment.UserID).filter(Participant.UserID == current_user.UserID, Participant.Role == 'Teacher').scalar() or 0.0
        }
        performance = db.session.query(StudentPerformance).filter(StudentPerformance.ClassroomID.in_(
            [c.ClassroomID for c in managed_courses]
        )).all()
        return render_template('analytics_teacher.html', stats=stats, performance=performance)
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/edit_classroom/<int:classroom_id>', methods=['GET', 'POST'])
@login_required
def edit_classroom(classroom_id):
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    classroom = Classroom.query.get_or_404(classroom_id)
    form = ClassroomForm(obj=classroom)
    if form.validate_on_submit():
        try:
            classroom.StartDate = form.start_date.data
            classroom.EndDate = form.end_date.data
            db.session.commit()
            flash('Classroom updated successfully!', 'success')
            return redirect(url_for('course_detail', course_id=classroom.CourseID))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating classroom: {str(e)}', 'danger')
    return render_template('edit_classroom.html', form=form, classroom=classroom)

@app.route('/delete_classroom/<int:classroom_id>', methods=['POST'])
@login_required
def delete_classroom(classroom_id):
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        classroom = Classroom.query.get_or_404(classroom_id)
        course_id = classroom.CourseID
        db.session.delete(classroom)
        db.session.commit()
        flash('Classroom deleted successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting classroom: {str(e)}', 'danger')
        return redirect(url_for('course_detail', course_id=classroom.CourseID))

@app.route('/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm(obj=lesson)
    form.classroom_id.choices = [(c.ClassroomID, f"Classroom {c.ClassroomID}") for c in Classroom.query.all()]
    if form.validate_on_submit():
        try:
            lesson.ClassroomID = form.classroom_id.data
            lesson.LessonName = form.lesson_name.data
            lesson.Content = form.content.data
            db.session.commit()
            flash('Lesson updated successfully!', 'success')
            return redirect(url_for('course_detail', course_id=lesson.classroom.course.CourseID))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating lesson: {str(e)}', 'danger')
    return render_template('edit_lesson.html', form=form, lesson=lesson)

@app.route('/delete_lesson/<int:lesson_id>', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    if current_user.Role != 'Teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        course_id = lesson.classroom.course.CourseID
        db.session.delete(lesson)
        db.session.commit()
        flash('Lesson deleted successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting lesson: {str(e)}', 'danger')
        return redirect(url_for('course_detail', course_id=lesson.classroom.course.CourseID))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        try:
            current_user.Name = form.name.data
            current_user.Email = form.email.data
            if current_user.Role == 'Student':
                current_user.RollNo = form.roll_no.data
            elif current_user.Role == 'Teacher':
                current_user.FacultyID = form.faculty_id.data
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    return render_template('profile.html', form=form)


@app.route('/submit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    if current_user.Role != 'Student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))

    assignment = Assignment.query.get_or_404(assignment_id)
    # Check if the student is enrolled in the classroom
    lesson = assignment.lesson
    classroom = lesson.classroom
    participant = Participant.query.filter_by(ClassroomID=classroom.ClassroomID, UserID=current_user.UserID).first()
    if not participant:
        flash('You are not enrolled in this classroom.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # In a real app, you'd handle file uploads or text submissions here
        # For simplicity, we'll just mark the assignment as submitted
        submission = Submission(
            AssignmentID=assignment_id,
            UserID=current_user.UserID,
            SubmissionDate=datetime.utcnow().date()
        )
        db.session.add(submission)

        # Update the timeline (optional, if you want to reflect the submission)
        timeline = Timeline.query.filter_by(UserID=current_user.UserID, ActivityType='Assignment',
                                            ActivityID=assignment_id).first()
        if timeline:
            # You could update the timeline if needed
            pass

        db.session.commit()
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('classroom', classroom_id=classroom.ClassroomID))

    return render_template('submit_assignment.html', assignment=assignment)


@app.route('/submit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def submit_project(project_id):
    if current_user.Role != 'Student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))

    project = Project.query.get_or_404(project_id)
    # Check if the student is enrolled in the classroom
    lesson = project.lesson
    classroom = lesson.classroom
    participant = Participant.query.filter_by(ClassroomID=classroom.ClassroomID, UserID=current_user.UserID).first()
    if not participant:
        flash('You are not enrolled in this classroom.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # In a real app, you'd handle file uploads or text submissions here
        # For simplicity, we'll just mark the project as submitted
        submission = ProjectSubmission(
            ProjectID=project_id,
            UserID=current_user.UserID,
            SubmissionDate=datetime.utcnow().date()
        )
        db.session.add(submission)

        # Update the timeline (optional)
        timeline = Timeline.query.filter_by(UserID=current_user.UserID, ActivityType='Project',
                                            ActivityID=project_id).first()
        if timeline:
            # You could update the timeline if needed
            pass

        db.session.commit()
        flash('Project submitted successfully!', 'success')
        return redirect(url_for('classroom', classroom_id=classroom.ClassroomID))

    return render_template('submit_project.html', project=project)


if __name__ == '__main__':
    app.run(debug=True)