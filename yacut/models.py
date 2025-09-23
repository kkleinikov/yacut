from datetime import datetime, timezone
from typing import Any, Dict

from yacut import db
from yacut.constants import URLMAP_VALID_FIELDS, URL_MAX_LENGTH, SHORTENED_ID_MAX_LENGTH


class URLMap(db.Model):
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


    def from_dict(self, data: Dict[str, Any]) -> None:
        """Заполняет атрибуты экземпляра данными из словаря.

        Аргумент:
            data (Dict[str, Any]): Словарь с данными, где ключи соответствуют
                                   именам полей модели.

        Поведение:
            Обходит список допустимых полей и устанавливает значения атрибутов
            только если они присутствуют в переданном словаре. Это позволяет
            обновлять модель частично, без перезаписи всех полей.
        """

        for field in data:
            if field in URLMAP_VALID_FIELDS:
                setattr(self, field, data[field])
