from collections import namedtuple

from django.db import connection


def fetch_one(sql, sql_vars):
    """Return first row from a cursor as a namedtuple"""
    with connection.cursor() as cursor:
        cursor.execute(sql, sql_vars)
        nt_result = namedtuple("SQLResult", [col[0] for col in cursor.description])
        row = cursor.fetchone()
    if row:
        return nt_result(*row)._asdict()
    else:
        return {}


def fetch_all(sql, sql_vars):
    """Return all rows from a cursor as a namedtuple"""
    with connection.cursor() as cursor:
        cursor.execute(sql, sql_vars)
        nt_result = namedtuple("SQLResult", [col[0] for col in cursor.description])
        return [nt_result(*row)._asdict() for row in cursor.fetchall()]
