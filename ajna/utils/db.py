from collections import namedtuple


def fetch_one(cursor):
    """Return first row from a cursor as a namedtuple"""
    nt_result = namedtuple("SQLResult", [col[0] for col in cursor.description])
    row = cursor.fetchone()
    if row:
        return nt_result(*row)._asdict()
    else:
        return {}


def fetch_all(cursor):
    """Return all rows from a cursor as a namedtuple"""
    nt_result = namedtuple("SQLResult", [col[0] for col in cursor.description])
    return [nt_result(*row)._asdict() for row in cursor.fetchall()]
