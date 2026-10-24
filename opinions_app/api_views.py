from flask import jsonify, request

from . import app, db
from .models import Opinion
from .views import random_opinion

NOT_FOUND = 'Мнение не найдено'
REQUIRED_FIELDS = 'Поля title и text обязательны'
EMPTY_FIELDS = 'Поля title и text не могут быть пустыми'
DUPLICATE_TEXT = 'Такое мнение уже есть в базе данных'
NOT_JSON_OBJECT = 'Тело запроса должно быть JSON-объектом'
NO_OPINIONS = 'В базе нет мнений'


def error_response(message, status_code):
    """Вернуть ошибку в формате JSON с нужным кодом ответа."""
    return jsonify({'error': message}), status_code


def text_is_taken(text, opinion_id=None):
    """Проверить, есть ли в базе другое мнение с таким же текстом."""
    query = Opinion.query.filter(Opinion.text == text)
    # При обновлении не считаю дубликатом само обновляемое мнение.
    if opinion_id is not None:
        query = query.filter(Opinion.id != opinion_id)
    return query.first() is not None


@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    """Вернуть список мнений, при необходимости отфильтрованный по названию."""
    query = Opinion.query
    title = request.args.get('title')
    if title:
        # ilike ищет подстроку в названии без учёта регистра.
        query = query.filter(Opinion.title.ilike(f'%{title}%'))
    opinions = [opinion.to_dict() for opinion in query.all()]
    return jsonify({'opinions': opinions}), 200


@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    """Создать новое мнение из тела запроса."""
    # silent=True: при пустом или битом теле получаю None, а не HTML-ошибку.
    data = request.get_json(silent=True)
    if (
        not isinstance(data, dict)
        or not data.get('title')
        or not data.get('text')
    ):
        return error_response(REQUIRED_FIELDS, 400)
    if text_is_taken(data['text']):
        return error_response(DUPLICATE_TEXT, 400)
    opinion = Opinion()
    opinion.from_dict(data)
    db.session.add(opinion)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201


@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id):
    """Вернуть одно мнение по id."""
    opinion = db.session.get(Opinion, id)
    if opinion is None:
        return error_response(NOT_FOUND, 404)
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id):
    """Обновить переданные поля существующего мнения."""
    opinion = db.session.get(Opinion, id)
    if opinion is None:
        return error_response(NOT_FOUND, 404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response(NOT_JSON_OBJECT, 400)
    # Обязательные поля можно не передавать, но нельзя стирать.
    if any(field in data and not data[field] for field in ('title', 'text')):
        return error_response(EMPTY_FIELDS, 400)
    if 'text' in data and text_is_taken(data['text'], opinion.id):
        return error_response(DUPLICATE_TEXT, 400)
    opinion.from_dict(data)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    """Удалить мнение по id."""
    opinion = db.session.get(Opinion, id)
    if opinion is None:
        return error_response(NOT_FOUND, 404)
    db.session.delete(opinion)
    db.session.commit()
    return '', 204


@app.route('/api/opinions/random/', methods=['GET'])
def get_random_opinion():
    """Вернуть случайное мнение."""
    opinion = random_opinion()
    if opinion is None:
        return error_response(NO_OPINIONS, 404)
    return jsonify({'opinion': opinion.to_dict()}), 200
