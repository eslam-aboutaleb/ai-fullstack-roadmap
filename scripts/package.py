"""Package only the public static site, excluding private authoring and Git data."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parent.parent
source=root/'_build'
if not (source/'manifest.json').exists():raise SystemExit('Run python3 scripts/build.py before packaging')
out=root/'_site'
if out.exists(): shutil.rmtree(out)
out.mkdir()
for pattern in ('*.html','*.css','*.js'):
    for path in source.glob(pattern): shutil.copy2(path,out/path.name)
for name in ('manifest.json','.nojekyll','LICENSE'):
    shutil.copy2(source/name,out/name)
for name in ('diagrams','examples'):
    shutil.copytree(source/name,out/name)
print('Static Pages artifact ready')
