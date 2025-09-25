import random
import re
import string
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from flask import url_for
from sqlalchemy.exc import SQLAlchemyError

from yacut import db
from yacut.constants import (CUSTOM_ID_REGEX, MAX_GEN_ATTEMPTS,
                             SHORTENED_ID_GEN_LENGTH, SHORTENED_ID_MAX_LENGTH,
                             URL_MAX_LENGTH)
from yacut.exceptions import ShortIDGenerationError


class URLMap(db.Model):
    """
    Модель данных для хранения оригинальной и короткой ссылок.

    Представляет собой запись в базе данных, где хранятся:
    - оригинальная (полная) ссылка,
    - сгенерированная или пользовательская короткая ссылка,
    - дата создания записи.

    Используется в приложении YaCut для управления короткими ссылками.

    Attributes:
        id (int): Уникальный идентификатор записи (автоматически генерируется).
        original (str): Оригинальная, длинная ссылка.
        short (str): Короткая ссылка, по которой будет происходить редирект.
        created_at (datetime): Дата и время создания записи.
    """

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(URL_MAX_LENGTH), nullable=False)
    short = db.Column(
        db.String(SHORTENED_ID_MAX_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<URLMap {self.short}>'

    @staticmethod
    def get_by_short(short_id: str) -> Optional['URLMap']:
        """
        Возвращает объект URLMap по короткому идентификатору.

        Args:
            short_id (str): Короткий идентификатор ссылки.

        Returns:
            Optional[URLMap]: Объект URLMap, если найден, иначе None.
        """
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def get_unique_short_id():
        """
        Генерирует уникальную короткую ссылку случайным образом.

        Функция создаёт случайную строку из заглавных и строчных букв
        английского алфавита и цифр длиной `length` символов, которая будет
        использоваться как уникальный идентификатор для короткой ссылки.
        Если сгенерированная строка уже существует в базе данных, то
        генерация повторяется до тех пор, пока не будет найдено свободное
        значение.

        Returns:
            str: Строка длиной `length`, состоящая из букв и цифр.

        Raises:
            RuntimeError: Если невозможно создать уникальный short_id
                (например, из-за истощения всех возможных комбинаций).
        """
        selected_symbols = string.ascii_letters + string.digits

        for _ in range(MAX_GEN_ATTEMPTS):
            new_id = ''.join(random.choices(
                selected_symbols,
                k=SHORTENED_ID_GEN_LENGTH
            )
            )
            if not URLMap.get_by_short(new_id):
                return new_id

        raise ShortIDGenerationError(
            f'Не удалось создать уникальный short_id за {MAX_GEN_ATTEMPTS} '
            'попыток.'
        )

    @staticmethod
    def create_urlmap(original: str, custom_short: str = None) -> 'URLMap':
        """
        Создаёт новую запись в базе данных.

        Если передан `custom_short`, проверяет его на уникальность.
        Если не передан — генерирует случайный уникальный short_id.
        Добавляет запись в сессию и сохраняет в БД.

        Args:
            original (str): Оригинальная длинная ссылка.
            custom_short (str, optional): Пользовательский short_id.

        Returns:
            URLMap: Созданный объект.

        Raises:
            ValueError: Если указан недопустимый или занятый short_id.
            SQLAlchemyError: При ошибке сохранения в БД.
        """
        if custom_short:
            if (not re.fullmatch(CUSTOM_ID_REGEX, custom_short)
                    or len(custom_short) > SHORTENED_ID_MAX_LENGTH):
                raise ValueError(
                    'Указано недопустимое имя для короткой ссылки'
                )

            if URLMap.get_by_short(custom_short):
                raise ValueError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )

            short_id = custom_short
        else:
            short_id = URLMap.get_unique_short_id()

        urlmap = URLMap(original=original, short=short_id)

        try:
            db.session.add(urlmap)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

        return urlmap

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует экземпляр модели в словарь для сериализации в JSON.

        Возвращает:
            Dict[str, Any]: Словарное представление модели.
        """
        return {
            'original': self.original,
            'short': self.short
        }

    def get_short_url(self) -> str:
        """
        Возвращает полную короткую ссылку на основе текущего short_id.

        Returns:
            str: Полная короткая ссылка (например, http://localhost/abc123).
        """
        return url_for(
            'redirect_to_original',
            short=self.short,
            _external=True
        )
