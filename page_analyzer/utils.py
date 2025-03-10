import validators
from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """
    Normalizes the given URL to 'https://www.example.com' format.

    Parameters:
    url (str): The URL to normalize. May not contain protocol and 'www.'.

    Returns:
    str: The normalized URL in 'https://www.example.com' format.
    If the URL is invalid, returns an empty string.

    Example:
    normalize_url("example.com")
    'https://www.example.com'

    normalize_url("http://example.com/path")
    'https://www.example.com/path'
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'https://' + url
    if not parsed_url.netloc.startswith('www.'):
        netloc = 'www.' + parsed_url.netloc
    else:
        netloc = parsed_url.netloc
    normalized_url = f'https://{netloc}{parsed_url.path}'
    return normalized_url


def validate(url: str) -> list:
    """
   Validates the given URL and checks for common issues.

    Args:
        url (str): The URL string to be validated.

    Returns:
        list: A list of error messages. If no errors are found,
        an empty list is returned.

    Errors:
        - "Invalid URL": If the URL does not match the standard format.
        - "URL is required": If the URL is an empty string.
        - "URL exceeds 255 characters": If the length of the URL is
           greater than 255 characters.
    """
    errors = []
    if not url:
        errors.append("URL обязателен")
    if len(url) > 255:
        errors.append("URL превышает 255 символов")
    if not validators.url(url):
        errors.append("Некорректный URL")
    return errors