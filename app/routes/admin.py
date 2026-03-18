from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app import db
from app.models import User, Task, UserTask, Transaction, Withdrawal
from datetime import datetime

class AdminSecureView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

class UserAdmin(AdminSecureView):
    column_list = ['id', 'username', 'email', 'balance', 'hold_balance', 'is_admin', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['is_admin', 'created_at']
    column_editable_list = ['balance', 'hold_balance', 'is_admin']
    form_columns = ['username', 'email', 'balance', 'hold_balance', 'is_admin', 'birth_date', 'phone']
    
    column_formatters = {
        'created_at': lambda v, c, m, p: m.created_at.strftime('%d.%m.%Y %H:%M') if m.created_at else '-',
        'balance': lambda v, c, m, p: f'{m.balance} 🍊' if m.balance else '0 🍊',
        'hold_balance': lambda v, c, m, p: f'{m.hold_balance} 🍊' if m.hold_balance else '0 🍊',
        'is_admin': lambda v, c, m, p: '✅' if m.is_admin else '❌'
    }

class TaskAdmin(AdminSecureView):
    column_list = ['id', 'title', 'reward', 'type', 'min_age', 'is_active', 'created_at']
    column_searchable_list = ['title']
    column_filters = ['type', 'min_age', 'is_active']
    column_editable_list = ['reward', 'is_active']
    form_columns = ['title', 'description', 'reward', 'type', 'min_age', 'requirements', 'instructions', 'is_active']

class UserTaskAdmin(AdminSecureView):
    column_list = ['id', 'user', 'task', 'status', 'created_at', 'approved_at']
    column_searchable_list = ['user.username', 'task.title']
    column_filters = ['status']
    column_editable_list = ['status']
    
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

class TransactionAdmin(AdminSecureView):
    column_list = ['id', 'user', 'amount', 'type', 'description', 'created_at']
    column_searchable_list = ['user.username', 'description']
    column_filters = ['type', 'created_at']
    
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
        'task': lambda v, c, m, p: m.task.title if m.task else 'Прямой вывод',
        'status': lambda v, c, m, p: {
            'pending': '⏳ Ожидает',
            'approved': '✅ Выплачено',
            'rejected': '❌ Отказ'
        }.get(m.status, m.status)
    }
    
    def approve_withdrawal(self, ids):
        for id in ids:
            withdrawal = Withdrawal.query.get(id)
            if withdrawal and withdrawal.status == 'pending':
                withdrawal.status = 'approved'
                withdrawal.approved_at = datetime.utcnow()
                user = withdrawal.user
                if user:
                    user.hold_balance -= withdrawal.amount
                    trans = Transaction(
                        user_id=user.id,
                        amount=withdrawal.amount,
                        type='withdrawal',
                        description=f'Вывод средств'
                    )
                    db.session.add(trans)
                db.session.commit()
    
    def reject_withdrawal(self, ids):
        for id in ids:
            withdrawal = Withdrawal.query.get(id)
            if withdrawal and withdrawal.status == 'pending':
                withdrawal.status = 'rejected'
                user = withdrawal.user
                if user:
                    user.balance += withdrawal.amount
                    user.hold_balance -= withdrawal.amount
                db.session.commit()
    
    column_actions_list = [
        ('approve', 'Одобрить'),
        ('reject', 'Отклонить')
    ]

def init_admin(app):
    admin = Admin(app, name='Easy Movie Admin', template_mode='bootstrap4')
    admin.add_view(UserAdmin(User, db.session, name='👥 Пользователи'))
    admin.add_view(TaskAdmin(Task, db.session, name='📋 Задания'))
    admin.add_view(UserTaskAdmin(UserTask, db.session, name='✅ Выполненные задания'))
    admin.add_view(TransactionAdmin(Transaction, db.session, name='💰 Транзакции'))
    admin.add_view(WithdrawalAdmin(Withdrawal, db.session, name='💸 Заявки на вывод'))
    return admin