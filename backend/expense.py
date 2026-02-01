from flask import request, redirect, session, render_template
from database import get_db_connection

def edit_expense(expense_id):
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()

    expense = cursor.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    ).fetchone()

    if not expense:
        conn.close()
        return redirect("/dashboard")

    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        description = request.form["description"]

        cursor.execute("""
            UPDATE expenses
            SET amount=?, category=?, date=?, description=?
            WHERE id=? AND user_id=?
        """, (amount, category, date, description, expense_id, session["user_id"]))

        conn.commit()
        conn.close()
        return redirect("/dashboard")

    conn.close()
    return render_template("edit_expense.html", expense=expense)


def delete_expense(expense_id):
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    )

    conn.commit()
    conn.close()
    return redirect("/dashboard")

def add_income():
    if "user_id" not in session:
        return redirect("/")

    amount = request.form["amount"]
    source = request.form["source"]
    date = request.form["date"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO income (user_id, amount, source, date)
        VALUES (?, ?, ?, ?)
    """, (session["user_id"], amount, source, date))

    conn.commit()
    conn.close()
    return redirect("/dashboard")


def get_total_income(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    result = cursor.execute(
        "SELECT SUM(amount) FROM income WHERE user_id=?",
        (user_id,)
    ).fetchone()

    conn.close()
    return result[0] if result[0] else 0

def get_expenses(user_id, start_date=None, end_date=None, category=None, keyword=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]

    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if keyword:
        query += " AND description LIKE ?"
        params.append(f"%{keyword}%")

    query += " ORDER BY date DESC"

    expenses = cursor.execute(query, params).fetchall()
    conn.close()
    return expenses
