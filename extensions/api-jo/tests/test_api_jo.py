import contextlib
import json
import sys
from pathlib import Path
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import api_jo as a


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = a.connect(Path(self.tmp.name) / 'catalog.db')
        self.addCleanup(self.db.close)

    def test_seed_search_and_rag(self):
        result = a.seed(self.db)
        self.assertGreaterEqual(result['imported'], 15)
        self.assertGreaterEqual(len(a.search(self.db, 'weather')), 1)
        result = a.rag(self.db, 'weather')
        self.assertGreaterEqual(result['retrieved'], 1)
        self.assertIn('Registry:', result['context'])
        self.assertIn('untrusted', result['context'].lower())
        self.assertNotIn('Authorization: Bearer', result['context'])

    def test_markdown_parser(self):
        md = '## Animals\n| API | Description | Auth | HTTPS | CORS |\n| [Cat API](https://cat.test/api) | cats | `apiKey` | Yes | No |\n| [Ad](https://ads.test) | buy now | <img /> | Foo | Bar |'
        rows = a.parse_markdown(md, 'test', 'https://src.test')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Cat API')
        self.assertEqual(rows[0]['category'], 'Animals')

    def test_resources_and_guru(self):
        data = '{"entries":[{"API":"R","Link":"https://api.vendor.test/docs","Description":"demo","Category":"Testing","Auth":"No"}]}'
        self.assertEqual(a.parse_resources(data, 'resources', 'https://src.test')[0]['name'], 'R')
        guru = json.dumps({'foo.example.com': {'preferred': 'v1', 'versions': {'v1': {
            'info': {'title': 'Foo', 'description': 'foo API'},
            'swaggerUrl': 'https://foo.example.com/openapi.json'}}}})
        self.assertEqual(a.parse_guru(guru, 'guru', 'https://src.test')[0]['spec_url'], 'https://foo.example.com/openapi.json')

    def test_ingest_replaces_stale_rows(self):
        rows = a.parse_markdown('| [One](https://one.test) | one | No | Yes | Yes |\n| [Two](https://two.test) | two | No | Yes | Yes |', 'x', 'https://src.test')
        a.save_rows(self.db, 'x', 'https://src.test', 'a', rows)
        self.assertEqual(len(a.search(self.db, 'one OR two')), 2)
        a.save_rows(self.db, 'x', 'https://src.test', 'b', rows[:1])
        self.assertEqual(self.db.execute('SELECT count(*) FROM catalog WHERE source="x"').fetchone()[0], 1)

    def test_export_never_exports_tokens(self):
        a.seed(self.db)
        f = Path(self.tmp.name) / 'note.md'
        a.archive(self.db, f)
        self.assertIn('APIجو', f.read_text(encoding='utf-8'))
        self.assertNotIn('AGENT_VAULT_TOKEN=', f.read_text(encoding='utf-8'))

    def test_host_validation(self):
        self.assertFalse(a.valid_https_url('http://127.0.0.1:9000/key'))
        self.assertFalse(a.valid_https_url('https://u:p@evil.test/foo'))
        for host in ('127.0.0.1', 'localhost', '*.example.com', 'foo.internal', 'example.com:80'):
            with self.assertRaises(ValueError):
                a.propose_access('svc', host, 'GOOD_KEY', 'Need a test key', existing=True)
        with self.assertRaises(ValueError):
            a.propose_access('svc', 'api.vendor.com', 'secret-value', 'Need API', existing=True)

    def test_human_approval_never_contains_secret(self):
        with patch.object(a, 'vault_call', return_value={'status': 'pending', 'id': 4}) as vault:
            r = a.propose_access('vendor', 'api.vendor.com', 'VENDOR_KEY', 'Needed for forecast', existing=True)
        self.assertEqual(r['status'], 'pending')
        payload = vault.call_args[0][2]
        self.assertEqual(payload['services'][0]['auth']['token'], 'VENDOR_KEY')
        self.assertEqual(payload['credentials'], [])
        self.assertNotIn('approved', json.dumps(payload).lower())


class TestServer(unittest.TestCase):
    def test_panel_is_readonly_and_local(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'data.db'
            db = a.connect(path)
            a.seed(db)
            db.close()
            server = a.ThreadingHTTPServer(('127.0.0.1', 0), a.Handler)
            server.db_path = str(path)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f'http://127.0.0.1:{server.server_port}'
                with urllib.request.urlopen(base + '/api/search?q=weather', timeout=4) as r:
                    self.assertGreater(len(json.loads(r.read())), 0)
                request = urllib.request.Request(base + '/api/stats', method='POST', data=b'{}')
                with self.assertRaises(urllib.error.HTTPError) as ex:
                    urllib.request.urlopen(request, timeout=4)
                self.assertEqual(ex.exception.code, 405)
                with urllib.request.urlopen(base, timeout=4) as r:
                    self.assertIn('text/html', r.headers['Content-Type'])
                    self.assertEqual(r.headers['X-Frame-Options'], 'DENY')
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == '__main__':
    unittest.main()