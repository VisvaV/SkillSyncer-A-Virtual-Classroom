# Skillsyncer - Educational Management System

## Overview
Skillsyncer is an educational management system which is designed to manage academic activities for students and teachers, including course enrollment, classroom management, lessons, assignments, quizzes, projects, and badge awards. It uses MySQL 8.0 as the backend database, implementing PL/SQL components like stored procedures, functions, triggers, and views to automate processes. The frontend is a Python Flask application with HTML, CSS (Bootstrap 5), and JavaScript, providing an interactive interface for users.
This repository highlights the DBMS implementation, focusing on database automation and its integration with a web application to streamline educational workflows.
Features

- Relational database with 19 tables to manage users, courses, classrooms, lessons, tasks, badges, and timelines.  
- Automated progress tracking for students, updating course and classroom progress after each submission.  
- Task management system with a timeline to track deadlines for assignments, quizzes, and projects.  
- Badge system that awards students for achieving performance milestones (e.g., 80%+ progress in a course).  
- Analytics through views and functions to display average grades, pending tasks, and badge counts.  
- Real-time automation using triggers and procedures to ensure data consistency after user actions.

## Technologies Used

Database: MySQL 8.0  
Backend: Python 3.9, Flask 2.0.1  
Frontend: HTML5, CSS3 (Bootstrap 5), JavaScript  
Tools: MySQL Workbench, Visual Studio Code, Git

## Database Setup
### Step 1: Create Database
Create the skillsyncer database and set it as the active database:
CREATE DATABASE skillsyncer;
USE skillsyncer;


If the database already exists, you may need to drop it first using DROP DATABASE skillsyncer; to avoid conflicts.

### Step 2: Import Schema
Note: The schema.sql file, which includes table definitions, procedures, functions, triggers, views, and sample data, is not included in this repository due to legal constraints. Please contact the authors (see Contact section) to obtain the schema file for setup.
Once you have the schema.sql file, import it using:
mysql -u yourusername -p skillsyncer < schema.sql

This sets up:

19 tables with primary and foreign key constraints (ON DELETE CASCADE, ON UPDATE RESTRICT).  
Stored procedures like UpdateCourseProgress, AddUserToClassroom, and AwardBadge.  
Functions such as GetAvgGrade, GetPendingTasks, and GetBadgeCount.  
Triggers including AfterSubmission, AfterQuizSubmission, and UpdateLastLogin.  
Views like StudentPerformance and TimelineOverview.  
Sample data for users, courses, classrooms, and tasks for testing purposes.

## Application Setup
### Step 1: Install Dependencies
Install the required Python packages for the Flask application:
pip install flask mysql-connector-python


Ensure Python 3.9 is installed. Use pip3 if pip points to Python 2.x.

### Step 2: Configure Database
Create or edit the config.py file in the project root directory to set up the database connection:
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_mysql_username',
    'password': 'your_mysql_password',
    'database': 'skillsyncer'
}


Replace your_mysql_username with your MySQL username (e.g., root).  
Replace your_mysql_password with your MySQL password. If no password is set, use an empty string ('').  
The host is localhost if MySQL runs on the same machine; otherwise, use the server’s IP address.

### Step 3: Run Flask App
Start the Flask application:
python app.py

Access the app in your browser at: http://localhost:5000

If port 5000 is in use, edit app.py to change the port (e.g., app.run(port=5001)), then access at http://localhost:5001.

## Usage Guide
### Login
Log in using sample credentials from the dataset:  

Email: student@example.com  
Password: password

This authenticates against the User table, verifying the email and password. Upon login, the UpdateLastLogin trigger updates the LastLoginTime column in the User table with the current timestamp, helping track user activity.
### Enroll in Course
To enroll in a course:

Navigate to the enrollment section on the web interface.  
Select a classroom from the available list (populated from the Classroom table).  
Submit the enrollment request.

This action calls the AddUserToClassroom procedure, which:

Checks for duplicate enrollments in the Enrollment table.  
If none exist, adds a new record to Enrollment with user_id, classroom_id, EnrollmentDate (current date), and Progress (0.00).  
Adds a record to the Participant table with the user’s role (Student or Teacher).  
Increments the NumberOfEnrollments in the Classroom table.

### Submit Assignment/Quiz
To submit an assignment or quiz:

Go to the tasks section and select an assignment or quiz (listed from the Assignment or Quiz table).  
Enter your submission details (e.g., answers or grades for testing).  
Submit the form.

This process:

Inserts a record into the Submission (for assignments) or QuizSubmission (for quizzes) table with the user_id, assignment_id or quiz_id, SubmissionDate, and Grade or Score.  
Triggers AfterSubmission (for assignments) or AfterQuizSubmission (for quizzes), which:  
Calls UpdateCourseProgress to recalculate the student’s progress based on completed tasks, updating Progress in Enrollment and CompletionPercentage in Course.  
Calls AwardBadge to check if the student’s progress exceeds 80%, awarding a badge by adding a record to UserBadge if eligible.


### View Analytics
Access analytics through the web interface under the analytics section:

StudentPerformance View: Displays a table with:  
Student name and roll number (from User).  
Course and classroom details (from Course and Classroom).  
Progress percentage (from Enrollment).  
Average quiz scores, assignment grades, and project grades (from QuizSubmission, Submission, ProjectSubmission).


TimelineOverview View: Shows a list of upcoming tasks:  
Task type (Assignment, Quiz, or Project) and name (e.g., “Math Assignment 1”).  
Due date (from Timeline).  
Helps students plan their schedules and teachers monitor task completion.



## DBMS Implementation
Database Tables
The database consists of 19 tables to manage the system’s data:

User: Stores user details (e.g., UserID, Name, Email, Password, Role, LastLoginTime).  
Course: Holds course information (e.g., CourseID, CourseName, CompletionPercentage).  
Classroom: Links to Course, tracks enrollments (e.g., ClassroomID, CourseID, NumberOfEnrollments).  
Lesson: Contains lesson content (e.g., LessonID, ClassroomID, LessonName).  
Assignment, Quiz, Project: Manage tasks (e.g., AssignmentID, LessonID, DueDate, TotalMarks).  
Submission, QuizSubmission, ProjectSubmission: Record submissions (e.g., SubmissionID, UserID, Grade).  
Enrollment: Tracks user enrollment (e.g., EnrollmentID, UserID, ClassroomID, Progress).  
Participant: Defines user roles in classrooms (e.g., ParticipantID, ClassroomID, Role).  
Badge, UserBadge: Manage badges (e.g., BadgeID, CourseID, UserBadgeID, AwardedDate).  
Timeline: Tracks deadlines (e.g., TimelineID, UserID, ActivityType, DueDate).  
SampleVideo, Material: Store lesson resources (e.g., SampleVideoID, VideoLink).  
Question, ExerciseProblem: Support quizzes and exercises (e.g., QuestionID, QuizID, QuestionText).

Foreign keys ensure data integrity with ON DELETE CASCADE (e.g., deleting a course removes its classrooms) and ON UPDATE RESTRICT (prevents invalid updates to parent keys).
Stored Procedures

UpdateCourseProgress(user_id, classroom_id):  

Calculates progress by dividing completed lessons (based on submissions) by total lessons in the classroom.  
Updates Progress in Enrollment, CompletionPercentage in Course (average of all enrollments), and NumberOfEnrollments in Classroom.  
Used after submissions to keep progress metrics current.


AddUserToClassroom(user_id, classroom_id, user_role):  

Adds a user to a classroom if not already enrolled.  
Inserts into Enrollment and Participant tables, increments NumberOfEnrollments.  
Ensures no duplicate enrollments with a check.


AwardBadge(user_id, course_id):  

Checks if the user’s average progress in the course (across classrooms) exceeds 80%.  
If eligible and no prior badge exists, adds a record to UserBadge with the current date.  
Prevents duplicate badge awards for the same course.



## Functions

GetAvgGrade(user_id):  

Combines grades from Submission, QuizSubmission, and ProjectSubmission.  
Returns the average as a decimal (e.g., 85.50), or 0.00 if no submissions exist.  
Used to display a student’s overall performance.


GetPendingTasks(user_id):  

Counts tasks in Timeline due on or after the current date, excluding completed ones.  
Returns an integer (e.g., 3 pending tasks).  
Helps users see upcoming workloads.


GetBadgeCount(user_id):  

Counts records in UserBadge for the user.  
Returns an integer (e.g., 5 badges).  
Displays a user’s achievements on their profile.



Triggers

AfterSubmission:  

Executes after an assignment submission.  
Calls UpdateCourseProgress to update the student’s progress.  
Calls AwardBadge to check for badge eligibility.


AfterQuizSubmission:  

Executes after a quiz submission.  
Performs the same actions as AfterSubmission.


UpdateLastLogin:  

Executes before a User table update.  
Sets LastLoginTime to the current timestamp if it’s outdated or null.



Views

StudentPerformance:  

Joins User, Enrollment, Classroom, Course, and submission tables.  
Shows student details, course progress, and average grades/scores.  
Used by teachers to monitor performance and by students to track their progress.


TimelineOverview:  

Joins Timeline with Assignment, Quiz, and Project tables.  
Lists pending tasks with their names and due dates (e.g., “Math Quiz 1, Due: 2025-05-25”).  
Helps users manage their schedules.



## Project Structure
skillsyncer/
├── app.py              # Flask main application with routes
├── config.py           # Database connection settings
├── templates/          # HTML templates for the web interface
│   ├── login.html      # Login page
│   ├── dashboard.html  # User dashboard (student/teacher)
│   ├── enroll.html     # Enrollment form
│   ├── tasks.html      # Task submission page
│   ├── analytics.html  # Analytics display page
│   └── error.html      # Error page
├── static/             # Static assets
│   ├── css/            # CSS files
│   │   └── style.css   # Custom styles
│   └── js/             # JavaScript files
│       └── script.js   # Custom scripts
├── README.md           # Project documentation
└── LICENSE             # MIT License file

Note: The schema.sql file is not included due to legal constraints.
## Screenshots

Login Page
Description: The login page where users enter their email and password to access the system.
Student Dashboard
Description: The student dashboard showing enrolled courses, progress, and pending tasks.
Enrollment Form
Description: The form where users select a classroom to enroll in a course.
Task Submission
Description: The page for submitting an assignment or quiz, showing task details and submission form.
Analytics Page
Description: The analytics page displaying the StudentPerformance view with progress and grades.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Authors

Email Visva V at visvafelix2005@gmail.com  for the schema file or inquiries.  
Report issues at: https://github.com/VisvaV/skillsyncer/issues

