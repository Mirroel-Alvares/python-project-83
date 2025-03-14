from urllib.parse import urlparse

import validators


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
    netloc = parsed_url.netloc
    normalized_url = f'https://{netloc}'
    return normalized_url


def validate(url: str):
    """
    Validates a given URL.

    :param url: The URL string to validate.
    :return: A string containing an error message if validation fails;
            an empty string if the URL is valid.
             Possible error messages include:
             - "URL exceeds 255 characters" if the URL length
                is greater than 255.
             - "Invalid URL" if the URL format is incorrect.
    """
    error = ""
    if len(url) > 255:
        error = "URL превышает 255 символов"
    if not validators.url(url):
        error = "Некорректный URL"
    return error
