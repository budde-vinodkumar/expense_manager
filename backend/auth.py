from flask import request, redirect, render_template, session
from database import get_db_connection

def register_user():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("register.html", error="All fields required")

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user:
        conn.close()
        return render_template("register.html", error="Username already exists")

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )

    conn.commit()
    conn.close()
    return redirect("/")

def login_user():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()

    print("LOGIN ROUTE HIT")


    conn.close()

    if user:
        session["user_id"] = user["id"]
        return redirect("/dashboard")

    return render_template("login.html", error="Invalid login")
