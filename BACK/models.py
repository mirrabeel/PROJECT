from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

userproject = db.Table('userproject',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)                       # უნიკალური იდენტიფიკატორი 
    username = db.Column(db.String(120), unique=True, nullable=False)  # მომხმარებლის სახელი, გვარი
    email = db.Column(db.String(120), unique=True, nullable=False)     # მომხმარებლის იმეილი
    password = db.Column(db.String(60), nullable=False)                # მომხმარებლის პაროლი
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)  # როდის დარეგისტრირდა მომხმარებელი

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)          # პროექტის უნიკალური იდენტიფიკატორი
    title = db.Column(db.String(120), nullable=False)     # პროექტის სათაური
    description = db.Column(db.Text, nullable=False)      # პროექტის აღწერა
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)  # როდის დაიდო პროექტი

    def __repr__(self):
        return f"Project('{self.title}', '{self.date_posted}')"   

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)                     # უნიკალური იდენტიფიკატორი
    title = db.Column(db.String(120), nullable=False)                # ვიდეოს სათაური
    url = db.Column(db.String(200), nullable=False)                  # ვიდეოს url მისამართი
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)  # როდის დაემატა ვიდეო

    def __repr__(self):
        return f"Video('{self.title}', '{self.date_uploaded}')"

