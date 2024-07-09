def generate_script_to_mark_elements(mark_image=False, mark_map=False, mark_all=False, specific_ids=None,
                                     specific_classes=None, remove_headers=False,
                                     remove_nav=False,
                                     remove_footers=False,
                                     remove_ads=False, remove_forms=False, show_only_image_urls=False):
    if specific_ids is None:
        specific_ids = []
    if specific_classes is None:
        specific_classes = []

    # Script para mostrar apenas URLs de imagens
    if show_only_image_urls:
        script_parts = [
            "(function(){",
            "function createImageTable(urls){",
            "var table=document.createElement('table');",
            "table.style.width='100%';",
            "table.style.borderCollapse='collapse';",
            "table.style.marginTop='50px';",
            "table.style.fontSize='16px';",
            "table.style.fontWeight='bold';",
            "table.style.tableLayout='fixed';",
            "var domain=urls[0].match(/https?:\\/\\/([^\\/]+)/)[1];",
            "var headerRow=table.insertRow();",
            "var headerCell=headerRow.insertCell();",
            "headerCell.colSpan=1;",
            "headerCell.style.fontSize='20px';",
            "headerCell.style.textAlign='center';",
            "headerCell.textContent='Images from '+domain;",
            "urls.forEach(function(url){",
            "var row=table.insertRow();",
            "var cell=row.insertCell();",
            "cell.style.padding='5px';",
            "cell.style.textAlign='center';",
            "var urlElement=document.createElement('div');",
            "urlElement.textContent=url;",
            "urlElement.style.wordWrap='break-word';",
            "cell.appendChild(urlElement);",
            "});",
            "return table;",
            "}",
            "function addImageTableToPage(){",
            "var containers=document.querySelectorAll('div, section, article, main');",
            "var urlsToTable=[];",
            "var urlSet=new Set;",
            "var excludedPatterns=['openstreetmap.org','logo','icon','favicon','sprite'];",
            "function isExcluded(url){",
            "return excludedPatterns.some(pattern=>url.includes(pattern));",
            "}",
            "containers.forEach(function(container){",
            "var images=container.querySelectorAll('img');",
            "if(images.length>1){",
            "images.forEach(function(image){",
            "if(image.offsetWidth>0&&image.offsetHeight>0&&!urlSet.has(image.src)&&!isExcluded(image.src)){",
            "urlsToTable.push(image.src);",
            "urlSet.add(image.src);",
            "}",
            "});",
            "}",
            "var links=container.querySelectorAll('a[href]');",
            "links.forEach(function(link){",
            "var href=link.href;",
            "if(href.match(/\\.(jpeg|jpg|gif|png|svg)$/)&&!urlSet.has(href)&&!isExcluded(href)){",
            "urlsToTable.push(href);",
            "urlSet.add(href);",
            "}",
            "});",
            "});",
            "document.body.innerHTML='';",
            "if(urlsToTable.length>0){",
            "var table=createImageTable(urlsToTable);",
            "document.body.appendChild(table);",
            "}",
            "}",
            "addImageTableToPage();",
            "})();"
        ]
        return ''.join(script_parts)

    # Base script
    script_parts = [
        "(function(){",
        "function removeElements(selectors){const elements=document.querySelectorAll(selectors);elements.forEach(el=>el.remove());}",
        "function removeCookieDialogs(){",
        "const cookieDialogs=document.querySelectorAll('[id*=\"cookie\"], [class*=\"cookie\"], [id*=\"gdpr\"], [class*=\"gdpr\"], [id*=\"consent\"], [class*=\"consent\"], [id*=\"lgpd\"], [class*=\"lgpd\"]');",
        "cookieDialogs.forEach(dialog=>dialog.remove());",
        "const allElements=document.querySelectorAll('*');",
        "allElements.forEach(function(element){",
        "if(element && element.innerText && element.innerText.includes('Cookies')){",
        "element.remove();",
        "}});",
        "}",
        "removeCookieDialogs();"
    ]

    if remove_headers:
        script_parts.append(
            "removeElements('header, [id*=\"header\"], [class*=\"header\"]');"
        )

    if remove_nav:
        script_parts.append(
            "removeElements('nav');"
        )


    if remove_footers:
        script_parts.append(
            "removeElements('footer, [id*=\"footer\"], [class*=\"footer\"]');"
        )

    if remove_ads:
        script_parts.append(
            "removeElements('[id*=\"google_ads\"], [class*=\"google_ads\"], [id*=\"ad\"], [class*=\"ad\"]');"
        )

    if remove_forms:
        script_parts.append(
            "removeElements('form');"
        )

    if mark_image:
        script_parts.append(
            "var containers=document.querySelectorAll('div, section, article, main');"
            "containers.forEach(function(container){"
            "var images=container.querySelectorAll('img');"
            "if(images.length>1){"
            "images.forEach(function(image){"
            "if(image.offsetWidth>0&&image.offsetHeight>0){"
            "addXPathLabel(image);}});}});"
        )

    if mark_map:
        script_parts.append(
            "var elements=document.querySelectorAll('iframe[src*=\"google.com/maps\"], iframe[src*=\"map\"]');"
            "elements.forEach(function(element){"
            "if(element.offsetWidth>0&&element.offsetHeight>0){"
            "addXPathLabel(element);}});"
        )

    if mark_all:
        script_parts.append(
            "var elements=document.querySelectorAll('*');"
            "elements.forEach(function(element){"
            "if(element.offsetWidth>0&&element.offsetHeight>0){"
            "addXPathLabel(element);}});"
        )

    if specific_ids:
        script_parts.append(
            "var ids=[" + ",".join(f"'{id_}'" for id_ in specific_ids) + "];"
                                                                         "ids.forEach(function(id){"
                                                                         "var element=document.getElementById(id);"
                                                                         "if(element&&element.offsetWidth>0&&element.offsetHeight>0){"
                                                                         "addXPathLabel(element);}});"
        )

    if specific_classes:
        script_parts.append(
            "var classes=[" + ",".join(f"'{cls}'" for cls in specific_classes) + "];"
                                                                                 "classes.forEach(function(cls){"
                                                                                 "var elements=document.getElementsByClassName(cls);"
                                                                                 "Array.from(elements).forEach(function(element){"
                                                                                 "if(element.offsetWidth>0&&element.offsetHeight>0){"
                                                                                 "addXPathLabel(element);}});"
                                                                                 "});"
        )

    # Adding the common functions
    script_parts.extend([
        "function getXPath(element){if(element.id!==''){return'id(\"'+element.id+'\")';}if(element===document.body){return element.tagName.toLowerCase();}var ix=0;var siblings=element.parentNode.childNodes;for(var i=0;i<siblings.length;i++){var sibling=siblings[i];if(sibling===element){return getXPath(element.parentNode)+'/'+element.tagName.toLowerCase()+'['+(ix+1)+']';}if(sibling.nodeType===1&&sibling.tagName===element.tagName){ix++;}}}",
        "function addXPathLabel(element){var xpath=getXPath(element);var label=document.createElement('div');label.textContent=xpath;label.style.position='absolute';label.style.backgroundColor='rgba(0, 0, 0, 0.7)';label.style.color='white';label.style.padding='2px 5px';label.style.fontSize='16px';label.style.zIndex='10000';label.style.pointerEvents='none';document.body.appendChild(label);var rect=element.getBoundingClientRect();label.style.top=(window.scrollY+rect.top)+'px';label.style.left=(window.scrollX+rect.left)+'px';}",
        "function extractLatLng(){var scripts=document.querySelectorAll('script');for(var i=0;i<scripts.length;i++){var scriptContent=scripts[i].textContent;var latMatch=scriptContent.match(/var\\s+latitude\\s*=\\s*[\"](-?\\d+\\.\\d+)[\"]/);var lngMatch=scriptContent.match(/var\\s+longitude\\s*=\\s*[\"](-?\\d+\\.\\d+)[\"]/);if(latMatch&&lngMatch){return{latitude:latMatch[1],longitude:lngMatch[1]};}}return null;}",
        "function extractLatLngFromIframe(){var iframes=document.querySelectorAll('iframe');for(var i=0;i<iframes.length;i++){var src=iframes[i].src||iframes[i].dataset.src;if(src.includes('center=')){var centerPart=src.split('center=')[1].split('&')[0];var decodedCenterPart=decodeURIComponent(centerPart);var coordinates=decodedCenterPart.split(',');if(coordinates.length===2){var latitude=coordinates[0].trim();var longitude=coordinates[1].trim();return{latitude:latitude,longitude:longitude};}}}return null;}",
        "var latLng=extractLatLng()||extractLatLngFromIframe();if(latLng){var headerContainer=document.createElement('div');headerContainer.style.position='relative';headerContainer.style.minHeight='50px';headerContainer.style.zIndex='10000';headerContainer.style.backgroundColor='rgba(0, 0, 0, 0.7)';headerContainer.style.textAlign='center';var header=document.createElement('h1');header.textContent=`Location: Latitude ${latLng.latitude}, Longitude ${latLng.longitude}`;header.style.color='white';header.style.padding='10px';header.style.margin='0';header.style.fontSize='24px';headerContainer.appendChild(header);document.body.insertBefore(headerContainer,document.body.firstChild);}",
        "})();"
    ])

    return ''.join(script_parts)


if __name__ == '__main__':
    script = generate_script_to_mark_elements(mark_image=False, mark_map=True, remove_headers=True, remove_footers=True,
                                              remove_ads=True, remove_forms=True, show_only_image_urls=True)
    print(script)
