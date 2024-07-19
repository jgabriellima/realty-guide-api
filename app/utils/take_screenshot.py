import requests

TARGET_URL = 'https://demo.fincoder.ai'

data = {
    'url': TARGET_URL,
    'options': {
        'fullPage': True,
        'type': 'png',
    }
}


def main(url: str, full_page: bool = True, type: str = 'png'):
    data = {
        'url': url,
        'options': {
            'fullPage': full_page,
            'type': type,
        }
    }
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }

    API_TOKEN = "6R0W53R13FLKASFJ2934JDNHG48AK5510"
    URL = 'https://tpam3pmumu.us-east-1.awsapprunner.com/screenshot'
    response = requests.post(URL, headers=headers, json=data, params={'token': API_TOKEN})
    response.raise_for_status()
    img_bytes = response.content

    #pase to base64
    import base64
    base64.b64encode(img_bytes)
    return base64.b64encode(img_bytes)
