import re, json, html, unicodedata
def norm(w):
    w = unicodedata.normalize('NFC', html.unescape(w)).lower()
    return re.sub(r'[“”"«»]', '', w)
def load(fn):
    s = open(fn, encoding='utf-8').read(); pages = []
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', s, re.S):
        words = []
        for li, lm in enumerate(re.finditer(r'<line[^>]*>(.*?)</line>', pm.group(3), re.S)):
            for wm in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', lm.group(1)):
                words.append(dict(x0=float(wm[1]), y0=float(wm[2]), x1=float(wm[3]), y1=float(wm[4]), t=norm(wm[5]), line=li))
        pages.append(dict(w=float(pm[1]), h=float(pm[2]), words=words))
    return pages
def find(pages, phrase):
    toks = [norm(t) for t in phrase.split()]
    for pi, p in enumerate(pages):
        W = p['words']
        for i in range(len(W) - len(toks) + 1):
            if all(W[i + k]['t'] == toks[k] for k in range(len(toks))):
                seg = W[i:i + len(toks)]; rects = []
                for w in seg:
                    if rects and rects[-1]['line'] == w['line']:
                        r = rects[-1]; r['x1'] = w['x1']; r['y0'] = min(r['y0'], w['y0']); r['y1'] = max(r['y1'], w['y1'])
                    else: rects.append(dict(line=w['line'], x0=w['x0'], x1=w['x1'], y0=w['y0'], y1=w['y1']))
                return pi, [[r['x0'], r['y0'], r['x1'], r['y1']] for r in rects]
    raise SystemExit('NOT FOUND: ' + phrase)
A, B = load('A.html'), load('B.html')
ITEMS = [
 (A, ['suministro, mediante renovación, de 50 licencias Office 365 E3 EEE (sin Teams),', 'Cloud Solution Provider (CSP) de Microsoft,', 'CPV: 48000000-8, Paquetes de software y sistemas de información.']),
 (A, ['La duración del contrato será de 24 meses,', '(22.620,00 €), IVA excluido.', 'El coste máximo unitario es de 226,20 € por licencia y anualidad, IVA excluido']),
 (A, ['Se establece como único criterio de adjudicación el PRECIO, con una ponderación del 100 %.']),
 (A, ['habilitación necesaria para comercializar las suscripciones objeto del contrato a través del programa oficial Cloud Solution Provider (CSP) de Microsoft.', 'inscritos en el Registro Oficial de Licitadores y Empresas Clasificadas del Sector Público (ROLECE),', 'estarán exentos de acreditar la solvencia económica y financiera y la solvencia técnica o profesional,']),
 (A, ['DIEZ DÍAS HÁBILES', 'finalizando dicho plazo a las 14.00 horas del último día del plazo.']),
 (B, ['deberá ser partner autorizado de Microsoft para la reventa de licencias Microsoft 365/Office 365 en modalidad CSP (Cloud Solution Provider). Se excluirán ofertas que no cumplan este requisito.']),
 (B, ['La duración del contrato será de DOS AÑOS (24 meses), contados desde el 10 de diciembre de 2026.', 'el 10 de diciembre de 2026 exista plena continuidad del servicio.']),
 (B, ['acusar recibo en un plazo máximo de dos (2) horas e iniciar las actuaciones necesarias para su resolución o escalado al fabricante en un plazo máximo de cuatro (4) horas laborables']),
]
out = []
for doc, phr in ITEMS:
    rs = []; pg = None
    for ph in phr:
        pi, r = find(doc, ph); rs.append(dict(page=pi, rects=r)); pg = pi
    out.append(rs)
json.dump(dict(items=out, pw=A[0]['w'], ph=A[0]['h'], nA=len(A), nB=len(B)), open('hl.json', 'w'))
for i, it in enumerate(out): print(i, [(x['page'], len(x['rects']), round(x['rects'][0][1])) for x in it])
