from datetime import datetime, timezone
from typing import Any, Dict

from yacut import db
from yacut.constants import (SHORTENED_ID_MAX_LENGTH, URL_MAX_LENGTH)


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

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует экземпляр модели в словарь для сериализации в JSON.

        Возвращает:
            Dict[str, Any]: Словарное представление модели.
        """
        return {
            'original': self.original,
            'short': self.short
        }
