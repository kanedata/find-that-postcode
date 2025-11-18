from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from findthatpostcode.blueprints import (
    addtocsv,
    areas,
    areatypes,
    places,
    points,
    postcodes,
    reconcile,
    search,
    tools,
)
from findthatpostcode.controllers.areas import area_types_count
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.utils import templates

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.get("/")
def index(es: ElasticsearchDep, request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html.j2",
        context={"result": area_types_count(es)},
        media_type="text/html",
    )


@app.get("/robots.txt")
def robots(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="robots.txt",
        media_type="text/plain",
    )


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html.j2",
        media_type="text/html",
    )


app.include_router(areas.bp)
app.include_router(addtocsv.bp)
app.include_router(areatypes.bp)
app.include_router(places.bp)
app.include_router(points.bp)
app.include_router(postcodes.bp)
app.include_router(reconcile.bp)
app.include_router(search.bp)
app.include_router(tools.bp)


api = APIRouter(tags=["Legacy"])

api.include_router(areas.api)
api.include_router(areatypes.api)
api.include_router(places.api)
api.include_router(points.api)
api.include_router(postcodes.api)
api.include_router(reconcile.api)
