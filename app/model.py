import string
from random import random
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user



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
    avatar = db.Column(db.LargeBinary)  # Аватар хранится как бинарные данные
    birthday = db.Column(db.Date)  # День рождения хранится как дата

    def __repr__(self):
        return f'<User {self.username}>'


class UserCategories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Связь с таблицей User
    category_1 = db.Column(db.String(255), nullable=False)
    category_2 = db.Column(db.String(255), nullable=False)
    category_3 = db.Column(db.String(255), nullable=False)

    user = db.relationship('User', backref=db.backref('categories', lazy=True))


class TherapistCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    therapist_id = db.Column(db.Integer, db.ForeignKey('therapist.id'), nullable=False)  # Связь с терапевтом
    category_name = db.Column(db.String(255), nullable=False)

    therapist = db.relationship('Therapist', backref=db.backref('categories', lazy=True))

    def __init__(self, therapist_id, category_name):
        self.therapist_id = therapist_id
        self.category_name = category_name

class Therapist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(100))
    certificate_path = db.Column(db.String(200))
    email_verified = db.Column(db.Boolean, default=False)  # Статус подтверждения email
    verification_code = db.Column(db.String(6), nullable=True)  # Код подтверждения
    image = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'<Therapist {self.first_name} {self.last_name}>'

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



class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)


    question = db.relationship('Question', backref=db.backref('answers', lazy=True))

    def __repr__(self):
        return f"<Answer {self.selected_answer} for Question {self.question_id}>"

class AvailableTime(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        therapist_id = db.Column(db.Integer, db.ForeignKey('therapist.id'), nullable=False)
        therapist = db.relationship('Therapist', backref='available_times')
        date = db.Column(db.Date, nullable=False)
        time = db.Column(db.String(5), nullable=False)  # Time in HH:MM format
        is_available = db.Column(db.Boolean, default=True)

        def __repr__(self):
            return f'<AvailableTime {self.date} {self.time}>'

class Certificates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    therapist_id = db.Column(db.Integer, db.ForeignKey('therapist.id'), nullable=False)
    certificate_data = db.Column(db.LargeBinary, nullable=False)  # Бинарные данные сертификата
    filename = db.Column(db.String(255), nullable=False)  # Имя файла для скачивания
    mimetype = db.Column(db.String(255), nullable=False)  # Тип контента (например, 'application/pdf')

    therapist = db.relationship('Therapist', backref=db.backref('certificates', lazy=True))


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    therapist_id = db.Column(db.Integer, db.ForeignKey('therapist.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)  # Combine date and time into a single field

    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    therapist = db.relationship('Therapist', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f"<Booking user_id={self.user_id}, therapist_id={self.therapist_id}, time={self.time}>"
