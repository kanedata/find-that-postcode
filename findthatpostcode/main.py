from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from findthatpostcode import create_app

flask_app = create_app()
app = FastAPI()


@app.get("/api/v1/")
def read_main():
    return {"message": "Hello World"}


app.mount("/", WSGIMiddleware(flask_app))
