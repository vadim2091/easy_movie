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
        print("✅ Админ создан при запуске")
    
    # Создаем категории если нет
    if Category.query.count() == 0:
        categories = [
            Category(name='Дебетовые карты', slug='debit-cards', icon='💳', min_age=14, sort_order=1),
            Category(name='Кредитные карты', slug='credit-cards', icon='💳', min_age=18, sort_order=2),
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        print("✅ Категории созданы при запуске")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)