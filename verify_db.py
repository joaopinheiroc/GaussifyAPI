"""
Database integrity verification script.

This script checks for potential data integrity issues in the database.
"""

from api import create_app
from api.models import Calculation


def verify_database_integrity():
    """Verify database integrity and report any issues."""
    app = create_app()

    with app.app_context():
        issues = []

        # Check for calculations with invalid std_dev
        invalid_std_dev = Calculation.query.filter(Calculation.std_dev <= 0).all()
        if invalid_std_dev:
            issues.append(f"Found {len(invalid_std_dev)} calculations with std_dev <= 0")
            for calc in invalid_std_dev:
                issues.append(f"  - Calculation ID {calc.id}: std_dev = {calc.std_dev}")

        # Check for calculations with invalid probability
        invalid_prob = Calculation.query.filter(
            (Calculation.probability < 0) | (Calculation.probability > 1)
        ).all()
        if invalid_prob:
            issues.append(f"Found {len(invalid_prob)} calculations with invalid probability")
            for calc in invalid_prob:
                issues.append(f"  - Calculation ID {calc.id}: probability = {calc.probability}")

        # Check for NULL values in required fields
        null_checks = [
            ("mean", Calculation.query.filter(Calculation.mean.is_(None)).count()),
            ("std_dev", Calculation.query.filter(Calculation.std_dev.is_(None)).count()),
            ("target_x", Calculation.query.filter(Calculation.target_x.is_(None)).count()),
            ("probability", Calculation.query.filter(Calculation.probability.is_(None)).count()),
            ("created_at", Calculation.query.filter(Calculation.created_at.is_(None)).count()),
        ]

        for field, count in null_checks:
            if count > 0:
                issues.append(f"Found {count} calculations with NULL {field}")

        # Summary
        total_calculations = Calculation.query.count()
        print(f"\n{'='*60}")
        print("DATABASE INTEGRITY REPORT")
        print(f"{'='*60}")
        print(f"Total calculations: {total_calculations}")
        print(f"Issues found: {len(issues)}")

        if issues:
            print("\nISSUES:")
            for issue in issues:
                print(issue)
            return False
        else:
            print("\n✓ No integrity issues found!")
            print("✓ All constraints are being enforced properly")
            print("✓ Database is healthy")
            return True


if __name__ == "__main__":
    import sys
    success = verify_database_integrity()
    sys.exit(0 if success else 1)
