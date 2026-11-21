import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from serve import state_body, ASSETS


class SnapshotTests(unittest.TestCase):
    def test_demo_is_identified_and_contains_branching_evidence(self):
        state = json.loads(state_body())
        self.assertTrue(state['demo'])
        self.assertTrue(any(len(c['parents']) > 1 for c in state['campaigns'][0]['candidates']))
        self.assertTrue(state['campaigns'][0]['guidance'])

    def test_saved_snapshot_is_identified_without_changing_source_time(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'state.json'
            p.write_text(json.dumps({'campaigns': [], 'generated_at': 100}))
            state = json.loads(state_body(snapshot=p))
        self.assertTrue(state['snapshot'])
        self.assertEqual(state['generated_at'], 100)
        self.assertNotIn('demo', state)

    def test_team_only_export_does_not_invent_campaigns_or_live_status(self):
        ledger = json.loads(state_body())['team_search']
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'team.json'
            p.write_text(json.dumps(ledger))
            state = json.loads(state_body(team_snapshot=p))
        self.assertEqual(state['campaigns'], [])
        self.assertTrue(state['snapshot'])
        self.assertEqual(state['team_search'], ledger)
        self.assertEqual(state['team_search_source']['mode'], 'local_snapshot')

    def test_invalid_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'state.json'
            for payload in ('[]', '{"campaigns":{}}', 'broken'):
                p.write_text(payload)
                with self.assertRaises(ValueError):
                    state_body(snapshot=p)

    def test_proxy_reads_only_configured_snapshot_endpoint(self):
        with patch('serve.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value = b'{"campaigns":[]}'
            state = json.loads(state_body(api_url='http://127.0.0.1:8765/'))
        request.assert_called_once_with('http://127.0.0.1:8765/api/state', timeout=10)
        self.assertEqual(state, {'campaigns': []})

    def test_local_assets_do_not_include_records_or_server_source(self):
        for private in ('serve.py', '.env', 'fixtures/demo-state.json', '.local/state.json', '../README.md'):
            self.assertNotIn(private, ASSETS)


if __name__ == '__main__':
    unittest.main()
