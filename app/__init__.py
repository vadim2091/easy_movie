from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.websocket import socketio
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///easy_movie.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    # === 1. Инициализация расширений ===
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    socketio.init_app(app, cors_allowed_origins="*")

    # === 2. Загрузчик пользователя (должен быть после инициализации db) ===
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # === 3. Регистрация blueprint'ов ===
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.profile import profile_bp
    from app.routes.main import main_bp
    from app.routes.support import support_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(support_bp)

    # === 4. Админка ===
    try:
        from app.admin import init_admin
        init_admin(app)
        print("✅ Админка загружена")
    except Exception as e:
        print(f"❌ Ошибка админки: {e}")

    # === 5. Создание таблиц и наполнение данными (в контексте приложения) ===
    with app.app_context():
        # Сначала создаём таблицы
        db.create_all()
        print("✅ Таблицы созданы (если не существовали)")

        # Теперь импортируем модели внутри контекста
        from app.models import Category, Task, User
        from werkzeug.security import generate_password_hash
        import random

        # === СОЗДАЁМ АДМИНА ЕСЛИ НЕТ ===
        admin = User.query.filter_by(email='admin@yandex.ru').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@yandex.ru',
                password_hash=generate_password_hash('dimala209'),
                is_admin=True,
                balance=0
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Админ создан: admin@yandex.ru / dimala209")

        # Категории
        if Category.query.count() == 0:
            categories = [
                Category(name='💳 Дебетовые', slug='debit-cards', icon='💎', min_age=14, sort_order=1),
                Category(name='🏦 Кредитные', slug='credit-cards', icon='💳', min_age=18, sort_order=2),
                Category(name='📊 РКО', slug='business-accounts', icon='📈', min_age=18, sort_order=3),
                Category(name='👤 ИП', slug='ip-registration', icon='👔', min_age=18, sort_order=4),
                Category(name='🚚 Вакансии', slug='vacancy', icon='📦', min_age=18, sort_order=5),
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
            print("✅ Категории созданы")

        # Задания (если их нет)
        if Task.query.count() == 0:
            debit = Category.query.filter_by(slug='debit-cards').first()
            credit = Category.query.filter_by(slug='credit-cards').first()
            business = Category.query.filter_by(slug='business-accounts').first()
            vacancy = Category.query.filter_by(slug='vacancy').first()

            tasks = [
                # ===== ДЕБЕТОВЫЕ КАРТЫ =====
                Task(
                    title='💎 Т-Банк Black',
                    description='''**🔥 Топ-карта с кэшбэком до 30%**
• Бесплатное обслуживание от 50к баланса
• 4 категории с кэшбэком 15%
• Снятие до 500к без комиссии''',
                    reward=2100,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ',
                    instructions='https://trk.ppdu.ru/click/sWjR7kOv',
                    rating=round(random.uniform(4.2, 5.0), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='👑 Т-Банк Молодёжная',
                    description='''**🚀 Для молодых и активных**
• Кэшбэк до 30%
• Бесплатное обслуживание
• 4 любимые категории''',
                    reward=2200,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+',
                    instructions='https://trk.ppdu.ru/click/dBXaBPbP',
                    rating=round(random.uniform(4.0, 4.9), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='🕌 Исламская карта',
                    description='''**☪ Соответствует нормам шариата**
• Кожаный картхолдер в подарок
• Без комиссии за переводы
• До 30 млн ₽ переводов''',
                    reward=1100,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ',
                    instructions='https://trk.ppdu.ru/click/BUb3cOmt',
                    rating=round(random.uniform(4.3, 5.0), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='📱 МТС Деньги',
                    description='''**🎯 Кэшбэк до 30% за связь**
• 5 категорий на выбор
• До 30% за оплату МТС
• 10% на маркетплейсы''',
                    reward=2300,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ',
                    instructions='https://trk.ppdu.ru/click/a40lVV2h',
                    rating=round(random.uniform(4.1, 4.8), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='🏆 БСПБ Platinum',
                    description='''**💎 Mir Platinum Cash Back**
• 7% в ресторанах
• 5% на АЗС
• Страхование в путешествиях''',
                    reward=1920,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ',
                    instructions='https://trk.ppdu.ru/click/8C0qmXXH',
                    rating=round(random.uniform(4.2, 4.9), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='⭐ Альфа-Смарт',
                    description='''**✨ Привилегии за подписку**
• Кэшбэк до 100%
• 2% на остаток
• Бесплатное обслуживание''',
                    reward=1200,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ',
                    instructions='https://trk.ppdu.ru/click/wcIXwd1G',
                    rating=round(random.uniform(3.9, 4.7), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),

                # ===== КРЕДИТНЫЕ КАРТЫ =====
                Task(
                    title='🏦 ВТБ Кредитная',
                    description='''**💰 До 1 млн ₽**
• Льготный период до 200 дней
• Снятие без комиссии 30 дней
• Бесплатная доставка''',
                    reward=1200,
                    category_id=credit.id,
                    min_age=18,
                    requirements='Паспорт РФ, 18+',
                    instructions='https://trk.ppdu.ru/click/kE0noVk6',
                    rating=round(random.uniform(4.2, 4.9), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='💳 Т-Банк Платинум',
                    description='''**👑 Премиальная карта**
• До 1 млн ₽
• Рассрочка до 12 месяцев
• Бесплатные переводы''',
                    reward=2100,
                    category_id=credit.id,
                    min_age=18,
                    requirements='Паспорт РФ',
                    instructions='https://trk.ppdu.ru/click/lprRzKZd',
                    rating=round(random.uniform(4.3, 5.0), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='⏳ Уралсиб 120 дней',
                    description='''**📅 Без процентов 120 дней**
• Лимит до 1 млн
• Бесплатное обслуживание
• Кэшбэк до 30%''',
                    reward=2900,
                    category_id=credit.id,
                    min_age=18,
                    requirements='Паспорт РФ',
                    instructions='https://trk.ppdu.ru/click/t5H6vwqu',
                    rating=round(random.uniform(4.1, 4.8), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),

                # ===== РКО =====
                Task(
                    title='🏢 ВТБ Бизнес',
                    description='''**📊 Регистрация + РКО**
• Открытие за 1 день
• Фиксированная ставка
• 50 отделений в РФ''',
                    reward=7200,
                    category_id=business.id,
                    min_age=18,
                    requirements='Для юрлиц и ИП',
                    instructions='https://trk.ppdu.ru/click/Z4BkvJPV',
                    rating=round(random.uniform(4.0, 4.7), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='🎯 Точка Банк',
                    description='''**⚡ РКО за 0 ₽**
• Скидка 80% первые 3 мес
• До 7% на остаток
• Круглосуточная поддержка''',
                    reward=5200,
                    category_id=business.id,
                    min_age=18,
                    requirements='Для ИП и ООО',
                    instructions='https://trk.ppdu.ru/click/OGDQBFwh',
                    rating=round(random.uniform(4.4, 5.0), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='🏛 Уралсиб РКО',
                    description='''**📈 Пакет «Удобный»**
• 0 ₽ за месяц
• 10 платежей бесплатно
• Бесплатная бизнес-карта''',
                    reward=5200,
                    category_id=business.id,
                    min_age=18,
                    requirements='Для новых клиентов',
                    instructions='https://trk.ppdu.ru/click/bN3VxKqP',
                    rating=round(random.uniform(4.2, 4.9), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
                Task(
                    title='🏦 Норвик Банк',
                    description='''**💼 РКО для бизнеса**
• Корпоративная карта бесплатно
• Кешбэк до 5%
• Открытие за 1 день''',
                    reward=6200,
                    category_id=business.id,
                    min_age=18,
                    requirements='ЮЛ от 6 мес',
                    instructions='https://trk.ppdu.ru/click/uKpgCQsc',
                    rating=round(random.uniform(4.0, 4.8), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),

                # ===== ВАКАНСИИ =====
                Task(
                    title='🚚 Яндекс Еда',
                    description='''**⚡ Заработок до 3500 ₽/день**
• Гибкий график
• Заказы 24/7
• Бонусы за первые заказы

🔥 **20 000 мандаринов** за 5 заказов!''',
                    reward=20000,
                    category_id=vacancy.id,
                    min_age=18,
                    requirements='18+, желание работать',
                    instructions='https://trk.ppdu.ru/click/pKYWYSuY',
                    rating=round(random.uniform(4.5, 5.0), 1),
                    completed_count=random.randint(50, 500),
                    is_active=True
                ),
            ]

            for task in tasks:
                db.session.add(task)
            db.session.commit()
            print(f"✅ Добавлено {len(tasks)} заданий с рейтингами")

    return app