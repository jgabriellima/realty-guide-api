import re


def url_to_slug(url: str) -> str:
    # Remove 'https://', 'http://', and 'www.' from the URL
    if url.startswith('https://'):
        url = url[len('https://'):]
    elif url.startswith('http://'):
        url = url[len('http://'):]

    if url.startswith('www.'):
        url = url[len('www.'):]

    # Remove trailing slash if present
    if url.endswith('/'):
        url = url[:-1]

    # Remove all non-alphanumeric characters except hyphens and slashes
    url = re.sub(r'[^\w\-\/]', ' ', url)

    # Replace sequences of spaces or slashes with a single hyphen
    slug = re.sub(r'[\s\/]+', '-', url)

    # Convert to lowercase
    slug = slug.lower()

    return slug
