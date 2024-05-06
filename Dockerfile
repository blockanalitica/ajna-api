FROM python:3.11.6-slim-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-o", "errexit", "-o", "nounset", "-o", "xtrace", "-c"]

ENV PYTHONPATH=/code \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.base \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN apt-get -y update ; \
    apt-get -y install postgresql-client-15 curl wget gnupg libpq-dev build-essential; \
    apt-get clean

WORKDIR /code

RUN pip install "poetry==$POETRY_VERSION" && poetry --version

COPY . /code/

RUN poetry install --only main

RUN django-admin collectstatic --noinput

EXPOSE 8000
