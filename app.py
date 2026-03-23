from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', 
            port=int(os.environ.get('PORT', 5000)))
    
def get_jobs():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM jobs ORDER BY date_applied DESC")
    jobs = c.fetchall()
    conn.close()
    return jobs

@app.route('/')
def home():
    jobs = get_jobs()
    return render_template('index.html', jobs=jobs)

@app.route('/add', methods=['POST'])
def add_job():
    company = request.form['company']
    role = request.form['role']
    link = request.form['link']
    date_applied = datetime.now().strftime("%Y-%m-%d")
    follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    status = "Applied"

    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("INSERT INTO jobs (company, role, link, status, date_applied, follow_up) VALUES (?, ?, ?, ?, ?, ?)",
              (company, role, link, status, date_applied, follow_up))
    conn.commit()
    conn.close()

    return redirect('/')

def home():
    return render_template('index.html')

@app.route('/delete/<int:job_id>')
def delete_job(job_id):
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update/<int:job_id>', methods=['POST'])
def update_status(job_id):
    status = request.form['status']
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
