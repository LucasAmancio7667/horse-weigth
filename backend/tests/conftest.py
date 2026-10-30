import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app import db as app_db
from app.db import Base, get_db
from app.main import app
from sqlalchemy import create_engine


@pytest.fixture()
def engine():
    # SQLite em memória; StaticPool mantém a mesma conexão entre as threads do TestClient
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    from sqlalchemy import event

    @event.listens_for(eng, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session(engine):
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = Session()
    yield s
    s.close()


@pytest.fixture()
def client(engine, monkeypatch):
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        s = Session()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    # Não bate no Blob Storage real durante os testes
    monkeypatch.setattr("app.storage.is_available", lambda: False)
    # Evita criar tabelas no banco de arquivo durante o lifespan
    monkeypatch.setattr(app_db, "engine", engine)
    monkeypatch.setattr("app.main.engine", engine)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
