"""Local evidence capture; role identity and review gates remain a team protocol."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import uuid


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def source(root, name):
    name = name.replace('\\', '/')
    if PureWindowsPath(name).drive or name.startswith('/') or any(
        p in ('', '.', '..') or p.endswith((' ', '.')) for p in name.split('/')
    ) or any(c in name for c in '<>:"|?*'):
        raise ValueError('Source paths must be explicit workspace-relative files')
    path = root
    for part in name.split('/'):
        path = path / part
        if path.exists() or path.is_symlink():
            info = path.lstat()
            if path.is_symlink() or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError('Source redirects are forbidden')
    if not path.resolve().is_relative_to(root) or (path.exists() and not path.is_file()):
        raise ValueError('Source scope must contain files inside the workspace')
    return path


def scope_file(path):
    scope = json.loads(Path(path).read_text(encoding='utf-8'))
    root = Path(scope['workspace'])
    if not root.is_absolute() or not root.is_dir():
        raise ValueError('workspace must be an existing absolute directory')
    root = root.resolve()
    files = scope['files']
    if not isinstance(files, list) or not files or any(not isinstance(p, str) for p in files):
        raise ValueError('files must be a nonempty file list')
    files = sorted(p.replace('\\', '/') for p in files)
    if len({p.casefold() for p in files}) != len(files):
        raise ValueError('Duplicate source paths')
    if not isinstance(scope['design_id'], str) or len(scope['design_id']) != 64 or any(
        c not in '0123456789abcdef' for c in scope['design_id']
    ):
        raise ValueError('design_id must be the computed SHA-256')
    for name in files:
        source(root, name)
    return {'workspace': str(root), 'design_id': scope['design_id'], 'files': files}


def hashes(scope, base=None):
    root = Path(base or scope['workspace']).resolve()
    result = {}
    for name in scope['files']:
        path = source(root, name)
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return result


def new_directory(parent, kind):
    path = Path(parent) / (kind + '-' + uuid.uuid4().hex)
    path.mkdir(parents=True, exist_ok=False)
    return path


def invalidate(path, reason):
    marker = Path(path).parent / 'invalid.json'
    if not marker.exists():
        save(marker, {'observed_at': now(), 'reason': reason})


def check_snapshot(path, scope=None):
    path = Path(path)
    try:
        if (path.parent / 'invalid.json').exists():
            raise ValueError('Snapshot was previously invalidated')
        record = json.loads(path.read_text(encoding='utf-8'))
        frozen_scope = scope_file(path.parent / 'scope.json')
        core = {'scope': frozen_scope, 'hashes': record['hashes'], 'revision': record['revision']}
        if (record['snapshot_id'] != digest(core) or record['design_id'] != frozen_scope['design_id'] or
                (scope is not None and scope != frozen_scope)):
            raise ValueError('Snapshot identity or scope mismatch')
        if hashes(frozen_scope) != record['hashes'] or hashes(frozen_scope, path.parent / 'files') != record['hashes']:
            raise ValueError('Frozen source or snapshot copy drifted')
        return record
    except (ValueError, OSError, KeyError, TypeError) as error:
        invalidate(path, str(error))
        raise ValueError(str(error)) from error


def snapshot(scope, output):
    before = hashes(scope)
    if any(value is None for value in before.values()):
        raise ValueError('All frozen source files must exist')
    directory = new_directory(output, 'snapshot')
    save(directory / 'scope.json', scope)
    for name in scope['files']:
        target = directory / 'files' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source(Path(scope['workspace']), name), target)
    revision = uuid.uuid4().hex
    record = {'snapshot_id': digest({'scope': scope, 'hashes': before, 'revision': revision}),
              'revision': revision, 'design_id': scope['design_id'],
              'created_at': now(), 'hashes': before}
    save(directory / 'snapshot.json', record)
    check_snapshot(directory / 'snapshot.json', scope)
    return directory / 'snapshot.json'


def run(scope, output, argv, frozen=None, timeout=120):
    if not argv or timeout <= 0:
        raise ValueError('Provide an argv command and a positive timeout')
    directory = new_directory(output, 'evidence')
    record = {'argv': argv, 'cwd': scope['workspace'], 'design_id': scope['design_id'],
              'snapshot': str(Path(frozen).resolve()) if frozen else None,
              'started_at': now(), 'exit_code': None, 'timed_out': False, 'valid': False}
    stdout, stderr = b'', b''
    try:
        record['before_hashes'] = hashes(scope)
        if frozen:
            record['snapshot_id'] = check_snapshot(frozen, scope)['snapshot_id']
        options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
        result = subprocess.run(argv, cwd=scope['workspace'], stdin=subprocess.DEVNULL,
                                capture_output=True, shell=False, timeout=timeout, **options)
        stdout, stderr = result.stdout, result.stderr
        record['exit_code'] = result.returncode
    except subprocess.TimeoutExpired as error:
        record['timed_out'] = True
        stdout, stderr = error.stdout or b'', error.stderr or b''
    except (OSError, ValueError) as error:
        record['error'] = str(error)
    finally:
        try:
            record['after_hashes'] = hashes(scope)
            if frozen:
                check_snapshot(frozen, scope)
            record['valid'] = (record['exit_code'] == 0 and not record['timed_out'] and
                               'error' not in record and record.get('before_hashes') == record['after_hashes'])
        except (OSError, ValueError) as error:
            record['error'] = str(error)
            if frozen:
                invalidate(frozen, str(error))
        record['ended_at'] = now()
        (directory / 'stdout.log').write_bytes(stdout)
        (directory / 'stderr.log').write_bytes(stderr)
        save(directory / 'evidence.json', record)
    return directory / 'evidence.json', record['valid']


def main():
    # Split before argparse so command flags are never interpreted as evidence options.
    args = sys.argv[1:]
    command = []
    if '--' in args:
        index = args.index('--')
        args, command = args[:index], args[index + 1:]
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('design').add_argument('file')
    sub.add_parser('check').add_argument('file')
    for action in ('snapshot', 'run'):
        child = sub.add_parser(action)
        child.add_argument('scope')
        child.add_argument('output')
        if action == 'run':
            child.add_argument('--snapshot')
            child.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args(args)
    try:
        if args.action == 'design':
            print(hashlib.sha256(Path(args.file).read_bytes()).hexdigest())
        elif args.action == 'check':
            print(json.dumps(check_snapshot(args.file)))
        elif args.action == 'snapshot':
            print(snapshot(scope_file(args.scope), args.output))
        else:
            path, valid = run(scope_file(args.scope), args.output, command, args.snapshot, args.timeout)
            print(json.dumps({'evidence': str(path), 'valid': valid}))
            return 0 if valid else 1
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
