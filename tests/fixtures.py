import os
import json
from contextlib import contextmanager

import pytest
from flask import appcontext_pushed, g

import dkpostcodes

mock_data = {}
mock_data_dir = os.path.join(os.path.dirname(__file__), 'mock_data')
for i in os.listdir(mock_data_dir):
    with open(os.path.join(mock_data_dir, i)) as a:
        mock_data[i.replace(".json", "")] = json.load(a)


@contextmanager
def db_set(app, db):
    def handler(sender, **kwargs):
        g.db = db
    with appcontext_pushed.connected_to(handler, app):
        yield


@pytest.fixture
def client():
    app = dkpostcodes.create_app()
    app.config['TESTING'] = True
    db = MockElasticsearch()

    with db_set(app, db):
        with app.test_client() as client:
            # with app.app_context():
            #     app.init_db()
            yield client


class MockElasticsearch:

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def search_result_wrapper(hits=[], aggregates=None):
        max_score = max([h.get("_score", 0) for h in hits]) if hits else 0
        result = {
            "took": 1,
            "timed_out": False,
            "_shards": {
                "total": 5,
                "successful": 5,
                "skipped": 0,
                "failed": 0
            },
            "hits": {
                "total": len(hits),
                "max_score": max_score,
                "hits": hits
            }
        }
        if aggregates:
            result["aggregations"] = aggregates
        return result

    def search(self, **kwargs):

        # get some specific queries used in the data
        if kwargs.get("index") == 'geo_area' and kwargs.get("body", {}).get("aggs", {}).get("group_by_type", {}).get("terms", {}).get("field") == 'entity.keyword':
            return self.search_result_wrapper([], {
                "group_by_type": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 455,
                    "buckets": [
                        {
                            "key": "S18",
                            "doc_count": 175741
                        },
                        {
                            "key": "E05",
                            "doc_count": 135306
                        },
                        {
                            "key": "E07",
                            "doc_count": 50868
                        }
                    ]
                }
            })

        # match all queries
        return self.search_result_wrapper(mock_data.get(kwargs["index"], []))

    def get(self, **kwargs):
        potentials = {i.get("_id", "__missing"): i for i in mock_data.get(kwargs["index"], [])}

        if potentials.get(kwargs["id"]):
            return {
                "_version": 9,
                "_seq_no": 694904,
                "_primary_term": 9,
                "found": True,
                **potentials[kwargs["id"]]
            }
        return {
            "_index": kwargs["index"],
            "_type": "_doc",
            "_id": kwargs["id"],
            "found": False
        }