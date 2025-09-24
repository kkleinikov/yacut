import random
import string

from yacut.constants import MAX_GEN_ATTEMPTS, SHORTENED_ID_GEN_LENGTH
from yacut.models import URLMap


def get_unique_short_id(length=SHORTENED_ID_GEN_LENGTH):
    """
    Генерирует уникальную короткую ссылку случайным образом.

    Функция создаёт случайную строку из заглавных и строчных букв английского
    алфавита и цифр длиной SHORTENED_ID_GEN_LENGTH символов, которая будет
    использоваться как уникальный идентификатор для короткой ссылки.
    Если сгенерированная строка уже существует в базе данных, то
    генерация повторяется до тех пор, пока не будет найдено свободное значение.

    Returns:
        str: Строка длиной SHORTENED_ID_GEN_LENGTH символов,
        состоящая из букв и цифр.

    Args:
        Эта функция не принимает аргументов.

    Raises:
        RuntimeError: Если невозможно создать уникальный short_id
                (например, из-за истощения всех возможных комбинаций).

    Examples:
        >>> get_unique_short_id()
        'aB3x9K'
    """
    selected_symbols = string.ascii_letters + string.digits
    attempts = 0

    while True:
        new_id = ''.join(random.choices(selected_symbols, k=length))
        if not URLMap.query.filter_by(short=new_id).first():
            return new_id

        attempts += 1
        if attempts > MAX_GEN_ATTEMPTS:
            raise RuntimeError(
                f'Превышено максимальное количество попыток: '
                f'{MAX_GEN_ATTEMPTS}, для генерации уникального short_id'
            )
