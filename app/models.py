from flask import current_app
from . import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(255), index=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255),unique=True,index=True)
    bio = db.Column(db.String(255))
    profile_pic_path = db.Column(db.String())
    password_hash = db.Column(db.String(255))
    blogs = db.relationship('Blog',backref='user',lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('You cannot read the password attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f'{self.username}'

class Blog(db.Model):
    all_blogs=[]
    __tablename__='blogs'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String())
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,default=datetime.utcnow)
    user_id= db.Column(db.Integer,db.ForeignKey('users.id'))
    comments = db.relationship('Comment',backref='blog',lazy='dynamic')

    def __init__(self,title,body,user):
        self.user = user
        self.title = title
        self.body = body

    def save_blog(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_blogs(cls):
        blogs=Blog.query.all()
        return blogs

    @classmethod
    def clear_blogs(cls):
        Blog.all_blogs.clear()

class Comment(db.Model):
    all_comments=[]
    __tablename__='comments'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    comment_body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,default=datetime.utcnow)
    author_id= db.Column(db.Integer,db.ForeignKey('users.id'))
    blog_id = db.Column(db.Integer,db.ForeignKey('blogs.id'))


    def __init__(self,name,comment_body,blog):
        self.name = name
        self.comment_body = comment_body
        self.blog = blog

    def save_comment(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_comments(cls,blog_id):
        comments=Comment.query.filter_by(blog_id=blog_id).all()
        return comments

    @classmethod
    def clear_blogs(cls):
        Blog.all_blogs.clear()

class Subscribe(db.Model):
    # all_subscription = []
    __tablename__='subscribe'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(255))
    email=db.Column(db.String(255))

    def __init__(self,name,email):
        self.name = name
        self.email = email

    def save_subscriber(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_subscribers(cls):
        subscribers=Subscribe.query.all()
        return subscribers
