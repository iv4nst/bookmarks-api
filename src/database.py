from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship('Bookmark', backref='user')

    def __repr__(self) -> str:
        return f'User >>> {self.username}'


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.short_url = self.generate_short_chars()

    def __repr__(self) -> str:
        return f'Bookmark >>> {self.url}'

    def generate_short_chars(self) -> str:
        """
        Create short characters for url using all digits and ascii letters (lower & upper case)
        :return: shortened url
        """
        chars = string.digits + string.ascii_letters  # all digits and letters
        picked_chars = ''.join(random.choices(chars, k=3))  # get 3 random keys from chars

        link = self.query.filter_by(short_url=picked_chars).first()
        # if link exists
        if link:
            self.generate_short_chars()  # repeat generating if exists
        else:
            return picked_chars
