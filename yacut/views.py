from typing import Union

from flask import Response, flash, redirect, render_template
from sqlalchemy.exc import SQLAlchemyError

from yacut import app, db
from yacut.exceptions import ShortIDGenerationError
from yacut.forms import CreateLinkForm
from yacut.models import URLMap


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
    original_link = form.original_link.data.strip()

    try:
        urlmap = URLMap.create_urlmap(
            original=original_link,
            custom_short=custom_id
        )
        short_url = urlmap.get_short_url()

    except ValueError as e:
        flash(str(e), 'error')
        return render_template('index.html', form=form)
    except ShortIDGenerationError as e:
        flash(
            f'Не удалось создать уникальную короткую ссылку: {str(e)}',
            'error'
        )
        return render_template('index.html', form=form)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Произошла ошибка: {str(e)}', 'error')
        app.logger.error(f'Ошибка базы данных: {e}')
        return render_template('index.html', form=form)

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
