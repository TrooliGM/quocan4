"""PostgreSQL local tách biệt; không đọc DATABASE_URL hoặc credentials production."""
import os
import socket
import subprocess
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]


class LocalPostgres:
    def __enter__(self):
        binaries = Path(os.getenv('LABAN_TEST_PG_BIN', str(ROOT/'artifacts/postgres-tools/pgsql/bin')))
        suffix = '.exe' if os.name == 'nt' else ''
        self.ctl = binaries/('pg_ctl'+suffix)
        if not self.ctl.is_file():
            from unittest import SkipTest
            raise SkipTest('Cần PostgreSQL kiểm thử local; đặt LABAN_TEST_PG_BIN trỏ tới thư mục bin (xem docs/guest-chat.md).')
        self.directory = ROOT/'artifacts'/('pg-guest-test-'+uuid4().hex[:10])
        self.directory.mkdir(parents=True)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0)); self.port = sock.getsockname()[1]
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        self.flags = flags
        for command in ([str(binaries/('initdb'+suffix)), '-D',str(self.directory),'-U','laban_test','-A','trust','--encoding=UTF8','--no-locale'],
                        [str(self.ctl),'-D',str(self.directory),'-l',str(self.directory/'server.log'),'-o',f'-h 127.0.0.1 -p {self.port}','-w','start']):
            with self.directory.with_suffix('.fixture.log').open('ab') as log:
                result = subprocess.run(command,stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=flags,timeout=45)
            if result.returncode:
                raise RuntimeError('Không khởi động được PostgreSQL kiểm thử local; xem thư mục artifacts/pg-guest-test-*')
        self.url = f'postgresql://laban_test@127.0.0.1:{self.port}/postgres'
        return self

    def __exit__(self,*args):
        # Chỉ dừng cluster duy nhất do fixture này tạo; không xóa thư mục/database khác.
        with self.directory.with_suffix('.fixture.log').open('ab') as log:
            subprocess.run([str(self.ctl),'-D',str(self.directory),'-w','stop','-m','fast'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=self.flags,timeout=30)

    def schema(self, initialize=True):
        name = 'guest_test_'+uuid4().hex
        with psycopg.connect(self.url,autocommit=True) as db:
            from psycopg import sql
            db.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(name)))
        def connect():
            return psycopg.connect(self.url,options=f'-c search_path={name}',row_factory=dict_row)
        @contextmanager
        def connection():
            with connect() as db:
                yield db
        connection.schema_name = name
        if initialize:
            with connect() as db:
                db.autocommit = True
                for migration in ('001_conversations.sql', '002_guest_quota.sql', '004_shared_ai_protection.sql'):
                    db.execute((ROOT/'migrations'/migration).read_text(encoding='utf-8'))
        return connection
