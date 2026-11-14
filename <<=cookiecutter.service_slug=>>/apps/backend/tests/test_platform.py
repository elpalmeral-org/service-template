"""Salud, métricas, información y configuración. Sin rutas de negocio: nace vacío a propósito."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from <<=cookiecutter.package_name=>> import main
from <<=cookiecutter.package_name=>>.config import normalize_database_url
from <<=cookiecutter.package_name=>>.db import Base, get_engine

BACKEND = Path(__file__).resolve().parents[1]


def test_healthz(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_readyz_ok_with_database(client: TestClient) -> None:
    assert client.get("/readyz").status_code == 200


def test_readyz_unavailable_without_database(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    broken = create_engine("postgresql+psycopg://nadie:nada@127.0.0.1:1/ninguna")
    monkeypatch.setattr(main, "get_engine", lambda: broken)
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_metrics_exposes_request_counter(client: TestClient) -> None:
    client.get("/api/info")
    body = client.get("/metrics").text
    assert "<<=cookiecutter.package_name=>>_http_requests_total" in body
    assert 'route="/api/info"' in body


def test_info_reports_version(client: TestClient) -> None:
    body = client.get("/api/info").json()
    assert body["version"]
    assert body["environment"] == "local"


def test_get_engine_hides_parameters(client: TestClient) -> None:
    """El motor real de la app esconde los parámetros en los mensajes de error
    (corpus/03-data-classification.md §2) — por defecto de plataforma, antes de que exista
    ninguna ruta de negocio. `client` ya disparó `get_engine()` una vez."""
    assert get_engine().hide_parameters is True


def test_hide_parameters_omits_values_from_db_errors() -> None:
    """Comprobación independiente del comportamiento de SQLAlchemy con hide_parameters=True: un
    fallo de BD no debe volcar un parámetro en claro (corpus/03-data-classification.md §2).
    Motor propio, no el compartido por la app (que otros tests siguen usando); sin tablas de
    negocio todavía, se prueba contra una consulta cualquiera con un parámetro de ejemplo."""
    engine = create_engine("sqlite+pysqlite:///:memory:", hide_parameters=True)
    session = sessionmaker(bind=engine)()
    try:
        with pytest.raises(OperationalError) as excinfo:
            session.execute(
                text("SELECT * FROM tabla_inexistente WHERE dato = :valor"),
                {"valor": "secreto-de-ejemplo"},
            )
        assert "secreto-de-ejemplo" not in str(excinfo.value)
    finally:
        session.close()
        engine.dispose()


def test_strip_query_string_removes_sensitive_params() -> None:
    """El server_request_hook de OTel (F6.1, ADR 0032) no debe mandar la query string de ninguna
    petición a las trazas del obs-stack, igual que ya se evita en el log de acceso y en los
    errores de SQLAlchemy — por defecto, antes de que exista ninguna ruta de negocio."""
    from opentelemetry.sdk.trace import TracerProvider

    from <<=cookiecutter.package_name=>>.otel import _strip_query_string

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)
    leaked = "http://api/api/ejemplo?token=secreto-de-ejemplo"
    with tracer.start_as_current_span("test") as span:
        span.set_attribute("http.target", leaked)
        span.set_attribute("http.url", leaked)
        span.set_attribute("url.full", leaked)
        span.set_attribute("url.query", "token=secreto-de-ejemplo")

        _strip_query_string(span, {"path": "/api/ejemplo"})

        assert span.attributes is not None
        for attribute in ("http.target", "http.url", "url.full"):
            assert span.attributes[attribute] == "/api/ejemplo"
        assert span.attributes["url.query"] == ""
        assert "secreto-de-ejemplo" not in str(span.attributes)


def test_dockerfile_disables_access_log() -> None:
    """--no-access-log: el log de acceso registraría en claro cualquier dato sensible que una
    ruta de negocio futura ponga en la query string (corpus/03-data-classification.md §2)."""
    cmd_line = next(
        line for line in (BACKEND / "Dockerfile").read_text().splitlines() if line.startswith("CMD")
    )
    assert "--no-access-log" in cmd_line


def test_normalize_cnpg_url() -> None:
    assert (
        normalize_database_url("postgresql://app:x@app-db-rw:5432/app")
        == "postgresql+psycopg://app:x@app-db-rw:5432/app"
    )
    assert normalize_database_url("sqlite+pysqlite:///:memory:") == "sqlite+pysqlite:///:memory:"


def test_migrations_upgrade_and_downgrade(tmp_path: Path) -> None:
    """Sin migraciones todavía (nace vacío): upgrade/downgrade no deben fallar aunque no haya
    nada que aplicar — la primera feature real añade la primera migración."""
    url = f"sqlite+pysqlite:///{tmp_path / 'm.db'}"
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    engine = create_engine(url)
    try:
        command.upgrade(cfg, "head")
        command.downgrade(cfg, "base")
    finally:
        engine.dispose()


def test_base_has_no_tables_yet() -> None:
    """El esqueleto nace sin ninguna entidad de negocio; Base.metadata está vacío a propósito."""
    assert Base.metadata.tables == {}
