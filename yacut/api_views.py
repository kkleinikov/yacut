from http import HTTPStatus

from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from yacut import app, db
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.utils import get_unique_short_id
from yacut.validators import validate_url, validate_custom_id, validate_data


@app.route('/api/id/', methods=['POST'])
def add_short_id():
    if not request.is_json or request.json is None:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса'
        )
    data = request.get_json()
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
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), HTTPStatus.OK