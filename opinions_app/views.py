from random import randrange

from .models import Opinion


def random_opinion():
    """Вернуть случайное мнение или None, если мнений в базе нет."""
    quantity = Opinion.query.count()
    if not quantity:
        return None
    # Пропускаю случайное число записей и беру следующую за ними.
    return Opinion.query.offset(randrange(quantity)).first()
