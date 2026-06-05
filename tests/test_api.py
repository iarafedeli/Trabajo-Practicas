import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

engine_test = create_engine(
    "sqlite:///./test.db", connect_args={"check_same_thread": False}
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
Base.metadata.create_all(bind=engine_test)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.anyio
async def test_root(client):
    r = await client.get("/")
    assert r.status_code == 200


@pytest.mark.anyio
async def test_create_question(client):
    r = await client.post("/questions", json={
        "question": "¿Capital de Francia?",
        "answer": "París",
        "category": "geography"
    })
    assert r.status_code == 201
    assert r.json()["id"] is not None


@pytest.mark.anyio
async def test_get_by_category(client):
    await client.post("/questions", json={
        "question": "¿Planeta más grande?",
        "answer": "Júpiter",
        "category": "science"
    })
    r = await client.get("/questions/category/science")
    assert r.status_code == 200
    assert len(r.json()) >= 1


@pytest.mark.anyio
async def test_category_not_found(client):
    r = await client.get("/questions/category/categoria_inexistente_xyz")
    assert r.status_code == 404


@pytest.mark.anyio
async def test_stats(client):
    r = await client.get("/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "by_category" in data