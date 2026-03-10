# ---- Build stage ----
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS build
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
COPY src/ ./src/

RUN uv sync --frozen --no-dev --no-install-project
RUN uv build --wheel

# ---- Base image ----
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt install -y --no-install-recommends \
        libreoffice-writer-nogui \
        libreoffice-calc-nogui \
        libmagic1 \
        tesseract-ocr  \
        tesseract-ocr-swe \
        ghostscript \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ---- Final image ----
FROM base AS runtime

ENV TZ="Europe/Stockholm"

WORKDIR /app

COPY --from=build /app/dist/*.whl /tmp/

RUN pip install --break-system-packages --no-cache-dir /tmp/*.whl

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app

ENTRYPOINT [ "parseidon" ]
