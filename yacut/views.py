from typing import Union

from flask import flash, redirect, render_template, url_for, Response
from sqlalchemy.exc import SQLAlchemyError

from yacut import app, db
from yacut.forms import CreateLinkForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view() -> str:
    """
    Обрабатывает GET и POST-запросы к главной странице.

    При POST-запросе создаёт новую запись в базе данных на основе формы,
    генерирует короткую ссылку и отображает её пользователю.

    Returns:
        str: HTML-шаблон главной страницы с заполненной формой и сообщением
        о результате.
    """
    form = CreateLinkForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    custom_id = form.custom_id.data
    if custom_id and URLMap.query.filter_by(short=custom_id).first():
        flash('Предложенный вариант короткой ссылки уже существует.',
              'error')
        return render_template('index.html', form=form)

    url_map = URLMap(
        original=form.original_link.data,
        short=custom_id or get_unique_short_id()
    )
    try:
        db.session.add(url_map)
        db.session.commit()
        short_url = url_for(
            'redirect_to_original',
            short=url_map.short,
            _external=True
        )
        flash('Ссылка успешно создана', 'link-ready')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Произошла ошибка ({e}) при сохранении ссылки.',
              'error')
        app.logger.error("Database error: %s", e)

    return render_template(
        'index.html',
        form=form,
        link=short_url
    )


@app.route('/<string:short>', methods=['GET'])
def redirect_to_original(short: str) -> Union[Response, str]:
    """
    Перенаправляет пользователя по короткой ссылке.

    Args:
        short (str): Короткий идентификатор, используемый для поиска
        оригинальной ссылки.

    Returns:
        Response: HTTP-перенаправление на оригинальную ссылку.
        str: Если не найдено — Flask автоматически вернёт 404.
    """
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)
