from flask import Blueprint, render_template, redirect, url_for, request, session
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
                return redirect(url_for("app.website"))
            else:
                """flash --> the password in incorrect"""
                # return redirect(request.url)
                return 'password incorrect'
        else:
            """flash --> the given informations are wrong"""
            #return redirect(request.url)
            return 'user not found'
    return render_template("log_in.html")

@app.route('/de', methods=["POST", "GET"])
def delete_data():
    all_users = users.query.all()
    db.session.delete(all_users)
    db.session.commit()

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
            return "user already exist"
        else:
            usr = users(f_name=f_name, l_name=l_name, username=username, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(usr)
            db.session.commit()
            return redirect(url_for("app.login"))
    else:
        return render_template("sign_up.html")

@app.route("/website")
@login_required
def website():
    username = current_user.username
    return render_template("index.html", username=username)

# this need to be deleted 
#create a new app.handeler that give 404 instead of that shit 
#use abort(404)

@app.route("/error404")
def error():
    return render_template("error.html")

@login_required
@app.route("/")
def logout():
    logout_user()
    if session.get('was_once_logged_in'):
        del session['was_once_logged_in']
    return redirect(url_for("app.login"))

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
            def send_code():
                email_sender = "pythonsender02@gmail.com"
                app_password = "omof nqiy kezv czrh"
                email_receiver = session["email_pass"]
                subject = "Verivication code"
                em = EmailMessage()
                em["From"] = email_sender
                em["To"] = email_receiver
                em["Subject"] = subject
                code = code_generator()
                session["veri_code"] = code
                em.set_content(code)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, app_password)
                    smtp.sendmail(email_sender, email_receiver, em.as_string())
            send_code()
            return redirect(url_for("app.verification"))
        else:
            return "email not found"
    else:
        return render_template("password.html")

@app.route("/verification", methods=['POST', 'GET'])
def verification():
    if request.method == "POST":
        code1 = request.form.get("code")
        if code1 == session["veri_code"]:
            return redirect(url_for("app.confirm_pass"))
        else:
            return "<p>bro there's 2 only options,<br><br>either you are somehow blind<br>or<br> you are a damn theif(like what are you gonna achieve if u stole someone's account)</p>"
    else:
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
            return "dude come on how old are you, you still can't memorize your new password"
    else:
        return render_template("new_pass.html")



