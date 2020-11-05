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

def serverHTML(sdata, cdata, tdata, idata):
    return fr"""
        <html><head>
            <title>{cdata["Name"]} players be like</title>
            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:title" content="Should you play {cdata["Name"]}?" />
            <meta name="twitter:description" content="Let's find out" />
            <meta name="twitter:image" content="{tdata.data[0].imageUrl}" />
            <link rel="icon" href="{idata.data[0].imageUrl}">
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
    response = await jsonGET(fr"//games.roblox.com/v1/games/{placeId}/servers/Public")
    if "errors" in response:
        return serverErr
    else:
		productInfo = await jsonGET(fr"//api.roblox.com/marketplace/productinfo?assetId={placeId}")
        return serverHTML(
            response, 
            productInfo,
			await jsonGET(fr"//thumbnails.roblox.com/v1/assets?assetIds={placeId}&size=768x432"),
			await jsonGET(fr"//thumbnails.roblox.com/v1/assets?assetIds={productInfo.IconImageAssetId}&size=110x110&isCircular=true")
        )

app.mount("/", StaticFiles(directory="public_html"), name="static")