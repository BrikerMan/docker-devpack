# test

Downstream test project to verify `docker-devpack` base image.

## What It Tests

- `uv sync` dependency installation (no permission errors)
- FastAPI app startup via `uv run uvicorn`
- pytest with pytest-asyncio (20 tests)
- Framework imports: FastAPI, uvicorn, httpx, SQLAlchemy, alembic, Pydantic, Rich
- Python 3.13 features: match statements, async/await, pathlib, json
- Database: sqlite3 + SQLAlchemy engine
- Linting: ruff, mypy

## Quick Run

```bash
# From repo root: build base + test
docker build -f Dockerfile.minimal \
  --build-arg UBUNTU_VERSION=24.04 \
  --build-arg PYTHON_VERSION=3.13 \
  --build-arg CHINA_MIRROR=true \
  -t devpack-base:local .

cd test
docker build -t devpack-test:local .

# Run tests
docker run --rm devpack-test:local sh -c "cd /app && PYTHONPATH=/app uv run pytest tests/ -v"

# Run as service
docker run -d -p 8000:8000 --name test-api devpack-test:local
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/items
docker rm -f test-api
```
