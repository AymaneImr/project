from flask import Blueprint, request, url_for, redirect, render_template, session, flash, current_app
from admin.models import users
from admin.extensions import db
import random
from email.message import EmailMessage
import ssl
import smtplib
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid as uuid


third = Blueprint("third", __name__,template_folder="templates", static_folder="static")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# this page will contain a global user and channel setting 
# 1--> give the user the full controll of his acc 
# 2--> the user can change his 'password' and 'email' and 'username'
# 3--> user have access to delete his acc and his channel 
# 4--> user can make updates in his channel 
# 5--> user can add a phone number to his account

@third.route("/")
@login_required
def settings():
    usr = users.query.filter_by(_id=current_user._id).first()
    return render_template("settings.html", usr=usr)


@third.route("/change_password", methods=["POST", "GET"])
@login_required
def change_password():
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
    return redirect(request.referrer)

# check if the code in session so the page can't be loaded without doing all the steps 
@third.route("/verification", methods=['POST', 'GET'])
@login_required
def verification():
    if request.method == "POST":
        code1 = request.form.get("code")
        if code1 == session["veri_code"]:
            return redirect(url_for("app.confirm_pass"))
        else:
            return "<p>bro there's 2 only options,<br><br>either you are somehow blind<br>or<br> you are a damn theif(like what are you gonna achieve if u stole someone's account)</p>"
    else:
        return render_template("verification_code.html")

@third.route("/confirm_pass", methods=["POST", "GET"])
@login_required
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


@third.route("/email_verification", methods=["POST", "GET"])
@login_required
def email_verification():
    if request.method == "POST":
        email = request.form.get("email")
        confirm_email = request.form.get("confirm_email")
        password = request.form.get("password")
        correct_user = users.query.filter_by(username=current_user.username).first()
        correct_email = correct_user.email 
        correct_password = correct_user.password
        if email == correct_email:
            if email == confirm_email:
                if check_password_hash(correct_password, password):
                    return redirect(url_for("third.change_email"))
                else:
                    '''flash -> wrong password Sir'''
                    return ' wrong password Sir'
            else:
                '''flash -> it should be the same email '''
                return 'it should be the same email Sir'
        else:
            '''flash -> this is not your email Sir'''
            return "this is not your email Sir"
    else:
        return render_template("verify_email.html")


@third.route("/change_email", methods=["POST", "GET"])
@login_required
def change_email():
    if request.method == "POST":
        email = request.form.get("email")
        confirm_email = request.form.get("confirm_email")
        correct_user = users.query.filter_by(username=current_user.username).first()
        email_exist = users.query.filter(users.email == email).first()
        if not email_exist:
            if email == confirm_email:
                correct_user.email = email
                db.session.commit()
                return redirect(url_for("third.settings"))
            else:
                flash('It should be the same Email', 'error')
                return 'machi nefs email'
        else:
            '''flash -> email already taken Sir'''
            return 'email already taken Sir'
    return render_template("change_email.html")

@third.route("/change-user-info", methods=["POST", "GET"])
@login_required
def change_user_info():
    if request.method == "POST":
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        username = request.form.get("username")
        password = request.form.get("password")
        correct_user = users.query.filter_by(username=current_user.username).first()
        correct_password = correct_user.password
        username_exist = users.query.filter(users.username == username).first()
        if not username_exist:
            if check_password_hash(correct_password, password):
                correct_user.f_name = f_name  
                correct_user.l_name = l_name 
                correct_user.username = username 
                db.session.commit()
                return redirect(url_for("third.settings"))
            else:
                '''flash -> wrong password Sir'''
                return ' wrong password Sir'
        else:
            '''flash -> username already taken Sir'''
            return ' username already taken Sir'
    else:
        return render_template("user_info.html")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@third.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        usr = users.query.filter_by(_id=current_user._id).first()
        image = request.files['image']
        if image.filename == '':
            flash('no file selected', 'error')
            return redirect(request.url)
        if image and allowed_file(image.filename):
            pic_filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name))
            usr.image_profile = pic_name
            db.session.commit()
            flash('Picture added successfuly', 'success')
            return redirect(url_for('third.settings'))
    return render_template("settings.html")
