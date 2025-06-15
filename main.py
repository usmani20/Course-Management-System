import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import func
from dotenv import load_dotenv

load_dotenv()

# --- Flask Setup with SQLite database configration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instances', 'courses.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Database Setup ---
db = SQLAlchemy(app)

# -- defining tables for the database --
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    students = db.relationship('Student', backref='department', lazy=True)
    instructors = db.relationship('Instructor', backref='department', lazy=True)

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    courses = db.relationship('Course', backref='instructor', lazy=True)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Course', backref='semester', lazy=True)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    schedules = db.relationship('Schedule', backref='course', lazy=True)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    student = db.relationship('Student', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date_submitted = db.Column(db.Date, default=datetime.date.today)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    student = db.relationship('Student', backref='feedbacks')
    course = db.relationship('Course', backref='feedbacks')

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    course = db.relationship('Course', backref='assignments')

# -- Routes to access the webpages--

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    departments = Department.query.all()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        year = request.form['year']
        section = request.form['section']
        department_id = request.form['department_id']

        new_student = Student(
            name=name,
            email=email,
            phone=phone,
            year=int(year),
            section=section,
            department_id=int(department_id)
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('show_all_students'))

    return render_template('add_student.html', departments=departments)


@app.route('/show_all_students')
def show_all_students():
    students = Student.query.all()
    return render_template('show_students.html', students=students)

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        code = request.form['code']
        title = request.form['title']
        instructor_id = request.form['instructor_id']
        semester_id = request.form['semester_id']
        new_course = Course(code=code, title=title, instructor_id=instructor_id, semester_id=semester_id)
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('show_all_courses'))
    instructors = Instructor.query.all()
    semesters = Semester.query.all()
    return render_template('add_course.html', instructors=instructors, semesters=semesters)

@app.route('/show_all_courses')
def show_all_courses():
    courses = Course.query.all()
    return render_template('show_courses.html', courses=courses)

@app.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department_id = request.form['department_id']
        instructor = Instructor(name=name, email=email, department_id=department_id)
        db.session.add(instructor)
        db.session.commit()
        return redirect(url_for('show_all_instructors'))
    departments = Department.query.all()
    return render_template('add_instructor.html', departments=departments)

@app.route('/show_all_instructors')
def show_all_instructors():
    instructors = Instructor.query.all()
    return render_template('show_instructors.html', instructors=instructors)

@app.route('/show_all_departments')
def show_all_departments():
    departments = Department.query.all()
    return render_template('show_departments.html', departments=departments)

@app.route('/show_schedule')
def show_schedule():
    schedules = Schedule.query.all()
    return render_template('show_schedule.html', schedules=schedules)

@app.route('/announce_something', methods=['GET', 'POST'])
def announce_something():
    if request.method == 'POST':
        message = request.form['message']
        ann = Announcement(message=message)
        db.session.add(ann)
        db.session.commit()
        return redirect(url_for('all_announcements'))
    return render_template('announce.html')

@app.route('/all_announcements')
def all_announcements():
    announcements = Announcement.query.order_by(Announcement.date_posted.desc()).all()
    return render_template('all_announcements.html', announcements=announcements)

@app.route('/enrollments')
def show_enrollments():
    enrollments = Enrollment.query.all()
    return render_template('show_enrollments.html', enrollments=enrollments)

@app.route('/add_feedback', methods=['GET', 'POST'])
def add_feedback():
    students = Student.query.all()
    courses = Course.query.all()

    if request.method == 'POST':
        content = request.form['content']
        rating = int(request.form['rating'])
        student_id = int(request.form['student_id'])
        course_id = int(request.form['course_id'])

        new_feedback = Feedback(content=content, rating=rating,
                                student_id=student_id, course_id=course_id)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect('/show_feedback')

    return render_template('add_feedback.html', students=students, courses=courses)

@app.route('/show_feedback')
def show_feedback():
    feedbacks = Feedback.query.all()
    return render_template('show_feedback.html', feedbacks=feedbacks)

@app.route('/add_assignment', methods=['GET', 'POST'])
def add_assignment():
    courses = Course.query.all()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        course_id = int(request.form['course_id'])

        new_assignment = Assignment(
            title=title,
            description=description,
            due_date=datetime.datetime.strptime(due_date, "%Y-%m-%d").date(),
            course_id=course_id
        )
        db.session.add(new_assignment)
        db.session.commit()
        return redirect('/show_assignments')

    return render_template('add_assignment.html', courses=courses)

@app.route('/show_assignments')
def show_assignments():
    assignments = Assignment.query.order_by(Assignment.due_date).all()
    return render_template('show_assignments.html', assignments=assignments)

@app.route('/graphs')
def show_graphs():
    # --- Bar Chart: Students by Department ---
    dept_data = (
        db.session.query(Department.name, func.count(Student.id))
        .join(Student)
        .group_by(Department.id)
        .all()
    )
    labels = [d[0] for d in dept_data]
    values = [d[1] for d in dept_data]

    # --- Pie Chart: Course Enrollments ---
    course_data = (
        db.session.query(Course.title, func.count(Enrollment.id))
        .join(Enrollment)
        .group_by(Course.id)
        .all()
    )
    course_labels = [c[0] for c in course_data]
    course_counts = [c[1] for c in course_data]

    return render_template(
        'graphs.html',
        labels=labels,
        values=values,
        course_labels=course_labels,
        course_counts=course_counts
    )





# --- Run ---
if __name__ == '__main__':
    if not os.path.exists('instances'):
        os.makedirs('instances')
    with app.app_context():
        db.create_all()
    app.run(debug=True)
