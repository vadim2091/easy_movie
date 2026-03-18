from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from datetime import datetime, timedelta

# Защита админки - только для админов
class AdminSecureView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    
    # Настройки внешнего вида
    can_view_details = True
    create_modal = True
    edit_modal = True
    can_export = True
    page_size = 50

# Кастомная главная админки с реальной статистикой
class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.is_admin):
            return redirect(url_for('auth.login'))
        
        # Импортируем внутри функции
        from app import db
        from app.models import User, Task, UserTask, Transaction
        
        # РЕАЛЬНАЯ СТАТИСТИКА
        total_users = User.query.count()
        total_tasks = Task.query.count()
        total_completed = UserTask.query.filter_by(status='approved').count()
        total_pending = UserTask.query.filter_by(status='pending').count()
        total_hold = UserTask.query.filter_by(status='hold').count()
        
        # Сумма всех выплаченных мандаринов
        total_mandarin_paid = db.session.query(db.func.sum(Transaction.amount))\
            .filter(Transaction.type == 'task_reward').scalar() or 0
        
        # Последние пользователи
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        
        # Последние задания
        recent_tasks = UserTask.query\
            .order_by(UserTask.created_at.desc())\
            .limit(10)\
            .all()
        
        # Топ пользователей по балансу
        top_users = User.query.order_by(User.balance.desc()).limit(5).all()
        
        # Статистика по дням
        dates = []
        counts = []
        for i in range(6, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            count = UserTask.query.filter(
                db.func.date(UserTask.created_at) == date
            ).count()
            dates.append(date.strftime('%d.%m'))
            counts.append(count)
        
        return self.render('admin/dashboard.html',
            total_users=total_users,
            total_tasks=total_tasks,
            total_completed=total_completed,
            total_pending=total_pending,
            total_hold=total_hold,
            total_mandarin_paid=total_mandarin_paid,
            recent_users=recent_users,
            recent_tasks=recent_tasks,
            top_users=top_users,
            chart_dates=dates,
            chart_counts=counts
        )

# Класс для пользователей
class UserAdmin(AdminSecureView):
    column_list = ['id', 'username', 'email', 'balance', 'hold_balance', 'is_admin', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['is_admin', 'created_at']
    column_editable_list = ['balance', 'hold_balance', 'is_admin']
    form_columns = ['username', 'email', 'balance', 'hold_balance', 'is_admin', 'birth_date', 'phone']
    
    column_labels = {
        'id': 'ID',
        'username': 'Имя',
        'email': 'Email',
        'balance': 'Баланс',
        'hold_balance': 'Холд',
        'is_admin': 'Админ',
        'created_at': 'Дата'
    }
    
    column_formatters = {
        'created_at': lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-',
        'balance': lambda v, c, m, p: f'{m.balance} 🍊' if m.balance else '0 🍊',
        'hold_balance': lambda v, c, m, p: f'{m.hold_balance} 🍊' if m.hold_balance else '0 🍊',
        'is_admin': lambda v, c, m, p: '✅' if m.is_admin else '❌'
    }

# Класс для заданий
class TaskAdmin(AdminSecureView):
    column_list = ['id', 'title', 'reward', 'type', 'min_age', 'is_active', 'created_at']
    column_searchable_list = ['title']
    column_filters = ['type', 'min_age', 'is_active']
    column_editable_list = ['reward', 'is_active']
    form_columns = ['title', 'description', 'reward', 'type', 'min_age', 'requirements', 'instructions', 'is_active']
    
    column_labels = {
        'id': 'ID',
        'title': 'Название',
        'reward': 'Награда',
        'type': 'Тип',
        'min_age': 'Возраст',
        'is_active': 'Активно',
        'created_at': 'Дата'
    }
    
    column_formatters = {
        'reward': lambda v, c, m, p: f'{m.reward} 🍊',
        'min_age': lambda v, c, m, p: f'{m.min_age}+' if m.min_age else '0+',
        'is_active': lambda v, c, m, p: '✅' if m.is_active else '❌',
        'type': lambda v, c, m, p: {
            'debit': '💳 Дебетовая',
            'credit': '💳 Кредитная',
            'vacancy': '🚚 Вакансия',
            'rko': '🏢 РКО',
            'ip': '💼 ИП'
        }.get(m.type, m.type)
    }

# Класс для выполненных заданий
class UserTaskAdmin(AdminSecureView):
    column_list = ['id', 'user', 'task', 'status', 'created_at', 'approved_at']
    column_searchable_list = ['user.username', 'task.title']
    column_filters = ['status']
    column_editable_list = ['status']
    
    column_labels = {
        'id': 'ID',
        'user': 'Пользователь',
        'task': 'Задание',
        'status': 'Статус',
        'created_at': 'Взято',
        'approved_at': 'Подтверждено'
    }
    
    column_formatters = {
        'user': lambda v, c, m, p: m.user.username if m.user else '-',
        'task': lambda v, c, m, p: m.task.title if m.task else '-',
        'status': lambda v, c, m, p: {
            'pending': '⏳ Ожидает',
            'hold': '💰 На холде',
            'approved': '✅ Выполнено',
            'rejected': '❌ Отказ'
        }.get(m.status, m.status),
        'created_at': lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-',
        'approved_at': lambda v, c, m, p: m.approved_at.strftime('%d.%m.%Y %H:%M') if m.approved_at else '-'
    }

# Класс для транзакций
class TransactionAdmin(AdminSecureView):
    column_list = ['id', 'user', 'amount', 'type', 'description', 'created_at']
    column_searchable_list = ['user.username', 'description']
    column_filters = ['type', 'created_at']
    
    column_labels = {
        'id': 'ID',
        'user': 'Пользователь',
        'amount': 'Сумма',
        'type': 'Тип',
        'description': 'Описание',
        'created_at': 'Дата'
    }
    
    column_formatters = {
        'user': lambda v, c, m, p: m.user.username if m.user else '-',
        'amount': lambda v, c, m, p: f'+{m.amount} 🍊' if m.amount > 0 else f'{m.amount} 🍊',
        'type': lambda v, c, m, p: {
            'task_reward': '🎯 Задание',
            'referral_bonus': '👥 Реферал',
            'withdrawal': '💸 Вывод'
        }.get(m.type, m.type),
        'created_at': lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-'
    }
class WithdrawalAdmin(AdminSecureView):
    column_list = ['id', 'user', 'amount', 'task', 'status', 'created_at']
    column_searchable_list = ['user.username']
    column_filters = ['status']
    column_editable_list = ['status']
    
    column_formatters = {
        'user': lambda v, c, m, p: m.user.username if m.user else '-',
        'task': lambda v, c, m, p: m.task.title if m.task else 'Вывод',
        'status': lambda v, c, m, p: {
            'pending': '⏳ Ожидает',
            'approved': '✅ Одобрено',
            'rejected': '❌ Отказ'
        }.get(m.status, m.status)
    }
    
    # Действие для одобрения вывода
    def approve_withdrawal(self, ids):
        for id in ids:
            withdrawal = Withdrawal.query.get(id)
            if withdrawal and withdrawal.status == 'pending':
                withdrawal.status = 'approved'
                withdrawal.approved_at = datetime.utcnow()
                db.session.commit()
    
    column_actions_list = [('approve', 'Одобрить')]
    
# Инициализация админки
def init_admin(app):
    from app.models import User, Task, UserTask, Transaction
    from app import db
    
    admin = Admin(app, 
                  name='Easy Movie Admin', 
                  template_mode='bootstrap4',
                  index_view=DashboardView(),
                  base_template='admin/base.html')
    
    admin.add_view(UserAdmin(User, db.session, name='👥 Пользователи'))
    admin.add_view(TaskAdmin(Task, db.session, name='📋 Задания'))
    admin.add_view(UserTaskAdmin(UserTask, db.session, name='✅ Выполненные задания'))
    admin.add_view(TransactionAdmin(Transaction, db.session, name='💰 Транзакции'))
    
    print("✅ Админка успешно загружена!")
    return admin