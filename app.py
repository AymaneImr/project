from flask import Flask
from admin.models import db
from admin.models import users
from datetime import timedelta
from admin.app import app
from settings.settings import third
from channels.channel import fourth
from flask_login import LoginManager
from flask_migrate import Migrate
import os

flask_app = Flask(__name__)
flask_app.secret_key = "lovely29"
flask_app.permanent_session_lifetime = timedelta(days=1)
flask_app.app_context().push()



UPLOAD_FOLDER = 'admin/static/images/'

flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gogeta_user:NxCxcGMG5oIVJMldkOJwANoJpKPUE1Id@dpg-cmtcskqcn0vc73b9hpa0-a/gogeta'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


login_manager = LoginManager()
login_manager.init_app(flask_app)
login_manager.login_view = 'app.login'
@login_manager.user_loader
def load_user(get_id):
    return users.query.get(int(get_id))

db.init_app(flask_app)

migrate = Migrate(flask_app, db)

flask_app.register_blueprint(app, url_prefix='/admin')
flask_app.register_blueprint(third, url_prefix='/admin/settings')
flask_app.register_blueprint(fourth, url_prefix='/admin/channels')


if __name__ == "__main__":
    db.create_all()
    flask_app.run(debug=True)