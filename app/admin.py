from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app import db
from app.models import User, Task, UserTask

# Защита админки: только админы
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

# Кастомная главная страница админки
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.is_admin):
            return redirect(url_for('auth.login'))
        # Статистика
        users_count = User.query.count()
        tasks_count = Task.query.count()
        pending_tasks = UserTask.query.filter_by(status='pending').count()
        return self.render('admin/index.html', users_count=users_count, tasks_count=tasks_count, pending_tasks=pending_tasks)

# Функция инициализации админки
def init_admin(app):
    # УБИРАЕМ template_mode='bootstrap4' так как эта версия его не поддерживает
    admin = Admin(app, name='Easy Movie Admin', index_view=MyAdminIndexView())
    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(Task, db.session))
    admin.add_view(AdminModelView(UserTask, db.session))
    return admin