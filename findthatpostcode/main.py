import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration

from findthatpostcode.blueprints import app as legacy_app
from findthatpostcode.routers import router as api_router
from findthatpostcode.routers.legacy import router as legacy_router
from findthatpostcode.settings import ENVIRONMENT, SENTRY_DSN, STATIC_DIR

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FastApiIntegration()],
        environment=ENVIRONMENT,
        traces_sample_rate=0.005,
        profiles_sample_rate=0.005,
    )


app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

app.include_router(legacy_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v2")

app.mount("/", legacy_app)  # Mount the legacy FastAPI app at the root

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    # allow_credentials=True,
    # allow_methods=["*"],
    # allow_headers=["*"],
)
