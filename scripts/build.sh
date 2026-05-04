#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: ./scripts/build.sh [OPTIONS]

Options:
  -u, --ubuntu VERSION       Ubuntu version: 22.04 | 24.04 | 26.04  (default: 26.04)
  -p, --python VERSION       Python version: 3.12 | 3.13 | 3.14    (default: 3.14)
  -c, --china                Enable Aliyun mirrors (apt + PyPI + uv)
  -t, --tag TAG              Custom image tag
      --push                 Push to registry (requires --tag with registry prefix)
      --platform PLATFORMS   Target platforms, e.g. "linux/amd64,linux/arm64"
                              Default: current architecture only (faster)
  -h, --help                 Show this help

Examples:
  ./scripts/build.sh                                      # 24.04, py3.13
  ./scripts/build.sh -c                                   # with china mirrors
  ./scripts/build.sh -u 22.04 -p 3.12 --platform linux/amd64,linux/arm64
  ./scripts/build.sh -c --push -t ghcr.io/user/devpack:china
EOF
}

UBUNTU_VERSION="26.04"
PYTHON_VERSION="3.14"
CHINA_MIRROR="false"
TAG=""
PUSH=false
PLATFORMS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--ubuntu)   UBUNTU_VERSION="$2"; shift 2 ;;
        -p|--python)   PYTHON_VERSION="$2"; shift 2 ;;
        -c|--china)    CHINA_MIRROR="true"; shift ;;
        -t|--tag)      TAG="$2";           shift 2 ;;
        --push)        PUSH="true";        shift ;;
        --platform)    PLATFORMS="$2";     shift 2 ;;
        -h|--help)     usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ -z "$TAG" ]; then
    SUFFIX=""
    [ "$CHINA_MIRROR" = "true" ] && SUFFIX="-china"
    TAG="devpack:py${PYTHON_VERSION}-ubuntu${UBUNTU_VERSION}${SUFFIX}"
fi

BUILD_ARGS=(
    --build-arg "UBUNTU_VERSION=${UBUNTU_VERSION}"
    --build-arg "PYTHON_VERSION=${PYTHON_VERSION}"
    --build-arg "CHINA_MIRROR=${CHINA_MIRROR}"
)

DOCKER_CMD="docker"

if [ -n "$PLATFORMS" ]; then
    if ! docker buildx ls >/dev/null 2>&1; then
        echo "ERROR: docker buildx not available. Install it first."
        exit 1
    fi
    DOCKER_CMD="docker buildx"
    BUILD_ARGS+=(--platform "$PLATFORMS")
fi

if [ "$PUSH" = "true" ]; then
    echo "Building & pushing: ${TAG}"
    $DOCKER_CMD build \
        -f Dockerfile.minimal \
        -t "$TAG" \
        --push \
        "${BUILD_ARGS[@]}" \
        .
else
    echo "Building (local): ${TAG}"
    $DOCKER_CMD build \
        -f Dockerfile.minimal \
        -t "$TAG" \
        --load \
        "${BUILD_ARGS[@]}" \
        .
fi

echo "Done: ${TAG}"
