"""
Script to generate a test coverage report in HTML format.
"""

import subprocess
import sys
from pathlib import Path


def generate_coverage_report():
    """Generate HTML coverage report."""
    project_root = Path(__file__).resolve().parent.parent
    print(f"Running tests with coverage from {project_root}...")

    try:
        # Run tests with coverage from project root
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--cov=.", "--cov-report=html", "--cov-report=term"],
            cwd=project_root,
            check=True,
            capture_output=False
        )

        print("\n" + "="*60)
        print("✓ Coverage report generated successfully!")
        print("="*60)
        print("\nOpen htmlcov/index.html in your browser to view the detailed report.")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(generate_coverage_report())
