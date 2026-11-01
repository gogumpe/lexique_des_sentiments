"""Pour chaque fiche : valence et activation combinées (NRC recalé + EMONORM), avec les désaccords à trancher."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

import json, re, csv
import numpy as np
N = json.load(open(P('normes','norms.json'), encoding='utf-8')); E = N['emonorm']
L = {r[0]: tuple(map(float, r[1:])) for r in csv.reader(open(P('normes','NRC-VAD-Lexicon-v2.1','NRC-VAD-Lexicon-v2.1.txt'), encoding='utf-8'), delimiter='\t') if r[0] != 'term'}
def ekey(w):
    b = re.sub(r"\s*\(.*\)", "", w).strip()
    for k in (w, b, b.replace('·e', '')):
        if k in E: return k
F = []
exec(open(P('fiches','fiches.py'), encoding='utf-8').read())
import glob
for fn in sorted(glob.glob(P('fiches','fiches_lot*.py'))):
    ns = {}; exec(open(fn, encoding='utf-8').read(), ns); F += [v for k, vv in ns.items() if k.startswith('F') and isinstance(vv, list) for v in vv]
def nrc(f, i): return np.mean([L[e][i] for e in f['en'] if e in L])
# recalage de l'activation : EMONORM (0 à 1) vers l'échelle NRC (-1 à 1), sur les mots communs
pa = [(E[ekey(f['m'])]['ar'], nrc(f, 1)) for f in F if ekey(f['m']) and E[ekey(f['m'])]['ar'] is not None]
aa, ab = np.polyfit([p[0] for p in pa], [p[1] for p in pa], 1); ra = np.corrcoef([p[0] for p in pa], [p[1] for p in pa])[0, 1]
print(f"activation : {len(pa)} mots communs, r = {ra:.2f}")
out, flags = {}, []
for f in F:
    k = ekey(f['m']); vn, an, dn = nrc(f, 0), nrc(f, 1), nrc(f, 2)
    rec = {'va_nrc': vn, 'ar_nrc': an, 'do': dn, 'va': vn, 'ar': an, 'src_va': 'NRC', 'src_ar': 'NRC'}
    if k:
        ve = E[k]['va'] / 0.8  # EMONORM ramené à l'échelle du NRC (recalage inverse)
        rec['va_emo'] = ve
        if abs(ve - vn) < 0.375: rec.update(va=(ve + vn) / 2, src_va='moyenne NRC + EMONORM')
        else: flags.append((f['m'], 'valence', vn, ve))
        if E[k]['ar'] is not None:
            ae = aa * E[k]['ar'] + ab; rec['ar_emo'] = ae

    out[f['m']] = rec
# Décisions sur les désaccords de valence (l'activation reste celle du NRC : EMONORM y est peu fiable, r = 0,41)
OVR = {'manque': 'EMONORM', 'deuil': 'EMONORM', 'affolement': 'EMONORM', 'agitation': 'NRC', 'fragilité': 'NRC', 'vigilance': 'NRC', "échec (sentiment d')": 'EMONORM', 'attachement': 'EMONORM', 'sollicitude': 'NRC', 'dévotion': 'NRC', 'béguin': 'EMONORM', 'émoi': 'EMONORM', 'bouleversé·e': 'NRC', 'frisson': 'NRC', 'griserie': 'NRC', 'ardeur': 'EMONORM', 'délectation': 'NRC', 'plénitude': 'NRC', 'émerveillement': 'EMONORM', 'incertitude': 'EMONORM', 'fureur': 'NRC', 'animosité': 'EMONORM', 'envie': 'NRC', 'supériorité (sentiment de)': 'NRC', 'ivresse': 'NRC'}
# Valences posées à la main quand ni le NRC ni EMONORM ne captent le sens de la fiche
# (« hâte » : avoir hâte, impatience joyeuse ; aligné sur « anticipation joyeuse »).
MANUEL = {'hâte': 0.40}
for m, rec in out.items():
    rec['ar'], rec['src_ar'] = rec['ar_nrc'], 'NRC'
    if m in OVR:
        if OVR[m] == 'EMONORM': rec.update(va=max(-1, min(1, rec['va_emo'])), src_va='EMONORM (désaccord tranché)')
        else: rec.update(va=rec['va_nrc'], src_va='NRC (désaccord tranché)')
    if m in MANUEL: rec.update(va=MANUEL[m], src_va='manuel')
    for k, v in list(rec.items()):
        if isinstance(v, (np.floating, float)): rec[k] = round(float(v), 3)
json.dump(out, open(P('normes','vad_combined.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(F), 'fiches ;', sum(1 for r in out.values() if r['src_va'] != 'NRC'), 'valences combinées ;', len(flags), 'désaccords')
for m, dim, a, b in flags:
    if m not in OVR and m not in MANUEL: print(f"  {m:20s} {dim:10s} NRC {a:+.2f}  EMONORM {b:+.2f}")
for w in ['tristesse', 'désespoir', 'chagrin', 'mélancolie', 'nostalgie']: print(w, {k: round(v, 2) for k, v in out[w].items() if isinstance(v, float)})
