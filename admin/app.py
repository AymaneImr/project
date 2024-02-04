from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import random 
from email.message import EmailMessage
import ssl
import smtplib
from admin.models import users
from admin.extensions import db
from flask_login import logout_user, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Blueprint('app', __name__, static_folder='static', template_folder='templates')

'''
1 --> check if the user have an account
2 --> if the user habe an acc redirect him to the website 
3 --> else flash <user doesn't exist or the informations are wrong>
4 -->  if user found flash <welcome <username> and redirect him to the website>
'''

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                session["username"] = username
                session["password"] = password
                login_user(user, remember=True)
                return redirect(url_for("fourth.channels"))
            else:
                """flash --> the password in incorrect"""
                flash('The password is incorrect', 'error')
                return redirect(request.url)
        else:
            """flash --> the given informations are wrong"""
            flash('No such account with that name',  'error')
            return redirect(request.url)
    return render_template("log_in.html")


'''
firstly check if the user has already an acc 
secondly if user already have an acc redirect him to the login page 
    flash --> this user already has an acc 
finnaly create a new user acc and store his data
    flash --> you have created your acc seccessfuly 
redirect him to the login page
'''

@app.route("/sign_up", methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":  
        f_name = request.form["f_name"]
        l_name= request.form["l_name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        user_found = users.query.filter_by(email=email).first()
        if user_found:
            '''this user aleady has an acc'''
            flash('The email is taken')
            return redirect(request.url)
        elif users.query.filter_by(username=username).first():
            flash('The username is taken')
            return redirect(request.url)
        elif len(f_name) > 49 or len(l_name) > 49:
            flash('First/Last Name must be less than 49 characters')
            return redirect(request.url)
        elif users.query.filter_by(username=username).first():
            flash('The username is taken')
        elif len(email) > 49:
            flash('Too long email')
            return redirect(request.url)
        else:
            usr = users(f_name=f_name, l_name=l_name, username=username, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(usr)
            db.session.commit()
            return redirect(url_for("app.login"))
    else:
        return render_template("sign_up.html")


@login_required
@app.route("/")
def logout():
    logout_user()
    if session.get('was_once_logged_in'):
        del session['was_once_logged_in']
    flash('Logged out', 'info')
    return redirect(url_for("app.login"))

'''
generate code
'''

def code_generator():
    k = 0
    num_list = []
    for i in range(6):
        random_num = random.randint(0, 9)
        num_list.append(random_num)
        num_list[k] = str(random_num)
        k += 1
    verification_code = "".join(num_list)
    return verification_code

'''
send code in email
'''

def send_code(message, email):
    email_sender = "pythonsender02@gmail.com"
    app_password = "omof nqiy kezv czrh"
    email_receiver = email
    subject = "Verification Code"
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(message)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, app_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

'''
1 --> check if user exist 
    2 --> if the user exist send a code to his email and confirm the user
    3 --> if the code matchs the code sent by the system give him acces to change his current password 
    4 --> delete the old password  and save the new password in user's information 
    5 --> and then redirect the user to the login page
'''

@app.route("/backup_password", methods=["POST", "GET"])
def backup_password():
    if request.method == "POST":
        email_pass = request.form.get("email_ver")
        session["email_pass"] = email_pass
        email_found = users.query.filter_by(email=email_pass).first()
        if email_found:
            code = code_generator()
            send_code(code, email_pass)
            session["veri_code"] = code
            return redirect(url_for("app.verification"))
        else:
            flash("This email doesn't exist", 'error')
            return redirect(request.url)
    return render_template("password.html")

@app.route("/verification", methods=['POST', 'GET'])
def verification():
    if request.method == "POST":
        code1 = request.form.get("code")
        if code1 == session["veri_code"]:
            return redirect(url_for("app.confirm_pass"))
        else:
            flash('Incorrect code', 'error')
            return redirect(request.url)
    return render_template("verification_code.html")

@app.route("/confirm_pass", methods=["POST", "GET"])
def confirm_pass():
    if request.method == "POST":
        new_pass = request.form.get("new_pass1")
        confirm_pass = request.form.get("new_pass2")
        if new_pass == confirm_pass:
            admin = users.query.filter_by(email=session["email_pass"]).first()
            admin.password = confirm_pass
            db.session.commit()
            return redirect(url_for("app.login"))
        else:
            flash('Must be the same password !', 'warning')
            return redirect(request.url)
    return render_template("new_pass.html")

@app.route('/support', methods=['POST', 'GET'])
def support():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        complain = request.form.get('complain')
        content = name +  "\n" + complain 
        send_code(content, email)
        return redirect(url_for('app.login'))
    return render_template('support.html')

