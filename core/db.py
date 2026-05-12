import uuid
from django.db import connection


def _serialize(val):
    return str(val) if isinstance(val, uuid.UUID) else val


def _row_to_dict(cols, row):
    return {col: _serialize(val) for col, val in zip(cols, row)}


def fetch_all(sql, params=None):
    """Execute SELECT and return list of dicts."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        cols = [col[0] for col in cursor.description]
        return [_row_to_dict(cols, row) for row in cursor.fetchall()]


def fetch_one(sql, params=None):
    """Execute SELECT and return single dict or None."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        return _row_to_dict(cols, row) if row else None


def execute_query(sql, params=None):
    """Execute INSERT, UPDATE, or DELETE."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
