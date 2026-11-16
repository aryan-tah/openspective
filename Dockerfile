# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.11@sha256:77280f2f771df71f90786c314fe1bbc1e023feac652969bbf139c280babf2eb7 AS uv

FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS build
COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE NOTICE ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-editable
# Bake the models into the image so containers start without network access.
ENV HF_HOME=/models
RUN /app/.venv/bin/openspective download && rm -rf /models/xet /models/hub/.locks

FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
LABEL org.opencontainers.image.title="openspective" \
      org.opencontainers.image.description="Self-hosted, Perspective API compatible comment scoring" \
      org.opencontainers.image.source="https://github.com/aryan-tah/openspective" \
      org.opencontainers.image.licenses="Apache-2.0"
RUN useradd --system --uid 10001 --home /app openspective
COPY --from=build --chown=10001 /app /app
COPY --from=build --chown=10001 /models /models
ENV PATH=/app/.venv/bin:$PATH \
    HF_HOME=/models \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PYTHONUNBUFFERED=1 \
    OPENSPECTIVE_HOST=0.0.0.0 \
    PORT=8080
USER 10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/healthz')"
CMD ["openspective", "serve"]
