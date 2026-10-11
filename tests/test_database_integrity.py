import pytest
from api import create_app
from api.extensions import db
from api.models import Calculation
from sqlalchemy.exc import IntegrityError


class TestDatabaseIntegrity:
    """Tests for database integrity constraints and validation"""

    def test_std_dev_positive_constraint(self, app):
        """Test that std_dev must be positive (database constraint)"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=-1.0,  # Invalid: negative
                target_x=12.0,
                probability=0.5
            )
            db.session.add(calc)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

    def test_std_dev_zero_constraint(self, app):
        """Test that std_dev cannot be zero (database constraint)"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=0.0,  # Invalid: zero
                target_x=12.0,
                probability=0.5
            )
            db.session.add(calc)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

    def test_probability_range_constraint_upper(self, app):
        """Test that probability cannot be greater than 1"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=1.5  # Invalid: > 1
            )
            db.session.add(calc)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

    def test_probability_range_constraint_lower(self, app):
        """Test that probability cannot be negative"""
        with app.app_context():
            calc = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=-0.1  # Invalid: < 0
            )
            db.session.add(calc)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

    def test_probability_edge_cases_valid(self, app):
        """Test that probability 0 and 1 are valid"""
        with app.app_context():
            # Probability = 0
            calc1 = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=0.0
            )
            db.session.add(calc1)
            db.session.commit()

            assert calc1.id is not None
            assert calc1.probability == 0.0

            # Probability = 1
            calc2 = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=1.0
            )
            db.session.add(calc2)
            db.session.commit()

            assert calc2.id is not None
            assert calc2.probability == 1.0

    def test_created_at_index_exists(self, app):
        """Test that created_at has an index for performance"""
        with app.app_context():
            # Get table metadata
            table = Calculation.__table__

            # Check if created_at column has index=True
            created_at_col = table.c.created_at
            assert created_at_col.index is True

    def test_bulk_insert_performance(self, app):
        """Test bulk insert of calculations"""
        with app.app_context():
            calculations = [
                Calculation(
                    mean=float(i),
                    std_dev=2.0,
                    target_x=float(i + 1),
                    probability=0.5
                )
                for i in range(100)
            ]

            db.session.bulk_save_objects(calculations)
            db.session.commit()

            count = Calculation.query.count()
            assert count == 100

    def test_database_transaction_rollback(self, app):
        """Test that failed transactions properly rollback"""
        with app.app_context():
            # Add valid calculation
            calc1 = Calculation(
                mean=10.0,
                std_dev=2.0,
                target_x=12.0,
                probability=0.5
            )
            db.session.add(calc1)
            db.session.commit()

            initial_count = Calculation.query.count()

            # Try to add invalid calculation
            calc2 = Calculation(
                mean=10.0,
                std_dev=-1.0,  # Invalid
                target_x=12.0,
                probability=0.5
            )
            db.session.add(calc2)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            # Verify count hasn't changed
            final_count = Calculation.query.count()
            assert final_count == initial_count
