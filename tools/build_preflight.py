"""Build-time checks using only the Python standard library."""
import hashlib, json, sqlite3, tempfile, zipfile
from pathlib import Path
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root/'release_manifest.json').read_text())
with zipfile.ZipFile(root/'app/src/main/assets/runtime.zip') as z:
    assert z.testzip() is None, 'Corrupt embedded runtime'
    assert not any(n.startswith('private/') for n in z.namelist()), 'Private data bundled'
    database = z.read('warehouse.sqlite')
    assert hashlib.sha256(database).hexdigest() == manifest['database_sha256'], 'Warehouse hash mismatch'
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)/'warehouse.sqlite'; p.write_bytes(database)
        with sqlite3.connect(p) as db:
            assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            assert db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0] == manifest['warehouse_tables']
    assert len(json.loads(z.read('help_catalogue.json'))['entries']) == manifest['help_entries']
print('PASS: embedded ZIP, private data exclusion, database hash, SQLite integrity, table count, help catalogue')
