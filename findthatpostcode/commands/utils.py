import json

import click
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

GEOPORTAL_API_URL = "https://hub.arcgis.com/api/search/v1/collections/all/items"
GEOPORTAL_DATA_URL = "https://www.arcgis.com/sharing/rest/content/items/{}/data"


def get_latest_geoportal_url(product_code: str) -> str:
    """
    Returns the latest URL for a given product code.
    """
    click.echo(f"Fetching latest URL for product code: {product_code}")
    api_response = requests.get(
        GEOPORTAL_API_URL, params={"q": product_code, "sortBy": "-properties.created"}
    )
    api_response.raise_for_status()
    item = api_response.json()["features"][0]["id"]
    url = GEOPORTAL_DATA_URL.format(item)
    click.echo(f"Latest URL for product code {product_code}: {url}")
    return url


def bulk_upload(
    items: list[dict], es: Elasticsearch, es_index: str, item_type: str
) -> None:
    click.echo(f"[{item_type}] Processed {len(items):,.0f} {item_type}")
    click.echo(f"[elasticsearch] {len(items):,.0f} {item_type} to save")
    result_count, error_count = bulk(es, items, stats_only=True)
    click.echo(f"[elasticsearch] saved {result_count} {item_type} to {es_index} index")
    click.echo(f"[elasticsearch] {error_count} errors reported")


def json_to_python(file_path: str) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # output the JSON data as a Python dictionary
    with open(file_path.replace(".json", ".py"), "w", encoding="utf-8") as f:
        f.write("# Auto-generated from JSON file\n")
        # create an enum from the keys
        f.write("import enum\n\n")
        f.write("class AreaTypeEnum(str, enum.Enum):\n")
        for key in data.keys():
            f.write(f'    {key.upper()} = "{key}"\n')
        f.write("\n")
        f.write("AREA_TYPES = {\n")
        # write the dictionary - replacing the keys with the enum references
        for key, value in data.items():
            # add countries to the value if not present
            value["countries"] = list(set([e[0] for e in value["entities"]]))
            f.write(f"    AreaTypeEnum.{key.upper()}: {repr(value)},\n")
        f.write("}\n")
