from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from <<=cookiecutter.package_name=>>.db import Base, get_engine
from <<=cookiecutter.package_name=>>.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = get_engine()  # SQLite en memoria por defecto (<<=cookiecutter.env_prefix=>>DATABASE_URL sin definir)
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(engine)
