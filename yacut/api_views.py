from http import HTTPStatus

from flask import jsonify, request, Response
from sqlalchemy.exc import SQLAlchemyError

from yacut import app, db
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.utils import get_unique_short_id
from yacut.validators import validate_custom_id, validate_data, validate_url


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
        validate_url(data['url'])
        custom_id = data.get('custom_id', '').strip()
        if custom_id:
            validate_custom_id(custom_id)
            if URLMap.query.filter_by(short=custom_id).first():
                raise InvalidAPIUsage(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
        else:
            custom_id = get_unique_short_id()

        url_map = URLMap(original=data['url'], short=custom_id)
        db.session.add(url_map)
        db.session.commit()
        return jsonify({
            'url': data['url'],
            'short_link': f'{request.host_url.rstrip("/")}/{custom_id}'
        }), HTTPStatus.CREATED

    except ValueError as e:
        raise InvalidAPIUsage(str(e))
    except SQLAlchemyError as e:
        db.session.rollback()
        raise InvalidAPIUsage(
            f'Произошла ошибка базы данных: {str(e)}',
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


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
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
