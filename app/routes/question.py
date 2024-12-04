import os
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, session
from werkzeug.utils import secure_filename

from .auth import auth_bp, send_verification_email
from ..model import Question, User, Therapist, Answer
from .. import db, bcrypt

question_bp = Blueprint('question', __name__)


@question_bp.route('/questions', methods=['GET', 'POST'])
def questions():
    questions = Question.query.all()  # Retrieve all questions
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('auth.login'))  # Redirect to login if no user found or session is invalid

    user = User.query.get(user_id)

    if request.method == 'POST':
        # Get the selected answers for all questions
        answers = request.form
        for question_id, selected_answer in answers.items():
            answer = Answer(user_id=user_id, question_id=question_id, selected_answer=selected_answer, email=user.email)
            db.session.add(answer)
        db.session.commit()

        return redirect(url_for('main.home', first_name=user.first_name, last_name=user.last_name))

    return render_template('question.html', questions=questions)


@auth_bp.route('/home', methods=['GET'])
def home():
    # Get the first_name and last_name from the query parameters
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')

    return render_template('home.html', first_name=first_name, last_name=last_name)




# Therapist profile page after registration
@auth_bp.route('/therapist_profile/<int:therapist_id>', methods=['GET'])
def therapist_profile(therapist_id):
    therapist = Therapist.query.get(therapist_id)
    if therapist:
        return render_template('therapist_profile.html', therapist=therapist)
    return "Therapist not found", 404


def generate_available_times(start_time="08:00", end_time="18:00", interval_minutes=30):
    times = []
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")

    current_time = start
    while current_time <= end:
        times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=interval_minutes)

    return times


@auth_bp.route('/therapists')
def index():
    therapists = Therapist.query.all()
    return render_template('therapists.html', therapists=therapists)


@auth_bp.route('/book/<int:therapist_id>', methods=['GET', 'POST'])
def book(therapist_id):
    therapist = Therapist.query.get_or_404(therapist_id)

    # Генерация доступных времен для выбора
    available_times = generate_available_times()

    if request.method == 'POST':
        send_verification_email(therapist.email, "dfdfdf")

        selected_time = request.form.get('time')
        return redirect(url_for('auth.confirm_booking', therapist_id=therapist_id, time=selected_time))

    return render_template('booking.html', therapist=therapist, available_times=available_times)


@auth_bp.route('/confirm/<int:therapist_id>/<time>')
def confirm_booking(therapist_id, time):
    therapist = Therapist.query.get_or_404(therapist_id)
    return render_template('confirm.html', therapist=therapist, time=time)