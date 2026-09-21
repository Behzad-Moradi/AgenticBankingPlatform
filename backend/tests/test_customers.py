from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db.base import Base
from backend.db.session import get_db
from backend.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def test_create_customer() -> None:
    response = client.post(
        "/customers",
        json={
            "first_name": "Alice",
            "last_name": "Brown",
            "email": "alice@example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["first_name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "created_at" in data


def test_get_customers() -> None:
    client.post(
        "/customers",
        json={
            "first_name": "Alice",
            "last_name": "Brown",
            "email": "alice@example.com",
        },
    )

    response = client.get("/customers")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_customer() -> None:
    created = client.post(
        "/customers",
        json={
            "first_name": "Alice",
            "last_name": "Brown",
            "email": "alice@example.com",
        },
    ).json()

    response = client.get(f"/customers/{created['id']}")

    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_customer_not_found() -> None:
    response = client.get("/customers/999")

    assert response.status_code == 404


def test_duplicate_email() -> None:
    customer = {
        "first_name": "Alice",
        "last_name": "Brown",
        "email": "alice@example.com",
    }

    first_response = client.post("/customers", json=customer)
    second_response = client.post("/customers", json=customer)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_update_customer() -> None:
    created = client.post(
        "/customers",
        json={
            "first_name": "Alice",
            "last_name": "Brown",
            "email": "alice@example.com",
        },
    ).json()

    response = client.patch(
        f"/customers/{created['id']}",
        json={
            "first_name": "Alicia",
        },
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "Alicia"
    assert response.json()["last_name"] == "Brown"


def test_delete_customer() -> None:
    created = client.post(
        "/customers",
        json={
            "first_name": "Alice",
            "last_name": "Brown",
            "email": "alice@example.com",
        },
    ).json()

    response = client.delete(f"/customers/{created['id']}")

    assert response.status_code == 204

    get_response = client.get(f"/customers/{created['id']}")

    assert get_response.status_code == 404