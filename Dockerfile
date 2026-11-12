FROM python:3.15.2-alpine3.24 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM python:3.15.2-alpine3.24

LABEL maintainer="hello@mazzotta.me"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH=/app/.venv/bin:$PATH

COPY src /app/src

CMD ["python", "src/carstatus.py"]
