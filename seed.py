from app import create_app, db
from app.models import Task, User
from datetime import date

app = create_app()
with app.app_context():
    db.create_all()
    
    tasks = [
        Task(title='Т-Банк Black', description='Дебетовка', reward=120, type='debit', min_age=14),
        Task(title='Альфа-Карта', description='Дебетовка', reward=120, type='debit', min_age=14),
        Task(title='Сбер Молодежная', description='Дебетовка', reward=100, type='debit', min_age=14),
        Task(title='Т-Банк Кредитная', description='Кредитка', reward=200, type='credit', min_age=18),
        Task(title='Яндекс Еда', description='Курьер', reward=300, type='vacancy', min_age=18),
    ]
    
    for t in tasks:
        db.session.add(t)
    
    db.session.commit()
    print(f'✅ {len(tasks)} заданий создано')