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
