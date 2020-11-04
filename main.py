import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

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


@app.get("/servers/{placeId}", tags = ["Servers"])
async def find_place(placeId: int):
    return requests.get(
        f"https://games.roblox.com/v1/games/{placeId}/servers/Public"
    )
