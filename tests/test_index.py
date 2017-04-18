mport server
import bottle
import pytest
from elasticsearch import Elasticsearch

app = bottle.default_app()
app.config["es"] = Elasticsearch()
app.config["es_index"] = "postcode"

def test_index():
    pass
