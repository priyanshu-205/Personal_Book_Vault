from core.extensions import db, bcrypt, login_manager
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, current_user
from auth.models_user import User

auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/", methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("books.home_page"))
        else:
            return render_template("login_page.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:  ## to check if such a user exists
            flash("Invalid username or password")
            return render_template("login_page.html")
        elif bcrypt.check_password_hash(existing_user.password, password):
            #   create session for the user if log in successfull
            login_user(existing_user, remember=True)
            flash("Login Sucessfull")
            return redirect(url_for("books.home_page"))
        else:  ## if the user exists but the password is wrong
            flash("Invalid username or password")
            return render_template("login_page.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup_page.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken")
            return render_template("signup_page.html")
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.")
        return redirect(url_for("auth.login_page"))
