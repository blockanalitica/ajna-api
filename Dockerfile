FROM python:3.11.5-slim-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-o", "errexit", "-o", "nounset", "-o", "xtrace", "-c"]

ENV PYTHONPATH=/code \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.base

RUN apt-get -y update ; \
    apt-get -y install postgresql-client-15 curl wget gnupg libpq-dev build-essential; \
    apt-get clean

WORKDIR /code

COPY /requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN django-admin collectstatic --noinput

EXPOSE 8000
