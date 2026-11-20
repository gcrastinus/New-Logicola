"""Traditional (Aristotelian) vs modern star test for Set B syllogisms.

Enumerates all 256 standard-form categorical syllogisms (64 moods x 4 figures),
the 512 A/B/C forms the Set B generator can build, and every singular-term
syllogism (one or two small letters) in the forms Set B uses. Ground truth is
an independent brute-force model check written here (Venn-region occupancy for
general terms; small domains for singular terms), with every general term
non-empty on the traditional model. The app's verdicts (starTestG, catValid,
catValidTrad) and Gensler's star rules (modern: each capital starred exactly
once; traditional: at least once; both: exactly one right-hand star) must all
agree with it. Also checks the star-test explanation wording.

Run a local server, then: python3 tests/test_traditional_star.py [base]
"""
import itertools, sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
CHROME = '/usr/bin/google-chrome'
results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + str(info)) if info and not cond else ''))

CAT = ['all', 'no', 'some', 'somenot']
SINGLE = ['is', 'isnot']        # x is F / x is not F
IDENT = ['ident', 'identnot']   # x is y / x is not y
LETTER = {'all': 'A', 'no': 'E', 'some': 'I', 'somenot': 'O'}

# ---------------- independent ground truth ----------------
def holds(st, ext, ind):
    t, a, b = st['t'], st['a'], st['b']
    if t == 'is':       return ind[a] in ext[b]
    if t == 'isnot':    return ind[a] not in ext[b]
    if t == 'ident':    return ind[a] == ind[b]
    if t == 'identnot': return ind[a] != ind[b]
    A, B = ext[a], ext[b]
    if t == 'all':      return A <= B
    if t == 'no':       return not (A & B)
    if t == 'some':     return bool(A & B)
    if t == 'somenot':  return bool(A - B)

def letters_of(form):
    ls = []
    for st in form:
        for x in (st['a'], st['b']):
            if x not in ls: ls.append(x)
    caps = [x for x in ls if x.isupper()]; smalls = [x for x in ls if x.islower()]
    return caps, smalls

def sem_valid(prem, concl, traditional):
    caps, smalls = letters_of(prem + [concl])
    if not smalls:
        # each element of the domain is fully described by which caps it is in,
        # so a model = a set of occupied regions (exact for categorical forms)
        regions = list(itertools.product([0, 1], repeat=len(caps)))
        for occ in itertools.product([0, 1], repeat=len(regions)):
            elems = [r for r, o in zip(regions, occ) if o]
            ext = {c: frozenset(i for i, r in enumerate(elems) if r[k]) for k, c in enumerate(caps)}
            if traditional and any(not ext[c] for c in caps): continue
            if all(holds(p, ext, {}) for p in prem) and not holds(concl, ext, {}): return False
        return True
    for n in range(1, 6):
        dom = range(n)
        subsets = [frozenset(s) for k in range(n + 1) for s in itertools.combinations(dom, k)]
        for exts in itertools.product(subsets, repeat=len(caps)):
            ext = dict(zip(caps, exts))
            if traditional and any(not ext[c] for c in caps): continue
            for inds in itertools.product(dom, repeat=len(smalls)):
                ind = dict(zip(smalls, inds))
                if all(holds(p, ext, ind) for p in prem) and not holds(concl, ext, ind): return False
    return True

# ---------------- Gensler's star rules, written out independently ----------------
def dist(st, side):
    t = st['t']
    return {'all': side == 'a', 'no': True, 'some': False, 'somenot': side == 'b',
            'is': False, 'isnot': side == 'b', 'ident': False, 'identnot': side == 'b'}[t]

def star_counts(prem, concl):
    cnt, right = {}, 0
    for st, isc in [(prem[0], False), (prem[1], False), (concl, True)]:
        for side in 'ab':
            if dist(st, side) != isc:
                L = st[side]; cnt[L] = cnt.get(L, 0) + 1
                if side == 'b': right += 1
    return cnt, right

def gensler(prem, concl, traditional):
    cnt, right = star_counts(prem, concl)
    caps, _ = letters_of(prem + [concl])
    if right != 1: return False
    if traditional: return all(cnt.get(c, 0) >= 1 for c in caps)
    return all(cnt.get(c, 0) == 1 for c in caps)

def S(t, a, b): return {'t': t, 'a': a, 'b': b}

# 256 standard forms: major premise has P, minor has S, conclusion S-P
FIG = {1: (('M', 'P'), ('S', 'M')), 2: (('P', 'M'), ('S', 'M')),
       3: (('M', 'P'), ('M', 'S')), 4: (('P', 'M'), ('M', 'S'))}
standard = []
for fig, ((a1, b1), (a2, b2)) in FIG.items():
    for t1, t2, t3 in itertools.product(CAT, repeat=3):
        mood = LETTER[t1] + LETTER[t2] + LETTER[t3]
        standard.append((mood + '-' + str(fig), [S(t1, a1, b1), S(t2, a2, b2)], S(t3, 'S', 'P')))

# 512 generator forms (makeSyll: A-B, B-C, conclusion A-C, any order)
gen = []
for (a1, b1), (a2, b2), (ac, bc) in itertools.product([('A', 'B'), ('B', 'A')], [('B', 'C'), ('C', 'B')], [('A', 'C'), ('C', 'A')]):
    for t1, t2, t3 in itertools.product(CAT, repeat=3):
        gen.append(([S(t1, a1, b1), S(t2, a2, b2)], S(t3, ac, bc)))

# singular-term syllogisms: every 3-wff form where each term occurs exactly
# twice, over terms {a,F,G} (one small, two capitals) and {a,b,F} (two smalls)
def all_wffs(terms):
    out = []
    for x, y in itertools.permutations(terms, 2):
        if x.isupper() and y.isupper(): out += [S(t, x, y) for t in CAT]
        elif x.islower() and y.isupper(): out += [S(t, x, y) for t in SINGLE]
        elif x.islower() and y.islower(): out += [S(t, x, y) for t in IDENT]
    return out
singular = []
for terms in (['a', 'F', 'G'], ['a', 'b', 'F']):
    W = all_wffs(terms)
    for p1, p2, c in itertools.product(W, repeat=3):
        occ = {}
        for st in (p1, p2, c):
            for x in (st['a'], st['b']): occ[x] = occ.get(x, 0) + 1
        if sorted(occ) == sorted(terms) and all(v == 2 for v in occ.values()):
            # conclusion must not repeat a premise's term pair (a real syllogism)
            if {c['a'], c['b']} not in ({p1['a'], p1['b']}, {p2['a'], p2['b']}):
                singular.append(([p1, p2], c))

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=CHROME, args=['--headless=new', '--no-sandbox', '--disable-gpu'])
    pg = br.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function('()=>typeof starTestG==="function" && typeof catValidTrad==="function"')

    def app(forms, capsOnly):
        return pg.evaluate("""([forms,capsOnly]) => forms.map(([prem,concl]) => {
          const L=[...new Set([...prem,concl].flatMap(s=>[s.a,s.b]))];
          const r={sm:starTestG(prem,concl,'modern'), st:starTestG(prem,concl,'traditional')};
          if(capsOnly){ r.cm=catValid(prem,concl,L); r.ct=catValidTrad(prem,concl,L); r.old=starTest(prem,concl); }
          return r; })""", [forms, capsOnly])

    # ---- 256 standard forms ----
    res = app([[p, c] for _, p, c in standard], True)
    gm = {n for (n, p, c) in standard if sem_valid(p, c, False)}
    gt = {n for (n, p, c) in standard if sem_valid(p, c, True)}
    print('ground truth: modern valid =', len(gm), sorted(gm))
    print('ground truth: traditional valid =', len(gt), sorted(gt))
    print('traditional-only:', sorted(gt - gm))
    check('ground truth: 15 modern-valid forms', len(gm) == 15)
    check('ground truth: 24 traditional-valid forms', len(gt) == 24 and gm <= gt)
    EXPECT_TRAD = {'AAA-1','EAE-1','AII-1','EIO-1','AAI-1','EAO-1',
                   'EAE-2','AEE-2','EIO-2','AOO-2','EAO-2','AEO-2',
                   'IAI-3','AII-3','OAO-3','EIO-3','AAI-3','EAO-3',
                   'AEE-4','IAI-4','EIO-4','AEO-4','AAI-4','EAO-4'}
    check('ground truth matches the textbook list of 24 (Barbara ... Fesapo)', gt == EXPECT_TRAD, sorted(gt ^ EXPECT_TRAD))
    for key, label, truth in [('sm', 'starTestG modern', gm), ('st', 'starTestG traditional', gt),
                              ('cm', 'catValid (modern)', gm), ('ct', 'catValidTrad', gt), ('old', 'starTest (legacy)', gm)]:
        got = {n for (n, _, _), r in zip(standard, res) if r[key]}
        check(f'256 forms: {label} valid set == ground truth', got == truth, f'extra={sorted(got-truth)} missing={sorted(truth-got)}')
    gs_m = {n for (n, p, c) in standard if gensler(p, c, False)}
    gs_t = {n for (n, p, c) in standard if gensler(p, c, True)}
    check('256 forms: Gensler modern rule (exactly once) == ground truth', gs_m == gm)
    check('256 forms: Gensler traditional rule (at least once) == ground truth', gs_t == gt, f'{sorted(gs_t ^ gt)}')
    twice = sorted(n for (n, p, c) in standard if n in gt and max(star_counts(p, c)[0].values()) == 2)
    print('traditional-valid forms with a letter starred twice:', twice)
    check('every traditional-only form has a letter starred twice', set(twice) == gt - gm)

    # ---- 512 generator forms ----
    res = app(gen, True)
    bad = []
    for (p, c), r in zip(gen, res):
        tm, tt = sem_valid(p, c, False), sem_valid(p, c, True)
        if not (r['sm'] == r['cm'] == gensler(p, c, False) == tm and r['st'] == r['ct'] == gensler(p, c, True) == tt):
            bad.append((p, c, r, tm, tt))
    check(f'512 generator forms: app star test, app semantics, Gensler rules and ground truth agree in both models', not bad, bad[:3])

    # ---- singular-term forms ----
    res = app(singular, False)
    badm, badt = [], []
    for (p, c), r in zip(singular, res):
        tm, tt = sem_valid(p, c, False), sem_valid(p, c, True)
        if not (r['sm'] == gensler(p, c, False) == tm): badm.append((p, c, r, tm))
        if not (r['st'] == gensler(p, c, True) == tt): badt.append((p, c, r, tt))
    print('singular-term forms checked:', len(singular), 'valid modern:', sum(sem_valid(p, c, False) for p, c in singular),
          'valid traditional:', sum(sem_valid(p, c, True) for p, c in singular))
    check('singular forms: modern star test == ground truth', not badm, badm[:3])
    check('singular forms: traditional star test == ground truth', not badt, badt[:3])

    # ---- Venn diagrams: app's premise diagram (+ Gensler's traditional ✕) read off ----
    vt = pg.evaluate("""(forms) => forms.map(([prem,concl]) => { const L=['A','B','C'];
        const t=vennTarget(prem,L); if(!t) return null;
        return {shaded:t.shaded, xs:t.xs, tx:vennTradXs(t,L), codes:[0,1,2,3,4,5,6].map(regionCode)}; })""", gen)
    def read(concl, shaded, xs, codes):
        idx = {'A': 0, 'B': 1, 'C': 2}
        ina = lambda i, L: codes[i][idx[L]]
        a, b, t = concl['a'], concl['b'], concl['t']
        if t == 'all': return all(i in shaded for i in range(7) if ina(i, a) and not ina(i, b))
        if t == 'no':  return all(i in shaded for i in range(7) if ina(i, a) and ina(i, b))
        if t == 'some': return any(ina(i, a) and ina(i, b) for i in xs)
        return any(ina(i, a) and not ina(i, b) for i in xs)
    vbad, nv = [], 0
    for (p_, c), r in zip(gen, vt):
        if r is None: continue
        nv += 1
        if read(c, r['shaded'], r['xs'], r['codes']) != sem_valid(p_, c, False): vbad.append(('modern', p_, c))
        if read(c, r['shaded'], r['tx'], r['codes']) != sem_valid(p_, c, True): vbad.append(('traditional', p_, c))
    print('Venn forms checked (deterministic diagrams):', nv)
    check('Venn: modern diagram, and traditional diagram with the one-unshaded-area ✕, decide validity correctly', not vbad, vbad[:3])

    # ---- explanation wording ----
    def reason(prem, concl, model):
        return pg.evaluate("""([prem,concl,model]) => { state.bImport=model;
          const L=['A','B','C'];
          const s={prem,concl,letters:L,model,validModern:catValid(prem,concl,L),validTrad:catValidTrad(prem,concl,L)};
          s.valid=model==='traditional'?s.validTrad:s.validModern;
          const d=document.createElement('div'); d.innerHTML=starReason(s); return d.textContent; }""", [prem, concl, model])
    tim = ([S('no', 'A', 'B'), S('all', 'C', 'B')], S('no', 'A', 'C'))
    t1 = reason(*tim, 'traditional'); print('  Timothy example, traditional:', t1)
    check('traditional explanation states the "at least once" rule', 'at least once' in t1 and 'VALID' in t1)
    check('traditional explanation keeps "exactly one right-hand star"', 'exactly one right-hand star' in t1)
    m1 = reason(*tim, 'modern'); print('  Timothy example, modern:', m1)
    check('modern explanation unchanged', 'The star test: there is exactly one right-hand star, and A is starred 1×, B is starred 1×, C is starred 1×. So this argument is VALID (modern model).' in m1)
    dar = ([S('all', 'B', 'C'), S('all', 'B', 'A')], S('some', 'A', 'C'))
    t2 = reason(*dar, 'traditional'); print('  Darapti, traditional:', t2)
    check('Darapti traditional: B starred 2x, VALID', 'B is starred 2×' in t2 and 'B is starred twice, which the traditional test allows' in t2 and 'VALID' in t2 and 'INVALID' not in t2)
    m2 = reason(*dar, 'modern'); print('  Darapti, modern:', m2)
    check('Darapti modern: INVALID, B starred 2x', 'INVALID' in m2 and 'B is starred 2×' in m2)
    rule = pg.evaluate("()=>starRuleText('traditional')")
    check('starRuleText(traditional) says at least once', 'at least once' in rule)
    check('no page errors', not errs, errs)
    br.close()

print(f"\n{sum(ok for _, ok in results)}/{len(results)} passed")
sys.exit(0 if all(ok for _, ok in results) else 1)
