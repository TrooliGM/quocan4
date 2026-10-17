"""Kiểm tra metadata bằng biến riêng; không tự đọc .env hoặc DATABASE_URL Production."""
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import psycopg
from psycopg.rows import dict_row
from advisor.schema_check import inspect_schema


def main():
    url = os.getenv('LABAN_CHECK_DATABASE_URL', '').strip()
    if not url.startswith(('postgresql://', 'postgres://')):
        print(json.dumps({'ready': False, 'code': 'CHECK_DATABASE_URL_REQUIRED'}))
        return 2
    try:
        with psycopg.connect(url, connect_timeout=8, row_factory=dict_row) as db:
            db.execute("SET TRANSACTION READ ONLY; SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'")
            report = inspect_schema(db)
    except psycopg.Error as error:
        print(json.dumps({'ready': False, 'code': 'DATABASE_CHECK_FAILED', 'error_type': type(error).__name__}))
        return 2
    print(json.dumps(report))
    return 0 if report['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
