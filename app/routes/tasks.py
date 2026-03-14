from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user
from app.models import Task, Category
from app import db

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks')
def tasks_list():
    # Получаем параметры из URL
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    min_age = request.args.get('min_age', type=int)
    sort = request.args.get('sort', 'newest')
    search = request.args.get('search', '')
    
    # Базовый запрос
    query = Task.query.filter_by(is_active=True)
    
    # Фильтр по категории
    if category:
        query = query.filter(Task.category.has(slug=category))
    
    # Фильтр по возрасту
    if min_age:
        query = query.filter(Task.min_age <= min_age)
    
    # Поиск по названию/описанию
    if search:
        query = query.filter(
            db.or_(
                Task.title.contains(search),
                Task.description.contains(search)
            )
        )
    
    # Сортировка
    if sort == 'price_asc':
        query = query.order_by(Task.reward.asc())
    elif sort == 'price_desc':
        query = query.order_by(Task.reward.desc())
    elif sort == 'popular':
        query = query.order_by(Task.completed_count.desc())
    elif sort == 'rating':
        query = query.order_by(Task.rating.desc())
    else:  # newest
        query = query.order_by(Task.created_at.desc())
    
    # Пагинация (20 заданий на странице)
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    tasks = pagination.items
    
    # Все категории для фильтра
    categories = Category.query.order_by(Category.sort_order).all()
    
    return render_template('tasks.html', 
                         tasks=tasks,
                         categories=categories,
                         pagination=pagination,
                         current_category=category,
                         current_min_age=min_age,
                         current_sort=sort,
                         current_search=search)

@tasks_bp.route('/tasks/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Считаем рейтинг (если есть отзывы)
    reviews = task.reviews.all() if hasattr(task, 'reviews') else []
    avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else task.rating
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'reward': task.reward,
        'category': task.category.name if task.category else 'Другое',
        'requirements': task.requirements or 'Нет особых требований',
        'instructions': task.instructions or 'Инструкция появится после взятия задания',
        'min_age': task.min_age,
        'rating': avg_rating,
        'completed': task.completed_count
    })

@tasks_bp.route('/tasks/categories')
def get_categories():
    """API для получения категорий"""
    categories = Category.query.order_by(Category.sort_order).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'slug': c.slug,
        'icon': c.icon,
        'min_age': c.min_age
    } for c in categories])