from http import HTTPStatus

import pytest


class TestAreaTypeRouter:
    """Tests for the /api/v2/areatypes router endpoints"""

    def test_read_areatype(self, client):
        """Test GET /api/v2/areatypes/{areatype}"""
        rv = client.get("/api/v2/areatypes/lsoa11")
        assert rv.status_code == HTTPStatus.OK

    def test_read_areatype_entity(self, client):
        """Test GET /api/v2/areatypes/{areatype} with entity code"""
        # Entity codes may not be valid enum values
        rv = client.get("/api/v2/areatypes/E05")
        assert rv.status_code == HTTPStatus.OK

    def test_read_areatype_not_found(self, client):
        """Test GET /api/v2/areatypes/{areatype} with non-existent type"""
        rv = client.get("/api/v2/areatypes/NOTFOUND")
        assert rv.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_read_areatype_areas(self, client):
        """Test GET /api/v2/areatypes/{areatype}/areas"""
        rv = client.get("/api/v2/areatypes/lsoa11/areas")
        assert rv.status_code == HTTPStatus.OK

        if rv.status_code == HTTPStatus.OK:
            data = rv.json()
            assert isinstance(data, list)

    def test_read_areatype_areas_entity(self, client):
        """Test GET /api/v2/areatypes/{areatype}/areas with entity code"""
        rv = client.get("/api/v2/areatypes/E05/areas")
        assert rv.status_code == HTTPStatus.OK

    def test_read_areatype_areas_not_found(self, client):
        """Test GET /api/v2/areatypes/{areatype}/areas with non-existent type"""
        rv = client.get("/api/v2/areatypes/NOTFOUND/areas")
        assert rv.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("areatype", ["lsoa11", "ward", "laua"])
    def test_read_areatype_valid_types(self, client, areatype):
        """Test GET /api/v2/areatypes/{areatype} with various valid types"""
        rv = client.get(f"/api/v2/areatypes/{areatype}")
        assert rv.status_code == HTTPStatus.OK

    @pytest.mark.parametrize("origin", ["http://example.com", None])
    def test_read_areatype_cors(self, client, origin):
        """Test CORS headers on areatype endpoints"""
        headers = {}
        if origin:
            headers["Origin"] = origin

        rv = client.get("/api/v2/areatypes/lsoa11", headers=headers)
        assert rv.status_code == HTTPStatus.OK

        if origin and rv.status_code == HTTPStatus.OK:
            assert rv.headers.get("Access-Control-Allow-Origin") == "*"
