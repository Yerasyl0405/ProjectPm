import os
from datetime import datetime, timedelta
import io
from sched import scheduler

from PIL import Image
from flask_mail import Message
from flask_mail import Mail

import re
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

from io import BytesIO

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename
from flask import send_file, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.utils import secure_filename

from .auth import auth_bp,  generate_verification_code, is_email_valid, send_verification_emaill
from ..gemini import model
from ..model import Question, User, Therapist, Answer, AvailableTime, Certificates, UserCategories, TherapistCategory, \
    Booking
from .. import db, bcrypt
mail = Mail()

question_bp = Blueprint('question', __name__)

def is_valid_password(password):
    if len(password) < 8:
        return False  # Длина меньше 8 символов
    if not re.search(r"[A-Za-z]", password):
        return False  # Нет букв
    if not re.search(r"\d", password):
        return False  # Нет цифр
    return True

@question_bp.route('/question_and_registration', methods=['GET', 'POST'])
def question_and_registration():
    questions = Question.query.all()  # Получаем все вопросы
    error = session.pop('error', None)  # Извлекаем ошибку из сессии, если она есть

    if request.method == 'POST':

        # Сначала обрабатываем форму ответов на вопросы
        name = request.form.get('name')  # Имя из формы
        concerns = request.form.get('concerns')  # Концерны (если есть)
        selected_issues = request.form.getlist('issues')
        # Выбранные проблемы (множество чекбоксов)
        # Подсчёт количества выборов по категориям
        categories = {
            "What has been worrying you recently?": [
                "Panic attacks", "Stress", "Constant headaches", "Personal Fears", "Phobias", "Burnouts", "Irritations"
            ],
            "Relationships": [
                "With kids", "With partner", "Conflicts", "Getting divorced", "Personal Boundaries", "Work Colleagues",
                "Parents"
            ],
            "Crisis and Life worries": [
                "Loneliness", "Self-Esteem", "Financial crisis", "Searching the meaning of life",
                "Losing someone important"
            ],
            "Personal growth and Career goals": [
                "Procrastination", "Goals", "Lack of motivation", "Losing a job", "Searching inner peace"
            ],
            "Addictions": [
                "Addictive relationships", "Alcohol", "Gaming", "Drug addiction"
            ],
            "Perinatal psychology": [
                "Miscarriage", "Abortion", "Pregnancy planning", "Infertility", "Childbirth"
            ],
            "Psychosomatics": [
                "surgeries", "head aches", "skin", "inner illnesses", "oncology"
            ]
        }
        category_counts = {
            category: sum(1 for issue in selected_issues if issue in options)
            for category, options in categories.items()
        }

        # Топ-3 категории
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat[0] for cat in sorted_categories[:3]]

        # Проверяем, существует ли уже пользователь с таким именем

        # Теперь обрабатываем регистрацию пользователя
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        if not is_valid_password(password):
            session['error'] = "Password must be at least 8 characters long and contain both letters and numbers."
            return redirect(url_for('question.question_and_registration'))

        if not is_email_valid(email):
            session['error'] = "The provided email address is invalid or does not exist."
            return redirect(url_for('question.question_and_registration'))
        # Проверяем, существует ли уже пользователь с таким именем или email
        if User.query.filter_by(username=name).first():
            session['error'] = "Имя пользователя уже существует."
            return redirect(url_for('question.question_and_registration'))

        if User.query.filter_by(email=email).first() or Therapist.query.filter_by(email=email).first():
            session['error'] = "Этот email уже существует."
            return redirect(url_for('question.question_and_registration'))

        # Генерация кода подтверждения
        verification_code = generate_verification_code()

        # Создаем нового пользователя
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=name,
            email=email,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            verification_code=verification_code
        )
        db.session.add(new_user)
        db.session.commit()
        usercategories = UserCategories(
            user_id=new_user.id,
            category_1=top_categories[0] if len(top_categories) > 0 else None,
            category_2=top_categories[1] if len(top_categories) > 1 else None,
            category_3=top_categories[2] if len(top_categories) > 2 else None
        )
        db.session.add(usercategories)
        db.session.commit()

        # Отправляем email для подтверждения
        send_verification_emaill(email, verification_code)

        # Перенаправляем на страницу подтверждения email
        return redirect(url_for('auth.verify_email', user_id=new_user.id))

    # Если запрос GET, отображаем форму
    return render_template('question_and_registration.html', questions=questions, error=error)

@auth_bp.route('/home', methods=['GET'])
def home():
    # Get the first_name and last_name from the query parameters
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')

    return render_template('home.html', first_name=first_name, last_name=last_name)




@auth_bp.route('/therapist/<int:id>', methods=['GET', 'POST'])
def therapist_profile(id):
    therapist = Therapist.query.get_or_404(id)
    available_times = AvailableTime.query.filter_by(therapist_id=id).all()

    if request.method == 'POST':
        # Handling form submission to add a new available time
        date_str = request.form['date']
        time_str = request.form['time']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        available_time = AvailableTime(therapist_id=id, date=date, time=time_str)
        db.session.add(available_time)
        db.session.commit()
        return redirect(url_for('auth.therapist_profile', id=id))

    return render_template('therapist_profile.html', therapist=therapist, available_times=available_times)



@auth_bp.route('/therapists')
def index():
    therapists = Therapist.query.all()
    return render_template('in_user_therapists.html', therapists=therapists)

@auth_bp.route('/special')
def special():
    therapists = Therapist.query.all()
    return render_template('special.html', therapists=therapists)



@auth_bp.route('/book/<int:therapist_id>', methods=['GET', 'POST'])
def book(therapist_id):
    therapist = Therapist.query.get_or_404(therapist_id)
    user_id = session.get('user_id')  # Get user_id from session
    user = User.query.filter_by(id=user_id).first()

    # Query available times for the specific therapist
    available_times = AvailableTime.query.filter_by(
        therapist_id=therapist_id, is_available=True
    ).order_by(AvailableTime.date, AvailableTime.time).all()

    if request.method == 'POST':
        selected_time_id = request.form.get('time')  # Get the selected time ID from the form
        selected_time = AvailableTime.query.get(selected_time_id)

        if selected_time and selected_time.is_available:
            # Mark the time as unavailable
            selected_time.is_available = False
            db.session.commit()

            # Redirect to confirmation page
            return redirect(
                url_for(
                    'auth.confirm_booking',
                    therapist_id=therapist_id,
                    time=f"{selected_time.date} {selected_time.time}",
                )
            )

    return render_template(
        'booking.html', therapist=therapist, available_times=available_times
    )


from datetime import datetime


@auth_bp.route('/confirm/<int:therapist_id>/<time>')
def confirm_booking(therapist_id, time):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    # Combine date and time into a datetime object
    selected_time = datetime.strptime(time, "%Y-%m-%d %H:%M")

    # Save the booking in the database
    booking = Booking(user_id=user_id, therapist_id=therapist_id, time=selected_time)
    db.session.add(booking)
    db.session.commit()
    therapist = Therapist.query.get_or_404(therapist_id)
    send_verification_email(therapist.email)

    return render_template(
        'confirm.html',
        therapist=Therapist.query.get_or_404(therapist_id),
        time=selected_time,
        id=user_id
    )

def send_verification_email(user_email):
    msg = Message('Email Verification Code', recipients=[user_email])
    msg.body = f'You have a new booking at your slot for ${user_email} ! Please check your profile!'
    mail.send(msg)

@auth_bp.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    therapist = Therapist.query.get_or_404(id)

    if request.method == 'POST':
        # Check if an avatar file is provided
        avatar = request.files.get('avatar')

        if avatar:
            # Validate file extension
            if not allowed_file(avatar.filename):
                # Optionally, return an error message if the file type is invalid
                return "Invalid file type. Only png, jpg, jpeg, and gif are allowed.", 400

            # Secure the filename and read the image as binary data
            filename = secure_filename(avatar.filename)
            img_data = avatar.read()

            # Optionally, validate the image with PIL
            try:
                img = Image.open(io.BytesIO(img_data))
                img.verify()  # Verify that the file is a valid image
            except Exception as e:
                return f"Invalid image file: {str(e)}", 400

            # Save the image data to the database
            therapist.image = img_data
            db.session.commit()

        # Handle other form fields and save changes
        therapist.first_name = request.form['first_name']
        therapist.last_name = request.form['last_name']
        therapist.email = request.form['email']
        therapist.birthday = request.form['birthday']
        db.session.commit()

        return redirect(url_for('auth.therapist_profile', id=id))

    return render_template('edit_profile.html', therapist=therapist)


# Utility function to check allowed file types
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import send_file, abort
from io import BytesIO

@auth_bp.route('/avatar/<int:id>')
def get_avatar(id):
    # First check for therapist
    therapist = Therapist.query.filter_by(id=id).first()
    if therapist and therapist.image:
        # Serve the therapist's image
        return send_file(BytesIO(therapist.image), mimetype='image/png')

    # If not found, check for user
    user = User.query.filter_by(id=id).first()
    if user and user.avatar:
        # Serve the user's image
        return send_file(BytesIO(user.avatar), mimetype='image/png')

    # If no image is found, serve the default image
    try:
        return send_file('static/default-avatar.png', mimetype='image/png')
    except FileNotFoundError:
        abort(404, description="Default avatar image not found.")


@auth_bp.route('/check_name_availability')
def check_name_availability():
    name = request.args.get('name')

    # Query to check if the name already exists in the Answer table
    existing_answer = Answer.query.filter_by(name=name).first()

    # If we find a result, the name is taken, so we return False
    if existing_answer:
        return jsonify(isAvailable=False)
    else:
        return jsonify(isAvailable=True)





@auth_bp.route('/therapist/<int:therapist_id>/certificates', methods=['GET', 'POST'])
def manage_certificates(therapist_id):
    therapist = Therapist.query.get_or_404(therapist_id)

    if request.method == 'POST':
        file = request.files.get('certificate')
        if not file or file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        # Сохранение файла в базу данных
        new_certificate = Certificates(
            therapist_id=therapist.id,
            certificate_data=file.read(),
            filename=file.filename,
            mimetype=file.mimetype
        )
        db.session.add(new_certificate)
        db.session.commit()

        flash('Certificate uploaded successfully!')
        return redirect(url_for('auth.manage_certificates', therapist_id=therapist.id))

    certificates = therapist.certificates
    return render_template('manage_certificates.html', therapist=therapist, certificates=certificates)


@auth_bp.route('/certificate/<int:certificate_id>/download', methods=['GET'])
def download_certificate(certificate_id):
    certificate = Certificates.query.get_or_404(certificate_id)
    return send_file(
        BytesIO(certificate.certificate_data),
        download_name=certificate.filename,  # Use download_name instead of attachment_filename
        mimetype=certificate.mimetype,
        as_attachment=True
    )


@auth_bp.route('/user_profile/<int:id>')
def user_profile(id):
    therapist = User.query.get_or_404(id)


    user_categories = UserCategories.query.filter_by(user_id=therapist.id).first()
    categories = [user_categories.category_1, user_categories.category_2, user_categories.category_3]
    user_bookings = Booking.query.filter_by(user_id=id).all()


    # Find therapists whose categories match the user's categories
    recommended_therapists = db.session.query(Therapist).join(TherapistCategory).filter(
        TherapistCategory.category_name.in_(categories)
    ).all()

    if request.method == 'POST':
        # Handling form submission to add a new available time

        return redirect(url_for('auth.user_profile', id=id))

    return render_template('user_profile.html', user=therapist,user_bookings=user_bookings,
 recommended_therapists=recommended_therapists )




@auth_bp.route('/edit_user_profile/<int:id>', methods=['GET', 'POST'])
def edit_user_profile(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        # Update user information
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.username = request.form['username']
        user.email = request.form['email']
        user.birthday = request.form['birthday'] if request.form['birthday'] else None

        # Handle avatar upload
        avatar = request.files.get('avatar')
        if avatar:
            # Save avatar as binary data in the database
            avatar_data = avatar.read()  # You could also save the file to the filesystem and save the path
            user.avatar = avatar_data

        db.session.commit()
        return redirect(url_for('auth.user_profile', id=user.id))

    return render_template('edit_user_profile.html', user=user)

@auth_bp.route('/view_therapist/<int:id>')
def view_therapist(id):
    therapist = Therapist.query.get(id)
    profecia = TherapistCategory.query.filter_by(therapist_id=id).all()

    # Fetch therapist details by ID
    if not therapist:
        abort(404)  # Return a 404 page if therapist is not found
    return render_template('select_therapists.html', therapist=therapist, profecia=profecia)

@auth_bp.route('/user_view_therapist/<int:id>')
def user_view_therapist(id):
    therapist = Therapist.query.get(id)
    profecia = TherapistCategory.query.filter_by(therapist_id=id).all()
    print(profecia)


    # Fetch therapist details by ID
    if not therapist:
        abort(404)  # Return a 404 page if therapist is not found
    return render_template('therapists.html', therapist=therapist, profecia=profecia)

@auth_bp.route('/blocks')
def blocks():
    return render_template('blocks.html')

@auth_bp.route('/gemini')
def gemini():
    return render_template('index.html')  # HTML-файл будет находиться в папке "templates"

@auth_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message not provided"}), 400

        # Начало сессии чата
        chat_session = model.start_chat(history=[])

        # Получение ответа от модели
        response = chat_session.send_message(data['message'])

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    from flask import render_template
    from sqlalchemy.orm import joinedload

@auth_bp.route('/recomendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
        # Get user and their categories
        user = User.query.get(user_id)
        user_categories = UserCategories.query.filter_by(user_id=user_id).first()

        if not user or not user_categories:
            # If user or categories not found, return an error or empty recommendations
            return render_template('no_recomendations.html')

        # Get the user's selected categories
        user_categories_list = [user_categories.category_1, user_categories.category_2, user_categories.category_3]

        # Find therapists with matching categories
        recommended_therapists = []

        for category in user_categories_list:
            # Get therapists who have the same category
            therapists_with_category = TherapistCategory.query.filter_by(category_name=category).all()

            # Add therapists to recommendations list
            for therapist_category in therapists_with_category:
                therapist = Therapist.query.get(therapist_category.therapist_id)
                if therapist and therapist not in recommended_therapists:
                    recommended_therapists.append(therapist)

        # Return the list of recommended therapists
        return render_template('recomendations.html', user=user, recommended_therapists=recommended_therapists)

