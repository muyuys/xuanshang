from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from config import config 


db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    from .base import base as base_blueprint
    app.register_blueprint(base_blueprint)
    return app
