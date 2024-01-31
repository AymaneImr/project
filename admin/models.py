from admin.extensions import db
from flask_login import UserMixin
from sqlalchemy.sql import func

'''
create a user database that stores his login information
'''
class users(db.Model, UserMixin):
    _id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(50), nullable=False)
    l_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    date_joined = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Post', backref='users', passive_deletes=True)
    comments = db.relationship('Comments', backref='users', passive_deletes=True)
    image_profile = db.Column(db.String(), nullable=True)
    likes = db.relationship('Like', backref='users', passive_deletes=True)
    
    def get_id(self):
        return (self._id)

class Post(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(14), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    #ondelete="CASCADE" this means that if we deleted a user all of his posts will be deleted too 
    users_id = db.Column(db.Integer, db.ForeignKey('users._id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comments', backref='post', passive_deletes=True)
    likes = db.relationship('Like', backref='post', passive_deletes=True)

class Comments(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now()) 
    users_id = db.Column(db.Integer, db.ForeignKey('users._id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post._id', ondelete="CASCADE"), nullable=False)

class Like(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey("users._id", ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post._id", ondelete="CASCADE"), nullable=False)
