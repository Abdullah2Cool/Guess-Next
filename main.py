from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# create the app
app = FastAPI()

# mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# main entry point
@app.get("/")
async def homepage():
    # redirect to index.html
    return RedirectResponse("/static/index.html")

