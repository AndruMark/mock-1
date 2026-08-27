# Stage 1: Constructor de dependencias con uv
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copiar manifiestos para aprovechar el cache de capas
COPY pyproject.toml uv.lock ./

# Instalar dependencias de producción
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime ligero final
FROM python:3.14-slim-bookworm

WORKDIR /app

# Copiar el entorno virtual generado
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el código fuente y migraciones
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]