#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 VERSION [VERSION ...]" >&2
    echo "Example: $0 1.27.0 1.28.0 1.29.0" >&2
    exit 2
fi

latest_image=""

for MP_VERSION in "$@"; do
    if ! printf '%s\n' "$MP_VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        echo "Invalid version: $MP_VERSION (expected X.Y.Z)" >&2
        exit 2
    fi

    revision_image=$(MP_VERSION="$MP_VERSION" docker compose config --images)
    release_image=${revision_image%.*}
    image_repository=${release_image%:*}

    MP_VERSION="$MP_VERSION" docker compose build
    docker push "$revision_image"
    docker tag "$revision_image" "$release_image"
    docker push "$release_image"
    latest_image="$revision_image"
done

docker tag "$latest_image" "${image_repository}:latest"
docker push "${image_repository}:latest"