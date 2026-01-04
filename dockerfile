FROM micropython/unix:v1.27.0

WORKDIR /bridge

# Install curl and ca-certificates for downloading uv
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv is in PATH (uv installs to ~/.local/bin)
ENV PATH="/root/.local/bin:${PATH}"

# Install Python 3.12 using uv (stable version)
RUN uv python install 3.12

ENV MICROPYTHON_PATH=/usr/local/bin/micropython

EXPOSE 2217
EXPOSE 2218

# Use uv run to execute the script (uv will manage dependencies automatically)
CMD uv run --python 3.12 --with pyserial https://raw.githubusercontent.com/Josverl/micropython/refs/heads/feat/MP_Bridge/tools/mpremote_bridge.py /usr/local/bin/micropython
    