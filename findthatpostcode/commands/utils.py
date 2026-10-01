import requests

GEOPORTAL_API_URL = "https://hub.arcgis.com/api/search/v1/collections/all/items"
GEOPORTAL_DATA_URL = "https://www.arcgis.com/sharing/rest/content/items/{}/data"


def get_latest_geoportal_url(product_code: str) -> str:
    """
    Returns the latest URL for a given product code.
    """
    print(f"Fetching latest URL for product code: {product_code}")
    api_response = requests.get(
        GEOPORTAL_API_URL, params={"q": product_code, "sortBy": "-properties.created"}
    )
    api_response.raise_for_status()
    items = api_response.json()["features"]
    for item in items:
        if item["properties"]["type"] != "CSV Collection":
            continue
        item_id = item["id"]
        url = GEOPORTAL_DATA_URL.format(item_id)
        print(f"Latest URL for product code {product_code}: {url}")
        return url

    raise ValueError(f"No hosted table found for product code {product_code}")
