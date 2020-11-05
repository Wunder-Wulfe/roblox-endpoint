import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

async def GET(url: str):
    return await client.get(url)
async def textGET(url: str):
    return (await GET(url)).text
async def jsonGET(url: str):
    return (await GET(url)).json()

def serverHTML(sdata, cdata):
    return fr"""
        <html><head>
            <title>MPB players be like</title>
            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:title" content="Should you play MPB Remastered?" />
            <meta name="twitter:description" content="Let's find out" />
            <meta name="twitter:image" content="//t4.rbxcdn.com/5e49e40ecc97314a8707e63fe175a5e2" />
            <link rel="icon" href="//t3.rbxcdn.com/05d00cf38d53e7ebd502ae1acb56570c">
            <link rel="stylesheet" href="/serverCSS.css">
        </head><body>
            <h1 class="header">Should you play {cdata["Name"]}?</h1>
            <div id="result"></div>
            <div id="reason"></div>
        </body></html>
    """

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

app.mount("/", StaticFiles(directory="public_html"), name="static")