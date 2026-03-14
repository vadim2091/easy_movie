from flask import Blueprint, render_template
from app.models import User, Task
from app.utils import generate_fake_rating
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Фейковый рейтинг для главной
    fake_rating = generate_fake_rating()
    # Актуальные задания для превью
    featured_tasks = Task.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html', fake_rating=fake_rating, featured_tasks=featured_tasks)

@main_bp.route('/about')
def about():
    founders = [
        {'name': 'Данила Коньков', 'role': 'Основатель, CEO'},
        {'name': 'Владислав Блинов', 'role': 'Технический директор'},
        {'name': 'Алексей Смирнов', 'role': 'Главный дизайнер'},
        {'name': 'Екатерина Воронцова', 'role': 'Руководитель отдела поддержки'}
    ]
    return render_template('about.html', founders=founders)

@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')