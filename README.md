# docker-devpack

Universal Python Docker base images built on Ubuntu + uv + Python.

## Pre-built Images

```bash
docker pull ghcr.io/brikerman/docker-devpack:<TAG>
```

### minimal

| Tag | Ubuntu | Python | Mirror |
|-----|--------|--------|--------|
| `minimal-py3.13-ubuntu24.04` | 24.04 | 3.13 | — |
| `minimal-py3.13-ubuntu22.04` | 22.04 | 3.13 | — |
| `minimal-py3.12-ubuntu24.04` | 24.04 | 3.12 | — |
| `minimal-py3.12-ubuntu22.04` | 22.04 | 3.12 | — |
| `minimal-py3.13-ubuntu24.04-china` | 24.04 | 3.13 | Aliyun |
| `minimal-py3.13-ubuntu22.04-china` | 22.04 | 3.13 | Aliyun |
| `minimal-py3.12-ubuntu24.04-china` | 24.04 | 3.12 | Aliyun |
| `minimal-py3.12-ubuntu22.04-china` | 22.04 | 3.12 | Aliyun |

### playwright

| Tag | Ubuntu | Python | Mirror |
|-----|--------|--------|--------|
| `playwright-py3.13-ubuntu24.04` | 24.04 | 3.13 | — |
| `playwright-py3.13-ubuntu22.04` | 22.04 | 3.13 | — |
| `playwright-py3.12-ubuntu24.04` | 24.04 | 3.12 | — |
| `playwright-py3.12-ubuntu22.04` | 22.04 | 3.12 | — |
| `playwright-py3.13-ubuntu24.04-china` | 24.04 | 3.13 | Aliyun |
| `playwright-py3.13-ubuntu22.04-china` | 22.04 | 3.13 | Aliyun |
| `playwright-py3.12-ubuntu24.04-china` | 24.04 | 3.12 | Aliyun |
| `playwright-py3.12-ubuntu22.04-china` | 22.04 | 3.12 | Aliyun |

All images support `linux/amd64` and `linux/arm64`.

## Image Variants

| Variant | Description | Approx. Size |
|---------|-------------|--------------|
| `minimal` | Ubuntu + uv + Python | ~200MB |
| `playwright` | minimal + Playwright system deps + CJK fonts | ~500MB |

## Build Arguments

| ARG | Options | Default | Description |
|-----|---------|---------|-------------|
| `UBUNTU_VERSION` | `22.04`, `24.04` | `24.04` | Ubuntu version |
| `PYTHON_VERSION` | `3.12`, `3.13` | `3.13` | Python version |
| `UV_VERSION` | any uv tag | `latest` | uv version |
| `CHINA_MIRROR` | `true`, `false` | `false` | Enable Aliyun mirrors (apt + PyPI + uv + Playwright) |

## Local Build

```bash
# Minimal image (default 24.04 + py3.13)
./scripts/build.sh

# Specify versions
./scripts/build.sh -v minimal -u 22.04 -p 3.12

# Playwright + China mirrors
./scripts/build.sh -v playwright -p 3.13 -c

# Multi-arch build & push
./scripts/build.sh -v playwright -c \
  --platform linux/amd64,linux/arm64 \
  --push -t your-registry/devpack:playwright-china
```

### build.sh Options

```
Usage: ./scripts/build.sh [OPTIONS]

Options:
  -v, --variant VARIANT      minimal | playwright          (default: minimal)
  -u, --ubuntu VERSION       22.04 | 24.04                (default: 24.04)
  -p, --python VERSION       3.12 | 3.13                  (default: 3.13)
  -c, --china                Enable Aliyun mirrors
  -t, --tag TAG              Custom image tag
      --push                 Push to registry
      --platform PLATFORMS   Target platforms (default: current arch only)
  -h, --help                 Show help
```

## CI Builds

GitHub Actions and Gitea Actions are included. Push to `main` to trigger automatic multi-arch builds.

Matrix: 2 (Ubuntu) x 2 (Python) x 2 (variant) x 2 (mirror) = 16 images

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
<variant>-py<version>-ubuntu<version>[-china]
```

Examples:
```
minimal-py3.13-ubuntu24.04
playwright-py3.12-ubuntu22.04-china
minimal-py3.13              (short form, no ubuntu version)
```

## Using in Your Project

### Minimal Example

```dockerfile
FROM ghcr.io/brikerman/docker-devpack:minimal-py3.13

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim curl \
    && rm -rf /var/lib/apt/lists/*

USER app

COPY --chown=app:app pyproject.toml uv.lock ./
# Source mirror env manually in RUN layers when using China mirrors
RUN . /etc/profile.d/china-mirror.sh && uv sync --no-cache

COPY --chown=app:app ./app /code/app

CMD ["uv", "run", "python", "-m", "app.main"]
```

### Playwright Example

```dockerfile
FROM ghcr.io/brikerman/docker-devpack:playwright-py3.13-china

USER root
COPY --chown=app:app pyproject.toml uv.lock ./
RUN . /etc/profile.d/china-mirror.sh && \
    uv sync --no-cache && \
    uv run playwright install --with-deps chromium && \
    chown -R app:app /code /opt/playwright

COPY --chown=app:app ./app /code/app
COPY --chown=app:app ./config /code/config

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uv", "run", "gunicorn", "app.main:app", "-c", "gunicorn_config.py"]
```

## China Mirror Configuration

When `CHINA_MIRROR=true`, the following mirrors are used:

| Type | Mirror | URL |
|------|--------|-----|
| Ubuntu APT | Aliyun | `mirrors.aliyun.com/ubuntu` |
| PyPI | Aliyun + pypi.org fallback | `mirrors.aliyun.com/pypi/simple` |
| Playwright | npmmirror | `npmmirror.com/mirrors/playwright` |

Environment variables are written to `/etc/profile.d/china-mirror.sh` and automatically loaded by the entrypoint.

In Dockerfile RUN layers, source it manually:
```dockerfile
RUN . /etc/profile.d/china-mirror.sh && uv sync
```

## Directory Permissions

```
/code              app:app  rwx    # working directory
/opt/uv            app:app  rwx    # uv toolchain
/opt/playwright    app:app  rwx    # Playwright browsers (playwright variant only)
/home/app          app:app  rwx    # user home
```

To install additional system packages:
```dockerfile
USER root
RUN apt-get install -y --no-install-recommends something && rm -rf /var/lib/apt/lists/*
USER app
```

## License

MIT
