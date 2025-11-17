import os

from a2wsgi import WSGIMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from findthatpostcode.blueprints.areas import bp as areas_bp

# from findthatpostcode.flask_app import app as flask_app
from findthatpostcode.routers import router as api_router
from findthatpostcode.routers.legacy import router as legacy_router
from findthatpostcode.settings import STATIC_DIR

app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

app.include_router(areas_bp)
app.include_router(legacy_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v2")


# app.mount("/", WSGIMiddleware(flask_app))
