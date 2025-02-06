import os
import json
from flask import Flask, request, render_template, jsonify
from datetime import date, datetime, timedelta
from flask_mail import Mail, Message
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# CORS Configuration
CORS(app, origins=["http://localhost:3000"])  # Specify the frontend port

# APScheduler initialization
scheduler = BackgroundScheduler()

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'official.skillvoyage@gmail.com'  
app.config['MAIL_PASSWORD'] = 'hylw rwau bosd uray'  # Update this to be secure in a real application

mail = Mail(app)

# Twilio Configuration (fill these with your actual credentials)
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
twilio_phone_number = 'your_twilio_phone_number'
client = Client(account_sid, auth_token)

# JSON file name
filename = 'tasks.json'

# Date format
datetoday = date.today().strftime("%m_%d_%y")

# Create JSON file if it doesn't exist
if not os.path.exists(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def get_users():
    """Retrieve tasks from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_users(tasklist):
    """Save current tasklist to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tasklist, f, ensure_ascii=False, indent=4)

def updatetasklist(tasklist):
    """Update the task list"""
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasklist, f, indent=4)

################## Route Functions #########################

@app.route('/')
def home():
    tasklist = get_users()
    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist))

# Add a new task
@app.route('/addtask', methods=['POST'])
def add_task():
    user = request.form.get('user')
    project = request.form.get('project')
    deadline = request.form.get('deadline')
    user_email = request.form.get('email')  
    user_phone = request.form.get('phone')

    if not user or not project or not deadline or not user_email or not user_phone:
        return "Missing required fields", 400

    new_task = {
        "user": user,
        "project": project,
        "deadline": deadline,
        "email": user_email,
        "phone": user_phone
    }
    
    tasklist = get_users()
    tasklist.append(new_task)
    updatetasklist(tasklist)

    # Schedule email reminder 24 hours before deadline
    reminder_time = datetime.strptime(deadline, '%Y-%m-%d') - timedelta(days=1)
    reminder_time = reminder_time - timedelta(minutes=10)  # Shift by 10 minutes for faster check

    # Schedule email reminder task
    scheduler.add_job(send_reminder_email, 'date', run_date=reminder_time, args=[user_email, project, deadline])

    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist), message="Reminder set successfully!")

# Send reminder email 24 hours before deadline
def send_reminder_email(user_email, project, deadline):
    subject = f"Project Deadline for {project}"
    body = f"Hello,\n\nThe deadline for your selected project '{project}' is approaching. Please remember that the registration for the project ends on: {deadline}.\nGood luck!"
    
    send_email(user_email, subject, body)  # Send the email

def send_email(to, subject, body):
    msg = Message(subject, recipients=[to], sender='official.skillvoyage@gmail.com')
    msg.body = body
    mail.send(msg)

def send_sms(to, body):
    message = client.messages.create(
        body=body,
        from_=twilio_phone_number,
        to=to
    )

# Test email route
@app.route("/send_test_email")
def send_test_email():
    msg = Message("Hello from Flask", 
                  sender="official.skillvoyage@gmail.com",  
                  recipients=["gamgebeli.tamar.21@gmail.com"])
    msg.body = "This is a test email sent from Flask."
    mail.send(msg)
    return "Test email sent!"

# Remove a task
@app.route('/deltask', methods=['GET'])
def remove_task():
    task_index = int(request.args.get('deltaskid'))
    tasklist = get_users()
    
    if task_index >= 0 and task_index < len(tasklist):
        tasklist.pop(task_index)
        save_users(tasklist)
    else:
        return "Invalid task index", 400

    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist))

# Clear the task list
@app.route('/clear')
def clear_list():
    save_users([])  # Clear the task list
    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=[], l=0)

# User registration route
@app.route('/register', methods=['POST'])
def register():
    fullname = request.form['fullname']
    age = request.form['age']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Ensure passwords match
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"})

    # Hash password
    hashed_password = generate_password_hash(password)

    # Store user data
    user_data = {
        "fullname": fullname,
        "age": age,
        "phone": phone,
        "email": email,
        "password": hashed_password,  # Store hashed password
    }

    users = get_users()  # Retrieve users from the JSON file
    users.append(user_data)  # Add new user
    save_users(users)  # Save updated user data

    return jsonify({"success": True, "message": "Registration successful!"})

if __name__ == '__main__':
    scheduler.start()  # Start the scheduler
    app.run(debug=True, port=5001)
