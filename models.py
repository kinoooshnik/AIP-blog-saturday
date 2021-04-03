from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from hashlib import sha256

db = SQLAlchemy()


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), unique=False, nullable=False)
    body = db.Column(db.Text, unique=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('articles', lazy=True))

    def __repr__(self):
        return f"Article({self.id}, {self.title}, {self.body})"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), unique=False, nullable=False)

    def check_password(self, password):
        return self.password == sha256(password.encode("utf-8")).hexdigest()

    def set_password(self, new_password):
        self.password = sha256(new_password.encode("utf-8")).hexdigest()

    def __repr__(self):
        return f"User({self.id}, {self.username}, {self.email}, {self.password})"
