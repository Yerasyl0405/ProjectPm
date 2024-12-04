import os

from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from ..model import User, Question, Therapist, Answer
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
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email belongs to a User or Therapist
        user = User.query.filter_by(email=email).first()
        if not user:
            user = Therapist.query.filter_by(email=email).first()

        ans = Answer.query.filter_by(email=email).first()

        # If there's an Answer, redirect to home
        if ans:
            return render_template("home.html")

        # Validate user credentials
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            session['user_type'] = 'User' if isinstance(user, User) else 'Therapist'  # Store user type

            if isinstance(user, User):
                # Redirect to user dashboard or first question
                first_question = Question.query.order_by(Question.id).first()
                if first_question:
                    return redirect(url_for('question.questions', question_id=first_question.id))
                else:
                    return "No questions available."
            elif isinstance(user, Therapist):
                # Redirect to therapist's profile or dashboard
                return redirect(url_for('auth.therapist_profile', therapist_id=user.id))
        else:
            return redirect(url_for('auth.login'))

    return render_template('login.html')



# Генерация кода подтверждения
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Отправка email с кодом подтверждения
def send_verification_email(user_email, verification_code):
    msg = Message('Email Verification Code', recipients=[user_email])
    msg.body = f'Your email verification code is {verification_code}. Please enter it on the verification page.'
    mail.send(msg)
# Генерация кода подтверждения
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Отправка email с кодом подтверждения
def send_verification_email(user_email, verification_code):
    msg = Message('Email Verification Code', recipients=[user_email])
    msg.body = f'Your email verification code is {verification_code}. Please enter it on the verification page.'
    mail.send(msg)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check the user type (user or therapist)
        user_type = request.form['user_type']

        # Check if the username or email already exists
        if User.query.filter_by(username=username).first() or Therapist.query.filter_by(username=username).first():
            session['error'] = "Username already exists."

            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first() or Therapist.query.filter_by(email=email).first():
            session['error'] = "Email already exists."
            return redirect(url_for('auth.register'))

        # Generate verification code
        verification_code = generate_verification_code()

        if user_type == 'user':
            # Register as a User
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=hashed_password,
                verification_code=verification_code
            )
            db.session.add(new_user)
            db.session.commit()

            # Send verification email
            send_verification_email(email, verification_code)

            # Redirect to email verification page
            return redirect(url_for('auth.verify_email', user_id=new_user.id))

        elif user_type == 'therapist':
            # Register as a Therapist
            specialty = request.form['specialty']
            certificate = request.files['certificate']

            # Save the certificate file
            if not certificate:
                session['error'] = "Please upload a certificate."

                return redirect(url_for('auth.register'))

            upload_folder = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            certificate_path = os.path.join(upload_folder, secure_filename(certificate.filename))
            certificate.save(certificate_path)

            new_therapist = Therapist(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=hashed_password,
                specialty=specialty,
                certificate_path=certificate_path,
                verification_code=verification_code
            )
            db.session.add(new_therapist)
            db.session.commit()

            # Send verification email
            send_verification_email(email, verification_code)

            # Redirect to email verification page
            return redirect(url_for('auth.verify_email', user_id=new_therapist.id))

    error = session.pop('error', None)
    return render_template('registration.html', error=error)

@auth_bp.route('/verify_email/<int:user_id>', methods=['GET', 'POST'])
def verify_email(user_id):
    # Try to find the user or therapist
    user = User.query.get(user_id) or Therapist.query.get(user_id)

    if not user:
        return "User or Therapist not found."

    if request.method == 'POST':
        entered_code = request.form['verification_code']

        if entered_code == user.verification_code:
            user.email_verified = True  # Update email verification status
            user.verification_code = None  # Remove the verification code after successful verification
            db.session.commit()
            return redirect(url_for('auth.login'))  # Redirect to login page
        else:
            return "Invalid verification code. Please try again."

    return render_template('verify_email.html', user=user)
