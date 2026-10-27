"""Release/catalog regressions for tasks 1+2, no production/provider access."""
import json
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app import app
from career_library import catalog, CATEGORIES, normalize_search

ROOT=Path(__file__).resolve().parents[1]

class Task12ReleaseTests(unittest.TestCase):
    def test_runtime_json_allowlist_excludes_all_other_local_data(self):
        required={f'data/careers-{n}.json' for n in range(1,5)}
        forbidden={'data/local.sqlite3','data/credentials.json','data/career-seeds.txt','data/careers-5.json','data/nested/history.json'}
        gitdir=subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=ROOT,text=True).strip()
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)
            for name in required|forbidden:
                path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.touch()
            # Native Git ignore parser with an empty worktree. No init/index/Git mutation,
            # and no repository .gitignore that could override .vercelignore semantics.
            result=subprocess.run(['git','--git-dir='+gitdir,'--work-tree='+str(target),
                '-c','core.excludesFile='+str(ROOT/'.vercelignore'),
                'check-ignore','--no-index','--stdin'],cwd=target,
                input=('\n'.join(sorted(required|forbidden))+'\n').encode('utf8'),capture_output=True)
            self.assertIn(result.returncode,(0,1),result.stderr.decode(errors='replace'))
            self.assertEqual(set(result.stdout.decode('utf8').splitlines()),forbidden)
        config=json.loads((ROOT/'vercel.json').read_text(encoding='utf8'))
        included=set(config['functions']['app.py']['includeFiles'].strip('{}').split(','))
        self.assertEqual({p for p in included if p.startswith('data/')},required)
        self.assertNotIn('rewrites',config)

    def test_missing_required_json_cannot_silently_publish_partial_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'data').mkdir()
            for n in range(1,4):(root/'data'/f'careers-{n}.json').write_bytes((ROOT/'data'/f'careers-{n}.json').read_bytes())
            catalog.cache_clear()
            try:
                with patch('career_library.__file__',str(root/'career_library.py')):
                    with self.assertRaises(FileNotFoundError) as caught:catalog()
                self.assertIn('careers-4.json',str(caught.exception))
            finally:catalog.cache_clear()

    def test_catalog_category_totals_and_keyword_accent_search(self):
        rows=catalog().careers
        self.assertEqual(len(rows),200)
        self.assertEqual(len({normalize_search(c.name) for c in rows}),200)
        self.assertEqual(len({normalize_search(c.description) for c in rows}),200)
        with TestClient(app) as client:
            categories=client.get('/api/career-library/categories').json()['items']
            self.assertEqual(sum(c['count'] for c in categories),200)
            for category in categories:
                data=client.get('/api/career-library',params={'category_id':category['category_id'],'limit':24}).json()
                self.assertEqual(data['total'],category['count'])
                self.assertTrue(all(c['category_id']==category['category_id'] for c in data['items']))
            for row in rows[::17]:
                found=client.get('/api/career-library',params={'q':row.keywords[0],'limit':24}).json()
                expected=catalog().search(row.keywords[0])
                self.assertEqual(found['total'],len(expected))
                self.assertEqual(client.get('/api/career-library',params={'q':normalize_search(row.name)}).json()['total'],len(catalog().search(row.name)))

    def test_public_assets_have_no_embedded_server_keys(self):
        import re
        patterns=(r'-----BEGIN (?:RSA )?PRIVATE KEY-----',r'\bsk-[A-Za-z0-9]{24,}\b',r'postgres(?:ql)?://[^\s\"\']+:[^\s\"\']+@')
        for path in (ROOT/'public').rglob('*'):
            if path.is_file() and path.suffix in ('.js','.html','.css'):
                text=path.read_text(encoding='utf8')
                for pattern in patterns:self.assertIsNone(re.search(pattern,text),path.relative_to(ROOT))

if __name__=='__main__':unittest.main()
