import httpx
from fastapi import FastAPI
from fastapi.responses import *

app = FastAPI(
    title = "Roblox Endpoint",
    description = "Unofficial hub for useful Roblox API interaction",
    openapi_tags = [
        {
            "name": "Servers",
            "description": "Find server information for places"
        }
    ]
)


client = httpx.AsyncClient()

async def GET(url: string):
    return client.get(url)
async def textGET(url: string):
    return (await GET(url)).text
async def jsonGET(url: string):
    return (await GET(url)).json()

def serverHTML(sdata, cdata):
    return fr"""<html><head></head><body>
        <h1 class="header">Should you play {cdata.Name}?</h1>
        <div id="result"></div>
        <div id="reason"></div>
    </body></html>"""

serverErr = r"""
<html><head></head><body>place does not exist</body></html>
"""

@app.get("/servers/{placeId}", tags = ["Servers"], response_class = HTMLResponse)
async def server_data(placeId: int):
    response = await jsonGET(fr"https://games.roblox.com/v1/games/{placeId}/servers/Public")
    if "errors" in response:
        return serverErr
    else:
        return serverHTML(
            response, 
            await jsonGET(fr"https://api.roblox.com/marketplace/productinfo?assetId={placeId}")
        )
