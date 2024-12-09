import os
from datetime import datetime, timedelta
from flask import current_app
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import re
from ..model import User, Question, Therapist, Answer, TherapistCategory, Booking
from .. import db, bcrypt
from flask_mail import Message
import random
import string
from flask_mail import Mail
from werkzeug.security import generate_password_hash

mail = Mail()

auth_bp = Blueprint('auth', __name__)







@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    username = request.args.get('username')  # Get the 'username' from the URL query parameters
    error = None  # Initialize error variable

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email belongs to a User or Therapist
        user = User.query.filter_by(email=email).first()
        if not user:
            user = Therapist.query.filter_by(email=email).first()

        # Validate user credentials
        if user and bcrypt.check_password_hash(user.password, password) and user.email_verified:
            session['user_id'] = user.id  # Store user ID in session
            session['user_type'] = 'User' if isinstance(user, User) else 'Therapist'  # Store user type

            if isinstance(user, User):
                # Redirect to user dashboard or first question
                return redirect(url_for('auth.user_profile', id=user.id))
            elif isinstance(user, Therapist):
                # Redirect to therapist's profile or dashboard
                return redirect(url_for('auth.therapist_profile', id=user.id))
        else:
            error = "Invalid email or password"  # Set error message

    return render_template('login.html', username=username, error=error)  # Pass error to the template


# Генерация кода подтверждения
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def is_email_valid(email):
    api_key = "b72a44e8d91f4ed8a4ef088467ff9fc8"
    url = f"https://api.zerobounce.net/v2/validate?api_key={api_key}&email={email}"

    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        return result.get('status') == 'valid'  # Проверяем статус ответа
    return False

# Отправка email с кодом подтверждения
def send_verification_emaill(user_email, verification_code):
    msg = Message('Email Verification Code', recipients=[user_email])
    msg.body = f'Your email verification code is {verification_code}. Please enter it on the verification page.'
    mail.send(msg)
# Генерация кода подтверждения
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Отправка email с кодом подтверждения
def is_valid_password(password):
    if len(password) < 8:
        return False  # Длина меньше 8 символов
    if not re.search(r"[A-Za-z]", password):
        return False  # Нет букв
    if not re.search(r"\d", password):
        return False  # Нет цифр
    return True

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        selected_categories = request.form.getlist('issues')
        if not is_valid_password(password):
            session['error'] = "Password must be at least 8 characters long and contain both letters and numbers."
            return redirect(url_for('auth.register'))

        # Проверяем, существует ли email
        if not is_email_valid(email):
            session['error'] = "The provided email address is invalid or does not exist."
            return redirect(url_for('auth.register'))

        # Проверяем, не используется ли email уже
        if User.query.filter_by(email=email).first() or Therapist.query.filter_by(email=email).first():
            session['error'] = "Email already exists."
            return redirect(url_for('auth.register'))

        # Хешируем пароль
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Генерируем код подтверждения
        verification_code = generate_verification_code()

        if user_type == 'user':
            # Регистрация как пользователь
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_password,
                verification_code=verification_code
            )
            db.session.add(new_user)
            db.session.commit()

            # Отправляем email с кодом подтверждения
            send_verification_emaill(email, verification_code)

            # Перенаправляем на страницу подтверждения email
            return redirect(url_for('auth.verify_email', user_id=new_user.id))

        elif user_type == 'therapist':
            # Регистрация как терапевт
            new_therapist = Therapist(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_password,
                verification_code=verification_code
            )
            db.session.add(new_therapist)
            db.session.commit()
            for category in selected_categories:
                therapist_category = TherapistCategory(therapist_id=new_therapist.id, category_name=category)
                db.session.add(therapist_category)

            db.session.commit()
            # Отправляем email с кодом подтверждения
            send_verification_emaill(email, verification_code)

            # Перенаправляем на страницу подтверждения email
            return redirect(url_for('auth.verify_email', user_id=new_therapist.id))

    # Получаем возможную ошибку из сессии
    error = session.pop('error', None)
    return render_template('registration.html', error=error)

@auth_bp.route('/verify_email/<int:user_id>', methods=['GET', 'POST'])
def verify_email(user_id):
    # Try to find the user or therapist
    user = User.query.get(user_id) or Therapist.query.get(user_id)

    if not user:
        return "User or Therapist not found."

    error_message = None  # Initialize error message

    if request.method == 'POST':
        entered_code = request.form['verification_code']

        if entered_code == user.verification_code:
            user.email_verified = True  # Update email verification status
            user.verification_code = None  # Remove the verification code after successful verification
            db.session.commit()
            return redirect(url_for('auth.login'))  # Redirect to login page
        else:
            error_message = "Invalid verification code. Please try again."

    return render_template('verify_email.html', user=user, error_message=error_message)



@auth_bp.after_request
def disable_cache(response):
    if request.endpoint == '/login':  # Только для страницы логина
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

@auth_bp.route("/index")
def ind():
    return render_template("index.html")




