# mpbridge Docker Container

A Docker container that runs the MicroPython mpremote bridge, allowing you to connect to a MicroPython Unix port instance over the network using `mpremote`.

## Quick Start

### Running from Docker Hub (Easiest)

The fastest way to get started is to pull and run the pre-built image:

```bash
# Pull and run the latest version
docker run -p 2217:2217 -p 2218:2218 josverlinde/mpbridge:latest

# Or run in detached mode (background)
docker run -d -p 2217:2217 -p 2218:2218 --name mpbridge josverlinde/mpbridge:latest

# Stop the container
docker stop mpbridge
```

You can now connect using `mpremote`:

```bash
# Using raw socket (faster, ~28% better performance)
mpremote connect socket://localhost:2218
```

### Using Docker Compose (Recommended)

```bash
# Build and run (ports configured automatically)
docker compose up

# Run in background
docker compose up -d

# Stop
docker compose down

# Run in detached mode (background) Optionall mount a local folder with -v
docker compose run --service-ports -d mpbridge
```

### Using Docker directly

```bash
# Build the image
docker build -t mpbridge .

# Run the container
docker run --rm -p 2217:2217 -p 2218:2218 mpbridge

# Run in detached mode (background)
docker run --rm -d -p 2217:2217 -p 2218:2218 --name mpbridge mpbridge
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

## Runtime Arguments

Additional arguments can be passed to the mpremote_bridge.py script:

```bash
# Run with default arguments
docker run --rm -p 2217:2217 -p 2218:2218 mpbridge

# Pass custom arguments to the bridge script
docker run --rm -p 2217:2217 -p 2218:2218 mpbridge /usr/local/bin/micropython --help

```

## Mounting Local Folders

To access local files from within the container, use the `-v` flag:

```bash
# Using docker compose run (detached with ports)
docker compose run -d -v "/path/to/local/folder:/test_data" --service-ports mpbridge

# Using docker directly
docker run --rm -d -p 2217:2217 -p 2218:2218 -v "/path/to/local/folder:/test_data" mpbridge
```

**Flags explained:**
- `-d` = detached (background)
- `-v` = mount volume (host_path:container_path)
- `--service-ports` = expose ports defined in compose file (required for `docker compose run`)

**Example (Windows):**
```powershell
docker compose run -d -v "D:/myproject/data:/test_data" --service-ports mpbridge
```

Files will be available at `/test_data` inside the container.

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
docker stop mpbridge
```

## View Logs

```bash
docker logs mpbridge
```

## Publishing to Docker Hub

### Prerequisites

1. Create an account at [hub.docker.com](https://hub.docker.com)
2. Login locally:
   ```bash
   docker login
   ```
   (Enter your Docker Hub username and password)

### Publishing Steps

```bash
# 1. Build the image using docker-compose
docker compose build

# 2. Tag the image with version numbers
docker tag josverlinde/mpbridge:latest josverlinde/mpbridge:1.27.0.1
docker tag josverlinde/mpbridge:latest josverlinde/mpbridge:1.27.0
docker tag josverlinde/mpbridge:latest josverlinde/mpbridge:latest

# 3. Push all tags to Docker Hub
docker push josverlinde/mpbridge:1.27.0.1
docker push josverlinde/mpbridge:1.27.0
docker push josverlinde/mpbridge:latest
```

### Using Published Images

Once published, others can use your image:

```bash
# Pull and run the latest version
docker pull josverlinde/mpbridge:latest
docker run -p 2217:2217 -p 2218:2218 josverlinde/mpbridge:latest

# Or use a specific version
docker run -p 2217:2217 -p 2218:2218 josverlinde/mpbridge:1.27.0.1

# Or update docker-compose.yml to use remote image
# image: josverlinde/mpbridge:1.27.0.1
```

### Recommended Workflow

1. Update versions in `docker-compose.yml`
2. Build locally: `docker compose build`
3. Test: `docker compose up`
4. Commit changes: `git add -A && git commit -m "Update to bridge v1.27.0.1"`
5. Tag release: `git tag v1.27.0.1 && git push origin v1.27.0.1`
6. Build and push to Docker Hub (see steps above)

## Build Arguments

The Dockerfile supports build-time arguments to customize versions. These are centrally managed in the `docker-compose.yml` file under the `x-versions` section:

| Argument | Default | Description |
|----------|---------|-------------|
| `MICROPYTHON_VERSION` | `v1.27.0` | MicroPython container version tag |
| `PYTHON_VERSION` | `3.12` | Python version for running the bridge script |
| `BRIDGE_VERSION` | `1.27.0.1` | Bridge container version (format: `MP_VERSION.BUILD_NUMBER`) |

> **Note:** The bridge script is copied from the local repo at build time and cached in the image. This means:
> - Faster container startup (no network fetch)
> - Works offline after build
> - Script version is locked at build time

### Version Management

Use `docker-compose.yml` for centralized version management:

```yaml
x-versions:
  micropython: &mp-version v1.27.0
  python: &py-version 3.12
  bridge: &bridge-version 1.27.0.1
```

Update versions here, then rebuild:

```bash
# Rebuild with versions from docker-compose.yml
docker compose build
```

### Examples

```bash
# Build with default versions (from docker-compose.yml)
docker compose build

# Build with specific versions via docker command
docker build \
  --build-arg MICROPYTHON_VERSION=v1.25.0 \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg BRIDGE_VERSION=1.25.0.1 \
  -t mpbridge:1.25.0.1 .

# Tag image with bridge version
docker build -t mpbridge:1.27.0.1 .

# Run specific version
docker run -p 2217:2217 -p 2218:2218 mpbridge:1.27.0.1
```

### Version Tag Format

- `MAJOR.MINOR.PATCH.BUILD` (e.g., `1.27.0.1`)
  - `1.27.0` = MicroPython version
  - `.1` = Your bridge build/revision number
  - Increment the build number when you update the bridge without changing MicroPython
  - Change all digits when upgrading MicroPython
