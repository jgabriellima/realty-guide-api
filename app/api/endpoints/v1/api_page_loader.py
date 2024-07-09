import httpx
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import HTMLResponse

from app.utils.html_injection import generate_script

page_loader = APIRouter()


@page_loader.get("/inject_script", response_class=HTMLResponse)
async def inject_script(url: str, mark_image: bool = False, mark_map: bool = False, mark_all: bool = False,
                        specific_ids: str = Query(None), specific_classes: str = Query(None)):
    specific_ids_list = specific_ids.split(',') if specific_ids else []
    specific_classes_list = specific_classes.split(',') if specific_classes else []

    script = generate_script(mark_image=mark_image, mark_map=mark_map, mark_all=mark_all,
                             specific_ids=specific_ids_list, specific_classes=specific_classes_list)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch the URL")

    html_content = response.text
    modified_html = html_content.replace("</body>", f"<script>{script}</script></body>")

    return HTMLResponse(content=modified_html, status_code=200)
