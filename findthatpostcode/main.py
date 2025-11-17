from a2wsgi import WSGIMiddleware
from fastapi import FastAPI

from findthatpostcode.flask_app import create_app

flask_app = create_app()
app = FastAPI()


@app.get("/api/v1/")
def read_main():
    return {"message": "Hello World"}


app.mount("/", WSGIMiddleware(flask_app))
