FROM python:3.13.3-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.6.17 /uv /uvx /bin/

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

ENV PYTHONPATH=/code \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    VIRTUAL_ENV=/code/.venv \
    UV_PROJECT_ENVIRONMENT=/code/.venv \
    DJANGO_SETTINGS_MODULE=config.settings.base

RUN apt-get update && apt-get upgrade -y && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    screen \
    # Cleaning cache:
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY ./src/ /code/
COPY ./abis/ /code/abis/

ENV PATH="/code/.venv/bin:$PATH"

RUN django-admin collectstatic --noinput

EXPOSE 8000
