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

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    socketio.init_app(app, cors_allowed_origins="*")

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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

    try:
        from app.admin import init_admin
        init_admin(app)
        print("✅ Админка загружена")
    except Exception as e:
        print(f"❌ Ошибка админки: {e}")

    with app.app_context():
        db.create_all()
        print("✅ Таблицы созданы (если не существовали)")

        from app.models import Category, Task

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

        if Task.query.count() == 0:
            debit = Category.query.filter_by(slug='debit-cards').first()
            credit = Category.query.filter_by(slug='credit-cards').first()
            business = Category.query.filter_by(slug='business-accounts').first()
            vacancy = Category.query.filter_by(slug='vacancy').first()

            tasks = [
                # ===== ДЕБЕТОВЫЕ КАРТЫ =====
                Task(
                    title='Т-банк - Дебетовая карта Black МИР',
                    description='''**Black** — главная дебетовая карта Т-Банка, с кэшбэком в рублях и процентом на остаток.

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
                    instructions='https://trk.ppdu.ru/click/sWjR7kOv?erid=Kra23xCCG',
                    is_active=True
                ),
                Task(
                    title='Т-Банк — Black / Молодежная карта',
                    description='''**Black** — главная дебетовая карта Т-Банк, с кэшбэком в рублях и процентом на остаток.

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
                    instructions='https://trk.ppdu.ru/click/dBXaBPbP?erid=Kra23VKkC',
                    is_active=True
                ),
                Task(
                    title='Т-Банк — Дебетовая исламская карта',
                    description='''**Исламская карта** — карта, соответствующая нормам шариата, разработана Т‑Банком совместно с духовным управлением мусульман Татарстана (ДУМ РТ) и одобрена им. Вместе с картой привезем кожаный картхолдер.

🔥 **УТП:**
• Вносите деньги на счет без комиссии
• Снимайте наличные бесплатно: до 500 000 ₽ в банкоматах Т Банка, от 3 000 до 100 000 ₽ в банкоматах партнеров
• Платежи и переводы без комиссии — переводы по России до 30 000 000 ₽ в месяц через СБП
• Повышенный лимит бесплатных переводов за рубеж — до 50 000 ₽ в месяц без комиссии''',
                    reward=1100,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+ лет',
                    instructions='https://trk.ppdu.ru/click/BUb3cOmt?erid=2SDnjeZwNoM',
                    is_active=True
                ),
                # Новые дебетовые карты
                Task(
                    title='МТС Деньги | Дебетовая карта',
                    description='''**Акция** — выбирайте до 5 категорий кешбэка каждый месяц, в том числе кешбэк 30% за оплату связи в Мой МТС.

🔥 **Категории на июль:**
• Супермаркеты с МТС Premium — 5% (до 1000₽)
• Все покупки — 5% (до 1000₽)
• Оплата мобильной связи МТС с МТС Premium — 30% (до 250₽)
• Развлечения и кино — 30% (до 100₽)
• Маркетплейсы — 10% (до 1000₽)
• Аптеки — 15% (до 1000₽)
• Путешествия — 9% (до 1000₽)
• Фастфуд и рестораны — 11% (до 1000₽)
• Одежда и обувь — 9% (до 1000₽)
• Питомцы — 11% (до 1000₽)
• Магазины МТС — 5%''',
                    reward=2300,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+ лет',
                    instructions='https://trk.ppdu.ru/click/a40lVV2h?erid=2SDnjeTdiDm',
                    is_active=True
                ),
                Task(
                    title='БСПБ - Дебетовая карта',
                    description='''**Mir Platinum Cash Back** — преимущества карты.

🔥 **Преимущества:**
• 7% кешбэк в ресторанах
• 5% кешбэк на АЗС
• 5% кешбэк в категории развлечения
• 1% кешбэк в прочих категориях
• Скидки и кешбэк от платёжной системы МИР
• Кешбэк до 7 000 ₽/мес
• Выпуск платёжного стикера
• Страхование семьи в путешествиях до 50 000 евро
• Привилегии участника программы «Премиум Лайт»
• Повышенный лимит на снятие
• Бесплатный смс-сервис''',
                    reward=1920,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+ лет',
                    instructions='https://trk.ppdu.ru/click/8C0qmXXH?erid=2SDnjcRFm6d',
                    is_active=True
                ),
                Task(
                    title='Альфа-Банк - Дебетовая Альфа‑Карта с привилегиями Альфа‑Смарт',
                    description='''**Целевое действие:** Активация дебетовой карты и подписки Альфа‑Смарт.

Активированная карта — карта, по которой была совершена расходная операция (только покупка) в течение 30 дней после получения, при условии отсутствия активных дебетовых карт у клиента в течение 90 дней.

**Не считаются целевым действием:**
• Пополнение счёта
• Операции в казино, тотализаторах
• Дорожные чеки, лотереи, облигации
• Снятие наличных
• Переводы между счетами
• Оплата связи, ЖКХ
• Переводы в электронные кошельки
• Коммерческие операции (оплата товаров/услуг для юрлиц)
• Платежи в пользу страховых и паевых фондов
• Мошеннические операции
• Возврат товара

Все остальные операции активируют карту.''',
                    reward=1200,
                    category_id=debit.id,
                    min_age=14,
                    requirements='Паспорт РФ, 14+ лет',
                    instructions='https://trk.ppdu.ru/click/wcIXwd1G?erid=2SDnje2HATp',
                    is_active=True
                ),

                # ===== КРЕДИТНЫЕ КАРТЫ =====
                Task(
                    title='ВТБ - Кредитная карта',
                    description='''**Кредитная карта ВТБ** — один из крупнейших банков России.

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
                    instructions='https://trk.ppdu.ru/click/kE0noVk6?erid=2SDnjeGCc2T',
                    is_active=True
                ),
                Task(
                    title='Т-банк — Кредитная карта Платинум',
                    description='''**Платинум** — премиальная кредитная карта Т-Банк.

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
                    instructions='https://trk.ppdu.ru/click/lprRzKZd?erid=2SDnjcyz7NY',
                    is_active=True
                ),
                Task(
                    title='Уралсиб — Кредитная карта 120 дней без %',
                    description='''**120 дней без процентов** — выгодная кредитная карта от банка Уралсиб.

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
                    instructions='https://trk.ppdu.ru/click/t5H6vwqu?erid=2SDnjeTpMvR',
                    is_active=True
                ),

                # ===== РКО =====
                Task(
                    title='ВТБ - Регистрация бизнеса + РКО',
                    description='''**Преимущества оффера для веб-мастеров:**
• Оперативное рассмотрение заявок
• Высокая лояльность к бренду
• Высокая конверсия
• Фиксированная ставка
• Широкая сеть отделений по всей РФ

**Механика присвоения счетов:**
• За каждой заявкой на регистрацию бизнеса закрепляется ИНН
• Повторный ИНН — статус «Дубль», не оплачивается
• Открытый счёт присваивается каналу, который первый привёл заявку с этим ИНН
• Если по заявке не дозвонились и не узнали ИНН — счёт не засчитывается
• Статусы «Окончательный недозвон КЦ» или «Отказ КЦ» — неактивны в течение 90 дней
• Новый клиент — юрлицо или ИП, не имевший продуктов ВТБ последние 90 дней''',
                    reward=7200,
                    category_id=business.id,
                    min_age=18,
                    requirements='Для юрлиц и ИП',
                    instructions='https://trk.ppdu.ru/click/Z4BkvJPV?erid=Kra23bNL5',
                    is_active=True
                ),
                Task(
                    title='Банк точка - РКО',
                    description='''**Преимущества РКО:**
• Расчётный счёт для юрлиц и ИП за 0 ₽
• Скидка 80% на первые 3 месяца обслуживания
• До 7% годовых на остаток кэшбеком
• Бесплатные платежи в любом количестве
• Переводы до 1 000 000 ₽ физлицам в месяц — бесплатно
• Круглосуточная поддержка в чате
• До 360 000 ₽ экономии на партнёрских сервисах

**Дополнительно:**
• Бизнес-карты — бесплатно, доставка бесплатная
• Бесплатный комплаенс-ассистент (анализ 115-ФЗ)
• Зарплатный проект для 1 сотрудника
• Все виды эквайринга

**Преимущества регистрации ИП и ООО:**
• Помощь без визита в банк
• Регистрация за 7 дней без похода в налоговую''',
                    reward=5200,
                    category_id=business.id,
                    min_age=18,
                    requirements='Для юрлиц и ИП',
                    instructions='https://trk.ppdu.ru/click/OGDQBFwh?erid=2SDnjduYB12',
                    is_active=True
                ),
                Task(
                    title='Уралсиб - РКО',
                    description='''**Условия акции (06.06.2025 – 30.09.2025):**
• Для новых клиентов
• Открытие счёта с подключением пакета «Удобный» (периодичность 1/3/6/12 месяцев)
• Применяется только к первому открытому счёту
• Не совмещается с другими акциями

**Тариф «Удобный»:**
• 0 ₽ за месяц (экономия до 8 280 ₽ за год, базовая стоимость 690 ₽/мес)
• Бизнес-карты: 1 шт. бесплатно
• Платежи контрагентам: 10 шт. – 0 ₽, далее 99 ₽
• Переводы ИП физлицам до 300 000 ₽ – бесплатно
• Переводы в рамках «Цифровой зарплаты» до 300 000 – бесплатно, далее 1%
• Снятие наличных по карте до 300 000 ₽ – 2%
• Внесение наличных до 150 000 ₽ – бесплатно''',
                    reward=5200,
                    category_id=business.id,
                    min_age=18,
                    requirements='Для новых клиентов',
                    instructions='https://trk.ppdu.ru/click/bN3VxKqP?erid=Kra23ww8p',
                    is_active=True
                ),
                Task(
                    title='Норвик банк - РКО',
                    description='''**Цель:** Оплачиваются открытые и активные счета.

**Условия:**
• ЮЛ старше 6 месяцев
• Любая расходная операция от 3000 ₽ в течение 30 дней после открытия
• С момента открытия прошло не менее 30 дней
• Счёт не закрыт до выплаты
• Отсутствие ограничений по счёту, непогашенной задолженности

**Бесплатно:**
• Корпоративная карта МИР
• Открытие счёта за 1 день
• Доступ к «Банк online» 24/7

**Преимущества:**
• Кешбэк до 5% в разных категориях
• Оплата корпоративных расходов без комиссий
• Быстрое зачисление наличных через банкоматы
• До 150 платежей юрлицам и ИП без комиссии
• До 500 000 ₽ переводов физлицам без комиссии

**Правила:** Оплата по дате совершения целевого действия, а не по дате заявки.''',
                    reward=6200,
                    category_id=business.id,
                    min_age=18,
                    requirements='ЮЛ старше 6 месяцев',
                    instructions='https://trk.ppdu.ru/click/uKpgCQsc?erid=2SDnjc1SD3P',
                    is_active=True
                ),

                # ===== ВАКАНСИИ =====
                Task(
                    title='Курьер в Яндекс Еду/Яндекс Лавка',
                    description='''**Работа в Яндексе** — стабильный доход каждый день!

🔥 **УТП:**
• Комфортное расписание и график работы
• Гарантии и бонусы от компании
• Заказы поступают 24/7
• Доход до 3 500 рублей в день
• Доплата за первые 100 заказов

⚡ **СПЕЦПРЕДЛОЖЕНИЕ:** 20 000 мандаринов за выполнение!''',
                    reward=20000,
                    category_id=vacancy.id,
                    min_age=18,
                    requirements='18+, желание работать',
                    instructions='https://trk.ppdu.ru/click/pKYWYSuY?erid=Kra23uVC3',
                    is_active=True
                ),
            ]

            for task in tasks:
                db.session.add(task)
            db.session.commit()
            print(f"✅ Добавлено {len(tasks)} заданий при запуске")

    return app