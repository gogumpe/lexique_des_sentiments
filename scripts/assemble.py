"""Assemble la page finale : src/app.html + data/vdata.js -> index.html (fichier autonome).
Les polices appelées par url(fonts/NOM) dans src/app.html sont intégrées en base64 depuis src/fonts/."""
import base64, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'src', 'app.html'), encoding='utf-8').read()
data = open(os.path.join(ROOT, 'data', 'vdata.js'), encoding='utf-8').read()
assert '/*DATA*/' in tpl

def font(m):
    name = m.group(1)
    raw = open(os.path.join(ROOT, 'src', 'fonts', name), 'rb').read()
    kind = 'woff2' if name.endswith('.woff2') else 'woff' if name.endswith('.woff') else 'ttf'
    return f'url(data:font/{kind};base64,{base64.b64encode(raw).decode()})'

tpl = re.sub(r'url\(fonts/([^)]+)\)', font, tpl)
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(tpl.replace('/*DATA*/', data))
print('index.html écrit')
