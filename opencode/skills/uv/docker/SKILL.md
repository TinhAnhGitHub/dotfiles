---
name: uv-docker
description: >
  Docker integration with uv: best-practice Dockerfiles, multi-stage builds,
  layer caching strategies, Docker Compose for development, environment variables,
  and Docker images for uv.
---

# uv Docker Integration

Best practices for containerizing Python projects managed with uv.

---

## Docker Images

**Available images from `ghcr.io/astral-sh/uv`:**

| Tag | Base | Use Case |
|-----|------|----------|
| `:latest` | Distroless | Copy uv binary only |
| `:{version}` | Distroless | Pin specific version |
| `:alpine` | Alpine | Small runtime |
| `:python3.12-alpine` | Alpine + Python | Alpine with Python |
| `:debian-slim` | Debian slim | Full-featured runtime |
| `:python3.12-trixie` | Debian + Python | Full Python runtime |

---

## Installing uv in Docker

**Copy from distroless image (recommended):**
```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

**Pin to a specific version:**
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /uvx /bin/
```

**Temporary uv (not in final image):**
```dockerfile
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync
```

---

## Best Practice Dockerfile (Multi-stage, Layer-cached)

```dockerfile
# --- Stage 1: Build ---
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable --no-dev

# Copy project code
COPY . .

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev

# --- Stage 2: Runtime ---
FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
CMD ["my-app"]
```

### Why This Works

1. **Layer 1** (deps): Only `uv.lock` + `pyproject.toml` → cached until deps change
2. **Layer 2** (code): `COPY .` → only rebuilds when code changes
3. **Stage 2**: Minimal runtime image with only `.venv` and source code

---

## Simpler Single-stage Dockerfile

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "my-app"]
```

---

## Key Docker Environment Variables

| Variable | Purpose |
|----------|---------|
| `UV_COMPILE_BYTECODE=1` | Compile `.pyc` for faster startup |
| `UV_LINK_MODE=copy` | Avoid cross-filesystem warnings with cache mounts |
| `UV_NO_DEV=1` | Exclude dev dependencies |
| `UV_CACHE_DIR` | Custom cache directory |

---

## Docker Compose (Development)

```yaml
services:
  app:
    build: .
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
```

---

## .dockerignore

```
.venv/
__pycache__/
*.pyc
.git/
.github/
.mypy_cache/
.pytest_cache/
.ruff_cache/
dist/
docs/
```

> **Important:** Exclude `.venv` from Docker build context — it's platform-specific.

---

## Docker with Workspaces

```dockerfile
# Install dependencies first (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace

# Copy all workspace members
COPY . .

# Install workspace members
RUN uv sync --locked
```

---

## Documentation

- **Docker guide:** https://docs.astral.sh/uv/guides/integration/docker/
- **Official example:** https://github.com/astral-sh/uv-docker-example
