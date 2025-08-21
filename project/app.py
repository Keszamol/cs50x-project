from cs50 import SQL
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'XmEiudHYPl2Yu6f3w5QB'


db = SQL("sqlite:///db/database.db")


@app.route("/", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":

        username = request.form.get("username")
        if not username:
            return render_template("error.html", message="Missing Username")

        password = request.form.get("password")
        if not password:
            return render_template("error.html", message="Missing Password")

        user = db.execute("SELECT * FROM users WHERE username = ?", (username,))

        if user:
            user = user[0]

            if check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                return redirect(url_for('main'))
            else:
                return render_template("error.html", message="Invalid Password")
        else:
            return render_template("error.html", message="Username does not exist")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        username = request.form.get("username")
        if not username:
            return render_template("error.html", message="Missing Username")

        password = request.form.get("password")
        if not password:
            return render_template("error.html", message="Missing Password")

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return render_template("error.html", message="Please confirm your password")
        elif confirmation != password:
            return render_template("error.html", message="Password and confirmation not identical")

        try:

            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, generate_password_hash(password))
        except ValueError as e:

            if "UNIQUE constraint failed" in str(e):
                return render_template("error.html", message="Username already exists")
            else:

                return render_template("error.html", message="An unexpected error occurred")

        return redirect(url_for('login'))



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route("/daily", methods=["GET", "POST"])
def daily():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    username = session['username']

    if not user_id:
        return redirect(url_for('login'))
    
    timezone = pytz.timezone('Europe/Berlin')
    now = datetime.now(timezone)
    today = now.strftime('%Y-%m-%d')

    entries = db.execute("SELECT date FROM entries WHERE date = ? AND user_id = ?", today, user_id)
    
    if entries:
        return render_template("daily.html", today=entries, username=username)

    if request.method == "POST":

        mood_work = float(request.form.get("mood_work"))
        mood_family = float(request.form.get("mood_family"))
        mood_friends = float(request.form.get("mood_friends"))
        mood_selfcare = float(request.form.get("mood_selfcare"))
        gratitude = request.form.get("gratitude")
        highlight = request.form.get("highlight")

        if not mood_work and not mood_family and not mood_friends and not mood_selfcare and not gratitude and not highlight:
            return render_template("error.html", message="You need to input something.")
        
        if mood_work < 1 or mood_work > 10 or mood_family < 1 or mood_family > 10 or mood_friends < 1 or mood_friends > 10 or mood_selfcare < 1 or mood_selfcare > 10:
            return render_template("error.html", message="Dein Wert darf nur auf einer Skala von 1-10 liegen.")

        db.execute("INSERT INTO entries (user_id, date, mood_work, mood_family, mood_friends, mood_selfcare, gratitude, highlight) VALUES (?, date('now'), ?, ?, ?, ?, ?, ?)", user_id, mood_work, mood_family, mood_friends, mood_selfcare, gratitude, highlight)

        flash("Entry saved succesfully!")
        return redirect(url_for('daily'))

    return render_template("daily.html", username=username)



@app.route("/history", methods=["GET", "POST"])
def history():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get("user_id")
    username = session['username']

    if not user_id:
        return redirect(url_for("login"))

    selected_date = ''

    if request.method == "POST":
        selected_date = request.form.get("date")
        entry = db.execute("SELECT * FROM entries WHERE user_id = ? AND date = ?", user_id, selected_date)
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%d-%m-%Y')

        if entry:
            return render_template("history.html", entry=entry[0], searched=True, username=username, selected_date=selected_date)
        else:
            return render_template("history.html", entry=None, searched=True, username=username, selected_date=selected_date)

    return render_template("history.html", username=username, selected_date=selected_date)



@app.route("/main")
def main():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    username = session.get('username', '')

    return render_template("main.html", username=username)

@app.route("/statistic", methods=["GET", "POST"])
def statistic():

    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    username = session.get('username', '')

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'alltime':
            action = "Alltime"
            return alltime(user_id, username, action=action)     
        elif action == '30-days':
            action = "30 Days"
            return thirty_days(user_id, username, action=action)
        elif action == '14-days':
            action = "14 Days"
            return fourteen_days(user_id, username, action=action)
        elif action == '7-days':
            action = "7 Days"
            return seven_days(user_id, username, action=action)
        elif action == '3-days':
            action = "3 Days"
            return three_days(user_id, username, action=action)
    
    return render_template("statistic.html", username=username)


def alltime(user_id, username, action):

    sum_mood_work = db.execute("SELECT SUM(mood_work) AS mood_work_sum FROM entries WHERE user_id = ?", user_id)
    mood_work_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ?", user_id)

    mood_work_sum = sum_mood_work[0]["mood_work_sum"] if sum_mood_work[0]["mood_work_sum"] is not None else 0
    mood_work_count = mood_work_count[0]["count"]

    if mood_work_sum > 0:
        mood_work_average = mood_work_sum / mood_work_count
        mood_work_average = round(mood_work_average, 2)
    else:
        mood_work_average = "No entries found"

    sum_mood_family = db.execute("SELECT SUM(mood_family) AS mood_family_sum FROM entries WHERE user_id = ?", user_id)
    mood_family_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ?", user_id)

    mood_family_sum = sum_mood_family[0]["mood_family_sum"] if sum_mood_family[0]["mood_family_sum"] is not None else 0
    mood_family_count = mood_family_count[0]["count"]

    if mood_family_sum > 0:
        mood_family_average = mood_family_sum / mood_family_count
        mood_family_average = round(mood_family_average, 2)
    else:
        mood_family_average = "No entries found"

    sum_mood_friends = db.execute("SELECT SUM(mood_friends) AS mood_friends_sum FROM entries WHERE user_id = ?", user_id)
    mood_friends_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ?", user_id)

    mood_friends_sum = sum_mood_friends[0]["mood_friends_sum"] if sum_mood_friends[0]["mood_friends_sum"] is not None else 0
    mood_friends_count = mood_friends_count[0]["count"]

    if mood_friends_sum > 0:
        mood_friends_average = mood_friends_sum / mood_friends_count
        mood_friends_average = round(mood_friends_average, 2)
    else:
        mood_friends_average = "No entries found"

    sum_mood_selfcare = db.execute("SELECT SUM(mood_selfcare) AS mood_selfcare_sum FROM entries WHERE user_id = ?", user_id)
    mood_selfcare_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ?", user_id)

    mood_selfcare_sum = sum_mood_selfcare[0]["mood_selfcare_sum"] if sum_mood_selfcare[0]["mood_selfcare_sum"] is not None else 0
    mood_selfcare_count = mood_selfcare_count[0]["count"]

    if mood_selfcare_sum > 0:
        mood_selfcare_average = mood_selfcare_sum / mood_selfcare_count
        mood_selfcare_average = round(mood_selfcare_average, 2)
    else:
        mood_selfcare_average = "No entries found"

    return render_template("statistic.html", username=username, show_average=True, 
                           mood_work_average=mood_work_average, mood_family_average=mood_family_average, 
                           mood_friends_average=mood_friends_average, mood_selfcare_average=mood_selfcare_average, action=action)


def thirty_days(user_id, username, action):

    sum_mood_work = db.execute("SELECT SUM(mood_work) AS mood_work_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)
    mood_work_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)

    mood_work_sum = sum_mood_work[0]["mood_work_sum"] if sum_mood_work[0]["mood_work_sum"] is not None else 0
    mood_work_count = mood_work_count[0]["count"]

    if mood_work_sum > 0:
        mood_work_average = mood_work_sum / mood_work_count
        mood_work_average = round(mood_work_average, 2)
    else:
        mood_work_average = "No entries found"

    sum_mood_family = db.execute("SELECT SUM(mood_family) AS mood_family_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)
    mood_family_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)

    mood_family_sum = sum_mood_family[0]["mood_family_sum"] if sum_mood_family[0]["mood_family_sum"] is not None else 0
    mood_family_count = mood_family_count[0]["count"]

    if mood_family_sum > 0:
        mood_family_average = mood_family_sum / mood_family_count
        mood_family_average = round(mood_family_average, 2)
    else:
        mood_family_average = "No entries found"

    sum_mood_friends = db.execute("SELECT SUM(mood_friends) AS mood_friends_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)
    mood_friends_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)

    mood_friends_sum = sum_mood_friends[0]["mood_friends_sum"] if sum_mood_friends[0]["mood_friends_sum"] is not None else 0
    mood_friends_count = mood_friends_count[0]["count"]

    if mood_friends_sum > 0:
        mood_friends_average = mood_friends_sum / mood_friends_count
        mood_friends_average = round(mood_friends_average, 2)
    else:
        mood_friends_average = "No entries found"

    sum_mood_selfcare = db.execute("SELECT SUM(mood_selfcare) AS mood_selfcare_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)
    mood_selfcare_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-30 days')", user_id)

    mood_selfcare_sum = sum_mood_selfcare[0]["mood_selfcare_sum"] if sum_mood_selfcare[0]["mood_selfcare_sum"] is not None else 0
    mood_selfcare_count = mood_selfcare_count[0]["count"]

    if mood_selfcare_sum > 0:
        mood_selfcare_average = mood_selfcare_sum / mood_selfcare_count
        mood_selfcare_average = round(mood_selfcare_average, 2)
    else:
        mood_selfcare_average = "No entries found"

    return render_template("statistic.html", username=username, show_average=True, 
                           mood_work_average=mood_work_average, mood_family_average=mood_family_average, 
                           mood_friends_average=mood_friends_average, mood_selfcare_average=mood_selfcare_average, action=action)


def fourteen_days(user_id, username, action):

    sum_mood_work = db.execute("SELECT SUM(mood_work) AS mood_work_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)
    mood_work_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)

    mood_work_sum = sum_mood_work[0]["mood_work_sum"] if sum_mood_work[0]["mood_work_sum"] is not None else 0
    mood_work_count = mood_work_count[0]["count"]

    if mood_work_sum > 0:
        mood_work_average = mood_work_sum / mood_work_count
        mood_work_average = round(mood_work_average, 2)
    else:
        mood_work_average = "No entries found"

    sum_mood_family = db.execute("SELECT SUM(mood_family) AS mood_family_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)
    mood_family_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)

    mood_family_sum = sum_mood_family[0]["mood_family_sum"] if sum_mood_family[0]["mood_family_sum"] is not None else 0
    mood_family_count = mood_family_count[0]["count"]

    if mood_family_sum > 0:
        mood_family_average = mood_family_sum / mood_family_count
        mood_family_average = round(mood_family_average, 2)
    else:
        mood_family_average = "No entries found"

    sum_mood_friends = db.execute("SELECT SUM(mood_friends) AS mood_friends_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)
    mood_friends_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)

    mood_friends_sum = sum_mood_friends[0]["mood_friends_sum"] if sum_mood_friends[0]["mood_friends_sum"] is not None else 0
    mood_friends_count = mood_friends_count[0]["count"]

    if mood_friends_sum > 0:
        mood_friends_average = mood_friends_sum / mood_friends_count
        mood_friends_average = round(mood_friends_average, 2)
    else:
        mood_friends_average = "No entries found"

    sum_mood_selfcare = db.execute("SELECT SUM(mood_selfcare) AS mood_selfcare_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)
    mood_selfcare_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-14 days')", user_id)

    mood_selfcare_sum = sum_mood_selfcare[0]["mood_selfcare_sum"] if sum_mood_selfcare[0]["mood_selfcare_sum"] is not None else 0
    mood_selfcare_count = mood_selfcare_count[0]["count"]

    if mood_selfcare_sum > 0:
        mood_selfcare_average = mood_selfcare_sum / mood_selfcare_count
        mood_selfcare_average = round(mood_selfcare_average, 2)
    else:
        mood_selfcare_average = "No entries found"

    return render_template("statistic.html", username=username, show_average=True, 
                           mood_work_average=mood_work_average, mood_family_average=mood_family_average, 
                           mood_friends_average=mood_friends_average, mood_selfcare_average=mood_selfcare_average, action=action)


def seven_days(user_id, username, action):

    sum_mood_work = db.execute("SELECT SUM(mood_work) AS mood_work_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)
    mood_work_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)

    mood_work_sum = sum_mood_work[0]["mood_work_sum"] if sum_mood_work[0]["mood_work_sum"] is not None else 0
    mood_work_count = mood_work_count[0]["count"]

    if mood_work_sum > 0:
        mood_work_average = mood_work_sum / mood_work_count
        mood_work_average = round(mood_work_average, 2)
    else:
        mood_work_average = "No entries found"

    sum_mood_family = db.execute("SELECT SUM(mood_family) AS mood_family_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)
    mood_family_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)

    mood_family_sum = sum_mood_family[0]["mood_family_sum"] if sum_mood_family[0]["mood_family_sum"] is not None else 0
    mood_family_count = mood_family_count[0]["count"]

    if mood_family_sum > 0:
        mood_family_average = mood_family_sum / mood_family_count
        mood_family_average = round(mood_family_average, 2)
    else:
        mood_family_average = "No entries found"

    sum_mood_friends = db.execute("SELECT SUM(mood_friends) AS mood_friends_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)
    mood_friends_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)

    mood_friends_sum = sum_mood_friends[0]["mood_friends_sum"] if sum_mood_friends[0]["mood_friends_sum"] is not None else 0
    mood_friends_count = mood_friends_count[0]["count"]

    if mood_friends_sum > 0:
        mood_friends_average = mood_friends_sum / mood_friends_count
        mood_friends_average = round(mood_friends_average, 2)
    else:
        mood_friends_average = "No entries found"

    sum_mood_selfcare = db.execute("SELECT SUM(mood_selfcare) AS mood_selfcare_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)
    mood_selfcare_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-7 days')", user_id)

    mood_selfcare_sum = sum_mood_selfcare[0]["mood_selfcare_sum"] if sum_mood_selfcare[0]["mood_selfcare_sum"] is not None else 0
    mood_selfcare_count = mood_selfcare_count[0]["count"]

    if mood_selfcare_sum > 0:
        mood_selfcare_average = mood_selfcare_sum / mood_selfcare_count
        mood_selfcare_average = round(mood_selfcare_average, 2)
    else:
        mood_selfcare_average = "No entries found"

    return render_template("statistic.html", username=username, show_average=True, 
                           mood_work_average=mood_work_average, mood_family_average=mood_family_average, 
                           mood_friends_average=mood_friends_average, mood_selfcare_average=mood_selfcare_average, action=action)


def three_days(user_id, username, action):

    sum_mood_work = db.execute("SELECT SUM(mood_work) AS mood_work_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)
    mood_work_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)

    mood_work_sum = sum_mood_work[0]["mood_work_sum"] if sum_mood_work[0]["mood_work_sum"] is not None else 0
    mood_work_count = mood_work_count[0]["count"]

    if mood_work_sum > 0:
        mood_work_average = mood_work_sum / mood_work_count
        mood_work_average = round(mood_work_average, 2)
    else:
        mood_work_average = "No entries found"

    sum_mood_family = db.execute("SELECT SUM(mood_family) AS mood_family_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)
    mood_family_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)

    mood_family_sum = sum_mood_family[0]["mood_family_sum"] if sum_mood_family[0]["mood_family_sum"] is not None else 0
    mood_family_count = mood_family_count[0]["count"]

    if mood_family_sum > 0:
        mood_family_average = mood_family_sum / mood_family_count
        mood_family_average = round(mood_family_average, 2)
    else:
        mood_family_average = "No entries found"

    sum_mood_friends = db.execute("SELECT SUM(mood_friends) AS mood_friends_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)
    mood_friends_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)

    mood_friends_sum = sum_mood_friends[0]["mood_friends_sum"] if sum_mood_friends[0]["mood_friends_sum"] is not None else 0
    mood_friends_count = mood_friends_count[0]["count"]

    if mood_friends_sum > 0:
        mood_friends_average = mood_friends_sum / mood_friends_count
        mood_friends_average = round(mood_friends_average, 2)
    else:
        mood_friends_average = "No entries found"

    sum_mood_selfcare = db.execute("SELECT SUM(mood_selfcare) AS mood_selfcare_sum FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)
    mood_selfcare_count = db.execute("SELECT COUNT(*) AS count FROM entries WHERE user_id = ? AND date >= DATE('now', '-3 days')", user_id)

    mood_selfcare_sum = sum_mood_selfcare[0]["mood_selfcare_sum"] if sum_mood_selfcare[0]["mood_selfcare_sum"] is not None else 0
    mood_selfcare_count = mood_selfcare_count[0]["count"]

    if mood_selfcare_sum > 0:
        mood_selfcare_average = mood_selfcare_sum / mood_selfcare_count
        mood_selfcare_average = round(mood_selfcare_average, 2)
    else:
        mood_selfcare_average = "No entries found"

    return render_template("statistic.html", username=username, show_average=True, 
                           mood_work_average=mood_work_average, mood_family_average=mood_family_average, 
                           mood_friends_average=mood_friends_average, mood_selfcare_average=mood_selfcare_average, action=action) 