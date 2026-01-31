from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# -----------------------------
# CREATE FLASK APP FIRST
# -----------------------------
app = Flask(__name__)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db():
    db = sqlite3.connect("attendance.db")
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

# -----------------------------
# INITIALIZE DATABASE
# -----------------------------
def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE,
            name TEXT,
            department TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    db.commit()

# -----------------------------
# HOME ROUTE
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()

    if request.method == "POST":

        # ADD STUDENT
        if "add_student" in request.form:
            roll_no = request.form.get("roll_no")
            name = request.form.get("name")
            department = request.form.get("department")

            if roll_no and name and department:
                db.execute(
                    "INSERT OR IGNORE INTO students (roll_no, name, department) VALUES (?, ?, ?)",
                    (roll_no, name, department)
                )
                db.commit()

        # MARK ATTENDANCE
        elif "mark_attendance" in request.form:
            student_id = request.form.get("student_id")
            status = request.form.get("status")

            if student_id and status:
                db.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (?, date('now'), ?)",
                    (student_id, status)
                )
                db.commit()

        # CLEAR REPORT
        elif "clear_report" in request.form:
            db.execute("DELETE FROM attendance")
            db.commit()

        return redirect(url_for("index"))

    # FETCH DATA
    students = db.execute("SELECT * FROM students ORDER BY roll_no").fetchall()

    attendance_records = db.execute("""
        SELECT students.roll_no, students.name, students.department,
               attendance.date, attendance.status
        FROM attendance
        JOIN students ON students.id = attendance.student_id
        ORDER BY attendance.id DESC
    """).fetchall()

    return render_template(
        "index.html",
        students=students,
        attendance_records=attendance_records
    )

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
