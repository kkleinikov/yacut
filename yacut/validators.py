from typing import Any, Dict

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
