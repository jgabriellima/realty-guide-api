import logging

import requests

from app.core.settings import settings
from app.setup_logging import setup_logging
from app.utils.slug import url_to_slug
from app.utils.timer import Timer

API_TOKEN = settings.browserless_key
URL = 'https://browserless-production-cbb6.up.railway.app/screenshot'
TARGET_URL = 'https://ibagy.com.br/imovel/123730/casa-em-condominio-3-quartos-jardim-ribeirao-ribeirao-da-ilha-florianopolis/'

SCRIPT = """
(function(){function removeCookieDialogs(){const cookieDialogs=document.querySelectorAll('[id*="cookie"], [class*="cookie"], [id*="gdpr"], [class*="gdpr"], [id*="consent"], [class*="consent"]');cookieDialogs.forEach(dialog=>dialog.remove());}removeCookieDialogs();function getXPath(element){if(element.id!==''){return'id("'+element.id+'")';}if(element===document.body){return element.tagName.toLowerCase();}var ix=0;var siblings=element.parentNode.childNodes;for(var i=0;i<siblings.length;i++){var sibling=siblings[i];if(sibling===element){return getXPath(element.parentNode)+'/'+element.tagName.toLowerCase()+'['+(ix+1)+']';}if(sibling.nodeType===1&&sibling.tagName===element.tagName){ix++;}}}function addXPathLabel(element){var xpath=getXPath(element);var label=document.createElement('div');label.textContent=xpath;label.style.position='absolute';label.style.backgroundColor='rgba(0, 0, 0, 0.7)';label.style.color='white';label.style.padding='2px 5px';label.style.fontSize='12px';label.style.zIndex='10000';label.style.pointerEvents='none';document.body.appendChild(label);var rect=element.getBoundingClientRect();label.style.top=(window.scrollY+rect.top)+'px';label.style.left=(window.scrollX+rect.left)+'px';}var elements=document.querySelectorAll('*');elements.forEach(function(element){if(element.offsetWidth>0&&element.offsetHeight>0&&element.querySelectorAll('img').length>1){addXPathLabel(element);}});function extractLatLng(){var scripts=document.querySelectorAll('script');for(var i=0;i<scripts.length;i++){var scriptContent=scripts[i].textContent;var latMatch=scriptContent.match(/var\\s+latitude\\s*=\\s*["'](-?\\d+\\.\\d+)["']/);var lngMatch=scriptContent.match(/var\\s+longitude\\s*=\\s*["'](-?\\d+\\.\\d+)["']/);if(latMatch&&lngMatch){return{latitude:latMatch[1],longitude:lngMatch[1]};}}return null;}function extractLatLngFromIframe(){var iframes=document.querySelectorAll('iframe');for(var i=0;i<iframes.length;i++){var src=iframes[i].src||iframes[i].dataset.src;if(src.includes('center=')){var centerPart=src.split('center=')[1].split('&')[0];var decodedCenterPart=decodeURIComponent(centerPart);var coordinates=decodedCenterPart.split(',');if(coordinates.length===2){var latitude=coordinates[0].trim();var longitude=coordinates[1].trim();return{latitude:latitude,longitude:longitude};}}}return null;}var latLng=extractLatLng()||extractLatLngFromIframe();if(latLng){var headerContainer=document.createElement('div');headerContainer.style.position='relative';headerContainer.style.minHeight='50px';headerContainer.style.zIndex='10000';headerContainer.style.backgroundColor='rgba(0, 0, 0, 0.7)';headerContainer.style.textAlign='center';var header=document.createElement('h1');header.textContent=`Location: Latitude ${latLng.latitude}, Longitude ${latLng.longitude}`;header.style.color='white';header.style.padding='10px';header.style.margin='0';header.style.fontSize='24px';headerContainer.appendChild(header);document.body.insertBefore(headerContainer,document.body.firstChild);}})();
"""

headers = {
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json'
}

data = {
    'url': TARGET_URL,
    'options': {
        'fullPage': True,
        'type': 'png',
    },
    'addScriptTag': [
        {
            'content': SCRIPT
        }
    ]
}

with Timer("Screenshot capture", logger=setup_logging(__name__), unit="seconds") as timer:
    try:
        response = requests.post(URL, headers=headers, json=data, params={'token': API_TOKEN})
        response.raise_for_status()
        with open(f'{url_to_slug(TARGET_URL)}.png', 'wb') as f:
            f.write(response.content)
        logging.info('Screenshot taken and saved as screenshot.png')
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to capture screenshot: {e}")
