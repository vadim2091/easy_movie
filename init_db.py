from app import create_app, db
from app.models import User, Category, Task
from werkzeug.security import generate_password_hash
from datetime import date
import os

app = create_app()

with app.app_context():
    # Удаляем старую базу если есть (для чистоты)
    db.drop_all()
    print("🗑️ Старые таблицы удалены")
    
    # Создаем таблицы
    db.create_all()
    print("✅ Новые таблицы созданы")
    
    # Создаем админа
    admin = User(
        username='admin',
        email='admin@yandex.ru',
        password_hash=generate_password_hash('dimala209'),
        is_admin=True,
        balance=1000
    )
    db.session.add(admin)
    
    # Создаем категории
    categories = [
        Category(name='Дебетовые карты', slug='debit-cards', icon='💳', min_age=14, sort_order=1),
        Category(name='Кредитные карты', slug='credit-cards', icon='💳', min_age=18, sort_order=2),
        Category(name='РКО', slug='business-accounts', icon='🏢', min_age=18, sort_order=3),
        Category(name='ИП', slug='ip-registration', icon='💼', min_age=18, sort_order=4),
        Category(name='Вакансии', slug='jobs', icon='🚚', min_age=18, sort_order=5),
    ]
    
    for cat in categories:
        db.session.add(cat)
    
    # Сохраняем
    db.session.commit()
    print("✅ Админ и категории созданы")
    
    # Проверяем
    print(f"👤 Пользователей: {User.query.count()}")
    print(f"📊 Категорий: {Category.query.count()}")
    print("\n🔐 Админ: admin@yandex.ru / dimala209")