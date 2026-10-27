"""Configuration diagnostics must reject mistakes without logging credentials."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]

class ReleaseConfigTests(unittest.TestCase):
    def run_check(self,value,flags=(),runtime=False):
        env={k:v for k,v in os.environ.items() if k not in ('LABAN_CHECK_DATABASE_URL','DATABASE_URL')}
        env['DATABASE_URL' if runtime else 'LABAN_CHECK_DATABASE_URL']=value
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/check_storage.py'),*flags],env=env,capture_output=True,text=True,timeout=12)
        self.assertNotIn('do-not-leak',p.stdout+p.stderr)
        return p,json.loads(p.stdout)
    def test_missing_or_wrong_scheme_is_not_schema_failure(self):
        for value in ('','sqlite:///local.db','DATABASE_URL=postgresql://u:do-not-leak@localhost/db'):
            with self.subTest(value=value.split(':')[0]):
                p,r=self.run_check(value);self.assertEqual(p.returncode,2);self.assertEqual(r['code'],'CHECK_DATABASE_URL_REQUIRED')
    def test_malformed_uri_is_redacted(self):
        for value in ('postgresql://u:do-not-leak@localhost:notaport/db','postgresql://u:do-not-leak@localhost/db#wrong','postgresql://u:do-not-leak@localhost/my db'):
            p,r=self.run_check(value);self.assertEqual(p.returncode,2);self.assertEqual(r['code'],'DATABASE_URL_INVALID')
    def test_runtime_is_explicit_and_wrong_target_stops_before_connect(self):
        url='postgresql://u:do-not-leak@127.0.0.1:1/neondb'
        p,r=self.run_check(url,('--runtime','--expected-host','different.invalid'),runtime=True)
        self.assertEqual(r['code'],'DATABASE_TARGET_MISMATCH')
        p,r=self.run_check(url,('--runtime','--expected-database','other'),runtime=True)
        self.assertEqual(r['code'],'DATABASE_TARGET_MISMATCH')
