import os
import json
from flask import Flask, request, render_template
from datetime import date
from flask_mail import Mail, Message
from twilio.rest import Client

app = Flask(__name__)

# Flask-Mail კონფიგურაცია
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # თქვენი E-mail
app.config['MAIL_PASSWORD'] = 'your_password'  # თქვენი პაროლი

mail = Mail(app)

# Twilio კონფიგურაცია
account_sid = 'your_twilio_account_sid'
auth_token = 'your_twilio_auth_token'
twilio_phone_number = 'your_twilio_phone_number'
client = Client(account_sid, auth_token)

def send_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)

def send_sms(to, body):
    message = client.messages.create(
        body=body,
        from_=twilio_phone_number,
        to=to
    )

# მონაცემთა ფაილის სახელია tasks.json
filename = 'tasks.json'

# დრო
datetoday = date.today().strftime("%m_%d_%y")

# JSON ფაილის შექმნა, თუ ის არ არსებობს
if not os.path.exists(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)


def get_task_list():
    """ფართობს JSON ფაილიდან ყველა ტასკი"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_task_list(tasklist):
    """შეინახავს ახლანდელ tasklist-ს JSON ფაილში"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tasklist, f, ensure_ascii=False, indent=4)


def updatetasklist(tasklist):
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasklist, f, indent=4)

################## როუტების ფუნქცია #########################

@app.route('/')
def home():
    tasklist = get_task_list()
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
    
    tasklist = get_task_list()
    tasklist.append(new_task)
    updatetasklist(tasklist)

    # მეილისა და SMS-ის გაგზავნა
    subject = f"პროექტის დედლაინი {project}"
    body = f"მოგესალმებით {user},\n\nთქვენ მიერ შერჩეული პროექტის დედლაინი მოახლოვდა. გთხოვთ გაითვალისწინოთ, რომ პროექტზე '{project}' რეგისტრაცია სრულდება: {deadline}.\n წარმატებები!"
    
    send_email(user_email, subject, body)  # Email გაგზავნა
    send_sms(user_phone, body)  # SMS გაგზავნა

    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist), message="დედლაინი წარმატებით გაიგზავნა!")


# ტასკის წაშლა
@app.route('/deltask', methods=['GET'])
def remove_task():
    task_index = int(request.args.get('deltaskid'))
    tasklist = get_task_list()
    if 0 <= task_index < len(tasklist):
        tasklist.pop(task_index)
        save_task_list(tasklist)
    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist))

# სიის გასუფთავება
@app.route('/clear')
def clear_list():
    save_task_list([])  # სიის გასუფთავება
    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=[], l=0)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

