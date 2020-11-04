from fastapi import FastAPI

app = FastAPI(
    title = "Roblox Endpoint",
    description = "Unofficial hub for useful Roblox API interaction",
    openapi_tags = [
        {
            "name": "pf",
            "description": "Find server information for a place"
        }
    ]
)

@app.get("/servers/{placeId}", tags = ["pf"])
async def find_place(placeId: int):
    return {"test": placeId}
