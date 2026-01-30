from flask import Flask, render_template, session, redirect
from database import create_tables
from auth import register_user, login_user
from expense import add_expense, get_expenses
from expense import add_expense, get_expenses, edit_expense, delete_expense


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
    return render_template("dashboard.html", expenses=[], total=0)

@app.route("/dashboard", methods=["POST"])
def dashboard_post():
    expenses = get_expenses(session["user_id"])

    total = sum(float(e["amount"]) for e in expenses)

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total=total
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



if __name__ == "__main__":
    app.run(debug=True)
