"""Mirror the published course reader on a domain accessible to web assistants."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'online/dist'
ORIGIN = 'https://yanisssvibecoder.github.io/campus-revisions-documents/'
CAMPUS = 'https://campus-revisions-aasem.aglowhawk.chatgpt.site/'
for source in (SOURCE / 'pour-chatgpt').glob('*.html'):
    target = ROOT / 'pour-chatgpt' / source.name
    target.parent.mkdir(exist_ok=True)
    content = source.read_text(encoding='utf-8')
    content = content.replace('href="/"', 'href="' + CAMPUS + '"')
    content = content.replace('href="/', 'href="' + ORIGIN)
    target.write_text(content, encoding='utf-8')
    if source.name == 'index.html':
        (ROOT / 'index.html').write_text(content, encoding='utf-8')
for source in (SOURCE / 'documents').iterdir():
    shutil.copyfile(source, ROOT / 'documents' / source.name)
data = json.loads((SOURCE / 'donnees/campus.json').read_text(encoding='utf-8'))
for resource in data['resources']:
    for key in ['fileUrl', 'textUrl']:
        if resource.get(key, '').startswith('/'):
            resource[key] = ORIGIN + resource[key].lstrip('/')
(ROOT / 'donnees').mkdir(exist_ok=True)
(ROOT / 'donnees/campus.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
assert len(data['courses']) == 6
assert all((ROOT / r[key].removeprefix(ORIGIN)).is_file()
           for r in data['resources'] for key in ['fileUrl', 'textUrl'] if r.get(key))
assert all((ROOT / 'pour-chatgpt' / (lesson['id'] + '.html')).is_file()
           for course in data['courses'] for lesson in course['lessons'])
print('Public reader mirrored: six courses, all lessons and available documents.')
