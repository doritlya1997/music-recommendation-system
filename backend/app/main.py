from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import songs

app = FastAPI()

# Include the router
app.include_router(songs.router)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="./frontend"), name="static")


@app.get("/")
async def read_root():
    return FileResponse("./frontend/index.html")
