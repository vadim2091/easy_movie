from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.websocket import socketio
import os

# СОЗДАЕМ db ЗДЕСЬ
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///easy_movie.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    
    # ИНИЦИАЛИЗИРУЕМ
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Blueprints
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
    
    # SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

       # Создаём задания, если их нет
if Task.query.count() == 0:
    debit = Category.query.filter_by(slug='debit-cards').first()
    credit = Category.query.filter_by(slug='credit-cards').first()
    vacancy = Category.query.filter_by(slug='vacancy').first()

    tasks = [
        # ===== ДЕБЕТОВЫЕ КАРТЫ =====
        Task(
            title='Т-банк - Дебетовая карта Black МИР',
            description='''**Black** - главная дебетовая карта Т-Банк, с кэшбэком в рублях и процентом на остаток.

🔥 **УТП:**
• Кэшбэк в рублях — до 30% по спецпредложениям от партнеров
• Обслуживание бесплатно (если на карте, вкладах, накопительных и брокерских счетах каждый день в сумме хранится не менее 50 000 ₽), в остальных случаях 99руб в месяц
• Возможность выбора 4-х любимых категорий каждый месяц с повышенным кэшбеком 15%
• Бесплатное снятие наличных в банкоматах Т-Банк — любую сумму до 500 000 ₽ в месяц, а в остальных банкоматах — от 3000 ₽ до 100 000 ₽
• Переводы без комиссии в другой банк по номеру карты или номеру телефона до 20 000 ₽ в месяц, с СБП без комиссии
• Мультифункциональное приложение
• Круглосуточная поддержка''',
            reward=2100,
            category_id=debit.id,
            min_age=14,
            requirements='Паспорт РФ, 14+ лет',
            instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/sWjR7kOv?erid=Kra23xCCG',
            is_active=True
        ),
        Task(
            title='Т-Банк — Black / Молодежная карта',
            description='''**Black** - главная дебетовая карта Т-Банк, с кэшбэком в рублях и процентом на остаток.

🔥 **УТП:**
• Кэшбэк в рублях — до 30% по спецпредложениям от партнеров
• Обслуживание бесплатно (если на карте, вкладах, накопительных и брокерских счетах каждый день в сумме хранится не менее 50 000 ₽), в остальных случаях 99руб в месяц
• Возможность выбора 4-х любимых категорий каждый месяц с повышенным кэшбеком 15%
• Бесплатное снятие наличных в банкоматах Т-Банк — любую сумму до 500 000 ₽ в месяц, а в остальных банкоматах — от 3000 ₽ до 100 000 ₽
• Переводы без комиссии в другой банк по номеру карты или номеру телефона до 20 000 ₽ в месяц, с СБП без комиссии
• Мультифункциональное приложение''',
            reward=2200,
            category_id=debit.id,
            min_age=14,
            requirements='Паспорт РФ, 14+ лет',
            instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/dBXaBPbP?erid=Kra23VKkC',
            is_active=True
        ),
        Task(
            title='Т-Банк — Дебетовая исламская карта',
            description='''**Исламская карта** - карта, соответствующая нормам шариата, разработана Т‑Банком совместно с духовным управлением мусульман Татарстана (ДУМ РТ) и одобрена им. Вместе с картой привезем кожаный картхолдер.

🔥 **УТП:**
• Вносите деньги на счет без комиссии
• Снимайте наличные бесплатно: до 500 000 ₽ в банкоматах Т Банка, от 3 000 до 100 000 ₽ в банкоматах партнеров
• Платежи и переводы без комиссии - переводы по России — до 30 000 000 ₽ в месяц через СБП
• Повышенный лимит бесплатных переводов за рубеж - до 50 000 ₽ в месяц без комиссии''',
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
            description='''**Кредитная карта ВТБ** – один из крупнейших банков России.

🔥 **УТП:**
• Кредитный лимит до 1 000 000 ₽
• Льготный период до 200 дней при рефинансировании
• Льготный период до 100 дней на покупки
• Снятие наличных до 50 000 ₽ без комиссии в первые 30 дней
• Бесплатное оформление и доставка''',
            reward=1200,
            category_id=credit.id,
            min_age=18,
            requirements='Паспорт РФ, 18+ лет',
            instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/kE0noVk6?erid=2SDnjeGCc2T',
            is_active=True
        ),
        Task(
            title='Т-банк — Кредитная карта Платинум',
            description='''**Платинум** - премиальная кредитная карта Т-Банк.

🔥 **УТП:**
• Кредитный лимит до 1 000 000 ₽
• Беспроцентный период до 55 дней на покупки
• Беспроцентный период до 120 дней при погашении других кредитов
• Рассрочка до 12 месяцев без процентов
• Бесплатные переводы до 50 000 ₽ в месяц
• Бесплатная доставка сегодня''',
            reward=2100,
            category_id=credit.id,
            min_age=18,
            requirements='Паспорт РФ, 18+ лет',
            instructions='Оформи карту по ссылке: https://trk.ppdu.ru/click/lprRzKZd?erid=2SDnjcyz7NY',
            is_active=True
        ),
        Task(
            title='Уралсиб — Кредитная карта 120 дней без %',
            description='''**120 дней без процентов** - выгодная кредитная карта от банка Уралсиб.

🔥 **УТП:**
• Кредитный лимит до 1 000 000 ₽
• Бесплатное обслуживание навсегда без каких‑либо условий
• До 120 дней без процентов
• Для оформления нужен только паспорт
• Ставка от 29,9% до 49,9%
• Кэшбэк до 30%''',
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
            description='''**Работа в Яндексе** - стабильный доход каждый день!

🔥 **УТП:**
• Комфортное расписание и график работы
• Гарантии и бонусы от компании
• Заказы поступают 24/7
• Доход до 3 500 рублей в день
• Доплата за первые 100 заказов

⚡ **СПЕЦПРЕДЛОЖЕНИЕ:** 20 000 мандаринов за выполнение!''',
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