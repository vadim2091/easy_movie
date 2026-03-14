import random

def generate_fake_rating():
    # Возвращает список словарей с именами и суммой заработка
    names = ['Анна С.', 'Иван П.', 'Мария К.', 'Дмитрий Л.', 'Елена В.', 'Алексей Н.', 'Ольга Т.', 'Сергей М.']
    rating = []
    for name in names:
        rating.append({
            'name': name,
            'earned': random.randint(500, 5000)
        })
    # Сортируем по убыванию
    rating.sort(key=lambda x: x['earned'], reverse=True)
    return rating