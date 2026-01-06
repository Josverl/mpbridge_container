# Build arguments for version configuration
ARG MICROPYTHON_VERSION=v1.27.0
ARG PYTHON_VERSION=3.12

FROM micropython/unix:${MICROPYTHON_VERSION}

# Re-declare ARGs after FROM (they go out of scope)
ARG PYTHON_VERSION=3.12

WORKDIR /bridge

# Install curl and ca-certificates for downloading uv
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv is in PATH (uv installs to ~/.local/bin)
ENV PATH="/root/.local/bin:${PATH}"

# Install Python using uv
RUN uv python install ${PYTHON_VERSION}

# Download the bridge script at build time (cached in image)
ARG BRIDGE_SCRIPT_URL=https://raw.githubusercontent.com/Josverl/micropython/refs/heads/feat/MP_Bridge/tools/mpremote_bridge.py
RUN curl -LsSf ${BRIDGE_SCRIPT_URL} -o /bridge/mpremote_bridge.py

# Copy readme into the image
COPY readme.md /bridge/readme.md

# Store Python version as environment variable for runtime
ENV PYTHON_VERSION=${PYTHON_VERSION}
ENV MICROPYTHON_PATH=/usr/local/bin/micropython

EXPOSE 2217
EXPOSE 2218

# Use the locally cached script instead of fetching from URL
ENTRYPOINT ["/bin/sh", "-c", "uv run --python ${PYTHON_VERSION} /bridge/mpremote_bridge.py $@", "--"]
CMD ["/usr/local/bin/micropython"]
    