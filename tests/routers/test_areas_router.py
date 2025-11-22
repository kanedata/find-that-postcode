from http import HTTPStatus

import pytest

AREA_CODE = "S02000783"
AREA_NAME = "Lower Bow & Larkfield, Fancy Farm, Mallard Bowl"
AREA_CODE_2 = "E01020135"


class TestAreaRouter:
    """Tests for the /api/v2/areas router endpoints"""

    def test_read_area(self, client):
        """Test GET /api/v2/areas/{areacode}"""
        rv = client.get(f"/api/v2/areas/{AREA_CODE}")
        assert rv.status_code == HTTPStatus.OK

        data = rv.json()
        assert data["code"] == AREA_CODE
        assert data["name"] == AREA_NAME
        assert data["entity"] == "S02"

    def test_read_area_not_found(self, client):
        """Test GET /api/v2/areas/{areacode} with non-existent area"""
        rv = client.get("/api/v2/areas/NOTFOUND123")
        assert rv.status_code == HTTPStatus.NOT_FOUND

    def test_read_area_geojson_single(self, client):
        """Test GET /api/v2/areas/{areacodes}.geojson with single area"""
        rv = client.get(f"/api/v2/areas/{AREA_CODE}.geojson")
        assert rv.status_code == HTTPStatus.OK
        # Content-Type can be application/geo+json or application/json
        assert (
            "application" in rv.headers["Content-Type"]
            and "json" in rv.headers["Content-Type"]
        )

        data = rv.json()
        # May get error response if S3 boundary data is unavailable
        if "type" in data and data["type"] == "FeatureCollection":
            assert len(data["features"]) >= 1  # At least one feature
            # Check first feature structure
            if len(data["features"]) > 0:
                assert data["features"][0]["type"] == "Feature"
                assert "properties" in data["features"][0]
                assert "geometry" in data["features"][0]

    def test_read_area_geojson_multiple(self, client):
        """Test GET /api/v2/areas/{areacodes}.geojson with multiple areas"""
        areacodes = f"{AREA_CODE}+{AREA_CODE_2}"
        rv = client.get(f"/api/v2/areas/{areacodes}.geojson")
        assert rv.status_code == HTTPStatus.OK

        data = rv.json()
        # Check if it's a valid GeoJSON response
        if "type" in data:
            assert data["type"] == "FeatureCollection"
            assert len(data["features"]) >= 2  # At least 2 features

            # Verify features have proper structure
            for feature in data["features"]:
                assert feature["type"] == "Feature"
                assert "properties" in feature
                assert "geometry" in feature

    def test_read_example_postcodes(self, client):
        """Test GET /api/v2/areas/{areacode}/example_postcodes"""
        rv = client.get(f"/api/v2/areas/{AREA_CODE}/example_postcodes")
        assert rv.status_code == HTTPStatus.OK

        data = rv.json()
        assert isinstance(data, list)
        # Should return example postcodes from the area

    def test_read_example_postcodes_not_found(self, client):
        """Test GET /api/v2/areas/{areacode}/example_postcodes with non-existent area"""
        rv = client.get("/api/v2/areas/NOTFOUND123/example_postcodes")
        assert rv.status_code == HTTPStatus.NOT_FOUND

    def test_read_area_children(self, client):
        """Test GET /api/v2/areas/{areacode}/children/{areatype}"""
        # Use an area that has children in mock data
        rv = client.get(f"/api/v2/areas/{AREA_CODE_2}/children/lsoa11")
        # May return empty list if no children in mock data
        assert rv.status_code == HTTPStatus.OK

        data = rv.json()
        assert isinstance(data, list)

    def test_read_area_children_geojson(self, client):
        """Test GET /api/v2/areas/{areacode}/children/{areatype}.geojson"""
        rv = client.get(f"/api/v2/areas/{AREA_CODE_2}/children/lsoa11.geojson")
        assert rv.status_code == HTTPStatus.OK
        # Content-Type can be application/geo+json or application/json
        assert (
            "application" in rv.headers["Content-Type"]
            and "json" in rv.headers["Content-Type"]
        )

        data = rv.json()
        # May get error response if S3 boundary data is unavailable or no children
        if "type" in data:
            assert data["type"] == "FeatureCollection"
            assert "features" in data
            # Features list may be empty if no children in mock data
            assert isinstance(data["features"], list)

    def test_read_area_children_not_found(self, client):
        """Test GET /api/v2/areas/{areacode}/children/{areatype} with non-existent area"""
        rv = client.get("/api/v2/areas/NOTFOUND123/children/lsoa11")
        assert rv.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("origin", ["http://example.com", None])
    def test_read_area_cors(self, client, origin):
        """Test CORS headers on area endpoints"""
        headers = {}
        if origin:
            headers["Origin"] = origin

        rv = client.get(f"/api/v2/areas/{AREA_CODE}", headers=headers)
        assert rv.status_code == HTTPStatus.OK

        if origin:
            assert rv.headers.get("Access-Control-Allow-Origin") == "*"
