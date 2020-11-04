from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/servers/{placeId}")
async def findPlace(placeId: int = 4953508391):
    return {"test": placeId}
