from flask import Blueprint, render_template

from app.model import Therapist

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def main():
    return render_template('main.html')

@main_bp.route('/home')
def home():
    return render_template('home.html')

