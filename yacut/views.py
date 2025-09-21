from flask import render_template, request, redirect

from yacut import app, db
from yacut.forms import CreateLinkForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = CreateLinkForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    form_short_id = form.custom_id.data.strip()
    if form_short_id and URLMap.query.filter_by(short=form_short_id).first():
        return render_template(
            'index.html',
            form=form,
            error='Предложенный вариант ИД для короткой ссылки '
                  f'{form_short_id} уже существует.'
        )

    original_link = form.original_link.data
    new_short_id = form_short_id or get_unique_short_id()

    url_map = URLMap(original=original_link, short=new_short_id)
    db.session.add(url_map)
    db.session.commit()

    base_url = request.host_url.rstrip('/')
    return render_template(
        'index.html',
        form=form,
        short_link=f'{base_url}/{new_short_id}'
    )


@app.route('/<str:short_id>')
def redirect_to_original(short_id):
    url_map = URLMap.query.get_or_404(short_id)
    return redirect(url_map.original)
