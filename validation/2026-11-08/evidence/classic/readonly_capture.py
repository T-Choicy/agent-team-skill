"""Print real command evidence without writing files; coordinator saves stdout."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

scope_path, snapshot_path, *argv = sys.argv[1:]
if argv and argv[0] == '--':
    argv = argv[1:]
scope = json.loads(Path(scope_path).read_text(encoding='utf-8'))
root = Path(scope['workspace'])

def hashes(base):
    return {name: hashlib.sha256((base / name).read_bytes()).hexdigest()
            if (base / name).is_file() else None for name in scope['files']}

record = {'argv': argv, 'cwd': str(root), 'design_id': scope['design_id'],
          'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'before_hashes': hashes(root), 'exit_code': None, 'stdout': '', 'stderr': '',
          'valid': False}
expected = None
if snapshot_path != '-':
    frozen = Path(snapshot_path)
    snapshot = json.loads(frozen.read_text(encoding='utf-8'))
    record['snapshot_id'] = snapshot['snapshot_id']
    expected = snapshot['hashes']
    record['snapshot_copy_before_hashes'] = hashes(frozen.parent / 'files')
    if (frozen.parent / 'invalid.json').exists() or expected != record['before_hashes'] or expected != record['snapshot_copy_before_hashes']:
        record['error'] = 'Frozen source or copy invalid before execution'
try:
    if 'error' not in record:
        options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
        done = subprocess.run(argv, cwd=root, stdin=subprocess.DEVNULL, capture_output=True, timeout=60, shell=False, **options)
        record.update(exit_code=done.returncode, stdout=done.stdout.decode('utf-8', 'replace'), stderr=done.stderr.decode('utf-8', 'replace'))
except (OSError, subprocess.TimeoutExpired) as error:
    record['error'] = str(error)
finally:
    record['after_hashes'] = hashes(root)
    if expected is not None:
        record['snapshot_copy_after_hashes'] = hashes(frozen.parent / 'files')
    record['ended_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record['valid'] = ('error' not in record and record['exit_code'] == 0 and
                       record['before_hashes'] == record['after_hashes'] and
                       (expected is None or expected == record['after_hashes'] == record['snapshot_copy_after_hashes']))
print(json.dumps(record, ensure_ascii=True))
raise SystemExit(0 if record['valid'] else 1)
