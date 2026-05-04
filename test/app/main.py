import asyncio
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

console = Console()


class Item(BaseModel):
    name: str
    price: float = Field(gt=0)
    tags: list[str] = []


class Settings(BaseSettings):
    app_name: str = "devpack-test"
    debug: bool = False
    max_items: int = 100


settings = Settings()


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[float]


app = FastAPI(title="devpack-test")


def check_python_features():
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Arch: {sys.byteorder}")

    match sys.version_info.major:
        case 3:
            print("Python 3 detected")
        case _:
            print("Unknown Python version")

    data = {"items": [Item(name=f"item-{i}", price=float(i * 10)) for i in range(1, 4)]}
    json_str = json.dumps(data, default=lambda o: o.model_dump() if hasattr(o, "model_dump") else str(o))
    parsed = json.loads(json_str)
    print(f"JSON round-trip: {len(parsed['items'])} items")

    paths = list(Path("/app").iterdir())
    print(f"Files in /app: {[p.name for p in paths]}")

    table = Table(title="System Check")
    table.add_column("Check", style="cyan")
    table.add_column("Result", style="green")
    table.add_row("Python", sys.version.split()[0])
    table.add_row("uv managed", "Yes")
    table.add_row("FastAPI", "OK")
    table.add_row("SQLAlchemy", "OK")
    table.add_row("Pydantic", "OK")
    table.add_row("Rich", "OK")
    console.print(table)


def check_sqlite():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, val TEXT)"))
        conn.execute(text("INSERT INTO test (val) VALUES (:val)"), [{"val": "hello"}, {"val": "world"}])
        result = conn.execute(text("SELECT * FROM test"))
        rows = result.fetchall()
        print(f"SQLite test: {len(rows)} rows -> {[r[1] for r in rows]}")


async def check_async():
    async def fetch(n):
        return n * n

    results = await asyncio.gather(*(fetch(i) for i in range(10)))
    print(f"Async gather: {results}")


@app.get("/")
async def root():
    return {"status": "ok", "app_name": settings.app_name}


@app.get("/health")
async def health():
    return {"healthy": True}


@app.get("/items")
async def list_items():
    items = [Item(name=f"item-{i}", price=float(i * 10)) for i in range(1, 4)]
    return {"items": [it.model_dump() for it in items]}


@app.post("/items")
async def create_item(item: Item):
    return {"created": item.model_dump()}


if __name__ == "__main__":
    check_python_features()
    check_sqlite()
    asyncio.run(check_async())
    print("\nAll checks passed!")
