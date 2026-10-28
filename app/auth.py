from flask import Blueprint, flash, redirect, render_template, request, abort
from flask import session, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
# -----------------------------------------------------------------------
from datetime import timedelta, datetime
from functools import wraps
from random import choices
from string import ascii_uppercase, ascii_lowercase, digits
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# ---------------------------------------------------------
from .exts import db
from .forms import SignUpForm, LoginForm, VerifyForm
from .models import User
from config import Config

auth = Blueprint("auth", __name__)

def not_verified(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if User.query.filter_by(id=session["current_user_id_temp"]).first(): #pyright:ignore
            abort(403)
        return function(*args, **kwargs)
    return wrapper

@auth.route("/auth/signup", methods=["GET", "POST"])
def signup():
    session["_flashes"] = []
    chars = ascii_uppercase + ascii_lowercase + digits
    if session.get("current_user_id") is None:
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password: str = generate_password_hash(request.form.get("password")) # pyright: ignore
            id = "".join(choices(chars, k=5))
            if User.query.filter_by(email=email).first() is not None:
                flash("Email already exists!", category="error")
            else:
                session["current_user_username"] = username
                session["current_user_email"] = email
                session["current_user_password"] = password
                session["current_user_id_temp"] = id
                return redirect(url_for("auth.verify", current_user_id=id))

        return render_template("signup.html", form=SignUpForm())

    else:
        return redirect("/")
    
@auth.route("/auth/login", methods=["GET", "POST"])
def login():
    session.permanent = True
    session.permanent_session_lifetime = timedelta(days=365) # pyright: ignore
    if session.get("current_user_id") is None:
        if request.method == "POST":
            email = request.form.get("email")
            password: str = request.form.get("password") # pyright: ignore
            user = User.query.filter_by(email=email).first()

            if user is not None and check_password_hash(user.password_hash, password):
                login_user(user)
                session["current_user_id"] = user.id
                return redirect(url_for("index.index_page"))

            else:
                if user is None:
                    flash("Email cannot be found!", category="error")
                else:
                    if not check_password_hash(user.password_hash, password):
                        flash("Password is incorrect!", category="error")
        return render_template("login.html", form=LoginForm())
    else:
        return redirect("/")

@auth.route("/auth/verify/<current_user_id>", methods=["GET", "POST"])
@not_verified
def verify(current_user_id):
    email = session.get("current_user_email") #pyright:ignore
    if "verification_code" not in session.keys():
        session["verification_code"] = "".join(choices(digits, k=6))
        #msg = Message("Welcome to ClassLog!", sender=Config.MAIL_USERNAME, recipients=[email])
        #msg.html = render_template("verification_email.html", code=session["verification_code"])
        #with mail.connect() as conn:
        #    conn.send(msg)
        subject = "Welcome to Spite Saver!"
        body = render_template("verification_email.html", code=session["verification_code"])
        msg = MIMEMultipart()
        msg["From"] = Config.MAIL_USERNAME #pyright:ignore
        msg["To"] = email #pyright:ignore
        msg["Subject"] = subject #pyright:ignore
        msg.attach(MIMEText(body, "html"))

        try:
            print(Config.MAIL_USERNAME, Config.MAIL_PASSWORD) #pyright:ignore
            server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD) #pyright:ignore
            server.sendmail(Config.MAIL_USERNAME, email, msg.as_string()) #pyright:ignore
            server.quit()
            session["verification_code_sent_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #pyright:ignore
        except Exception as e:
            flash("Failed to send verification email. Please try again later.", category="error")
            print(f"Error sending email: {e}")
        

    if request.method == "POST":
        verification_code = request.form.get("code")

        if verification_code == session["verification_code"]:
            session.pop("verification_code")
            username = session.get("current_user_username")
            password = session.get("current_user_password")
            if session.get("verification_code_sent_time") and (datetime.now() - datetime.strptime(session.get("verification_code_sent_time"), "%Y-%m-%d %H:%M:%S")).total_seconds() < 600: #pyright:ignore
                user = User(id=current_user_id, username=username, email=email, password_hash=password, verified=True) # pyright: ignore
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("auth.login"))
            else:
                return redirect(url_for("auth.resend_code"))

        else:
            flash("Codes don't match!")

    return render_template("verification.html", email=email, form=VerifyForm(), current_user_id=current_user_id)

@auth.route("/auth/resend-verification-code", methods=["GET", "POST"])
def resend_code():
    session.pop("verification_code", None)
    session.pop("verification_code_sent_time", None)
    return redirect(url_for("auth.verify", current_user_id=session.get("current_user_id_temp"))) #pyright:ignore

@auth.route("/auth/logout")
@login_required
def logout():
    logout_user()
    session.pop("current_user_id", None)
    return redirect(url_for("auth.login"))
