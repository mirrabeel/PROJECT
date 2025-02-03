import os
import json
from flask import Flask, request, render_template, jsonify
from datetime import date, datetime, timedelta
from flask_mail import Mail, Message
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS

app = Flask(__name__)

# CORS-ის კონფიგურაცია
CORS(app, origins=["http://localhost:3000"])  # მიუთითე აქ frontend-ის პორტი

# APScheduler-ის ინიციალიზაცია
scheduler = BackgroundScheduler()

# Flask-Mail კონფიგურაცია
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'official.skillvoyage@gmail.com'  
app.config['MAIL_PASSWORD'] = 'hylw rwau bosd uray'  

mail = Mail(app)

# Twilio კონფიგურაცია
account_sid = ''
auth_token = ''
twilio_phone_number = ''
client = Client(account_sid, auth_token)

# JSON ფაილის სახელია tasks.json
filename = 'tasks.json'

# დრო
datetoday = date.today().strftime("%m_%d_%y")

# JSON ფაილის შექმნა, თუ ის არ არსებობს
if not os.path.exists(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)


def get_users():
    """ფართობს JSON ფაილიდან ყველა ტასკი"""
    if os.path.exists():
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_users(tasklist):
    """შეინახავს ახლანდელ tasklist-ს JSON ფაილში"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tasklist, f, ensure_ascii=False, indent=4)


def updatetasklist(tasklist):
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasklist, f, indent=4)

################## როუტების ფუნქცია #########################

@app.route('/')
def home():
    tasklist = get_users()
    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist))

# ახალი ტასკის დამატება
@app.route('/addtask', methods=['POST'])
def add_task():
    user = request.form.get('user')
    project = request.form.get('project')
    deadline = request.form.get('deadline')
    user_email = request.form.get('email')  # დაამატეთ email
    user_phone = request.form.get('phone')  # დაამატეთ phone

    new_task = {
        "user": user,
        "project": project,
        "deadline": deadline,
        "email": user_email,  # Email-ის დამატება
        "phone": user_phone   # ტელეფონის ნომრის დამატება
    }
    
    tasklist = get_users()
    tasklist.append(new_task)
    updatetasklist(tasklist)

    # 24 საათით ადრე გაგზავნის დროს შეგვიძლია დავაყენოთ
    reminder_time = datetime.strptime(deadline, '%Y-%m-%d') - timedelta(days=1)
    # დროის გადაწევა, რომ შემოწმება მოხდეს უფრო სწრაფად
    reminder_time = reminder_time - timedelta(minutes=10)  

    # დაგეგმეთ მეილის გაგზავნა
    scheduler.add_job(send_reminder_email, 'date', run_date=reminder_time, args=[user_email, project, deadline])

    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist), message="დედლაინი წარმატებით გაიგზავნა!")

# 24 საათით ადრე ელექტრონული ფოსტის გაგზავნა
def send_reminder_email(user_email, project, deadline):
    subject = f"პროექტის დედლაინი {project}"
    body = f"მოგესალმებით,\n\nთქვენ მიერ შერჩეული პროექტის დედლაინი მოახლოვდა. გთხოვთ გაითვალისწინოთ, რომ პროექტზე '{project}' რეგისტრაცია სრულდება: {deadline}.\n წარმატებები!"
    
    send_email(user_email, subject, body)  # Email გაგზავნა

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

# ტესტის ელ-ფოსტა
@app.route("/send_test_email")
def send_test_email():
    msg = Message("Hello from Flask", 
                  sender="official.skillvoyage@gmail.com",  
                  recipients=["gamgebeli.tamar.21@gmail.com"])
    msg.body = "This is a test email sent from Flask."
    mail.send(msg)
    return "Test email sent!"

# ტასკის წაშლა
@app.route('/deltask', methods=['GET'])
def remove_task():
    task_index = int(request.args.get('deltaskid'))
    tasklist = get_users()
    if 0 <= task_index < len(tasklist):
        tasklist.pop(task_index)
        save_users(tasklist)
    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist))

# სიის გასუფთავება
@app.route('/clear')
def clear_list():
    save_users([])  # სიის გასუფთავება
    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=[], l=0)

@app.route('/register', methods=['POST'])
def register():
    fullname = request.form['fullname']
    age = request.form['age']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    # დაჟინებული შემოწმება, რომ პაროლები ემთხვევა
    if password != confirm_password:
        return jsonify({"success": False, "message": "პაროლები არ ემთხვევა"})

    # პაროლის ჰეშირება
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(password)

    # მომხმარებლის მონაცემების შენახვა
    user_data = {
        "fullname": fullname,
        "age": age,
        "phone": phone,
        "email": email,
        "password": hashed_password,  # პაროლი ჰეშირებულია
    }

    # JSON ფაილში შენახვა
    users = get_users()  # მიიღეთ ყველა მომხმარებელი JSON ფაილიდან
    users.append(user_data)  # დაამატეთ ახალი მომხმარებელი
    save_users(users)  # შეინახეთ განახლებული მონაცემები

    return jsonify({"success": True, "message": "რეგისტრაცია წარმატებით განხორციელდა!"})

if __name__ == '__main__':
    scheduler.start()  # APScheduler-ის დაწყება
    app.run(debug=True, port=5001)


