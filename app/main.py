"""Composition root de la aplicación."""
from app.adapters.inbound.http import create_http_app
from app.bootstrap import build_container

container = build_container()
app = create_http_app(
    list_fixtures=container.list_fixtures,
    predict_fixture=container.predict_fixture,
    model_version=container.model_version,
    data_source=container.data_source,
)
