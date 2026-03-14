from app import create_app, db
from app.models import User, Category, Task
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

with app.app_context():
    # Создаем таблицы
    db.create_all()
    print("✅ Таблицы созданы")
    
    # Создаем админа
    admin = User(
        username='admin',
        email='admin@yandex.ru',
        password_hash=generate_password_hash('dimala209'),
        is_admin=True,
        balance=1000
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Админ создан: admin@yandex.ru / dimala209")
    
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
    db.session.commit()
    print(f"✅ Добавлено {len(categories)} категорий")