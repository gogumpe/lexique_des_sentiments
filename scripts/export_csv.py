"""Exporte toutes les fiches et leurs valeurs dans export/fiches-sentiments.csv (à lancer après build.py)."""
import os, csv, json, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, 'data', 'vdata.js'), encoding='utf-8').read()
TREE = json.loads(re.search(r'const TREE = (\{.*?\});\n', s).group(1))
VW = json.loads(re.search(r'const VW = (\[.*?\]);\n', s, re.S).group(1))
FAM = {sf: fam for fam, sfs in TREE.items() for sf in sfs}
cols = ['mot', 'famille', 'sous-famille', 'orientation', 'définition', 'ce qui la déclenche', 'dans le corps',
        'ce vers quoi elle pousse', 'nuances', 'valence', 'source valence', 'activation', 'source activation',
        'contrôle', 'source contrôle', 'contrôle relatif (axe 3D)', 'termes NRC']
rows = [[w['m'], FAM[w['sf']], w['sf'], w['o'], w['d'], w['dec'], w['corps'], w['pousse'], w['nu'],
         w['va'], w['src'], w['ar'], w.get('sar', 'NRC'), w['do'], w['sdo'], w['dc'], ', '.join(w['en'])] for w in VW]
rows.sort(key=lambda r: (r[1], r[0].lower()))
with open(os.path.join(ROOT, 'export', 'fiches-sentiments.csv'), 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows([cols] + rows)
print(len(rows), 'fiches exportées')
