from api.models import Calculation
from api.extensions import db


class TestCreateCalculation:
    """Tests for POST /api/calculations endpoint"""

    def test_create_calculation_success(self, client):
        """Test successful calculation creation"""
        response = client.post(
            "/api/calculations",
            json={"mean": 10.0, "std_dev": 2.0, "target_x": 12.0},
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()

        assert "id" in data
        assert data["mean"] == 10.0
        assert data["std_dev"] == 2.0
        assert data["target_x"] == 12.0
        assert "probability" in data
        assert "chart_base64" in data
        assert "created_at" in data

    def test_create_calculation_missing_field(self, client):
        """Test creation with missing required field"""
        response = client.post(
            "/api/calculations",
            json={"mean": 10.0, "std_dev": 2.0},
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Missing required fields" in data["error"]

    def test_create_calculation_invalid_type(self, client):
        """Test creation with invalid data type"""
        response = client.post(
            "/api/calculations",
            json={"mean": "not_a_number", "std_dev": 2.0, "target_x": 12.0},
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "must be numbers" in data["error"]

    def test_create_calculation_zero_std_dev(self, client):
        """Test creation with zero standard deviation"""
        response = client.post(
            "/api/calculations",
            json={"mean": 10.0, "std_dev": 0.0, "target_x": 12.0},
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "greater than zero" in data["error"]

    def test_create_calculation_negative_std_dev(self, client):
        """Test creation with negative standard deviation"""
        response = client.post(
            "/api/calculations",
            json={"mean": 10.0, "std_dev": -2.0, "target_x": 12.0},
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_calculation_no_json(self, client):
        """Test creation without JSON data"""
        response = client.post("/api/calculations")

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_calculation_empty_json(self, client):
        """Test creation with empty JSON"""
        response = client.post(
            "/api/calculations",
            json={},
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_calculation_with_negative_values(self, client):
        """Test creation with negative mean and target"""
        response = client.post(
            "/api/calculations",
            json={"mean": -10.0, "std_dev": 2.0, "target_x": -8.0},
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["mean"] == -10.0
        assert data["target_x"] == -8.0

    def test_create_calculation_persists_to_db(self, client, app):
        """Test that calculation is persisted to database"""
        response = client.post(
            "/api/calculations",
            json={"mean": 10.0, "std_dev": 2.0, "target_x": 12.0},
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()

        with app.app_context():
            calc = db.session.get(Calculation, data["id"])
            assert calc is not None
            assert calc.mean == 10.0
            assert calc.std_dev == 2.0


class TestListCalculations:
    """Tests for GET /api/calculations endpoint"""

    def test_list_empty(self, client):
        """Test listing when no calculations exist"""
        response = client.get("/api/calculations")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_calculations(self, client, app):
        """Test listing calculations"""
        with app.app_context():
            calc1 = Calculation(mean=10.0, std_dev=2.0, target_x=12.0, probability=0.8413)
            calc2 = Calculation(mean=20.0, std_dev=3.0, target_x=22.0, probability=0.7486)
            db.session.add_all([calc1, calc2])
            db.session.commit()

        response = client.get("/api/calculations")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_list_ordered_by_created_at_desc(self, client, app):
        """Test that calculations are ordered by created_at descending"""
        with app.app_context():
            calc1 = Calculation(mean=10.0, std_dev=2.0, target_x=12.0, probability=0.8413)
            db.session.add(calc1)
            db.session.commit()
            id1 = calc1.id

            calc2 = Calculation(mean=20.0, std_dev=3.0, target_x=22.0, probability=0.7486)
            db.session.add(calc2)
            db.session.commit()
            id2 = calc2.id

        response = client.get("/api/calculations")
        data = response.get_json()

        assert data[0]["id"] == id2  # Most recent first
        assert data[1]["id"] == id1


class TestGetCalculation:
    """Tests for GET /api/calculations/<id> endpoint"""

    def test_get_calculation_success(self, client, app):
        """Test getting a specific calculation"""
        with app.app_context():
            calc = Calculation(mean=10.0, std_dev=2.0, target_x=12.0, probability=0.8413)
            db.session.add(calc)
            db.session.commit()
            calc_id = calc.id

        response = client.get(f"/api/calculations/{calc_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == calc_id
        assert data["mean"] == 10.0
        assert "chart_base64" in data

    def test_get_calculation_not_found(self, client):
        """Test getting non-existent calculation"""
        response = client.get("/api/calculations/999")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "not found" in data["error"].lower()

    def test_get_calculation_regenerates_chart(self, client, app):
        """Test that chart is regenerated on retrieval"""
        with app.app_context():
            calc = Calculation(mean=10.0, std_dev=2.0, target_x=12.0, probability=0.8413)
            db.session.add(calc)
            db.session.commit()
            calc_id = calc.id

        response = client.get(f"/api/calculations/{calc_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert "chart_base64" in data
        assert len(data["chart_base64"]) > 0


class TestDeleteCalculation:
    """Tests for DELETE /api/calculations/<id> endpoint"""

    def test_delete_calculation_success(self, client, app):
        """Test successful deletion"""
        with app.app_context():
            calc = Calculation(mean=10.0, std_dev=2.0, target_x=12.0, probability=0.8413)
            db.session.add(calc)
            db.session.commit()
            calc_id = calc.id

        response = client.delete(f"/api/calculations/{calc_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data
        assert str(calc_id) in data["message"]

        with app.app_context():
            calc = db.session.get(Calculation, calc_id)
            assert calc is None

    def test_delete_calculation_not_found(self, client):
        """Test deleting non-existent calculation"""
        response = client.delete("/api/calculations/999")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "not found" in data["error"].lower()

    def test_delete_calculation_removes_from_db(self, client, app):
        """Test that deletion removes from database"""
        with app.app_context():
            calc = Calculation(mean=10.0, std_dev=2.0, target_x=12.0, probability=0.8413)
            db.session.add(calc)
            db.session.commit()
            calc_id = calc.id

            # Verify it exists
            assert db.session.get(Calculation, calc_id) is not None

        client.delete(f"/api/calculations/{calc_id}")

        with app.app_context():
            # Verify it's gone
            assert db.session.get(Calculation, calc_id) is None


class TestIntegrationFlow:
    """Integration tests for complete workflows"""

    def test_create_list_get_delete_flow(self, client):
        """Test complete CRUD flow"""
        # Create
        create_response = client.post(
            "/api/calculations",
            json={"mean": 10.0, "std_dev": 2.0, "target_x": 12.0},
            content_type="application/json"
        )
        assert create_response.status_code == 201
        calc_id = create_response.get_json()["id"]

        # List
        list_response = client.get("/api/calculations")
        assert list_response.status_code == 200
        assert len(list_response.get_json()) == 1

        # Get
        get_response = client.get(f"/api/calculations/{calc_id}")
        assert get_response.status_code == 200

        # Delete
        delete_response = client.delete(f"/api/calculations/{calc_id}")
        assert delete_response.status_code == 200

        # Verify deleted
        list_response = client.get("/api/calculations")
        assert len(list_response.get_json()) == 0
