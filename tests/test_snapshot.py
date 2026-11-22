import hashlib
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class SnapshotTests(unittest.TestCase):
    def test_manifest_matches_committed_evidence(self):
        raw=(ROOT/'data/latest.json').read_bytes()
        manifest=json.loads((ROOT/'data/manifest.json').read_text())
        state=json.loads(raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),manifest['sha256'])
        self.assertEqual(len(state['jobs']),manifest['jobs'])
        self.assertTrue(state['snapshot'])
        self.assertFalse(state.get('demo',False))
        self.assertEqual([c['sha'] for c in state['submission']['candidates']],manifest['candidates'])
