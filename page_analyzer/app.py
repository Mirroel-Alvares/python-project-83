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

from page_analyzer.parser import extract_page_info
from page_analyzer.url_repository import UrlRepository
from page_analyzer.utils import normalize_url, validate


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlRepository(app.config['DATABASE_URL'])


def flash_and_redirect(message, category, endpoint, **kwargs):
    """
    Sends a message to the user and redirects to the specified route.

    :param message: The message to display.
    :param category: The category of the message (e.g., 'success', 'danger').
    :param endpoint: The name of the route to redirect to.
    :param kwargs: Additional parameters for the route.
    :return: Redirect to the specified route.
    """
    flash(message, category=category)
    return redirect(url_for(endpoint, **kwargs))


@app.route('/')
def main():
    return render_template('main.html')


@app.post('/')
def url_post():
    """
    Handles POST requests to add a new URL.

    :return: Redirects to the main page with
    a message about the result of the operation.
    """
    url = request.form.get('url')
    errors = validate(url)
    if errors:
        return flash_and_redirect(
            f'{errors}', 'danger', 'main', url=url
        ), 422
    normalized_url = normalize_url(url)

    existing_url = repo.get_url_by_name(normalized_url)

    if existing_url:
        return flash_and_redirect(
            'Страница уже существует', 'info',
            'url_details', id=existing_url['id']
        )

    url_id = repo.save_url(normalized_url)
    if not url_id:
        return flash_and_redirect(
            'Ошибка при сохранении URL', 'danger', 'main', url=url
        ), 500

    return flash_and_redirect(
        "Страница успешно добавлена", "success", "url_details", id=url_id
    )


@app.get('/urls/<id>')
def url_details(id):
    """
    Handles GET requests to display details of a specific URL.

    :param id: The ID of the URL to retrieve information for.
    :return: Renders the template with URL details and its checks.
    """
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
    """
    Handles POST requests to check the specified URL.

    :param id: The ID of the URL to check.
    :return: Redirects to the URL details page with
    a message about the result of the check.
    """
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
    """
    Handles GET requests to retrieve a list of all URLs.

    :return: Renders the template with a list of all URLs.
    """
    urls_info = repo.get_all_urls()
    return render_template(
        'urls.html',
        urls=urls_info,
    )
