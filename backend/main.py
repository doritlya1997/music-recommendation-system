from fastapi import FastAPI
from .database import engine, Base
from .routers import songs
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Include the router
app.include_router(songs.router)

# serve static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")
