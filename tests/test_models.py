import pytest
from datetime import datetime, timezone
from api.models import Calculation
from api.extensions import db


class TestCalculationModel:
    """Tests for Calculation model"""

    def test_create_calculation(self, app):
        """Test creating a calculation"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=0.8413
            )
            db.session.add(calc)
            db.session.commit()

            assert calc.id is not None
            assert calc.mean == 10.0
            assert calc.std_dev == 2.0
            assert calc.target_x == 12.0
            assert calc.probability == 0.8413
            assert calc.created_at is not None

    def test_created_at_auto_set(self, app):
        """Test that created_at is automatically set"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=0.8413
            )
            db.session.add(calc)
            db.session.commit()

            # Verify created_at was set
            assert calc.created_at is not None
            assert isinstance(calc.created_at, datetime)

    def test_to_dict(self, app):
        """Test to_dict method"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=0.8413
            )
            db.session.add(calc)
            db.session.commit()

            result = calc.to_dict()

            assert isinstance(result, dict)
            assert result["id"] == calc.id
            assert result["mean"] == 10.0
            assert result["std_dev"] == 2.0
            assert result["target_x"] == 12.0
            assert result["probability"] == 0.8413
            assert "created_at" in result
            assert isinstance(result["created_at"], str)

    def test_repr(self, app):
        """Test __repr__ method"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=0.8413
            )
            db.session.add(calc)
            db.session.commit()

            repr_str = repr(calc)
            assert "Calculation" in repr_str
            assert str(calc.id) in repr_str
            assert "0.8413" in repr_str

    def test_nullable_constraints(self, app):
        """Test that required fields cannot be null"""
        with app.app_context():
            # Missing mean
            calc = Calculation(
                std_dev=2.0,
                target_x=12.0,
                probability=0.8413
            )
            db.session.add(calc)

            with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
                db.session.commit()

    def test_query_ordering(self, app):
        """Test querying calculations"""
        with app.app_context():
            calc1 = Calculation(mean=10.0, std_dev=2.0, target_x=12.0, probability=0.8413)
            calc2 = Calculation(mean=20.0, std_dev=3.0, target_x=22.0, probability=0.7486)

            db.session.add_all([calc1, calc2])
            db.session.commit()

            results = Calculation.query.all()
            assert len(results) == 2

    def test_negative_values_allowed(self, app):
        """Test that negative values are allowed"""
        with app.app_context():
            calc = Calculation(
                mean=-10.0,
                std_dev=2.0,
                target_x=-8.0,
                probability=0.8413
            )
            db.session.add(calc)
            db.session.commit()

            assert calc.mean == -10.0
            assert calc.target_x == -8.0

    def test_float_precision(self, app):
        """Test float precision storage"""
        with app.app_context():
            calc = Calculation(
                mean=10.123456789,
                std_dev=2.987654321,
                target_x=12.555555555,
                probability=0.841344746
            )
            db.session.add(calc)
            db.session.commit()

            retrieved = db.session.get(Calculation, calc.id)
            assert abs(retrieved.mean - 10.123456789) < 0.0001
            assert abs(retrieved.std_dev - 2.987654321) < 0.0001
