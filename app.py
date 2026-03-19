from flask import Flask, request, jsonify, render_template, redirect, session, send_file
from datetime import datetime
import pandas as pd

from database import init_db, insert_record, get_all_records

app = Flask(__name__)
app.secret_key = "super_secret_key_2026"

# INIT DB
init_db()

students = {
    "91285723": "Abhishek",
    "1409145362": "Animesh",
    "77146475": "Nikhil"
}

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "1234":
            session['logged_in'] = True
            return redirect('/')
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# SCAN API
@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()

    uid = data.get('uid')
    name = students.get(uid, "Unknown")

    time_now = datetime.now().strftime("%H:%M:%S")
    date_now = datetime.now().strftime("%Y-%m-%d")

    insert_record(uid, name, time_now, date_now)

    return jsonify({"status": "success"})


# DATA API
@app.route('/data')
def data():
    rows = get_all_records()

    result = []
    for r in rows:
        result.append({
            "uid": r[0],
            "name": r[1],
            "time": r[2],
            "date": r[3]
        })

    return jsonify(result)


# EXPORT
@app.route('/export')
def export():
    rows = get_all_records()

    df = pd.DataFrame(rows, columns=["UID", "Name", "Time", "Date"])
    df.to_excel("attendance.xlsx", index=False)

    return send_file("attendance.xlsx", as_attachment=True)


# DASHBOARD
@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')

    return render_template("index.html")


# RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)