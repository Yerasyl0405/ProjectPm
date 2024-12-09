from flask import Blueprint, render_template

from app.model import Therapist, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def main():
    return render_template('main.html')

@main_bp.route('/home/<int:id>')
def home(id):
    user = User.query.get_or_404(id)

    return render_template('user_profile.html', therapist=user)

