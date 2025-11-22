from http import HTTPStatus

import pytest


class TestPlaceRouter:
    """Tests for the /api/v2/places router endpoints"""

    def test_read_place(self, client):
        """Test GET /api/v2/places/{placecode}"""
        # Using a place code that should exist in mock data
        rv = client.get("/api/v2/places/IPN0000543")
        assert rv.status_code == HTTPStatus.OK

        if rv.status_code == HTTPStatus.OK:
            data = rv.json()
            assert "code" in data
            assert "name" in data

    def test_read_place_not_found(self, client):
        """Test GET /api/v2/places/{placecode} with non-existent place"""
        rv = client.get("/api/v2/places/NOTFOUND123")
        assert rv.status_code == HTTPStatus.NOT_FOUND

    def test_read_nearby_places(self, client):
        """Test GET /api/v2/places/{placecode}/places"""
        rv = client.get("/api/v2/places/IPN0000543/places")
        assert rv.status_code == HTTPStatus.OK

        if rv.status_code == HTTPStatus.OK:
            data = rv.json()
            assert isinstance(data, list)

    def test_read_nearby_places_not_found(self, client):
        """Test GET /api/v2/places/{placecode}/places with non-existent place"""
        rv = client.get("/api/v2/places/NOTFOUND123/places")
        assert rv.status_code == HTTPStatus.NOT_FOUND

    def test_read_nearby_postcodes(self, client):
        """Test GET /api/v2/places/{placecode}/postcodes"""
        rv = client.get("/api/v2/places/IPN0000543/postcodes")
        assert rv.status_code == HTTPStatus.OK

        if rv.status_code == HTTPStatus.OK:
            data = rv.json()
            assert isinstance(data, list)

    def test_read_nearby_postcodes_with_within_param(self, client):
        """Test GET /api/v2/places/{placecode}/postcodes with within parameter"""
        rv = client.get("/api/v2/places/IPN0000543/postcodes?within=500")
        assert rv.status_code == HTTPStatus.OK

        if rv.status_code == HTTPStatus.OK:
            data = rv.json()
            assert isinstance(data, list)

    def test_read_nearby_postcodes_not_found(self, client):
        """Test GET /api/v2/places/{placecode}/postcodes with non-existent place"""
        rv = client.get("/api/v2/places/NOTFOUND123/postcodes")
        assert rv.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("origin", ["http://example.com", None])
    def test_read_place_cors(self, client, origin):
        """Test CORS headers on place endpoints"""
        headers = {}
        if origin:
            headers["Origin"] = origin

        rv = client.get("/api/v2/places/IPN0000543", headers=headers)
        assert rv.status_code == HTTPStatus.OK

        if origin and rv.status_code == HTTPStatus.OK:
            assert rv.headers.get("Access-Control-Allow-Origin") == "*"

    @pytest.mark.parametrize("within", [100, 500, 1000, 5000])
    def test_read_nearby_postcodes_various_distances(self, client, within):
        """Test GET /api/v2/places/{placecode}/postcodes with various within parameters"""
        rv = client.get(f"/api/v2/places/IPN0000543/postcodes?within={within}")
        assert rv.status_code == HTTPStatus.OK
