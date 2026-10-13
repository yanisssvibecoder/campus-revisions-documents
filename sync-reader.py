"""Mirror the published course reader on a domain accessible to web assistants."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'online/dist'
ORIGIN = 'https://yanisssvibecoder.github.io/campus-revisions-documents/'
CAMPUS = 'https://campus-revisions-aasem.aglowhawk.chatgpt.site/'
RAW = 'https://raw.githubusercontent.com/yanisssvibecoder/campus-revisions-documents/main/'
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
index = ['# Campus — accès aux cours pour ChatGPT', '',
         'Cours complets, exemples, exercices, corrections et documents disponibles. Réponds en français.',
         'La progression publiée est un instantané. Utilise le contexte IA fourni par l’étudiant pour sa progression actuelle.', '',
         '[Campus interactif](' + CAMPUS + ')', '', '## Six cours', '']
for course in data['courses']:
    filename = 'cours-' + course['id'] + '.md'
    index.append('- [' + course['title'] + '](' + RAW + filename + ')')
    lines = ['# ' + course['title'], '', '[Cours complet](' + RAW + 'pour-chatgpt/cours-' + course['id'] + '.html)', '']
    for key in ['lessons', 'officialExercises', 'projects', 'mocks', 'mockExams']:
        lines += ['## ' + key, '']
        lines += ['- [' + item.get('title', item['id']).replace('[', '(').replace(']', ')') + '](' + RAW + 'pour-chatgpt/' + item['id'] + '.html)'
                  for item in course.get(key, []) if isinstance(item, dict) and item.get('id')]
    lines += ['', '## Documents et textes', '']
    for resource in data['resources']:
        if resource.get('course') != course['id']:
            continue
        lines.append('- ' + resource['title'])
        for key, label in [('fileUrl', 'Document original'), ('textUrl', 'Texte extrait')]:
            if resource.get(key):
                lines.append('  - [' + label + '](' + RAW + resource[key].removeprefix(ORIGIN) + ')')
    (ROOT / filename).write_text('\n'.join(lines), encoding='utf-8')
index += ['', '[Planning publié](' + RAW + 'pour-chatgpt/planning.html)',
          '[Toutes les données JSON](' + RAW + 'donnees/campus.json)']
(ROOT / 'campus.md').write_text('\n'.join(index), encoding='utf-8')
assert len(data['courses']) == 6
assert all((ROOT / r[key].removeprefix(ORIGIN)).is_file()
           for r in data['resources'] for key in ['fileUrl', 'textUrl'] if r.get(key))
assert all((ROOT / 'pour-chatgpt' / (lesson['id'] + '.html')).is_file()
           for course in data['courses'] for lesson in course['lessons'])
print('Public reader mirrored: six courses, all lessons and available documents.')
