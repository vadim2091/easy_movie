from app import create_app
from app.websocket import socketio
import os

app = create_app()

# ИНИЦИАЛИЗАЦИЯ БАЗЫ ПРИ ЗАПУСКЕ
with app.app_context():
    from app import db
    from app.models import User, Category
    from werkzeug.security import generate_password_hash
    
    # Создаем таблицы если их нет
    db.create_all()
    print("✅ Таблицы проверены")
    
    # Создаем админа если нет
    if not User.query.filter_by(email='admin@yandex.ru').first():
        admin = User(
            username='admin',
            email='admin@yandex.ru',
            password_hash=generate_password_hash('dimala209'),
            is_admin=True,
            balance=1000
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Админ создан")
    
    # Создаем категории если нет
    if Category.query.count() == 0:
        categories = [
            Category(name='Дебетовые карты', slug='debit-cards', icon='💳', min_age=14, sort_order=1),
            Category(name='Кредитные карты', slug='credit-cards', icon='💳', min_age=18, sort_order=2),
            Category(name='РКО', slug='business-accounts', icon='🏢', min_age=18, sort_order=3),
            Category(name='ИП', slug='ip-registration', icon='💼', min_age=18, sort_order=4),
            Category(name='Вакансии', slug='jobs', icon='🚚', min_age=18, sort_order=5),
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        print(f"✅ Добавлено {len(categories)} категорий")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Сервер запущен на http://127.0.0.1:{port}")
    socketio.run(app, debug=True, host='127.0.0.1', port=port)