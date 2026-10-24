"""DevBoard - a tiny team status board used as the target application."""
from flask import Flask

from .metrics import init_metrics
from .routes import api, web


def create_app() -> Flask:
    app = Flask(__name__)
    init_metrics(app)
    app.register_blueprint(web)
    app.register_blueprint(api, url_prefix="/api")
    return app
