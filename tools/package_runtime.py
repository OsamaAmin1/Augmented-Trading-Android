"""Embed original runtime unchanged, adding mobile-only files."""
from pathlib import Path
import zipfile,sys,hashlib
P=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('Usage: python tools/package_runtime.py V1_19.zip')
with zipfile.ZipFile(sys.argv[1]) as src,zipfile.ZipFile(P/'app/src/main/assets/runtime.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
    assert src.testzip() is None
    for n in src.namelist():
        if n.startswith('private/') or n.startswith('/') or '..' in Path(n).parts:raise ValueError('Unsafe or private runtime entry: '+n)
        out.writestr(n,src.read(n))
    for n in ('mobile-help.js','mobile-catalogue.js','help_catalogue.json'):out.write(P/n,n)
print('Runtime packaged.')
