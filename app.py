from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import sqlite3
import os
import hashlib
from functools import wraps


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'devkey123')

def setup_database():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                (id INTEGER PRIMARY KEY,
                user_id INTEGER,
                company TEXT,
                role TEXT,
                link TEXT,
                status TEXT,
                date_applied TEXT,
                follow_up TEXT)''')
    conn.commit()
    conn.close()

with app.app_context():
    setup_database()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@login_required
def home():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE user_id = ? ORDER BY date_applied DESC", 
              (session['user_id'],))
    jobs = c.fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs, username=session['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        try:
            conn = sqlite3.connect('jobs.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, password))
            conn.commit()
            conn.close()
            return redirect('/login')
        except:
            return render_template('register.html', error="Username already exists!")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                  (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid username or password!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/add', methods=['POST'])
@login_required
def add_job():
    company = request.form['company']
    role = request.form['role']
    link = request.form['link']
    date_applied = datetime.now().strftime("%Y-%m-%d")
    follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    status = "Applied"
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("INSERT INTO jobs (user_id, company, role, link, status, date_applied, follow_up) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (session['user_id'], company, role, link, status, date_applied, follow_up))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:job_id>')
@login_required
def delete_job(job_id):
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("DELETE FROM jobs WHERE id = ? AND user_id = ?", 
              (job_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update/<int:job_id>', methods=['POST'])
@login_required
def update_status(job_id):
    status = request.form['status']
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("UPDATE jobs SET status = ? WHERE id = ? AND user_id = ?",
              (status, job_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
