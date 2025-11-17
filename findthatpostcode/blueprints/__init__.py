from fastapi import FastAPI

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

app = FastAPI()

app.include_router(areas.bp)
app.include_router(addtocsv.bp)
app.include_router(areatypes.bp)
app.include_router(places.bp)
app.include_router(points.bp)
# app.include_router(postcodes.bp)
# app.include_router(reconcile.bp)
# app.include_router(search.bp)
# app.include_router(tools.bp)
