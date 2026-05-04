import asyncio
import json
import sys
import sqlite3
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app, settings, Item


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── API tests ──────────────────────────────────────────────────────
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "devpack-test"


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["healthy"] is True


async def test_list_items(client):
    resp = await client.get("/items")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 3
    assert items[0]["name"] == "item-1"


async def test_create_item(client):
    resp = await client.post("/items", json={"name": "test-item", "price": 9.99, "tags": ["a"]})
    assert resp.status_code == 200
    data = resp.json()["created"]
    assert data["name"] == "test-item"
    assert data["price"] == 9.99


# ── Python features ───────────────────────────────────────────────
def test_python_version():
    assert sys.version_info >= (3, 13)


def test_match_statement():
    match 3:
        case 3:
            result = "three"
        case _:
            result = "other"
    assert result == "three"


def test_json_roundtrip():
    items = [Item(name=f"item-{i}", price=float((i + 1) * 10)) for i in range(5)]
    data = [it.model_dump() for it in items]
    json_str = json.dumps(data)
    parsed = json.loads(json_str)
    assert len(parsed) == 5
    assert parsed[2]["price"] == 30.0


def test_pathlib():
    paths = list(Path("/app").iterdir())
    names = {p.name for p in paths}
    assert "app" in names


# ── Database ───────────────────────────────────────────────────────
def test_sqlite():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, val TEXT)")
    conn.executemany("INSERT INTO test (val) VALUES (?)", [("a",), ("b",), ("c",)])
    rows = conn.execute("SELECT * FROM test").fetchall()
    assert len(rows) == 3
    conn.close()


# ── SQLAlchemy ─────────────────────────────────────────────────────
def test_sqlalchemy():
    from sqlalchemy import create_engine, text
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1 + 1"))
        result = conn.scalar(text("SELECT 42"))
        assert result == 42


# ── Pydantic ──────────────────────────────────────────────────────
def test_pydantic_model():
    item = Item(name="widget", price=19.99, tags=["sale", "new"])
    assert item.name == "widget"
    assert item.price == 19.99
    d = item.model_dump()
    assert d["tags"] == ["sale", "new"]
    item2 = Item.model_validate(d)
    assert item2 == item


def test_pydantic_settings():
    assert settings.app_name == "devpack-test"
    assert settings.debug is False
    assert settings.max_items == 100


# ── Rich ───────────────────────────────────────────────────────────
def test_rich_import():
    from rich.console import Console
    from rich.table import Table
    console = Console()
    table = Table(title="Test")
    table.add_column("A")
    table.add_row("hello")
    assert len(table.columns) == 1


# ── Async ─────────────────────────────────────────────────────────
async def test_async_gather():
    async def compute(n):
        return n * n
    results = await asyncio.gather(*(compute(i) for i in range(5)))
    assert results == [0, 1, 4, 9, 16]


# ── Framework imports ─────────────────────────────────────────────
def test_import_fastapi():
    from fastapi import FastAPI, HTTPException, Depends
    a = FastAPI()
    assert a.title == "FastAPI"


def test_import_uvicorn():
    import uvicorn
    assert hasattr(uvicorn, "run")


def test_import_httpx():
    import httpx
    assert hasattr(httpx, "AsyncClient")


def test_import_sqlalchemy():
    from sqlalchemy import create_engine, text, select
    assert callable(create_engine)


def test_import_alembic():
    import alembic
    assert hasattr(alembic, "__version__")


def test_import_pydantic():
    from pydantic import BaseModel, Field
    assert callable(BaseModel)
