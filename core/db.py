from django.db import connection


def fetch_all(sql, params=None):
    """Execute SELECT and return list of dicts."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        cols = [col[0] for col in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


def fetch_one(sql, params=None):
    """Execute SELECT and return single dict or None."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        return dict(zip(cols, row)) if row else None


def execute_query(sql, params=None):
    """Execute INSERT, UPDATE, or DELETE."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
