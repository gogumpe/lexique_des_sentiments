"""Vectorise les fiches avec BGE-M3 et exporte les données de la page (data/vdata.js).

python scripts/build.py                 -> recalcule les vecteurs (lent : charge BGE-M3)
python scripts/build.py --sans-vecteurs -> réutilise data/E_bge.npy (rapide). Possible tant que
    les textes vectorisés (définition, déclencheurs, corps, pousse) et la liste des mots n'ont pas changé.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

import csv, json, sys
import numpy as np

F = []
exec(open(P('fiches','fiches.py'), encoding='utf-8').read())
import glob
for fn in sorted(glob.glob(P('fiches','fiches_lot*.py'))):
    ns = {}; exec(open(fn, encoding='utf-8').read(), ns)
    F += [v for k, v in ns.items() if k.startswith('F') and isinstance(v, list) for v in v]
L = {}
for r in csv.reader(open(P('normes','NRC-VAD-Lexicon-v2.1','NRC-VAD-Lexicon-v2.1.txt'), encoding='utf-8'), delimiter='\t'):
    if r[0] != 'term': L[r[0]] = tuple(map(float, r[1:]))

texts = [f"{f['m']} : {f['d']} {f['dec']} {f['corps']} {f['pousse']}" for f in F]
if '--sans-vecteurs' in sys.argv:
    E = np.load(P('data','E_bge.npy'))
    assert len(E) == len(F), "Le nombre de mots a changé : relancer sans --sans-vecteurs."
else:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('BAAI/bge-m3', device='cpu')
    E = model.encode(texts, normalize_embeddings=True, batch_size=8)
S = E @ E.T

VC = json.load(open(P('normes','vad_combined.json'), encoding='utf-8'))
VV = {}; exec(open(P('fiches','vivier.py'), encoding='utf-8').read().split('if __name__')[0], VV)
ZK = {'Amour et lien':'amour','Manque et aspiration':'manque','Joie':'joie','Surprise et perplexité':'surprise','Colère':'colere','Dégoût':'degout','Tristesse':'tristesse','Peur et anxiété':'peur'}
ZONE = {}
for fam, v in VV['V'].items():
    for w in [x.strip() for x in v['P'].split(',')] + [m for m, _ in v['N']]: ZONE[w] = ZK[fam]
for f in F: f['z'] = ZONE.get(f['m'], f['z'])
TX = {}; exec(open(P('fiches','taxo.py'), encoding='utf-8').read(), TX)
PKO = json.load(open(P('fiches','pk_old.json'), encoding='utf-8'))
SF = {w: s for fam, sub in TX['TREE'].items() for s, ws in sub.items() for w in ws}
for f in F: f['sf'] = SF[f['m']]; f['i'] = PKO.get(f['m'], TX['PKN'].get(f['m'], ''))
CT = {}; exec(open(P('fiches','controle.py'), encoding='utf-8').read(), CT)
def ctrl(f, found):
    if f['m'] in CT['DO_MANUAL']: return CT['DO_MANUAL'][f['m']], 'manuel'
    if f['m'] in CT['DO_TERMS']: return float(np.mean([L[e][2] for e in CT['DO_TERMS'][f['m']]])), 'NRC (forme ressentie)'
    return float(np.mean([L[e][2] for e in found])), 'NRC'
AT = {}; exec(open(P('fiches','activation.py'), encoding='utf-8').read(), AT)
def activ(f, found):
    if f['m'] in AT['AR_TERMS']: return float(np.mean([L[e][1] for e in AT['AR_TERMS'][f['m']]])), 'NRC (terme corrigé)'
    return float(np.mean([L[e][1] for e in found])), 'NRC'
words = []
for k, f in enumerate(F):
    found = [e for e in f['en'] if e in L]
    words.append({**{x: f[x] for x in ['m', 'z', 'sf', 'i', 'o', 'd', 'dec', 'corps', 'pousse', 'nu']}, 'en': found,
                  'va': VC[f['m']]['va'], 'src': VC[f['m']]['src_va'],
                  'ar': round(activ(f, found)[0], 3), 'sar': activ(f, found)[1],
                  'do': round(ctrl(f, found)[0], 3), 'sdo': ctrl(f, found)[1]})
# Contrôle relatif (« à agrément égal ») pour l'axe 3D : on retire la part du contrôle prévisible
# par la valence (régression linéaire), puis on multiplie par 1,6 pour que les écarts entre voisins
# aient la même ampleur que sur la valence et l'activation. `do` (brut) reste celui de la fiche.
VA = np.array([w['va'] for w in words]); DO = np.array([w['do'] for w in words])
pente, orig = np.polyfit(VA, DO, 1)
for w in words:
    w['dc'] = round(float(1.6 * (w['do'] - (pente * w['va'] + orig))), 3)
    if w['m'] in CT['DC_PLANCHER'] and w['dc'] < 0: w['dc'] = 0.0
print(f"contrôle relatif : dc = 1,6 × (do − {pente:.3f} × va {-orig:+.3f})")
vec = [[round(float(x), 4) for x in v] for v in E]
open(P('data','vdata.js'), 'w', encoding='utf-8').write(
    'const TREE = ' + json.dumps({f: list(sub) for f, sub in TX['TREE'].items()}, ensure_ascii=False) + ';\n' + 'const VW = ' + json.dumps(words, ensure_ascii=False) + ';\nconst VEC = ' + json.dumps(vec, separators=(',', ':')) + ';\n')
if '--sans-vecteurs' not in sys.argv: np.save(P('data','E_bge.npy'), E)
for i, f in enumerate(F):
    nn = np.argsort(-S[i])[1:6]
    print(f"{f['m']:16s}", ', '.join(f"{F[j]['m']} {S[i, j]:.2f}" for j in nn))
