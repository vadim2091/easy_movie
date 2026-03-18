from flask_login import UserMixin
from datetime import datetime
import secrets

# ВАЖНО! ИМПОРТИРУЕМ db ИЗ __init__.py
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    google_id = db.Column(db.String(100), unique=True)
    avatar = db.Column(db.String(200), default='default.jpg')
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    balance = db.Column(db.Integer, default=0)
    hold_balance = db.Column(db.Integer, default=0)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    referral_code = db.Column(db.String(20), unique=True, default=lambda: secrets.token_urlsafe(8))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # НОВЫЕ ПОЛЯ (только те, что реально нужны)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')

    # Отношения
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))

class SupportMessage(db.Model):
    __tablename__ = 'support_messages'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_from_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('support_messages', lazy='dynamic'))

class Task(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reward = db.Column(db.Integer, nullable=False)
    
    # ВМЕСТО type ТЕПЕРЬ category_id
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    min_age = db.Column(db.Integer, default=0)
    requirements = db.Column(db.Text)
    instructions = db.Column(db.Text)
    
    # Дополнительные поля для статистики
    rating = db.Column(db.Float, default=0.0)
    completed_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с выполненными заданиями
    user_tasks = db.relationship('UserTask', backref='task_ref', lazy='dynamic')

class Task(db.Model):
    # ... существующие поля ...
    
    # Новые поля
    rating = db.Column(db.Float, default=0.0)
    completed_count = db.Column(db.Integer, default=0)

class Withdrawal(db.Model):
    __tablename__ = 'withdrawals'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='withdrawals')
    task = db.relationship('Task', backref='withdrawals')

    
def update_rating(self):
    """Обновляет рейтинг задания на основе отзывов"""
    reviews = self.reviews.all()
    if reviews:
        self.rating = sum([r.rating for r in reviews]) / len(reviews)
        self.completed_count = len(reviews)
    else:
        self.rating = 0.0
    db.session.commit()

class TaskReview(db.Model):
    __tablename__ = 'task_reviews'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ПЕРЕИМЕНОВАЛИ СВЯЗИ
    user = db.relationship('User', backref='task_reviews')  # было 'reviews'
    task = db.relationship('Task', backref='task_reviews')  # было 'reviews'
class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Дебетовые карты
    slug = db.Column(db.String(50), unique=True, nullable=False)  # debit-cards
    icon = db.Column(db.String(20), default='💳')  # эмодзи
    sort_order = db.Column(db.Integer, default=0)
    min_age = db.Column(db.Integer, default=0)  # минимальный возраст для категории
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с заданиями
    tasks = db.relationship('Task', backref='category', lazy='dynamic')

class TaskReview(db.Model):
    __tablename__ = 'task_reviews'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reviews')
    task = db.relationship('Task', backref='reviews')

class UserTask(db.Model):
    __tablename__ = 'user_tasks'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, hold, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    hold_until = db.Column(db.DateTime)

    # Связи
    user = db.relationship('User', backref=db.backref('user_tasks', lazy='dynamic'))
    task = db.relationship('Task')

class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20))
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('transactions', lazy='dynamic'))