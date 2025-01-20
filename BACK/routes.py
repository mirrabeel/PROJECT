from my_app import app, db, Mail   
from flask import render_template, url_for, redirect, request   
from flask_mail import Message
from my_app.models import User, Project, Video
from my_app.forms import RegistrationForm, ProjectForm
from werkzeug.security import generate_password_hash, check_password_hash

mail = Mail(app) 
message = Message(app) 
video = Video(app)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():     # ვიგებთ ფორმა სწორად არის შევსებული თუ არა
        hashed_password = generate_password_hash(form.password.data, method='sha256') # პაროლის ჰეშირება
        user = User(username=form.username.data, email=form.email.data, password=hashed_password) # ახალ მომხმარებელზე ობიექტის შექმნა
        db.session.add(user)            # მომხმარებლის მონაცემების დამატება
        db.session.commit()             # მონაცემთა ბაზაში შენახვა
        return redirect(url_for('login'))  # გადამისამართება log in -ის გვერდზე
    return render_template('register.html', form=form)      # თუ ფორმა არ არის შევსებული სწორად ან პირველად იჩენს, უკან დაუბრუნდება ფორმას

# ახალი მომხმარებლის დამატება
@app.route("/add_user", methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    new_user = User(username=username, email=email, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return "User added successfully"
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"


@app.route("/create_project", methods=['GET', 'POST'])
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():  # ვიგებთ ფორმა სწორად არის შევსებული თუ არა
        project = Project(title=form.title.data, description=form.description.data)
        db.session.add(project)   # პროექტის დამატება
        db.session.commit()       # მონაცემთა ბაზაში შენახვა
        return redirect(url_for('home'))  # მთავარ გვერდზე გადამისამართება
    return render_template('create_project.html', form=form)


@app.route("/assign_project", methods=['POST'])
def assign_project():
    user_id = request.form.get('user_id')      # მომხმარებლის ID
    project_id = request.form.get('project_id')  # პროექტის ID

    user = User.query.get(user_id)  # მომხმარებელის პოვნა
    project = Project.query.get(project_id)  # პროექტის პოვნა

    if user and project:
        user.projects.append(project)  # პროექტი ემატება მომხმარებელს
        try:
            db.session.commit()  # ცვლილებების შენახვა
            return f"Project '{project.title}' assigned to {user.username} successfully!"
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
    return "User or Project not found"


#მონაცემთა ბაზის ჩანაწერების ამოღება 
@app.route("/projects")
def projects():
    active_projects = Project.query.filter(Project.status == 'active').all()
    return render_template('projects.html', projects=active_projects)




