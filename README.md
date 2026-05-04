# docker-devpack

Universal Python Docker base images built on Ubuntu + uv + Python.

## Pre-built Images

```bash
docker pull ghcr.io/brikerman/docker-devpack:<TAG>
```

### `latest` / `latest-china` Tags

- `latest` → **`py3.14-ubuntu26.04`**
- `latest-china` → **`py3.14-ubuntu26.04-china`** (Aliyun mirrors)

```bash
docker pull ghcr.io/brikerman/docker-devpack:latest
docker pull ghcr.io/brikerman/docker-devpack:latest-china
```

### All Tags

> `latest` → `py3.14-ubuntu26.04` · `latest-china` → `py3.14-ubuntu26.04-china`

**Standard**

| Python \ Ubuntu | 26.04 | 24.04 | 22.04 |
|-----------------|-------|-------|-------|
| **3.14** | `py3.14-ubuntu26.04` | `py3.14-ubuntu24.04` | `py3.14-ubuntu22.04` |
| **3.13** | `py3.13-ubuntu26.04` | `py3.13-ubuntu24.04` | `py3.13-ubuntu22.04` |
| **3.12** | `py3.12-ubuntu26.04` | `py3.12-ubuntu24.04` | `py3.12-ubuntu22.04` |

**China Mirror (Aliyun)**

| Python \ Ubuntu | 26.04 | 24.04 | 22.04 |
|-----------------|-------|-------|-------|
| **3.14** | `py3.14-ubuntu26.04-china` | `py3.14-ubuntu24.04-china` | `py3.14-ubuntu22.04-china` |
| **3.13** | `py3.13-ubuntu26.04-china` | `py3.13-ubuntu24.04-china` | `py3.13-ubuntu22.04-china` |
| **3.12** | `py3.12-ubuntu26.04-china` | `py3.12-ubuntu24.04-china` | `py3.12-ubuntu22.04-china` |

All images support `linux/amd64` and `linux/arm64`.

Approx. size: ~200MB

## What's Inside

| Component | Version |
|-----------|---------|
| Ubuntu | 22.04 / 24.04 / 26.04 |
| Python | 3.12 / 3.13 / 3.14 (pre-installed via uv) |
| uv | latest (package manager) |
| build-essential | gcc, g++, make |

Pre-installed Python is managed by uv and located at `/home/app/.local/share/uv/python/`.

Use `uv run python` or `uv run <script>` to invoke Python — no need to manage PATH manually.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UV_COMPILE_BYTECODE` | `0` | Skip bytecode compilation for faster builds |
| `UV_LINK_MODE` | `copy` | Avoid hardlink issues across Docker filesystems |
| `PYTHONIOENCODING` | `utf-8` | UTF-8 encoding for stdin/stdout/stderr |
| `PYTHONUNBUFFERED` | `1` | Unbuffered Python output |
| `PYTHONDONTWRITEBYTECODE` | `1` | Skip `.pyc` file generation |

## Build Arguments

| ARG | Options | Default | Description |
|-----|---------|---------|-------------|
| `UBUNTU_VERSION` | `22.04`, `24.04`, `26.04` | `26.04` | Ubuntu version |
| `PYTHON_VERSION` | `3.12`, `3.13`, `3.14` | `3.14` | Python version |
| `UV_VERSION` | any uv tag | `latest` | uv version |
| `CHINA_MIRROR` | `true`, `false` | `false` | Enable Aliyun mirrors (apt + PyPI + uv) |

## Local Build

```bash
# Default (26.04 + py3.14)
./scripts/build.sh

# Specify versions
./scripts/build.sh -u 22.04 -p 3.12

# China mirrors
./scripts/build.sh -c

# Multi-arch build & push
./scripts/build.sh -c \
  --platform linux/amd64,linux/arm64 \
  --push -t your-registry/devpack:china
```

### build.sh Options

```
Usage: ./scripts/build.sh [OPTIONS]

Options:
  -u, --ubuntu VERSION       22.04 | 24.04 | 26.04           (default: 26.04)
  -p, --python VERSION       3.12 | 3.13 | 3.14              (default: 3.14)
  -c, --china                Enable Aliyun mirrors
  -t, --tag TAG              Custom image tag
      --push                 Push to registry
      --platform PLATFORMS   Target platforms (default: current arch only)
  -h, --help                 Show help
```

## CI Builds

GitHub Actions and Gitea Actions are included. Push to `main` to trigger automatic multi-arch builds.

Matrix: 3 (Ubuntu) x 3 (Python) x 2 (mirror) = 18 images

### GitHub Actions

1. Push to `main` branch to trigger
2. Images are pushed to `ghcr.io/brikerman/docker-devpack`
3. No extra config needed, uses built-in `GITHUB_TOKEN`

### Gitea Actions

Add these secrets in Settings > Actions > Secrets:

- `REGISTRY` — your container registry host
- `REGISTRY_USERNAME` — registry username
- `REGISTRY_PASSWORD` — registry password/token

### Image Tag Naming

```
py<version>-ubuntu<version>[-china]
```

Examples:
```
py3.14-ubuntu26.04
py3.13-ubuntu22.04-china
py3.14              (short form, no ubuntu version)
```

## Using in Your Project

```dockerfile
FROM ghcr.io/brikerman/docker-devpack:py3.13-ubuntu24.04-china

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg tzdata \
    && rm -rf /var/lib/apt/lists/*

USER app
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> **Tip**: Use `--no-install-project` during dependency installation, then copy source code and run `uv sync --frozen --no-dev` again to install the project itself. This maximizes Docker layer caching.

### Why `UV_LINK_MODE=copy`?

In Docker, uv's package cache and the target `.venv` are often on different filesystems or overlay layers. Hardlinking fails silently and falls back to copy with a warning. Setting `UV_LINK_MODE=copy` eliminates this warning and avoids potential issues.

## China Mirror Configuration

When `CHINA_MIRROR=true`, the following mirrors are used:

| Type | Mirror | URL |
|------|--------|-----|
| Ubuntu APT | Aliyun | `mirrors.aliyun.com/ubuntu` (including `ubuntu-ports` for arm64) |
| PyPI | Aliyun + pypi.org fallback | `mirrors.aliyun.com/pypi/simple` |

Environment variables are written to `/etc/profile.d/china-mirror.sh` and automatically loaded by the entrypoint.

In Dockerfile RUN layers, source it manually:
```dockerfile
RUN . /etc/profile.d/china-mirror.sh && uv sync
```

## Directory Permissions

```
/code              app:app  rwx    # default working directory
/home/app          app:app  rwx    # user home (uv-managed Python lives here)
```

Python is pre-installed as the `app` user, so there are no permission issues when creating venvs or installing packages at runtime.

To install additional system packages:
```dockerfile
USER root
RUN apt-get install -y --no-install-recommends something && rm -rf /var/lib/apt/lists/*
USER app
```

## Test Suite

A test project in `test/` verifies the base image works correctly in downstream Dockerfiles.

```bash
# Build base image locally
docker build -f Dockerfile.minimal \
  --build-arg UBUNTU_VERSION=24.04 \
  --build-arg PYTHON_VERSION=3.13 \
  --build-arg CHINA_MIRROR=true \
  -t devpack-base:local .

# Build and run test project
cd test
docker build -t devpack-test:local .
docker run --rm devpack-test:local uv run pytest tests/ -v
```

Test coverage: FastAPI API, SQLAlchemy, Pydantic, Rich, async, SQLite, JSON serialization, framework imports.

## License

MIT
