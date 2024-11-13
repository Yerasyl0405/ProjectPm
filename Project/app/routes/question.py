from flask import Blueprint, render_template, redirect, url_for, request
from ..model import Question
from .. import db

question_bp = Blueprint('question', __name__)

@question_bp.route('/questions/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    question = Question.query.get(question_id)
    if not question:
        return redirect(url_for('home'))

    if request.method == 'POST':
        selected_answer = request.form['answer']
        print(f'Answer for question "{question.question}" is: {selected_answer}')
        return redirect(url_for('question.question', question_id=question_id + 1))

    return render_template('question.html', question=question)
