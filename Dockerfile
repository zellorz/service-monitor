FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# 1) Dependencias: solo se reinstalan si cambia pyproject.toml o uv.lock
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# 2) Tu código: esta capa se rehace cada vez que cambias algo en src/
COPY README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["fastapi", "run", "src/service_monitor/main.py", "--port", "8000"]