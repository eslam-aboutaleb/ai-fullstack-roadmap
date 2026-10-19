"""Package only the public static site, excluding private authoring and Git data."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parent.parent
out=root/'_site'
if out.exists(): shutil.rmtree(out)
out.mkdir()
for pattern in ('*.html','*.css','*.js'):
    for path in root.glob(pattern): shutil.copy2(path,out/path.name)
for name in ('manifest.json','.nojekyll'):
    shutil.copy2(root/name,out/name)
for name in ('diagrams','examples'):
    shutil.copytree(root/name,out/name)
print('Static Pages artifact ready')
