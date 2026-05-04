# docker-devpack

Universal Python Docker base images built on Ubuntu + uv + Python.

## Pre-built Images

```bash
docker pull ghcr.io/brikerman/docker-devpack:<TAG>
```

### `latest` Tag

The `latest` tag always points to **`py3.14-ubuntu26.04`** (no mirror).

```bash
docker pull ghcr.io/brikerman/docker-devpack:latest
```

### All Tags

| Tag | Ubuntu | Python | Mirror |
|-----|--------|--------|--------|
| `latest` | 26.04 | 3.14 | — |
| `py3.14-ubuntu26.04` | 26.04 | 3.14 | — |
| `py3.14-ubuntu24.04` | 24.04 | 3.14 | — |
| `py3.14-ubuntu22.04` | 22.04 | 3.14 | — |
| `py3.13-ubuntu26.04` | 26.04 | 3.13 | — |
| `py3.13-ubuntu24.04` | 24.04 | 3.13 | — |
| `py3.13-ubuntu22.04` | 22.04 | 3.13 | — |
| `py3.12-ubuntu26.04` | 26.04 | 3.12 | — |
| `py3.12-ubuntu24.04` | 24.04 | 3.12 | — |
| `py3.12-ubuntu22.04` | 22.04 | 3.12 | — |
| `py3.14-ubuntu26.04-china` | 26.04 | 3.14 | Aliyun |
| `py3.14-ubuntu24.04-china` | 24.04 | 3.14 | Aliyun |
| `py3.14-ubuntu22.04-china` | 22.04 | 3.14 | Aliyun |
| `py3.13-ubuntu26.04-china` | 26.04 | 3.13 | Aliyun |
| `py3.13-ubuntu24.04-china` | 24.04 | 3.13 | Aliyun |
| `py3.13-ubuntu22.04-china` | 22.04 | 3.13 | Aliyun |
| `py3.12-ubuntu26.04-china` | 26.04 | 3.12 | Aliyun |
| `py3.12-ubuntu24.04-china` | 24.04 | 3.12 | Aliyun |
| `py3.12-ubuntu22.04-china` | 22.04 | 3.12 | Aliyun |

All images support `linux/amd64` and `linux/arm64`.

Approx. size: ~200MB

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
py3.13-ubuntu24.04
py3.12-ubuntu22.04-china
py3.13              (short form, no ubuntu version)
```

## Using in Your Project

```dockerfile
FROM ghcr.io/brikerman/docker-devpack:latest

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

## China Mirror Configuration

When `CHINA_MIRROR=true`, the following mirrors are used:

| Type | Mirror | URL |
|------|--------|-----|
| Ubuntu APT | Aliyun | `mirrors.aliyun.com/ubuntu` |
| PyPI | Aliyun + pypi.org fallback | `mirrors.aliyun.com/pypi/simple` |

Environment variables are written to `/etc/profile.d/china-mirror.sh` and automatically loaded by the entrypoint.

In Dockerfile RUN layers, source it manually:
```dockerfile
RUN . /etc/profile.d/china-mirror.sh && uv sync
```

## Directory Permissions

```
/code              app:app  rwx    # working directory
/opt/uv            app:app  rwx    # uv toolchain
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
