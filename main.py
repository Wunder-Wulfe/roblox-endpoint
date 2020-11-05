import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import *
from jinja2 import Environment, FileSystemLoader

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

file_loader = FileSystemLoader("templates")
env = Environment(loader=file_loader)

template = env.get_template("serverHTML.html")

def serverHTML(sdata, cdata, tdata, idata):
	return template.render(
		sdata = sdata,
		cdata = cdata,
		tdata = tdata['data'][0],
		idata = idata['data'][0]
	)

serverErr = r"""
<html><head></head><body>place does not exist</body></html>
"""

@app.get("/servers/{placeId}", tags = ["Servers"], response_class = HTMLResponse)
async def server_data(placeId: int):
	response = await jsonGET(fr"https://games.roblox.com/v1/games/{placeId}/servers/Public")
	if "errors" in response:
		return serverErr
	else:
		productInfo = await jsonGET(fr"https://api.roblox.com/marketplace/productinfo?assetId={placeId}")
		return serverHTML(
			response, 
			productInfo,
			await jsonGET(fr"https://thumbnails.roblox.com/v1/assets?assetIds={placeId}&size=768x432"),
			await jsonGET(fr"https://thumbnails.roblox.com/v1/assets?assetIds={productInfo['IconImageAssetId']}&size=50x50&isCircular=true")
		)

app.mount("/", StaticFiles(directory="public_html"), name="static")