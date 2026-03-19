from flask import Flask, request, jsonify, render_template, redirect, session, send_file
from datetime import datetime
import pandas as pd
import os
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = "my_super_secret_key_2026"

app.wsgi_app = ProxyFix(app.wsgi_app)

attendance = []

students = {
    "91285723": "Abhishek",
    "1409145362": "Animesh",
    "77146475": "Nikhil"
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['password'] == "1234":
            session['logged_in'] = True
            return redirect('/')
        else:
            error = "Invalid login"
    return render_template("login.html", error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    uid = data.get('uid')

    name = students.get(uid, "Unknown")

    for record in attendance:
        if record["uid"] == uid:
            return jsonify({"status": "already marked"})

    record = {
        "uid": uid,
        "name": name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    attendance.append(record)
    return jsonify({"status": "success", "data": record})


@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template("index.html", data=attendance, total=len(attendance))


@app.route('/export')
def export():
    if not attendance:
        return "No data"

    df = pd.DataFrame(attendance)
    file = "attendance.xlsx"
    df.to_excel(file, index=False)

    return send_file(file, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))