import requests


def get_text_from_url(url: str):
    url = f'https://r.jina.ai/{url}'
    headers = {
        "Accept": "application/json",
        "X-No-Cache": "true"
    }
    response = requests.get(url, headers=headers)
    return response.json()


if __name__ == '__main__':
    url = 'https://ibagy.com.br/imovel/123730/casa-em-condominio-3-quartos-jardim-ribeirao-ribeirao-da-ilha-florianopolis/'

    extracted_data = get_text_from_url(url)
    title = extracted_data.get('title', '')
    content = extracted_data.get('content', '')

    print(f'Title: {title}')
    print(f'Content: {content}')
