from __future__ import annotations

def create_app():
    from flask import Flask
    from app.routes import web

    app = Flask(__name__)
    app.register_blueprint(web)
    return app
