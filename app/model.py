import string
from random import random

from app import db, mail


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)

    password = db.Column(db.String(200))
    email_verified = db.Column(db.Boolean, default=False)  # Статус подтверждения email
    verification_code = db.Column(db.String(6), nullable=True)  # Код подтверждения

    def __repr__(self):
        return f'<User {self.username}>'


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    question_id = db.Column(db.Integer)
    ans = db.Column(db.String(80), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    variant_a = db.Column(db.String(255))
    variant_b = db.Column(db.String(255))
    variant_c = db.Column(db.String(255))
    variant_d = db.Column(db.String(255))
    variant_e = db.Column(db.String(255))


class Therapist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(100))
    certificate_path = db.Column(db.String(200))
    email_verified = db.Column(db.Boolean, default=False)  # Статус подтверждения email
    verification_code = db.Column(db.String(6), nullable=True)  # Код подтверждения

    def __repr__(self):
        return f'<Therapist {self.first_name} {self.last_name}>'


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))


    user = db.relationship('User', backref=db.backref('answers', lazy=True))
    question = db.relationship('Question', backref=db.backref('answers', lazy=True))

    def __repr__(self):
        return f"<Answer {self.selected_answer} for Question {self.question_id}>"