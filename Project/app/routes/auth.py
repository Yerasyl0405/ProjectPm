from flask import Blueprint, render_template, request, redirect, url_for, session
from ..model import User,Question
from .. import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            first_question = Question.query.order_by(Question.id).first()
            if first_question:
                return redirect(url_for('question', question_id=first_question.id))
            else:
                return "No questions available."
        else:
            return "Invalid username or password."
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        age = request.form['age']
        gender = request.form['gender']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        if User.query.filter_by(username=username).first():
            session['error'] = "Username already exists."
            return redirect(url_for('auth.register'))  # Corrected line to redirect to the register page in case of an error

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            age=age,
            gender=gender,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))  # Corrected line to redirect to the login page after registration

    error = session.pop('error', None)
    return render_template('registration.html', error=error)
