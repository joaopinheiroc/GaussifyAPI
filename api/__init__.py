import os
from flask import Flask
from dotenv import load_dotenv
from api.extensions import db

load_dotenv()

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    db_path = os.path.join(app.instance_path, "gaussify.db")
    secret_key = os.getenv("SECRET_KEY", "dev-secret-do-not-use-in-production")


    app.config.from_mapping(
        SECRET_KEY = secret_key,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from api.routes import gauss_bp
    app.register_blueprint(gauss_bp)

    with app.app_context():
        from api import models
        db.create_all()

    return app