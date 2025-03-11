import requests
from bs4 import BeautifulSoup


def extract_page_info(url):
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
