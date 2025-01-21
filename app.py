import os
import json
from flask import Flask, request, render_template
from datetime import date

app = Flask(__name__)

# მონაცემთა ფაილის სახელია tasks.json
filename = 'tasks.json'

#დრო
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

    new_task = {
        "user": user,
        "project": project,
        "deadline": deadline
    }
    
    tasklist = get_task_list()
    tasklist.append(new_task)
    updatetasklist(tasklist)

    return render_template('home.html', datetoday=date.today().strftime("%m_%d_%y"), tasklist=tasklist, l=len(tasklist))


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

