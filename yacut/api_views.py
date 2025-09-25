from http import HTTPStatus

from flask import Response, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from yacut import app, db
from yacut.error_handlers import InvalidAPIUsage
from yacut.exceptions import ShortIDGenerationError
from yacut.models import URLMap
from yacut.validators import validate_data


@app.route('/api/id/', methods=['POST'])
def add_short_id() -> tuple[Response, int]:
    """
    Обрабатывает POST-запрос на создание новой короткой ссылки.

    Ожидается JSON-тело с полем 'url' и опциональным полем 'custom_id'.
    Если 'custom_id' не указан — генерируется случайный уникальный
    идентификатор.
    Результат сохраняется в базу данных, и возвращается JSON-ответ
    с короткой ссылкой.

    Returns:
        tuple[Response, int]: Ответ Flask в формате JSON и HTTP-статус код.

    Raises:
        InvalidAPIUsage: При отсутствии данных, неверном формате или
        конфликте ID.
    """
    if not request.is_json:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса'
        )
    data = request.get_json(silent=True)
    validate_data(data)

    try:
        urlmap = URLMap.create_urlmap(
            original=data['url'],
            custom_short=data.get('custom_id')
        )
    except ValueError as e:
        raise InvalidAPIUsage(str(e))
    except ShortIDGenerationError as e:
        raise InvalidAPIUsage(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise InvalidAPIUsage(
            f'Произошла ошибка базы данных: {str(e)}',
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return jsonify({
        'url': data['url'],
        'short_link': urlmap.get_short_url()
    }), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/')
def get_original_link(short_id: str) -> tuple[Response, int]:
    """
    Возвращает оригинальную ссылку по короткому идентификатору.

    Args:
        short_id (str): Короткий идентификатор ссылки.

    Returns:
        tuple[Response, int]: Ответ Flask в формате JSON и HTTP-статус код.

    Raises:
        InvalidAPIUsage: Если указанный short_id не найден.
    """
    urlmap = URLMap.get_by_short(short_id)
    if not urlmap:
        raise InvalidAPIUsage(
            'Указанный id не найден', HTTPStatus.NOT_FOUND
        )
    return jsonify({'url': urlmap.original}), HTTPStatus.OK
