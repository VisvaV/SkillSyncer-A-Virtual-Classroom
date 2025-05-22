from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.Enum('Student', 'Teacher'), nullable=False)
    RollNo = db.Column(db.String(20), unique=True, nullable=True)
    FacultyID = db.Column(db.String(20), unique=True, nullable=True)
    LastLoginTime = db.Column(db.DateTime, nullable=True)

    def get_id(self):
        return str(self.UserID)

class Course(db.Model):
    __tablename__ = 'Course'
    CourseID = db.Column(db.Integer, primary_key=True)
    CourseName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    CompletionPercentage = db.Column(db.DECIMAL(5, 2), default=0.00)

class Classroom(db.Model):
    __tablename__ = 'Classroom'
    ClassroomID = db.Column(db.Integer, primary_key=True)
    CourseID = db.Column(db.Integer, db.ForeignKey('Course.CourseID'), nullable=False)
    StartDate = db.Column(db.Date, nullable=True)
    EndDate = db.Column(db.Date, nullable=True)
    NumberOfEnrollments = db.Column(db.Integer, default=0)
    course = db.relationship('Course', backref='classrooms')

class Lesson(db.Model):
    __tablename__ = 'Lesson'
    LessonID = db.Column(db.Integer, primary_key=True)
    ClassroomID = db.Column(db.Integer, db.ForeignKey('Classroom.ClassroomID'), nullable=False)
    LessonName = db.Column(db.String(100), nullable=False)
    Content = db.Column(db.Text, nullable=True)
    classroom = db.relationship('Classroom', backref='lessons')

class Assignment(db.Model):
    __tablename__ = 'Assignment'
    AssignmentID = db.Column(db.Integer, primary_key=True)
    LessonID = db.Column(db.Integer, db.ForeignKey('Lesson.LessonID'), nullable=False)
    AssignmentName = db.Column(db.String(100), nullable=False)
    DueDate = db.Column(db.Date, nullable=True)
    TotalMarks = db.Column(db.Integer, nullable=False, default=0)
    lesson = db.relationship('Lesson', backref='assignments')

class Submission(db.Model):
    __tablename__ = 'Submission'
    SubmissionID = db.Column(db.Integer, primary_key=True)
    AssignmentID = db.Column(db.Integer, db.ForeignKey('Assignment.AssignmentID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    SubmissionDate = db.Column(db.Date, nullable=True)
    Grade = db.Column(db.DECIMAL(5, 2), nullable=True)
    user = db.relationship('User', backref='submissions')
    assignment = db.relationship('Assignment', backref='submissions')

class Quiz(db.Model):
    __tablename__ = 'Quiz'
    QuizID = db.Column(db.Integer, primary_key=True)
    LessonID = db.Column(db.Integer, db.ForeignKey('Lesson.LessonID'), nullable=False)
    QuizName = db.Column(db.String(100), nullable=False)
    TotalQuestions = db.Column(db.Integer, nullable=False)
    TotalMarks = db.Column(db.Integer, nullable=False, default=0)
    lesson = db.relationship('Lesson', backref='quizzes')

class Question(db.Model):
    __tablename__ = 'Question'
    QuestionID = db.Column(db.Integer, primary_key=True)
    QuizID = db.Column(db.Integer, db.ForeignKey('Quiz.QuizID'), nullable=False)
    QuestionText = db.Column(db.Text, nullable=False)
    CorrectAnswer = db.Column(db.String(255), nullable=False)
    quiz = db.relationship('Quiz', backref='questions')

class QuizSubmission(db.Model):
    __tablename__ = 'QuizSubmission'
    SubmissionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    QuizID = db.Column(db.Integer, db.ForeignKey('Quiz.QuizID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    Score = db.Column(db.DECIMAL(5, 2), nullable=True)
    SubmissionDate = db.Column(db.Date, nullable=True)
    user = db.relationship('User', backref='quiz_submissions')
    quiz = db.relationship('Quiz', backref='quiz_submissions')

class ExerciseProblem(db.Model):
    __tablename__ = 'ExerciseProblem'
    ExerciseProblemID = db.Column(db.Integer, primary_key=True)
    LessonID = db.Column(db.Integer, db.ForeignKey('Lesson.LessonID'), nullable=False)
    ProblemText = db.Column(db.Text, nullable=False)
    Solution = db.Column(db.Text, nullable=True)
    lesson = db.relationship('Lesson', backref='exercise_problems')

class Project(db.Model):
    __tablename__ = 'Project'
    ProjectID = db.Column(db.Integer, primary_key=True)
    LessonID = db.Column(db.Integer, db.ForeignKey('Lesson.LessonID'), nullable=False)
    ProjectName = db.Column(db.String(100), nullable=False)
    DueDate = db.Column(db.Date, nullable=True)
    lesson = db.relationship('Lesson', backref='projects')

class ProjectSubmission(db.Model):
    __tablename__ = 'ProjectSubmission'
    SubmissionID = db.Column(db.Integer, primary_key=True)
    ProjectID = db.Column(db.Integer, db.ForeignKey('Project.ProjectID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    SubmissionDate = db.Column(db.Date, nullable=True)
    Grade = db.Column(db.DECIMAL(5, 2), nullable=True)
    user = db.relationship('User', backref='project_submissions')
    project = db.relationship('Project', backref='project_submissions')

class SampleVideo(db.Model):
    __tablename__ = 'SampleVideo'
    SampleVideoID = db.Column(db.Integer, primary_key=True)
    LessonID = db.Column(db.Integer, db.ForeignKey('Lesson.LessonID'), nullable=False)
    VideoLink = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    lesson = db.relationship('Lesson', backref='sample_videos')

class Material(db.Model):
    __tablename__ = 'Material'
    MaterialID = db.Column(db.Integer, primary_key=True)
    LessonID = db.Column(db.Integer, db.ForeignKey('Lesson.LessonID'), nullable=False)
    MaterialLink = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    lesson = db.relationship('Lesson', backref='materials')

class Badge(db.Model):
    __tablename__ = 'Badge'
    BadgeID = db.Column(db.Integer, primary_key=True)
    CourseID = db.Column(db.Integer, db.ForeignKey('Course.CourseID'), nullable=False)
    BadgeName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    course = db.relationship('Course', backref='badges')

class UserBadge(db.Model):
    __tablename__ = 'UserBadge'
    UserBadgeID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    BadgeID = db.Column(db.Integer, db.ForeignKey('Badge.BadgeID'), nullable=False)
    AwardedDate = db.Column(db.Date, nullable=True)
    user = db.relationship('User', backref='user_badges')
    badge = db.relationship('Badge', backref='user_badges')

class Enrollment(db.Model):
    __tablename__ = 'Enrollment'
    EnrollmentID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    ClassroomID = db.Column(db.Integer, db.ForeignKey('Classroom.ClassroomID'), nullable=False)
    EnrollmentDate = db.Column(db.Date, nullable=True)
    Progress = db.Column(db.DECIMAL(5, 2), default=0.00)
    user = db.relationship('User', backref='enrollments')
    classroom = db.relationship('Classroom', backref='enrollments')

class Participant(db.Model):
    __tablename__ = 'Participant'
    ParticipantID = db.Column(db.Integer, primary_key=True)
    ClassroomID = db.Column(db.Integer, db.ForeignKey('Classroom.ClassroomID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    Role = db.Column(db.Enum('Student', 'Teacher'), nullable=False)
    user = db.relationship('User', backref='participations')
    classroom = db.relationship('Classroom', backref='participants')

class Timeline(db.Model):
    __tablename__ = 'Timeline'
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), primary_key=True)  # Composite key part 1
    ActivityID = db.Column(db.Integer, primary_key=True)  # Composite key part 2
    ActivityType = db.Column(db.Enum('Assignment', 'Quiz', 'Project'), nullable=False)
    DueDate = db.Column(db.Date, nullable=True)
    user = db.relationship('User', backref='timelines')

class StudentPerformance(db.Model):
    __tablename__ = 'StudentPerformance'
    __table_args__ = {'info': dict(is_view=True)}

    UserID = db.Column(db.Integer, primary_key=True)
    ClassroomID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    RollNo = db.Column(db.String(20))
    CourseName = db.Column(db.String(100))
    Progress = db.Column(db.DECIMAL(5, 2))
    AvgQuizScore = db.Column(db.DECIMAL(5, 2))
    AvgAssignmentGrade = db.Column(db.DECIMAL(5, 2))
    AvgProjectGrade = db.Column(db.DECIMAL(5, 2))

class TimelineOverview(db.Model):
    __tablename__ = 'TimelineOverview'
    __table_args__ = {'info': dict(is_view=True)}

    UserID = db.Column(db.Integer, primary_key=True)  # Composite key part 1
    ActivityID = db.Column(db.Integer, primary_key=True)  # Composite key part 2
    Name = db.Column(db.String(100))
    ActivityType = db.Column(db.Enum('Assignment', 'Quiz', 'Project'))
    ActivityName = db.Column(db.String(100))
    DueDate = db.Column(db.Date)