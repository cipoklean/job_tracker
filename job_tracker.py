import sqlite3
from datetime import datetime, timedelta

def setup_database():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
              (id INTEGER PRIMARY KEY,
              company TEXT,
              role TEXT,
              link TEXT,
              status TEXT,
              date_applied TEXT,
              follow_up TEXT)''')
    conn.commit()
    conn.close()

setup_database()
print("Job Tracker ready")

def add_job():
    company = input("Company name: ")
    role = input("Job role: ")
    link = input("Job link: ")
    
    date_applied = datetime.now().strftime("%Y-%m-%d")
    follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    status = "Applied"
    
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("INSERT INTO jobs (company, role, link, status, date_applied, follow_up) VALUES (?, ?, ?, ?, ?, ?)",
              (company, role, link, status, date_applied, follow_up))
    conn.commit()
    conn.close()
    
    print(f"\n Job added!")
    print(f"Follow up date: {follow_up}")

def view_jobs():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM jobs ORDER BY date_applied DESC")
    jobs = c.fetchall()
    conn.close()

    if len(jobs) == 0:
        print("\nNo jobs tracked yet! Use option 1 to add one.")
    else:
        print("\n" + "=" * 70)
        print(f"{'ID':<5} {'Company':<20} {'Role':<25} {'Status':<12} {'Follow Up'}")
        print("=" * 70)
        for job in jobs:
            print(f"{job[0]:<5} {job[1]:<20} {job[2]:<25} {job[3]:<12} {job[6]}")
        print("=" * 70)


def update_status():
    view_jobs()
    job_id = int(input("\nEnter job ID to update: "))

    print("\nSelect new status:")
    print("1. Applied")
    print("2. Interview")
    print("3. Offer")
    print("4. Rejected")

    choice = input('Enter choice: ')
    statuses = {"1": "Applied", "2": "Interview", "3": "Offer", "4": "Rejected"}
    
    if choice in statuses:
        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()
        c.execute("UPDATE jobs SET status = ? WHERE id = ?", 
                  (statuses[choice], job_id))
        conn.commit()
        conn.close()
        print(f"\n Status updated to: {statuses[choice]}")
    else:
        print(" Invalid choice!")
    
def check_followups():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE follow_up <= ? AND status = 'Applied'", (today,))
    jobs = c.fetchall()
    conn.close()

    if len(jobs) == 0:
        print("\n✅ No follow ups due today!")
    else:
        print("\n⏰ FOLLOW UPS DUE:")
        print("=" * 70)
        for job in jobs:
            print(f" {job[1]} — {job[2]}")
            print(f"   Applied: {job[5]} | Link: {job[4]}")
        print("=" * 70)
def delete_job():
    view_jobs()
    job_id = int(input("\nEnter job ID to delete: "))
    
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT company, role FROM jobs WHERE id = ?", (job_id,))
    job = c.fetchone()
    
    if job is None:
        print("Job not found!")
    else:
        confirm = input(f"Delete {job[0]} - {job[1]}? (yes/no): ")
        if confirm.lower() == "yes":
            c.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            conn.commit()
            print("Job deleted!")
        else:
            print("Cancelled!")
    conn.close()

while True:
    print("\n JOB TRACKER")
    print("1. Add a job")
    print("2. View all jobs")
    print("3. Update job status")
    print("4. Check follow ups")
    print("5. Delete a job")
    print("6. Exit")
    
    choice = input("\nEnter choice: ")
    
    if choice == "1":
        add_job()
    elif choice == "2":
        view_jobs()
    elif choice == "3":
        update_status()
    elif choice == "4":
        check_followups()
    elif choice == "5":
        delete_job()
    elif choice == "6":
        print("Goodbye!")
        break
    else:
        print("Invalid choice!")

