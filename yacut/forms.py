from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, URL, Length, Regexp


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
                max=16,
                message='Длина ИД для короткой ссылки не должна превышать '
                        '16 символов'
            ),
            Regexp(
                r'^[a-zA-Z0-9]+$',
                message='Используйте только латинские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')