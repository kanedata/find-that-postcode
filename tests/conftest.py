import copy
import json
import os
from contextlib import contextmanager

import pytest
from flask import appcontext_pushed, g

import findthatpostcode

mock_data = {}
mock_data_dir = os.path.join(os.path.dirname(__file__), "mock_data")
for i in os.listdir(mock_data_dir):
    with open(os.path.join(mock_data_dir, i)) as a:
        mock_data[i.replace(".json", "")] = json.load(a)


@contextmanager
def db_set(app, db, s3_client):
    def handler(sender, **kwargs):
        g.db = db
        g.s3_client = s3_client

    with appcontext_pushed.connected_to(handler, app):
        yield


@pytest.fixture
def client():
    app = findthatpostcode.create_app()
    app.config["TESTING"] = True
    db = MockElasticsearch()
    s3_client = MockBoto3()

    with db_set(app, db, s3_client):
        with app.test_client() as client:
            # with app.app_context():
            #     app.init_db()
            yield client


class MockBoto3:
    def __init__(self, *args, **kwargs):
        pass

    def download_fileobj(self, bucket, filepath, fileobj, **kwargs):
        fileobj.write(json.dumps(mock_data.get("geo_boundary")).encode("utf-8"))

    def upload_fileobj(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass


class MockElasticsearch:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def search_result_wrapper(hits=[], aggregates=None, scroll=None):
        max_score = max([h.get("_score", 0) for h in hits]) if hits else 0
        result = {
            "took": 1,
            "timed_out": False,
            "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
            "hits": {"total": len(hits), "max_score": max_score, "hits": hits},
        }
        if aggregates:
            result["aggregations"] = aggregates
        if scroll:
            result["_scroll_id"] = 1

        return result

    def search(self, **kwargs):

        index = kwargs.get("index").split(",")

        # get some specific queries used in the data
        if (
            "geo_area" in index
            and kwargs.get("body", {})
            .get("aggs", {})
            .get("group_by_type", {})
            .get("terms", {})
            .get("field")
            == "entity.keyword"
        ):
            return self.search_result_wrapper(
                [],
                {
                    "group_by_type": {
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 455,
                        "buckets": [
                            {"key": "S18", "doc_count": 175741},
                            {"key": "E05", "doc_count": 135306},
                            {"key": "E07", "doc_count": 50868},
                        ],
                    }
                },
            )
        if (
            "geo_area" in index
            and kwargs.get("body", {})
            .get("aggs", {})
            .get("group_by_type", {})
            .get("terms", {})
            .get("field")
            == "type.keyword"
        ):
            return self.search_result_wrapper(
                [],
                {
                    "group_by_type": {
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 455,
                        "buckets": [
                            {"key": "cty", "doc_count": 175741},
                            {"key": "laua", "doc_count": 135306},
                            {"key": "lsoa11", "doc_count": 50868},
                        ],
                    }
                },
            )

        # match all queries
        hits = []
        for i in index:
            hits.extend(copy.deepcopy(mock_data.get(i, [])))
        hits = hits[: kwargs.get("size", 10)]

        # if there's a sort parameter then include a sort array
        if kwargs.get("body", {}).get("sort", []):
            for h in hits:
                h["sort"] = [68.9707515287199]

        return self.search_result_wrapper(hits, scroll=kwargs.get("scroll"))

    def get(self, **kwargs):
        potentials = {
            i.get("_id", "__missing"): i for i in mock_data.get(kwargs["index"], [])
        }

        if potentials.get(kwargs["id"]):
            return {
                "_version": 9,
                "_seq_no": 694904,
                "_primary_term": 9,
                "found": True,
                **copy.deepcopy(potentials[kwargs["id"]]),
            }
        return {
            "_index": kwargs["index"],
            "_type": "_doc",
            "_id": kwargs["id"],
            "found": False,
        }

    def scroll(self, body=None, scroll_id=None, **kwargs):
        result = self.search_result_wrapper()
        result["_scroll_id"] = None
        return result

    def clear_scroll(self, **kwargs):
        pass
