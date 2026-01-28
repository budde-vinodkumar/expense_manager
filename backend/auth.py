from flask import request, redirect, render_template
from database import get_db_connection

def register_user():
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    # Basic validation
    if not username or not password:
        return render_template("register.html", error="All fields are required")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    existing_user = cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if existing_user:
        conn.close()
        return render_template("register.html", error="Username already exists")

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )

    conn.commit()
    conn.close()

    return redirect("/")
