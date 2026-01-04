# mpremote-bridge Docker Container

A Docker container that runs the MicroPython mpremote bridge, allowing you to connect to a MicroPython Unix port instance over the network using `mpremote`.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and run (ports configured automatically)
docker compose up

# Run in background
docker compose up -d

# Stop
docker compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t mpremote-bridge .

# Run the container
docker run --rm -p 2217:2217 -p 2218:2218 mpremote-bridge
```

## Connecting

Once the container is running, connect using `mpremote`:

```bash
# Using raw socket (faster, ~28% better performance)
mpremote connect socket://localhost:2218

# Using RFC 2217
mpremote connect rfc2217://localhost:2217
```

### Example Commands

```bash
# Execute a simple command
mpremote connect socket://localhost:2218 exec "print('Hello from MicroPython!')"

# Run a script
mpremote connect socket://localhost:2218 run my_script.py

# Interactive REPL
mpremote connect socket://localhost:2218
```

## Build Arguments

The Dockerfile supports build-time arguments to customize versions:

| Argument | Default | Description |
|----------|---------|-------------|
| `MICROPYTHON_VERSION` | `v1.27.0` | MicroPython container version tag |
| `PYTHON_VERSION` | `3.12` | Python version for running the bridge script |
| `BRIDGE_SCRIPT_URL` | *(GitHub URL)* | URL to the mpremote_bridge.py script |

> **Note:** The bridge script is downloaded at build time and cached in the image. This means:
> - Faster container startup (no network fetch)
> - Works offline after build
> - Script version is locked at build time

### Examples

```bash
# Build with default versions (MicroPython v1.27.0, Python 3.12)
docker build -t mpremote-bridge .

# Build with a specific MicroPython version
docker build --build-arg MICROPYTHON_VERSION=v1.25.0 -t mpremote-bridge:mp1.25 .

# Build with a specific Python version
docker build --build-arg PYTHON_VERSION=3.11 -t mpremote-bridge:py3.11 .

# Build with both custom versions
docker build \
  --build-arg MICROPYTHON_VERSION=v1.25.0 \
  --build-arg PYTHON_VERSION=3.11 \
  -t mpremote-bridge:custom .

# Build with a custom bridge script (e.g., from a different branch or fork)
docker build \
  --build-arg BRIDGE_SCRIPT_URL=https://raw.githubusercontent.com/user/repo/branch/tools/mpremote_bridge.py \
  -t mpremote-bridge:custom-script .
```

## Runtime Arguments

Additional arguments can be passed to the mpremote_bridge.py script:

```bash
# Run with default arguments
docker run --rm -p 2217:2217 -p 2218:2218 mpremote-bridge

# Pass custom arguments to the bridge script
docker run --rm -p 2217:2217 -p 2218:2218 mpremote-bridge /usr/local/bin/micropython --help

# Run in detached mode (background)
docker run --rm -d -p 2217:2217 -p 2218:2218 --name mpremote-bridge mpremote-bridge
```

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 2217 | RFC 2217 | Serial port emulation over TCP |
| 2218 | Raw Socket | Direct socket connection (recommended) |

## Performance

Based on benchmarks, the raw socket connection (port 2218) is approximately **28% faster** than RFC 2217 (port 2217). Use the socket connection for better performance.

## Stopping the Container

```bash
# If running in foreground: Ctrl+C

# If running in detached mode
docker stop mpremote-bridge
```

## View Logs

```bash
docker logs mpremote-bridge
```