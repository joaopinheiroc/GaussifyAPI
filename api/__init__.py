import os
from flask import Flask
from dotenv import load_dotenv
from api.extensions import db

load_dotenv()

def criar_app(config_teste: dict | None = None) -> Flask:
    app = Flask(__name__)

    caminho
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')