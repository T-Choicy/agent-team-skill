import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('evidence', Path(__file__).with_name('evidence.py'))
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'source.txt').write_text('original')
        self.scope_path = self.root / 'scope.json'
        evidence.save(self.scope_path, {'workspace': str(self.root), 'design_id': 'a' * 64, 'files': ['source.txt']})
        self.scope = evidence.scope_file(self.scope_path)

    def test_real_command_exit_logs_and_argv(self):
        command = [sys.executable, '-c', 'import sys;print("hello");sys.stderr.write("error");sys.exit(7)']
        path, valid = evidence.run(self.scope, self.root / 'records', command)
        record = json.loads(path.read_text())
        self.assertFalse(valid)
        self.assertEqual(record['exit_code'], 7)
        self.assertEqual(record['argv'], command)
        self.assertIn(b'hello', (path.parent / 'stdout.log').read_bytes())
        self.assertEqual((path.parent / 'stderr.log').read_bytes(), b'error')

    def test_snapshot_drift_cannot_be_repaired_back_to_valid(self):
        frozen = evidence.snapshot(self.scope, self.root / 'snapshots')
        original = evidence.check_snapshot(frozen)['snapshot_id']
        (self.root / 'source.txt').write_text('changed')
        with self.assertRaises(ValueError):
            evidence.check_snapshot(frozen)
        (self.root / 'source.txt').write_text('original')
        with self.assertRaises(ValueError):
            evidence.check_snapshot(frozen)
        newer = evidence.snapshot(self.scope, self.root / 'snapshots')
        self.assertNotEqual(newer, frozen)
        self.assertNotEqual(evidence.check_snapshot(newer)['snapshot_id'], original)

    def test_frozen_command_mutation_invalidates_even_on_exit_zero(self):
        frozen = evidence.snapshot(self.scope, self.root / 'snapshots')
        path, valid = evidence.run(self.scope, self.root / 'records',
            [sys.executable, '-c', 'from pathlib import Path;Path("source.txt").write_text("changed")'], frozen)
        record = json.loads(path.read_text())
        self.assertEqual(record['exit_code'], 0)
        self.assertFalse(valid)
        self.assertTrue((frozen.parent / 'invalid.json').exists())

    def test_scope_paths_missing_sources_and_scope_mismatch(self):
        for invalid in ['../escape', 'C:/escape', '/escape', 'source.txt:stream', '.', 'source.txt/..']:
            with self.assertRaises(ValueError):
                evidence.source(self.root, invalid)
        future = {**self.scope, 'files': ['not-created.txt']}
        self.assertIsNone(evidence.hashes(future)['not-created.txt'])
        with self.assertRaises(ValueError):
            evidence.snapshot(future, self.root / 'snapshots')
        frozen = evidence.snapshot(self.scope, self.root / 'snapshots')
        with self.assertRaises(ValueError):
            evidence.check_snapshot(frozen, {**self.scope, 'design_id': 'b' * 64})

    def test_snapshot_copy_drift_and_timeout(self):
        frozen = evidence.snapshot(self.scope, self.root / 'snapshots')
        (frozen.parent / 'files/source.txt').write_text('changed copy')
        with self.assertRaises(ValueError):
            evidence.check_snapshot(frozen)
        path, valid = evidence.run(self.scope, self.root / 'records',
            [sys.executable, '-c', 'import time;time.sleep(5)'], timeout=0.1)
        self.assertFalse(valid)
        self.assertTrue(json.loads(path.read_text())['timed_out'])

    def test_cli_does_not_consume_child_options_and_preserves_history(self):
        command = [sys.executable, '-B', str(Path(evidence.__file__)), 'run', str(self.scope_path),
                   str(self.root / 'records'), '--', sys.executable, '-c', 'print("--snapshot")']
        for _ in range(2):
            result = subprocess.run(command, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.root / 'records').glob('*/evidence.json'))), 2)


if __name__ == '__main__':
    unittest.main()
