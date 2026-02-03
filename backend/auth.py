from flask import request, redirect, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

# --------------------
# REGISTER
# --------------------
def register_user():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("register.html", error="All fields required")

    conn = get_db_connection()
    cursor = conn.cursor()

    existing_user = cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if existing_user:
        conn.close()
        return render_template("register.html", error="Username already exists")

    hashed_password = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed_password)
    )

    conn.commit()
    conn.close()
    return redirect("/")


# --------------------
# LOGIN
# --------------------
def login_user():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    ).fetchone()

    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        return redirect("/dashboard")

    return render_template("login.html", error="Invalid username or password")
