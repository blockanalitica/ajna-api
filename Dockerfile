FROM python:3.10.9-buster

SHELL ["/bin/bash", "-o", "pipefail", "-o", "errexit", "-o", "nounset", "-o", "xtrace", "-c"]

ENV PYTHONPATH=/code \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.base

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get -y update ; \
    apt-get -y install postgresql-client-15 ; \
    apt-get clean

WORKDIR /code

COPY /requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN django-admin collectstatic --noinput

EXPOSE 8000
