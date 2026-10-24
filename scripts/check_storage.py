"""Kiểm tra metadata bằng biến riêng; không tự đọc .env hoặc DATABASE_URL Production."""
import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import psycopg
from psycopg.rows import dict_row
from advisor.schema_check import inspect_schema


def main():
    parser=argparse.ArgumentParser(description='Explicit read-only release database verification; never reads dotenv.')
    parser.add_argument('--runtime',action='store_true',help='Explicitly inspect DATABASE_URL in this process environment')
    parser.add_argument('--expected-host',default='')
    parser.add_argument('--expected-database',default='')
    args=parser.parse_args()
    url = os.getenv('DATABASE_URL' if args.runtime else 'LABAN_CHECK_DATABASE_URL', '').strip()
    if not url.startswith(('postgresql://', 'postgres://')):
        print(json.dumps({'ready': False, 'code': 'CHECK_DATABASE_URL_REQUIRED'}))
        return 2
    try:
        parsed=urlsplit(url)
        valid=bool(parsed.hostname and parsed.path.strip('/')) and not parsed.fragment and not any(c.isspace() for c in url)
        _=parsed.port
        if not valid:raise ValueError()
        config=psycopg.conninfo.conninfo_to_dict(url)
    except (ValueError,psycopg.Error):
        print(json.dumps({'ready':False,'code':'DATABASE_URL_INVALID'}));return 2
    if (args.expected_host and parsed.hostname.lower()!=args.expected_host.lower()) or (args.expected_database and config.get('dbname')!=args.expected_database):
        print(json.dumps({'ready':False,'code':'DATABASE_TARGET_MISMATCH'}));return 2
    try:
        # Preserve test search_path/options, but force read-only last at startup.
        options=config.get('options','')+' -c default_transaction_read_only=on -c statement_timeout=5000 -c lock_timeout=2000'
        with psycopg.connect(url, connect_timeout=8, row_factory=dict_row,options=options) as db:
            if db.execute('SHOW transaction_read_only').fetchone()['transaction_read_only']!='on':
                print(json.dumps({'ready':False,'code':'READ_ONLY_NOT_ENFORCED'}));return 2
            if args.expected_database and db.execute('SELECT current_database() AS name').fetchone()['name']!=args.expected_database:
                print(json.dumps({'ready':False,'code':'DATABASE_TARGET_MISMATCH'}));return 2
            report = inspect_schema(db)
            report.update(read_only=True,target_checked=bool(args.expected_host and args.expected_database))
            db.rollback()
    except psycopg.Error as error:
        print(json.dumps({'ready': False, 'code': 'DATABASE_CHECK_FAILED', 'error_type': type(error).__name__}))
        return 2
    print(json.dumps(report))
    return 0 if report['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
