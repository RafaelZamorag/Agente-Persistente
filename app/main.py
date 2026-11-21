"""Composition root de la aplicación."""
from app.adapters.inbound.http import create_http_app
from app.bootstrap import build_container

container = build_container()
app = create_http_app(container)
