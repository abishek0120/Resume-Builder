from flask import Flask, render_template
from flask import redirect, url_for,flash
from flask import request, session 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_mail import Mail,Message
#from sqlalchemy.orm import no_autoflush

app = Flask(__name__)

app.secret_key = 'Suiiiiiiiii'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Sbv%402528@localhost/resume'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tstark0120@gmail.com' 
app.config['MAIL_PASSWORD'] = 'drjj tbru yegb crzh' 
app.config['MAIL_DEFAULT_SENDER'] = ('Abishek BV', 'tstark0120@gmail.com' )

mail = Mail(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    forms = db.relationship('Form', backref='user', lazy=True)

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role=db.Column(db.String(100),nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    college_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    graduation_date = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    github = db.Column(db.String(255), nullable=True)  
    linkedin = db.Column(db.String(255), nullable=True)  
    portfolio = db.Column(db.String(255), nullable=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skills = db.relationship('Skill', backref='form', cascade="all, delete", passive_deletes=True)
    projects = db.relationship('Project', backref='form', cascade="all, delete", passive_deletes=True)
    experiences = db.relationship('Experience', backref='form', cascade="all, delete", passive_deletes=True)


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id', ondelete='CASCADE'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id', ondelete='CASCADE'), nullable=False)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id', ondelete='CASCADE'), nullable=False)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    #db.drop_all()

@app.route('/')
def home():
    reviews = Review.query.join(User).add_columns(User.email, Review.content).all() 
    recent_reviews = (
        db.session.query(Review.content, User.email)
        .join(User, Review.user_id == User.id)  
        .order_by(Review.created_at.desc()) 
        .limit(5)  
        .all() 
    )
    return render_template('home.html', reviews=recent_reviews)



@app.route('/send-message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message_content = request.form.get('message')

    if not name or not email or not message_content:
        flash('All fields are required!', 'danger')
        return redirect(url_for('home'))

    try:
        msg = Message(
            subject=f"The User {name} Sends You this email",
            recipients=['tstark0120@gmail.com'],  
        )
        msg.body = f"From: {name} <{email}>\n\nMessage:\n{message_content}"
        mail.send(msg)
        flash('Message sent successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred while sending the message: {str(e)}', 'danger')

    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    resumes = Form.query.filter_by(user_id=user_id).all()
    reviews = Review.query.filter_by(user_id=user_id).all() 
    return render_template('dashboard.html', resumes=resumes, reviews=reviews, email=current_user.email)


@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    review_content = request.form['review_content']
    new_review = Review(user_id=current_user.id, content=review_content)
    db.session.add(new_review)
    db.session.commit()
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/create_resume', methods=['GET', 'POST'])
@login_required
def create_resume():
    if request.method == 'POST':
        name = request.form['name']
        role=request.form['role']
        age = request.form['age']
        city = request.form['city']
        country = request.form['country']
        phone_number = request.form['phone_number']
        email = request.form['email']
        college_name = request.form['college_name']
        location = request.form['location']
        degree = request.form['degree']
        course = request.form['course']
        graduation_date = request.form['graduation_date']
        summary = request.form['summary']
        github = request.form.get('github', '')
        linkedin = request.form.get('linkedin', '')
        portfolio = request.form.get('portfolio', '')
        user_id = current_user.id

        new_resume = Form(
            name=name,role=role, age=age, city=city, country=country,
            phone_number=phone_number, email=email, college_name=college_name,
            location=location, degree=degree, course=course, graduation_date=graduation_date,
            summary=summary, github=github, linkedin=linkedin, portfolio=portfolio, user_id=user_id
        )
        db.session.add(new_resume)
        db.session.commit()

        return redirect(url_for('additional_info', resume_id=new_resume.id))

    return render_template('create_resume.html')

@app.route('/view_resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    user_id = current_user.id
    resume = Form.query.filter_by(id=resume_id, user_id=user_id).first_or_404()
    
    skills = Skill.query.filter_by(form_id=resume_id).all()
    projects = Project.query.filter_by(form_id=resume_id).all()
    experiences = Experience.query.filter_by(form_id=resume_id).all()

    return render_template('view_resume.html', resume=resume, skills=skills, projects=projects, experiences=experiences)

@app.route('/delete_resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    form = Form.query.get_or_404(resume_id)

    if form:
        Skill.query.filter_by(form_id=resume_id).delete()
        Project.query.filter_by(form_id=resume_id).delete()
        Experience.query.filter_by(form_id=resume_id).delete()
        db.session.delete(form)
        db.session.commit()
        flash('Resume deleted successfully!', 'success')
    else:
        flash('Resume not found!', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/additional_info/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def additional_info(resume_id):
    resume = Form.query.get_or_404(resume_id)
    skills = Skill.query.filter_by(form_id=resume_id).all()
    projects = Project.query.filter_by(form_id=resume_id).all()
    experiences = Experience.query.filter_by(form_id=resume_id).all()

    if request.method == 'POST':
        if 'skill_name' in request.form:
            new_skill = Skill(name=request.form['skill_name'], form_id=resume_id)
            db.session.add(new_skill)
            db.session.commit()
            flash('Skill added successfully!', 'success')

        if 'project_name' in request.form:
            new_project = Project(name=request.form['project_name'], 
                                  description=request.form['project_description'], 
                                  form_id=resume_id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project added successfully!', 'success')

        if 'title' in request.form:
            new_experience = Experience(
                title=request.form['title'],
                company=request.form['company'],
                description=request.form['job_description'],
                start_date=request.form['start_date'],
                end_date=request.form['end_date'],
                form_id=resume_id
            )
            db.session.add(new_experience)
            db.session.commit()
            flash('Experience added successfully!', 'success')

        return redirect(url_for('additional_info', resume_id=resume_id))

    return render_template('additional.html', 
                           resume=resume, 
                           skills=skills, 
                           projects=projects, 
                           experiences=experiences,form_id=resume_id)

@app.route('/delete_item/<item_type>/<int:resume_id>/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_type, resume_id, item_id):

    if item_type == 'skill':
        item = Skill.query.get_or_404(item_id)
    elif item_type == 'project':
        item = Project.query.get_or_404(item_id)
    elif item_type == 'experience':
        item = Experience.query.get_or_404(item_id)
    
    db.session.delete(item)
    db.session.commit()
    
    return redirect(url_for('additional_info', resume_id=resume_id))

@app.route('/update_skills/<int:resume_id>', methods=['POST'])
@login_required
def update_skills(resume_id):
    resume = Form.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    new_skill = request.form.get('new_skill')
    
    if new_skill and new_skill.strip():
        skill = Skill(name=new_skill, form_id=resume_id)
        db.session.add(skill)
        db.session.commit()

    for skill_id in request.form:
        if skill_id.startswith('skill_id_'):
            skill_id = int(skill_id.split('_')[2])
            skill = Skill.query.get(skill_id)
            if skill:
                skill.name = request.form.get(skill_id)
                db.session.commit()

    return redirect(url_for('edit_resume', resume_id=resume_id))

@app.route('/resume/<int:resume_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resume(resume_id):
    resume = Form.query.get_or_404(resume_id)
    if request.method == 'POST':
        resume.name = request.form.get('name', resume.name).strip()
        resume.role = request.form.get('role', resume.role).strip()
        resume.age = request.form.get('age', resume.age)
        resume.city = request.form.get('city', resume.city).strip()
        resume.country = request.form.get('country', resume.country).strip()
        resume.phone_number = request.form.get('phone_number', resume.phone_number).strip()
        resume.email = request.form.get('email', resume.email).strip()
        resume.college_name = request.form.get('college_name', resume.college_name).strip()
        resume.location = request.form.get('location', resume.location).strip()
        resume.degree = request.form.get('degree', resume.degree).strip()
        resume.course = request.form.get('course', resume.course).strip()
        resume.graduation_date = request.form.get('graduation_date', resume.graduation_date).strip()
        resume.summary = request.form.get('summary', resume.summary).strip()
        resume.github = request.form.get('github', resume.github).strip()
        resume.linkedin = request.form.get('linkedin', resume.linkedin).strip()
        resume.portfolio = request.form.get('portfolio', resume.portfolio).strip()

        if 'delete_skill_id' in request.form:
            skill_id = request.form.get('delete_skill_id')
            skill = Skill.query.get(skill_id)
            if skill and skill.form_id == resume.id:
                db.session.delete(skill)

        if 'delete_project_id' in request.form:
            project_id = request.form.get('delete_project_id')
            project = Project.query.get(project_id)
            if project and project.form_id == resume.id:
                db.session.delete(project)

        if 'delete_experience_id' in request.form:
            experience_id = request.form.get('delete_experience_id')
            experience = Experience.query.get(experience_id)
            if experience and experience.form_id == resume.id:
                db.session.delete(experience)

        for skill_id in request.form:
            if skill_id.startswith('skill_id_'):
                skill_id = int(skill_id.split('_')[2])
                skill = Skill.query.get(skill_id)
                if skill:
                    skill.name = request.form.get(f'skill_name_{skill_id}')
                    
        for project_id in request.form:
            if project_id.startswith('project_id_'):
                project_id = int(project_id.split('_')[2])
                project = Project.query.get(project_id)
                if project:
                    project.name = request.form.get(f'project_name_{project_id}')
                    project.description = request.form.get(f'project_description_{project_id}')

        for experience_id in request.form:
            if experience_id.startswith('experience_id_'):
                experience_id = int(experience_id.split('_')[2])
                experience = Experience.query.get(experience_id)
                if experience:
                    experience.title = request.form.get(f'experience_title_{experience_id}')
                    experience.company = request.form.get(f'experience_company_{experience_id}')
                    experience.description = request.form.get(f'job_description_{experience_id}')
                    experience.start_date = request.form.get(f'experience_start_date_{experience_id}')
                    experience.end_date = request.form.get(f'experience_end_date_{experience_id}')

        db.session.commit()
        flash('Resume updated successfully!', 'success')
        return redirect(url_for('view_resume', resume_id=resume.id))

    skills = resume.skills
    projects = resume.projects
    experiences = resume.experiences
    return render_template('edit_resume.html', resume=resume, skills=skills, projects=projects, experiences=experiences)


    experience = Experience.query.get_or_404(experience_id)
    db.session.delete(experience)
    db.session.commit()
    flash('Experience deleted successfully!', 'success')
    return redirect(url_for('edit_resume', resume_id=resume_id))

@app.route('/update_projects/<int:resume_id>', methods=['POST'])
@login_required
def update_projects(resume_id):
    resume = Form.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    new_project_name = request.form.get('new_project_name')
    new_project_description = request.form.get('new_project_description')
    
    if new_project_name and new_project_name.strip():
        project = Project(name=new_project_name, description=new_project_description, form_id=resume_id)
        db.session.add(project)
        db.session.commit()

    for project_id in request.form:
        if project_id.startswith('project_id_'):
            project_id = int(project_id.split('_')[2])
            project = Project.query.get(project_id)
            if project:
                project.name = request.form.get(f'project_name_{project_id}')
                project.description = request.form.get(f'project_description_{project_id}')
                db.session.commit()

    return redirect(url_for('edit_resume', resume_id=resume_id))

@app.route('/update_experiences/<int:resume_id>', methods=['POST'])
@login_required
def update_experiences(resume_id):
    resume = Form.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    new_experience_title = request.form.get('new_experience_title')
    new_experience_company = request.form.get('new_experience_company')
    new_experience_start_date = request.form.get('new_experience_start_date')
    new_experience_end_date = request.form.get('new_experience_end_date')
    
    if new_experience_title and new_experience_title.strip():
        experience = Experience(
            title=new_experience_title,
            company=new_experience_company,
            start_date=new_experience_start_date,
            end_date=new_experience_end_date,
            form_id=resume_id
        )
        db.session.add(experience)
        db.session.commit()

    for experience_id in request.form:
        if experience_id.startswith('experience_id_'):
            experience_id = int(experience_id.split('_')[2])
            experience = Experience.query.get(experience_id)
            if experience:
                experience.title = request.form.get(f'experience_title_{experience_id}')
                experience.company = request.form.get(f'experience_company_{experience_id}')
                experience.start_date = request.form.get(f'experience_start_date_{experience_id}')
                experience.end_date = request.form.get(f'experience_end_date_{experience_id}')
                db.session.commit()

    return redirect(url_for('edit_resume', resume_id=resume_id))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)