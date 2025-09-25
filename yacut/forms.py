from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from yacut.constants import (CUSTOM_ID_REGEX, SHORTENED_ID_MAX_LENGTH,
                             URL_MAX_LENGTH)


class CreateLinkForm(FlaskForm):
    original_link = StringField(
        'Исходная ссылка',
        validators=[
            DataRequired(message='Это обязательное поле'),
            URL(message='Некорректный формат URL'),
            Length(
                min=1,
                max=URL_MAX_LENGTH,
                message='URL должен быть от 1 до 256 символов'
            )
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        [
            Length(
                max=SHORTENED_ID_MAX_LENGTH,
                message='Длина ИД для короткой ссылки не должна превышать '
                        f'{SHORTENED_ID_MAX_LENGTH} символов'
            ),
            Optional(),
            Regexp(
                CUSTOM_ID_REGEX,
                message='Используйте только латинские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')
