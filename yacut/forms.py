from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from yacut.constants import SHORTENED_ID_MAX_LENGTH


class CreateLinkForm(FlaskForm):
    original_link = StringField(
        'Исходная ссылка',
        validators=[
            DataRequired(message='Это обязательное поле'),
            URL(message='Некорректный формат URL')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        [
            Length(
                max=SHORTENED_ID_MAX_LENGTH,
                message='Длина ИД для короткой ссылки не должна превышать '
                        '16 символов'
            ),
            Optional(),
            Regexp(
                r'^[a-zA-Z0-9]+$',
                message='Используйте только латинские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')