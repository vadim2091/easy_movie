from app import create_app, db
from app.models import Category, Task
from datetime import datetime

app = create_app()

with app.app_context():
    # === 1. СОЗДАЕМ КАТЕГОРИИ ===
    print("📁 Создаю категории...")
    
    categories_data = [
        {'name': 'Дебетовые карты', 'slug': 'debit-cards', 'icon': '💳', 'min_age': 14, 'sort_order': 1},
        {'name': 'Кредитные карты', 'slug': 'credit-cards', 'icon': '💳', 'min_age': 18, 'sort_order': 2},
        {'name': 'РКО', 'slug': 'business-accounts', 'icon': '🏢', 'min_age': 18, 'sort_order': 3},
        {'name': 'ИП', 'slug': 'ip-registration', 'icon': '💼', 'min_age': 18, 'sort_order': 4},
        {'name': 'Вакансии', 'slug': 'vacancy', 'icon': '🚚', 'min_age': 18, 'sort_order': 5},
    ]
    
    for cat_data in categories_data:
        if not Category.query.filter_by(slug=cat_data['slug']).first():
            cat = Category(**cat_data)
            db.session.add(cat)
    db.session.commit()
    print("✅ Категории готовы")

    # Получаем ID категорий
    debit = Category.query.filter_by(slug='debit-cards').first()
    credit = Category.query.filter_by(slug='credit-cards').first()
    vacancy = Category.query.filter_by(slug='vacancy').first()

    # === 2. УДАЛЯЕМ СТАРЫЕ ЗАДАНИЯ (ОПЦИОНАЛЬНО) ===
    print("🧹 Очищаю старые задания...")
    Task.query.delete()
    db.session.commit()

    # === 3. ДОБАВЛЯЕМ НОВЫЕ ЗАДАНИЯ ===
    print("📝 Добавляю новые задания...")
    
    tasks = [
        # ===== ДЕБЕТОВЫЕ КАРТЫ =====
        Task(
            title='Т-банк - Дебетовая карта Black МИР',
            description='''**Black** - главная дебетовая карта Т-Банк, с кэшбэком в рублях и процентом на остаток.

🔥 **УТП:**
• Кэшбэк в рублях — до 30% по спецпредложениям от партнеров
• Обслуживание бесплатно (при балансе от 50 000 ₽), иначе 99 ₽/мес
• Выбор 4-х любимых категорий каждый месяц с кэшбеком 15%
• Бесплатное снятие наличных: до 500 000 ₽ в банкоматах Т-Банк
• Переводы без комиссии до 20 000 ₽ в месяц
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
• Обслуживание бесплатно (при балансе от 50 000 ₽), иначе 99 ₽/мес
• Выбор 4-х любимых категорий каждый месяц с кэшбеком 15%
• Бесплатное снятие наличных: до 500 000 ₽ в банкоматах Т-Банк
• Переводы без комиссии до 20 000 ₽ в месяц
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
            description='''**Исламская карта** - соответствует нормам шариата, разработана совместно с ДУМ Татарстана.

🔥 **УТП:**
• В комплекте кожаный картхолдер
• Внесение денег без комиссии
• Снятие наличных: до 500 000 ₽ бесплатно
• Переводы по России до 30 000 000 ₽ в месяц
• Повышенный лимит переводов за рубеж - до 50 000 ₽ без комиссии''',
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
            description='''**Кредитная карта ВТБ** - один из крупнейших банков России.

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
• Бесплатное обслуживание навсегда
• До 120 дней без процентов
• Нужен только паспорт
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
    print(f"✅ Добавлено {len(tasks)} заданий!")
    print("\n📊 ИТОГО:")
    print(f"Категорий: {Category.query.count()}")
    print(f"Заданий: {Task.query.count()}")