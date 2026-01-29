from flask import request, redirect, session
from database import get_db_connection

def add_expense():
    if "user_id" not in session:
        return redirect("/")

    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]
    description = request.form["description"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, (session["user_id"], amount, category, date, description))

    conn.commit()
    conn.close()
    return redirect("/dashboard")

def get_expenses(user_id):
    conn = get_db_connection()
    expenses = conn.execute(
        "SELECT * FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return expenses
