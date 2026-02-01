from flask import Flask, render_template, session, redirect
from database import create_tables
from auth import register_user, login_user
from expense import add_expense, get_expenses
from expense import add_expense, get_expenses, edit_expense, delete_expense
from expense import (
    add_expense, get_expenses,
    edit_expense, delete_expense,
    add_income, get_total_income
)



app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
app.secret_key = "secret123"

create_tables()


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

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    category = request.args.get("category")
    keyword = request.args.get("keyword")

    expenses = get_expenses(
        session["user_id"],
        start_date=start_date,
        end_date=end_date,
        category=category,
        keyword=keyword
    )

    total_expense = sum(float(e["amount"]) for e in expenses)
    total_income = get_total_income(session["user_id"])
    balance = total_income - total_expense

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total=total_expense,
        income=total_income,
        balance=balance,
        selected_category=category,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date
    )




@app.route("/add-expense")
def add_expense_page():
    return render_template("add_expense.html")

@app.route("/add-expense", methods=["POST"])
def add_expense_post():
    return add_expense()

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/test")
def test():
    return "TEST PAGE WORKING"

@app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense_route(expense_id):
    return edit_expense(expense_id)


@app.route("/delete-expense/<int:expense_id>")
def delete_expense_route(expense_id):
    return delete_expense(expense_id)

@app.route("/add-income")
def add_income_page():
    return render_template("add_income.html")

@app.route("/add-income", methods=["POST"])
def add_income_post():
    return add_income()




if __name__ == "__main__":
    app.run(debug=True)
