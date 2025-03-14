import requests
from bs4 import BeautifulSoup


def extract_page_info(url):
    """
    Extracts information from a web page given its URL.

    :param url: The URL of the web page to extract information from.
    :return: A dictionary containing the HTTP status code, H1 text, title text,
            and meta description of the page.
             The dictionary has the following keys:
             - 'status_code': The HTTP status code of the response.
             - 'h1': The text of the first H1 tag on the page,
                or an empty string if not found.
             - 'title': The text of the title tag,
                or an empty string if not found.
             - 'description': The content of the meta description tag,
                or an empty string if not found.
    :raises Exception: If there is an error while making the request to the URL.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        h1 = soup.h1.text if soup.h1 else ''
        title = soup.title.text if soup.title else ''
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'] if description_tag else ''

        return {
            'status_code': response.status_code,
            'h1': h1,
            'title': title,
            'description': description,
        }
    except requests.RequestException as e:
        raise Exception(f"Ошибка при запросе к URL: {str(e)}")
