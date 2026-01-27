from flask import Flask, render_template, session
from database import create_tables
from auth import register_user, login_user
from expense import add_expense, get_expenses

app = Flask(__name__)
app.secret_key = "secretkey"

create_tables()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post():
    return register_user()

@app.route("/login", methods=["POST"])
def login_post():
    return login_user()

@app.route("/dashboard")
def dashboard():
    expenses = get_expenses(session["user_id"])
    total = sum([e["amount"] for e in expenses])
    return render_template("dashboard.html", expenses=expenses, total=total)

@app.route("/add-expense")
def add_expense_page():
    return render_template("add_expense.html")

@app.route("/add-expense", methods=["POST"])
def add_expense_post():
    return add_expense()

if __name__ == "__main__":
    app.run(debug=True)
