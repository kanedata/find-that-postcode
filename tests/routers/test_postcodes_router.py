import pytest

POSTCODE = "EX36 4AT"
LAT = 51.01467
LON = -3.83317
AREA_CODE = "E01020135"


class TestPostcodeRouter:
    """Tests for the /api/v2/postcodes router endpoints"""

    def test_read_postcode(self, client):
        """Test GET /api/v2/postcodes/{postcode}"""
        rv = client.get(f"/api/v2/postcodes/{POSTCODE}")
        assert rv.status_code == 200

        data = rv.json()
        assert data["pcds"] == POSTCODE
        # Location is nested
        assert data["location"]["lat"] == LAT
        assert data["location"]["lon"] == LON

    def test_read_postcode_normalized(self, client):
        """Test GET /api/v2/postcodes/{postcode} with non-normalized format"""
        rv = client.get("/api/v2/postcodes/EX364AT")
        assert rv.status_code == 200

        data = rv.json()
        assert data["pcds"] == POSTCODE

    def test_read_postcode_not_found(self, client):
        """Test GET /api/v2/postcodes/{postcode} with non-existent postcode"""
        rv = client.get("/api/v2/postcodes/NOTFOUND123")
        assert rv.status_code == 404

    def test_read_nearby_places(self, client):
        """Test GET /api/v2/postcodes/{postcode}/places"""
        rv = client.get(f"/api/v2/postcodes/{POSTCODE}/places")
        assert rv.status_code == 200

        data = rv.json()
        assert isinstance(data, list)

    def test_read_nearby_places_not_found(self, client):
        """Test GET /api/v2/postcodes/{postcode}/places with non-existent postcode"""
        rv = client.get("/api/v2/postcodes/NOTFOUND123/places")
        assert rv.status_code == 404

    def test_nearest_to_point(self, client):
        """Test GET /api/v2/postcodes/nearest/{lat},{lon}"""
        rv = client.get(f"/api/v2/postcodes/nearest/{LAT},{LON}")
        assert rv.status_code == 200

        data = rv.json()
        assert "pcds" in data
        assert "location" in data

    def test_nearest_to_point_different_location(self, client):
        """Test GET /api/v2/postcodes/nearest/{lat},{lon} with different coordinates"""
        rv = client.get(
            "/api/v2/postcodes/nearest/51.5074,-0.1278"
        )  # London coordinates
        assert rv.status_code == 200

        data = rv.json()
        assert "pcds" in data

    @pytest.mark.parametrize(
        "lat,lon",
        [
            (51.01467, -3.83317),
            (51.5074, -0.1278),
            (53.4808, -2.2426),  # Manchester
        ],
    )
    def test_nearest_to_point_various_locations(self, client, lat, lon):
        """Test GET /api/v2/postcodes/nearest/{lat},{lon} with various coordinates"""
        rv = client.get(f"/api/v2/postcodes/nearest/{lat},{lon}")
        assert rv.status_code == 200

        data = rv.json()
        assert "pcds" in data
        assert "location" in data

    @pytest.mark.parametrize("origin", ["http://example.com", None])
    def test_read_postcode_cors(self, client, origin):
        """Test CORS headers on postcode endpoints"""
        headers = {}
        if origin:
            headers["Origin"] = origin

        rv = client.get(f"/api/v2/postcodes/{POSTCODE}", headers=headers)
        assert rv.status_code == 200

        if origin:
            assert rv.headers.get("Access-Control-Allow-Origin") == "*"

    def test_read_postcode_structure(self, client):
        """Test the structure of postcode response"""
        rv = client.get(f"/api/v2/postcodes/{POSTCODE}")
        assert rv.status_code == 200

        data = rv.json()
        # Check for expected top-level fields
        expected_fields = ["pcds", "location", "areas"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

        # Check location structure
        assert "lat" in data["location"]
        assert "lon" in data["location"]

        # Check areas structure (nested)
        assert "lsoa11" in data["areas"] or "lsoa21" in data["areas"]
        assert "msoa11" in data["areas"] or "msoa21" in data["areas"]

    def test_read_postcode_location(self, client):
        """Test that postcode has location data"""
        rv = client.get(f"/api/v2/postcodes/{POSTCODE}")
        assert rv.status_code == 200

        data = rv.json()
        assert "location" in data
        assert data["location"]["lat"] == LAT
        assert data["location"]["lon"] == LON

    @pytest.mark.parametrize(
        "endpoint",
        [
            f"/api/v2/postcodes/{POSTCODE}",
            f"/api/v2/postcodes/{POSTCODE}/places",
            f"/api/v2/postcodes/nearest/{LAT},{LON}",
        ],
    )
    def test_postcode_endpoints_json_response(self, client, endpoint):
        """Test that all postcode endpoints return JSON"""
        rv = client.get(endpoint)
        assert rv.status_code == 200
        assert rv.headers["Content-Type"].startswith("application/json")

    def test_read_postcode_case_insensitive(self, client):
        """Test GET /api/v2/postcodes/{postcode} with different case"""
        rv = client.get("/api/v2/postcodes/ex36 4at")
        assert rv.status_code == 200

        data = rv.json()
        assert data["pcds"] == POSTCODE
