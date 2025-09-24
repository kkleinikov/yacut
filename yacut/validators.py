import re
from typing import Dict, Any

from yacut.constants import (CUSTOM_ID_REGEX, SHORTENED_ID_MAX_LENGTH,
                             URL_MAX_LENGTH)
from yacut.error_handlers import InvalidAPIUsage


def validate_data(data: Dict[str, Any]) -> None:
    """
    Проверяет, что тело запроса содержит минимально необходимые данные.

    Raises:
        InvalidAPIUsage: Если тело запроса отсутствует или не содержит
        поле 'url'.
    """
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')


def validate_url(url: str) -> None:
    """
    Проверяет корректность URL на соответствие требованиям.

    Raises:
        ValueError: Если URL пустой или превышает максимальную длину.
    """
    if not url.strip():
        raise ValueError('URL не может быть пустым')
    if len(url) > URL_MAX_LENGTH:
        raise ValueError(f'URL {url} слишком длинный')


def validate_custom_id(custom_id: str) -> None:
    """
    Проверяет корректность пользовательского ID короткой ссылки.

    Пользовательский ID должен состоять только из латинских букв и цифр
    и не превышать максимальную длину.

    Raises:
        ValueError: Если ID некорректен по формату или длине.
    """
    custom_id = custom_id.strip()
    if (len(custom_id) > SHORTENED_ID_MAX_LENGTH or
            not re.fullmatch(CUSTOM_ID_REGEX, custom_id)):
        raise ValueError('Указано недопустимое имя для короткой ссылки')
