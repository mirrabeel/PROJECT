import os
import json
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Secret key for session management

# File name for storing users
filename = 'users.json'

# Load user data (from JSON file)
def get_users():
    """Retrieve users from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading users from file: {e}")
        return []

# Save user data (to JSON file)
def save_users(userlist):
    """Save user list to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(userlist, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving users to file: {e}")

# Route to display the home page (with links to Sign Up and Log In)
@app.route('/')
def home():
    return render_template('home.html')

# Route to display the About page
@app.route('/about')
def about():
    return render_template('about.html')

# Route to display the Tutorials page
@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

# Route to display the Contact Us page
@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

# Route to display the Sign-Up page
@app.route('/register')
def register():
    return render_template('register.html')

# Route to handle Sign-Up form submission
@app.route('/register', methods=['POST'])
def handle_register():
    fullname = request.form['fullname']
    age = request.form['age']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Ensure passwords match
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"})

    # Hash the password
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

# Route to display the Login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route to handle Login form submission
@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form['email']
    password = request.form['password']

    users = get_users()

    # Find user by email
    user = next((u for u in users if u['email'] == email), None)

    if user and check_password_hash(user['password'], password):
        # Store user in session to keep them logged in
        session['user'] = user['email']
        return redirect(url_for('dashboard'))  # Redirect to dashboard or home page after login
    else:
        return jsonify({"success": False, "message": "Invalid credentials"})

# Route to display the dashboard after successful login
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Display the dashboard for logged-in users
    return render_template('dashboard.html', user_email=session['user'])

# Route to log out the user
@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
