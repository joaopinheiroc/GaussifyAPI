import pytest
from api import create_app
from api.extensions import db


@pytest.fixture
def app():
    """Create application for testing"""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for the application"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for the application"""
    return app.test_cli_runner()
