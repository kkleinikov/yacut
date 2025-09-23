import re

from yacut.constants import URL_MAX_LENGTH, SHORTENED_ID_MAX_LENGTH, CUSTOM_ID_REGEX
from yacut.error_handlers import InvalidAPIUsage




def validate_data(data):
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')


def validate_url(url):
    if not url.strip():
        raise ValueError('URL не может быть пустым')
    if len(url) > URL_MAX_LENGTH:
        raise ValueError(f'URL {url} слишком длинный')


def validate_custom_id(custom_id):
    custom_id = custom_id.strip()
    if (len(custom_id) > SHORTENED_ID_MAX_LENGTH or
            not re.fullmatch(CUSTOM_ID_REGEX, custom_id)):
        raise ValueError('Указано недопустимое имя для короткой ссылки')
