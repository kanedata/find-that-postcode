import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration

from findthatpostcode.blueprints import api as legacy_router
from findthatpostcode.blueprints import app as legacy_app
from findthatpostcode.routers import router as api_router
from findthatpostcode.settings import ENVIRONMENT, SENTRY_DSN, STATIC_DIR

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FastApiIntegration()],
        environment=ENVIRONMENT,
        traces_sample_rate=0.005,
        profiles_sample_rate=0.005,
    )


app = FastAPI(
    title="Find that Postcode",
    version="2.0",
    description="""
This API presents data on UK postcodes and geographical areas, based on open data released by
the [Office for National Statistics](https://geoportal.statistics.gov.uk/) and
[Ordnance Survey](https://osdatahub.os.uk/).
""",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {
            "name": "Area Type",
            "description": "Get information about the type of area",
        },
        {
            "name": "Area",
            "description": "Get information about an area",
        },
        {
            "name": "Place",
            "description": "Get information about a place in the UK",
        },
        {
            "name": "Point",
            "description": "Get information about the nearest postcode to a given lat/long",
        },
        {
            "name": "Postcode",
            "description": "Get information about an individual postcode",
        },
        {
            "name": "GeoJSON",
            "description": "Endpoints that return GeoJSON formatted data",
        },
        {
            "name": "Legacy",
            "description": "Legacy API endpoints from v1 of the Find that Postcode API",
        },
    ],
    contact={
        "name": "Find that Postcode",
        "url": "https://findthatpostcode.uk",
        "email": "info@findthatpostcode.uk",
    },
    # license_info={
    #     "name": "TBD",
    #     # "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    # },  # @todo License?
    swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
    swagger_css_url="/static/swagger-ui/swagger-ui.css",
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

app.include_router(legacy_router, prefix="/api/v1", deprecated=True)
app.include_router(api_router, prefix="/api/v2")
app.include_router(
    legacy_app, include_in_schema=False
)  # Mount the legacy FastAPI app at the root

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "images/favicon.ico"))


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    if app.openapi_url:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - API Documentation",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/lib/swagger-ui/swagger-ui-bundle.js",
            swagger_css_url="/static/css/swagger-ui.css",
            swagger_favicon_url="/favicon.ico",
            swagger_ui_parameters={
                "defaultModelsExpandDepth": 0,
            },
        )


if app.swagger_ui_oauth2_redirect_url:

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()
