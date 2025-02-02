from flask import Flask, request, jsonify, g, session, redirect, url_for, render_template
import sqlite3
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
import webview
from threading import Thread, Event
import sys
import logging
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
bcrypt = Bcrypt(app)
scheduler = APScheduler()  # Initialize the scheduler

DATABASE = os.path.join(os.path.dirname(__file__), 'homework.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                description TEXT,
                due_date DATE NOT NULL,
                due_time TEXT,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        db.commit()

create_tables()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    search_query = request.args.get('search')
    sort_by = request.args.get('sort_by', 'due_date, due_time')
    db = get_db()
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    order_clause = f"ORDER BY {sort_by} ASC"

    if search_query:
        assignments = db.execute(f'''
            SELECT * FROM assignments
            WHERE user_id = ? AND (subject LIKE ? OR description LIKE ?)
            {order_clause}
        ''', (user_id, f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        assignments = db.execute(f'''
            SELECT * FROM assignments
            WHERE user_id = ?
            {order_clause}
        ''', (user_id,)).fetchall()

    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    # Get the current date and time
    current_datetime = datetime.now()
    current_date = current_datetime.date()

    # Convert assignments to a list of dictionaries and calculate status
    assignments_list = []
    for assignment in assignments:
        # Adjusted the due time format if it's missing seconds
        due_datetime = datetime.strptime(assignment['due_date'] + ' ' + assignment['due_time'], '%Y-%m-%d %H:%M')
        due_date = due_datetime.date()
        
        # Calculate time left
        time_left = (due_datetime - current_datetime)
        days_left = time_left.days
        hours_left, seconds = divmod(time_left.seconds, 3600)
        minutes_left, _ = divmod(seconds, 60)

        # Determine assignment status
        if days_left == 0 and hours_left >= 0:  # Due today
            status = f"Due in {hours_left} hours and {minutes_left} minutes"
        elif days_left == 1:
            status = f"Due in {hours_left} hours and {minutes_left} minutes"
        elif days_left < 0:
            status = f"Overdue by {-days_left} days"
        else:
            status = f"Due in {days_left} days"

        assignments_list.append({
            'id': assignment['id'],
            'subject': assignment['subject'],
            'description': assignment['description'],
            'due_date': due_date,
            'due_time': assignment['due_time'],
            'completed': assignment['completed'],
            'status': status  # Include status in the dictionary
        })

    return render_template('index.html', user=user, assignments=assignments_list, current_date=current_date)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        db = get_db()
        try:
            # Insert the new user into the database
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already exists.")
        except Exception as e:
            db.rollback()  # Rollback on error
            logging.error(f"Error creating user: {e}")
            return render_template('register.html', error="An error occurred during registration.")
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add_assignment', methods=['POST'])
def add_assignment():
    subject = request.form['subject']
    description = request.form['description']
    due_date = request.form['due_date']
    due_time = request.form['due_time']
    user_id = session['user_id']
    
    db = get_db()
    db.execute('INSERT INTO assignments (user_id, subject, description, due_date, due_time) VALUES (?, ?, ?, ?, ?)', (user_id, subject, description, due_date, due_time))
    db.commit()
    
    return redirect(url_for('index'))

@app.route('/toggle_status', methods=['POST'])
def toggle_status():
    data = request.get_json()
    assignment_id = data['id']
    new_status = data['status'] == 'completed'
    
    db = get_db()
    db.execute('UPDATE assignments SET completed = ? WHERE id = ?', (new_status, assignment_id))
    db.commit()
    
    return jsonify(success=True)

@app.route('/edit_assignment', methods=['POST'])
def edit_assignment():
    assignment_id = request.form['id']
    subject = request.form['subject']
    description = request.form['description']
    due_date = request.form['due_date']
    due_time = request.form['due_time']
    
    db = get_db()
    db.execute('UPDATE assignments SET subject = ?, description = ?, due_date = ? , due_time = ? WHERE id = ?', (subject, description, due_date, due_time, assignment_id))
    db.commit()
    
    return redirect(url_for('index'))

@app.route('/delete_assignment', methods=['POST'])
def delete_assignment():
    data = request.get_json()
    assignment_id = data['id']
    
    db = get_db()
    db.execute('DELETE FROM assignments WHERE id = ?', (assignment_id,))
    db.commit()
    
    return jsonify(success=True)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    message = None
    message_type = None

    if request.method == 'POST':
        new_username = request.form.get('username', None)
        new_password = request.form.get('password', None)
        new_email = request.form.get('email', None)
        success = True
        
        try:
            if new_username:
                db.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
            if new_password:
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed_password, user_id))
            if new_email:
                db.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, user_id))
            
            db.commit()
            message = "Your settings have been updated successfully."
            message_type = "success"
        except Exception as e:
            db.rollback()
            logging.error(f"Error updating settings: {e}")
            message = "An error occurred while updating your settings."
            message_type = "error"

    return render_template('settings.html', user=user, message=message, message_type=message_type)

def run_flask_app():
    print("Starting Flask server...")
    app.run(port=5000, debug=True, use_reloader=False)

def start_webview():
    try:
        # Create a window with the desired properties
        webview.create_window('Homework Tracker', 'http://localhost:5000', resizable=True, width=1920, height=1080)
        
        # Start the webview
        webview.start()
    except KeyboardInterrupt:
        print("Webview interrupted.")

if __name__ == '__main__':
    # Run Flask app in a separate thread
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    # Create and start webview window
    start_webview()

    # Ensure Flask thread shuts down properly
    flask_thread.join()
