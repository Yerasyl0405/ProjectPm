from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)

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
