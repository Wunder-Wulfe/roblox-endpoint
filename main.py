import httpx
import urllib
import re
from typing import List, Optional
from fastapi import FastAPI, Path, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import *
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from enum import Enum

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
async def textPOST(url: str, data):
	return (await client.post(url, data = data)).text
async def jsonGET(url: str):
	return (await GET(url)).json()

file_loader = FileSystemLoader("templates")
env = Environment(loader=file_loader)

template = env.get_template("serverHTML.html")

def sweatCount(server, sweats: [int]):
	return sum(player in sweats for player in server['playerIds'])

def rating(voteR):
	if voteR < 0.31:
		return ('alert', 'No.', 'What the fuck is this')
	elif voteR < 0.59:
		return ('alert', 'No.', 'This game has a terrible rating')
	elif voteR < 0.82:
		return ('warn', 'Maybe?', 'This game has a decent rating')
	else:
		return ('success', 'Sure.', 'This game has a good rating')

def getResult(sdata, sweats: [int], voteR):
	if len(sdata['data']) == 0:
		if voteR is not None:
			return rating(voteR)
		else:
			return ('alert', 'No.', 'Nobody is playing this game')
	else:
		if voteR is not None and voteR < 0.59:
			return rating(voteR)
			
		servers = sdata['data']
		maxPlayerServer = None
		maxPlayers = 0
		for i in range(len(servers)):
			server = servers[i]
			if server['playing'] > maxPlayers:
				maxPlayerServer = server
				maxPlayers = server['playing']
		plLimit = max(server['maxPlayers'] for server in servers)
		
		if min(server['ping'] for server in servers) > 500:
			return ('alert', 'No.', 'All servers have awful ping')
		elif min(server['fps'] for server in servers) < 11:
			return ('alert', 'No.', 'All servers have awful framerates')
		elif plLimit > 6:
			sweatInMax = sweatCount(maxPlayerServer, sweats)
			if maxPlayers == 1:
				return ('alert', 'No.', 'Theres only one person per server')
			elif maxPlayers == 2:
				return ('warn', 'Maybe?', 'Looks like theres 1 v 1s going on')
			elif sweatInMax == maxPlayers:
				return ('alert', 'No.', 'Everyone in the biggest server is sweating')
			elif sweatInMax > 0:
				return ('warn', 'Maybe?', 'There are some sweats online')
			elif maxPlayers < 6:
				return ('warn', 'Maybe?', 'There are only a few people playing per server')
				
		if voteR is not None:
			return rating(voteR)
		else:
			return ('success', 'Sure.', 'There are quite a few players')

def serverHTML(sdata, cdata, tdata, idata, sweats: [int], placeId: int, voteR):
	resultClass, result, reason = getResult(sdata, sweats, voteR)
	return template.render(
		sdata = sdata,
		cdata = cdata,
		tdata = tdata['data'][0]['imageUrl'] if len(tdata['data']) > 0 else "",
		idata = idata['data'][0]['imageUrl'] if len(idata['data']) > 0 else "",
		resultClass = resultClass,
		result = result,
		reason = reason,
		placeId = placeId
	)

serverErr = r"""
<html><head></head><body>place does not exist</body></html>
"""

@app.get("/servers/{placeId}", tags = ["Servers"], response_class = HTMLResponse)
async def server_data(
		placeId: int = Path(
			5881457140, 
			title = "Place ID",
			description = "The place you wish to get the data for", 
			example = 5881457140
		), 
		sweat: Optional[List[int]] = Query(
			[], 
			title = "Sweat",
			description = "A player you hate playing with", 
			example = [161815003]
		)
	):
	response = await jsonGET(fr"https://games.roblox.com/v1/games/{placeId}/servers/Public")
	if "errors" in response:
		return serverErr
	else:
		productInfo = await jsonGET(fr"https://api.roblox.com/marketplace/productinfo?assetId={placeId}")
		details = await jsonGET(fr"https://api.roblox.com/universes/get-universe-containing-place?placeid={placeId}")
		votes = await jsonGET(fr"https://games.roblox.com/v1/games/{details['UniverseId']}/votes")
		voteTotal = votes['downVotes'] + votes['upVotes']
		if voteTotal == 0:
			voteRatio = None
		else:
			voteRatio = votes['upVotes'] / voteTotal
		return serverHTML(
			response, 
			productInfo,
			await jsonGET(fr"https://thumbnails.roblox.com/v1/assets?assetIds={placeId}&size=768x432&format=Png"),
			await jsonGET(fr"https://thumbnails.roblox.com/v1/assets?assetIds={productInfo['IconImageAssetId']}&size=50x50&format=Png&isCircular=true"),
			sweat,
			placeId,
			voteRatio
		)
		
def escape_string(string: str):
	return string.replace("'", r"\'").replace('"',r'\"')
def encode_hex(string: str):
	return "%%%02X" % ord(string.group(0))
def escape_query(string: str):
	return re.sub(r"\W", encode_hex, string)

searchErr = r"""
<html><head></head><body>no sign was found</body></html>
"""

class SITES(str, Enum):
    signsavvy = "signsavvy"
    handspeak = "handspeak"
searchTemplate = env.get_template("search.html")

@app.get("/sign/{website}", response_class = HTMLResponse)
async def search_sign(
		website: SITES = Path(
			SITES.signsavvy,
			title = "Site",
			description = "The website to search",
			example = SITES.signsavvy
		),
		query: str = Query(
			"hello",
			title = "Query",
			description = "Search term",
			example = "hello"
		)
	):
	if website == SITES.signsavvy:
		page = fr"https://www.signingsavvy.com/search/{escape_query(query)}"
		result = BeautifulSoup(
			await textGET(page),
			'html.parser'
		)
		source = result.find("source")
		if source is not None:
			url = source["src"]
			desc = result.find(class_ = "desc-active")
			if desc is not None:
				mean = desc.find("em").text if desc.find("em") else ""
				return searchTemplate.render(
					website = "SignSavvy",
					url = page,
					sign = escape_string(query).upper(),
					video = "https://www.signingsavvy.com/" + url,
					meaning = mean,
					icon = "https://www.signingsavvy.com/favicon.ico"
				)
	elif website == SITES.handspeak:
		"""
		firstPage = fr"https://www.handspeak.com/word/search/app/app-dictionary.php"
		firstResult = BeautifulSoup(
			await textPOST(firstPage, {"query": query}),
			'html.parser'
		)
		source = firstResult.find("a")
		if source is not None:
			url = source["href"]
			secondPage = "https://www.handspeak.com" + url
			secondResult = BeautifulSoup(
				await textGET(secondPage),
				'html.parser'
			)
			if secondResult is not None:
				video_url = secondResult.find("video")["src"]
				mean = secondResult.find_all("p")[1].text
				return searchTemplate.render(
					website = "HandSpeak",
					url = secondPage,
					sign = escape_string(query).upper(),
					video = "https://www.handspeak.com" + video_url,
					meaning = mean,
					icon = "https://www.handspeak.com/favicon.ico"
				)
		"""
	return searchErr

app.mount("/", StaticFiles(directory="public_html"), name="static")