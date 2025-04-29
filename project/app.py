from cs50 import SQL
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

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
                return redirect(url_for('daily'))
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

    if request.method == "POST":

        mood_work = request.form.get("mood_work")
        mood_family = request.form.get("mood_family")
        mood_friends = request.form.get("mood_friends")
        mood_selfcare = request.form.get("mood_selfcare")
        gratitude = request.form.get("gratitude")
        highlight = request.form.get("highlight")

        if not mood_work and not mood_family and not mood_friends and not mood_selfcare and not gratitude and not highlight:
            return render_template("error.html", message="You need to input something.")

        db.execute("INSERT INTO entries (user_id, date, mood_work, mood_family, mood_friends, mood_selfcare, gratitude, highlight) VALUES (?, date('now'), ?, ?, ?, ?, ?, ?)", user_id, mood_work, mood_family, mood_friends, mood_selfcare, gratitude, highlight)

        flash("Eintrag erfolgreich gespeichert!")
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



@app.route("/todo", methods=["GET", "POST"])
def todo():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    username = session.get('username', '')
    PRIOR = ['Low', 'Normal', 'High']
    selected_date = ''

    if request.method == 'POST':

        selected_date = request.form.get('selected_date') or request.form.get('todo_date', '')

        action = request.form.get('action')
        todo_id = request.form.get('todo_id')

        if action == 'show':
            return show_todo(selected_date, PRIOR, username, user_id)
        elif action == 'create':
            return create_todo(username, PRIOR, selected_date, user_id)
        elif action in ('delete', 'done'):
            return delete_todo(username, PRIOR, selected_date, user_id, todo_id)

    return render_template("todo.html", username=username, prior=PRIOR, selected_date=selected_date)


def show_todo(selected_date, PRIOR, username, user_id):

    todo_list = db.execute("SELECT * FROM todos WHERE user_id = ? AND date = ?", user_id, selected_date)

    display_date = ''
    if selected_date:
        try:
            display_date = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        except ValueError:
            display_date = selected_date

    return render_template("todo.html", username=username, prior=PRIOR, todo=todo_list, selected_date=selected_date, display_date=display_date)


def create_todo(username, PRIOR, selected_date, user_id):

    title = request.form.get('title')
    description = request.form.get('description')
    todo_date = request.form.get('todo_date')
    priority = request.form.get('priority')

    if not title or not description or not todo_date or not priority:
        return render_template("error.html", message="You need to fill everything.")
    
    if priority not in PRIOR:
        return render_template("error.html", message="Wrong priority.")

    db.execute("INSERT INTO todos (user_id, date, titel, description, priority) VALUES (?, ?, ?, ?, ?)",
        user_id, todo_date, title, description, priority)

    return show_todo(todo_date, PRIOR, username, user_id)


def delete_todo(username, PRIOR, selected_date, user_id, todo_id):

    db.execute("DELETE FROM todos WHERE id = ? AND user_id = ?", todo_id, user_id)

    return show_todo(selected_date, PRIOR, username, user_id)


@app.route("/statistic", methods=["GET", "POST"])
def statistic():

    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    username = session.get('username', '')
    PRIOR = ['Low', 'Normal', 'High']

    return render_template("statistic.html", username=username)


if __name__ == "__main__":
    app.run(debug=True)

