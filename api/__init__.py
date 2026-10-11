import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from api.extensions import db

load_dotenv()

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    # Load configuration
    if test_config:
        app.config.update(test_config)
    else:
        db_path = os.path.join(app.instance_path, "gaussify.db")
        secret_key = os.getenv("SECRET_KEY", "dev-secret-do-not-use-in-production")

        app.config.from_mapping(
            SECRET_KEY = secret_key,
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JSON_SORT_KEYS=False,
        )

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from api.routes import gauss_bp
    app.register_blueprint(gauss_bp)

    # Register error handlers
    register_error_handlers(app)

    # Create tables
    with app.app_context():
        import api.models  # noqa: F401
        db.create_all()

    return app


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the application."""

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500