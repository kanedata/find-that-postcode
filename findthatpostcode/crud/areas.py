import io
import json
from typing import Generator

from botocore.exceptions import ClientError
from elasticsearch import Elasticsearch
from mypy_boto3_s3 import S3Client

from findthatpostcode.areatypes import AreaTypeEnum
from findthatpostcode.crud.utils import get_or_404
from findthatpostcode.schema import Area, Postcode
from findthatpostcode.schema.db import Area as AreaDocument
from findthatpostcode.schema.db import Postcode as PostcodeDocument
from findthatpostcode.schema.geojson import (
    Geometry,
    GeometryCollection,
    geometry_from_dict,
)
from findthatpostcode.settings import S3_BUCKET


def get_areas(areacodes: list[str], es: Elasticsearch) -> Generator[Area, None, None]:
    results = AreaDocument.mget(areacodes, es)
    for result in results:
        if isinstance(result, AreaDocument):
            yield result.to_schema()


def get_area(areacode: str, es: Elasticsearch) -> Area:
    return get_or_404(AreaDocument, es, areacode).to_schema()


def get_area_boundary(
    area: Area, s3_client: S3Client
) -> Geometry | GeometryCollection | None:
    buffer = io.BytesIO()
    area_code = area.code
    if not area_code:
        return None
    prefix = area_code[0:3]
    try:
        s3_client.download_fileobj(
            S3_BUCKET,
            "%s/%s.json" % (prefix, area_code),
            buffer,
        )
        boundary = json.loads(buffer.getvalue().decode("utf-8"))
        return geometry_from_dict(boundary.get("geometry"))
    except ClientError:
        return None


def get_example_postcodes(
    area: Area, es: Elasticsearch, postcodes_to_return: int = 5
) -> list[Postcode]:
    query = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must_not": {"exists": {"field": "doterm"}},
                        "must": {"query_string": {"query": area.code}},
                    }
                },
                "random_score": {},
            }
        }
    }
    result = (
        PostcodeDocument.search(using=es)
        .update_from_dict(query)[0:postcodes_to_return]
        .execute()
    )
    if result:
        return [hit.to_schema() for hit in result.hits]  # type: ignore
    return []


def get_child_areas(
    area: Area, areatype: AreaTypeEnum, es: Elasticsearch
) -> list[Area]:
    query = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"parent.keyword": area.code}},
                    {"term": {"type.keyword": areatype.value}},
                ]
            }
        }
    }
    result = AreaDocument.search(using=es).update_from_dict(query)[0:100].execute()
    if result:
        return [hit.to_schema(es) for hit in result.hits]  # type: ignore
    return []
