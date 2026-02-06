from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import send_file
from datetime import datetime

from flask import (
    Flask, render_template,
    session, redirect, request, Response
)
import csv

from database import create_tables
from auth import register_user, login_user
from expense import (
    add_expense, get_expenses,
    edit_expense, delete_expense,
    add_income, get_total_income,
    set_budget, get_budget, get_current_month_expense,
    get_monthly_expense_summary, get_monthly_income_summary
    set_category_budget,
    get_category_budgets,
    get_category_expense_current_month
)

# --------------------
# Flask App Setup
# --------------------
app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
app.secret_key = "secret123"

create_tables()

# --------------------
# Authentication
# --------------------
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    return login_user()


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    return register_user()


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# --------------------
# Dashboard
# --------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    # Expenses
    expenses = get_expenses(user_id)
    total_expense = sum(float(e["amount"]) for e in expenses)

    # Income & balance
    total_income = get_total_income(user_id)
    balance = total_income - total_expense

    # Budget logic
    budget = get_budget(user_id)
    month_expense = get_current_month_expense(user_id)
    alert = bool(budget and month_expense > budget)

    # Analytics
    monthly_expense = get_monthly_expense_summary(user_id)
    monthly_income = get_monthly_income_summary(user_id)

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total=total_expense,
        income=total_income,
        balance=balance,
        budget=budget,
        month_expense=month_expense,
        alert=alert,
        monthly_expense=monthly_expense,
        monthly_income=monthly_income
    )


# --------------------
# Expense CRUD
# --------------------
@app.route("/add-expense")
def add_expense_page():
    return render_template("add_expense.html")


@app.route("/add-expense", methods=["POST"])
def add_expense_post():
    return add_expense()


@app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense_route(expense_id):
    return edit_expense(expense_id)


@app.route("/delete-expense/<int:expense_id>")
def delete_expense_route(expense_id):
    return delete_expense(expense_id)


# --------------------
# Income
# --------------------
@app.route("/add-income")
def add_income_page():
    return render_template("add_income.html")


@app.route("/add-income", methods=["POST"])
def add_income_post():
    return add_income()


# --------------------
# Budget
# --------------------
@app.route("/set-budget", methods=["POST"])
def set_budget_post():
    return set_budget()


# --------------------
# Export CSV
# --------------------
@app.route("/export-expenses")
def export_expenses():
    if "user_id" not in session:
        return redirect("/")

    expenses = get_expenses(session["user_id"])

    def generate():
        yield "Amount,Category,Date,Description\n"
        for e in expenses:
            yield f'{e["amount"]},{e["category"]},{e["date"]},{e["description"]}\n'

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=expenses.csv"
        }
    )

@app.route("/download-report")
def download_report():
    if "user_id" not in session:
        return redirect("/")

    month = request.args.get("month")  # format: YYYY-MM
    if not month:
        return redirect("/dashboard")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    expenses = cursor.execute("""
        SELECT amount, category, date, description
        FROM expenses
        WHERE user_id=?
        AND substr(date,1,7)=?
    """, (user_id, month)).fetchall()

    income = cursor.execute("""
        SELECT SUM(amount)
        FROM income
        WHERE user_id=?
        AND substr(date,1,7)=?
    """, (user_id, month)).fetchone()[0] or 0

    total_expense = sum(float(e["amount"]) for e in expenses)
    balance = income - total_expense

    conn.close()

    # PDF creation
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Monthly Expense Report")
    y -= 30

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Month: {month}")
    y -= 20
    pdf.drawString(50, y, f"Total Income: ₹ {income}")
    y -= 20
    pdf.drawString(50, y, f"Total Expense: ₹ {total_expense}")
    y -= 20
    pdf.drawString(50, y, f"Balance: ₹ {balance}")
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Expenses:")
    y -= 20

    pdf.setFont("Helvetica", 10)

    for e in expenses:
        line = f"{e['date']} | {e['category']} | ₹{e['amount']} | {e['description']}"
        pdf.drawString(50, y, line)
        y -= 15

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 50

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"expense_report_{month}.pdf",
        mimetype="application/pdf"
    )


# --------------------
# Test Route
# --------------------
@app.route("/test")
def test():
    return "TEST PAGE WORKING"


# --------------------
# Run App
# --------------------
if __name__ == "__main__":
    app.run(debug=True)

def set_category_budget():
    if "user_id" not in session:
        return redirect("/")

    category = request.form["category"]
    limit_amount = request.form["limit"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO category_budget (user_id, category, limit_amount)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, category)
        DO UPDATE SET limit_amount=excluded.limit_amount
    """, (session["user_id"], category, limit_amount))

    conn.commit()
    conn.close()
    return redirect("/dashboard")


def get_category_budgets(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT category, limit_amount
        FROM category_budget
        WHERE user_id=?
    """, (user_id,)).fetchall()

    conn.close()
    return rows


def get_category_expense_current_month(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id=?
        AND substr(date,1,7)=substr(date('now'),1,7)
        GROUP BY category
    """, (user_id,)).fetchall()

    conn.close()
    return rows
