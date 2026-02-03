from flask import request, redirect, session, render_template
from database import get_db_connection

# --------------------
# EXPENSE CRUD
# --------------------
def edit_expense(expense_id):
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()

    expense = cursor.execute(
        "SELECT * FROM expenses WHERE id=? AND user_id=?",
        (expense_id, session["user_id"])
    ).fetchone()

    if not expense:
        conn.close()
        return redirect("/dashboard")

    if request.method == "POST":
        cursor.execute("""
            UPDATE expenses
            SET amount=?, category=?, date=?, description=?
            WHERE id=? AND user_id=?
        """, (
            request.form["amount"],
            request.form["category"],
            request.form["date"],
            request.form["description"],
            expense_id,
            session["user_id"]
        ))

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
        "DELETE FROM expenses WHERE id=? AND user_id=?",
        (expense_id, session["user_id"])
    )

    conn.commit()
    conn.close()
    return redirect("/dashboard")


# --------------------
# INCOME
# --------------------
def add_income():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO income (user_id, amount, source, date)
        VALUES (?, ?, ?, ?)
    """, (
        session["user_id"],
        request.form["amount"],
        request.form["source"],
        request.form["date"]
    ))

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
    return result[0] if result and result[0] else 0


# --------------------
# EXPENSE LIST + FILTER + PAGINATION
# --------------------
def get_expenses(user_id, page=1, limit=5,
                 start_date=None, end_date=None,
                 category=None, keyword=None):

    offset = (page - 1) * limit
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM expenses WHERE user_id=?"
    params = [user_id]

    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    if category and category != "All":
        query += " AND category=?"
        params.append(category)

    if keyword:
        query += " AND description LIKE ?"
        params.append(f"%{keyword}%")

    query += " ORDER BY date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    expenses = cursor.execute(query, params).fetchall()
    conn.close()
    return expenses


def get_expense_count(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    count = cursor.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id=?",
        (user_id,)
    ).fetchone()[0]

    conn.close()
    return count


# --------------------
# BUDGET
# --------------------
def set_budget():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budget (user_id, monthly_budget)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET monthly_budget=excluded.monthly_budget
    """, (session["user_id"], request.form["amount"]))

    conn.commit()
    conn.close()
    return redirect("/dashboard")


def get_budget(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    result = cursor.execute(
        "SELECT monthly_budget FROM budget WHERE user_id=?",
        (user_id,)
    ).fetchone()

    conn.close()
    return result[0] if result else None


def get_current_month_expense(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    result = cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE user_id=?
        AND substr(date,1,7)=substr(date('now'),1,7)
    """, (user_id,)).fetchone()

    conn.close()
    return result[0] if result and result[0] else 0


# --------------------
# ANALYTICS
# --------------------
def get_monthly_expense_summary(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT substr(date,1,7) AS month, SUM(amount) AS total
        FROM expenses
        WHERE user_id=?
        GROUP BY month
        ORDER BY month
    """, (user_id,)).fetchall()

    conn.close()
    return rows


def get_monthly_income_summary(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT substr(date,1,7) AS month, SUM(amount) AS total
        FROM income
        WHERE user_id=?
        GROUP BY month
        ORDER BY month
    """, (user_id,)).fetchall()

    conn.close()
    return rows
