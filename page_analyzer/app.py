import os

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
import psycopg2

from page_analyzer.url_repository import UrlRepository
from page_analyzer.utils import normalize_url, validate
from page_analyzer.parser import extract_page_info


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


conn = psycopg2.connect(app.config['DATABASE_URL'])
repo = UrlRepository(conn)


@app.route('/')
def main():
    return render_template(
        'main.html'
    )


@app.post('/')
def url_post():
    url = request.form.get('url')
    normalized_url = normalize_url(url)
    errors = validate(normalized_url)
    if errors:
        flash('Некорректный URL', category="danger")
        return render_template(
            'main.html',
            url=url
        ), 422

    existing_url = repo.get_url_by_name(normalized_url)

    if existing_url:
        flash('Страница уже существует', category="info")
        id = existing_url['id']
        return redirect(url_for("url_details", id=id))

    id = repo.save_url(normalized_url)
    flash("Страница успешно добавлена", category="success")
    return redirect(url_for("url_details", id=id))


@app.get('/urls/<id>')
def url_details(id):
    messages = get_flashed_messages(with_categories=True)
    url_info = repo.get_url_by_id(id)
    url_checks_details = repo.get_url_checks(id)
    return render_template(
        'url_details.html',
        url=url_info,
        url_checks_details=url_checks_details,
        messages=messages
    )


@app.post('/urls/<id>/checks')
def url_parse_check(id):
    try:
        url_info = repo.get_url_by_id(id)
        url_name = url_info['name']
        url_id = url_info['id']
        url_check_data = extract_page_info(url_name)
        url_check_data['url_id'] = url_id
        repo.save_url_check(url_check_data)
        flash('Страница успешно проверена', category="success")
    except Exception as e:
        flash(f'Ошибка при проверке страницы: {str(e)}', category="danger")

    return redirect(url_for("url_details", id=id))


@app.route('/urls/')
def urls_get():
    urls_info = repo.get_all_urls()
    return render_template(
        'urls.html',
        urls=urls_info,
    )
