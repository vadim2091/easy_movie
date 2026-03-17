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

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    socketio.init_app(app, cors_allowed_origins="*")

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация blueprint'ов
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

    # Админка
    try:
        from app.admin import init_admin
        init_admin(app)
        print("✅ Админка загружена")
    except Exception as e:
        print(f"❌ Ошибка админки: {e}")

    # Создание таблиц и наполнение базы
    with app.app_context():
        db.create_all()
        print("✅ Таблицы созданы (если не существовали)")

        from app.models import Category, Task

        # Категории
        if Category.query.count() == 0:
            categories = [
                Category(name='Дебетовые карты', slug='debit-cards', icon='💳', min_age=14, sort_order=1),
                Category(name='Кредитные карты', slug='credit-cards', icon='💳', min_age=18, sort_order=2),
                Category(name='РКО', slug='business-accounts', icon='🏢', min_age=18, sort_order=3),
                Category(name='ИП', slug='ip-registration', icon='💼', min_age=18, sort_order=4),
                Category(name='Вакансии', slug='vacancy', icon='🚚', min_age=18, sort_order=5),
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
            print("✅ Категории созданы")

        # Задания
        if Task.query.count() == 0:
            debit = Category.query.filter_by(slug='debit-cards').first()
            credit = Category.query.filter_by(slug='credit-cards').first()
            vacancy = Category.query.filter_by(slug='vacancy').first()

            tasks = [
                # ===== ДЕБЕТОВЫЕ КАРТЫ =====
                Task(
                    title='Т-банк - Дебетовая карта Black МИР',
                    description='''**Black** — главная дебетовая карта Т-Банка. Кэшбэк до 30%, бесплатное обслуживание при балансе от 50 000₽, выбор 4 категорий с повышенным кэшбеком 15%. Снятие без комиссии до 500 000₽, переводы до 20 000₽.

⚠️ **Важно:** Если вы не выполните условия, то вам будет заблокирован вывод.''',
                    reward=2100,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+ лет',
                    instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/sWjR7kOv?erid=Kra23xCCG',
                    is_active=True
                ),
                Task(
                    title='Т-Банк — Black / Молодежная карта',
                    description='''**Black** — дебетовая карта для молодых. Кэшбэк до 30%, бесплатное обслуживание при балансе от 50 000₽, выбор 4 любимых категорий. Снятие до 500 000₽, переводы до 20 000₽.

⚠️ **Важно:** Если вы не выполните условия, то вам будет заблокирован вывод.''',
                    reward=2200,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+ лет',
                    instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/dBXaBPbP?erid=Kra23VKkC',
                    is_active=True
                ),
                Task(
                    title='Т-Банк — Дебетовая исламская карта',
                    description='''**Исламская карта** — соответствует нормам шариата. В подарок кожаный картхолдер. Внесение и снятие без комиссии, переводы по России до 30 млн ₽, за рубеж до 50 000₽ без комиссии.

⚠️ **Важно:** Если вы не выполните условия, то вам будет заблокирован вывод.''',
                    reward=1100,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+ лет',
                    instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/BUb3cOmt?erid=2SDnjeZwNoM',
                    is_active=True
                ),

                # ===== КРЕДИТНЫЕ КАРТЫ =====
                Task(
                    title='ВТБ - Кредитная карта',
                    description='''**Кредитная карта ВТБ** — лимит до 1 млн ₽. Льготный период до 200 дней при рефинансировании, до 100 дней на покупки. Снятие наличных без комиссии первые 30 дней. Бесплатное оформление и доставка.

⚠️ **Важно:** Если вы не выполните условия, то вам будет заблокирован вывод.''',
                    reward=1200,
                    category_id=credit.id,
                    min_age=18,
                    requirements='Паспорт РФ, 18+ лет',
                    instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/kE0noVk6?erid=2SDnjeGCc2T',
                    is_active=True
                ),
                Task(
                    title='Т-банк — Кредитная карта Платинум',
                    description='''**Платинум** — кредитная карта с лимитом до 1 млн ₽. Беспроцентный период до 55 дней на покупки, до 120 дней при погашении других кредитов. Рассрочка до 12 месяцев, бесплатные переводы до 50 000₽.

⚠️ **Важно:** Если вы не выполните условия, то вам будет заблокирован вывод.''',
                    reward=2100,
                    category_id=credit.id,
                    min_age=18,
                    requirements='Паспорт РФ, 18+ лет',
                    instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/lprRzKZd?erid=2SDnjcyz7NY',
                    is_active=True
                ),
                Task(
                    title='Уралсиб — Кредитная карта 120 дней без %',
                    description='''**120 дней без процентов** — кредитная карта Уралсиба. Лимит до 1 млн ₽, бесплатное обслуживание навсегда. До 120 дней без процентов, нужен только паспорт. Кэшбэк до 30%.

⚠️ **Важно:** Если вы не выполните условия, то вам будет заблокирован вывод.''',
                    reward=2900,
                    category_id=credit.id,
                    min_age=18,
                    requirements='Паспорт РФ, 18+ лет',
                    instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/t5H6vwqu?erid=2SDnjeTpMvR',
                    is_active=True
                ),

                # ===== ВАКАНСИИ =====
                Task(
                    title='Курьер в Яндекс Еду/Яндекс Лавка',
                    description='''**Работа в Яндексе** — доход до 3500 ₽/день. Гибкий график, гарантии, бонусы. Доплата за первые 100 заказов.

⚡ **СПЕЦПРЕДЛОЖЕНИЕ:** 20 000 мандаринов за выполнение!''',
                    reward=20000,
                    category_id=vacancy.id,
                    min_age=18,
                    requirements='18+, желание работать',
                    instructions='''Задание считается выполненным, если:
1. Зарегистрироваться по ссылке
2. Выполнить 5 заказов в течение 14 дней

Ссылка: https://trk.ppdu.ru/click/pKYWYSuY?erid=Kra23uVC3''',
                    is_active=True
                ),
            ]

            for task in tasks:
                db.session.add(task)
            db.session.commit()
            print(f"✅ Добавлено {len(tasks)} заданий при запуске")

    return app