"""Set B syllogism coverage, and the no-points-after-a-wrong-verdict rule (Set B and the other true/false sets: D, E, K, M, S).

Coverage: draws thousands of problems from makeSyll and makeSyllSingular in
both models and checks that every valid mood/figure (15 modern, 24
traditional) appears at a fair rate, that invalid problems lean toward tricky
near misses (incl. the existential fallacy on the modern model), that every
rule violation shows up, that obvious junk stays rare, and that the singular
forms include every valid kind plus the classic tricky invalid ones.

Singular-term mix: simulated sets of the English and letter-form generators
(bEnglish, bSym, bStar) must keep at least 60% of items with no singular
term, at most 40% with any singular term, at most 15% (never above 20%)
with more than one, and must not place singular-term items back to back.

Scoring: on a Set B valid/invalid problem, a wrong click costs the usual
points; clicking the right answer afterwards shows it but earns 0. A first-try
right answer still earns +10. Optional screenshots of the sequence.

Run a local server, then: python3 tests/test_syllogism_coverage.py [base] [shots-dir]
"""
import collections, os, sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
SHOTS = sys.argv[2] if len(sys.argv) > 2 else ''
CHROME = '/usr/bin/google-chrome'
N = 12000
results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + str(info)) if info and not cond else ''))

LET = {'all': 'A', 'no': 'E', 'some': 'I', 'somenot': 'O'}
def dist(st, side): return {'all': side == 'a', 'no': True, 'some': False, 'somenot': side == 'b'}[st['t']]
def classify(p, c, model='modern'):
    S, P = c['a'], c['b']; M = ({p[0]['a'], p[0]['b'], p[1]['a'], p[1]['b']} - {S, P}).pop()
    maj = [x for x in p if P in (x['a'], x['b'])][0]; mn = [x for x in p if x is not maj][0]
    fig = {(True, False): 1, (False, False): 2, (True, True): 3, (False, True): 4}[(maj['a'] == M, mn['a'] == M)]
    br = []
    dp = lambda T: any(dist(x, 'a' if x['a'] == T else 'b') for x in p if T in (x['a'], x['b']))
    if not dp(M): br.append('undistributed middle')
    if dist(c, 'b') and not dp(P): br.append('illicit major')
    if dist(c, 'a') and not dp(S): br.append('illicit minor')
    neg = sum(x['t'] in ('no', 'somenot') for x in p); cneg = c['t'] in ('no', 'somenot')
    if neg == 2: br.append('two negative premises')
    elif neg == 1 and not cneg: br.append('affirmative conclusion, negative premise')
    elif neg == 0 and cneg: br.append('negative conclusion, affirmative premises')
    if model == 'modern' and all(x['t'] in ('all', 'no') for x in p) and c['t'] in ('some', 'somenot'): br.append('existential fallacy')
    return LET[maj['t']] + LET[mn['t']] + LET[c['t']] + '-' + str(fig), br

def canon(p, c):  # singular form up to renaming of letters
    ren = {}
    def r(x):
        if x not in ren: ren[x] = ('XYZ' if x.isupper() else 'xyz')[sum(k.isupper() == x.isupper() for k in ren)]
        return ren[x]
    return ' / '.join(f"{st['t']} {r(st['a'])} {r(st['b'])}" for st in p + [c])

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=CHROME, args=['--headless=new', '--no-sandbox', '--disable-gpu'])
    pg = br.new_page(viewport={'width': 1000, 'height': 860})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function('()=>typeof makeSyll==="function" && typeof syllCatPools==="function"')

    for model, nvalid in (('modern', 15), ('traditional', 24)):
        res = pg.evaluate("""([n,model])=>{state.bImport=model; const r=[];
            for(let i=0;i<n;i++){ const s=makeSyll(); r.push([s.prem,s.concl,s.valid,s.kind]); } return r;}""", [N, model])
        vc, kinds, rules, nbreak = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
        for p, c, v, k in res:
            mf, b = classify(p, c, model)
            if v: vc[mf] += 1
            else:
                kinds[k] += 1; nbreak[len(b)] += 1
                for x in b: rules[x] += 1
            if v and b: check(f'{model}: valid form {mf} breaks no rule', False, b)
        nv = sum(vc.values()); ni = len(res) - nv
        print(f'{model}: valid {nv}, invalid {ni}; valid mood-figures {len(vc)}; invalid kinds {dict(kinds)}; rules-broken histogram {dict(sorted(nbreak.items()))}')
        check(f'{model}: all {nvalid} valid mood/figures appear', len(vc) == nvalid, sorted(vc))
        lo = min(vc.values()) / (nv / nvalid)
        check(f'{model}: each valid mood/figure within 25% of an even share (lowest {lo:.2f})', lo > 0.75)
        check(f'{model}: about half the problems are valid', 0.45 < nv / len(res) < 0.55)
        check(f'{model}: invalid problems are mostly near misses: one rule broken or existential (>=70%)', (kinds['near'] + kinds['exist']) / ni >= 0.70, dict(kinds))
        check(f'{model}: obvious junk (3+ rules broken) under 5% of invalid', (sum(v for k, v in nbreak.items() if k >= 3)) / ni < 0.05, dict(nbreak))
        want = {'undistributed middle', 'illicit major', 'illicit minor', 'two negative premises',
                'affirmative conclusion, negative premise', 'negative conclusion, affirmative premises'}
        if model == 'modern': want.add('existential fallacy')
        check(f'{model}: every rule violation appears', want <= set(rules), sorted(want - set(rules)))
        print(f'  {model} invalid problems by rule broken:', dict(rules.most_common()))
        if model == 'modern':
            check('modern: existential-fallacy forms (Darapti, Barbari, ...) ~20% of invalid', 0.15 < kinds['exist'] / ni < 0.27, kinds['exist'] / ni)
        # Venn problems still find a deterministic diagram, both verdicts
        vv = pg.evaluate("""(model)=>{state.bImport=model; let ok=0,v=0; for(let i=0;i<400;i++){ const s=makeSyll({deterministicVenn:true,wantValid:i%2===0,model});
            if(vennTarget(s.prem,s.letters)) ok++; if(s.valid) v++; } return [ok,v];}""", model)
        check(f'{model}: Venn generator gets deterministic diagrams with both verdicts', vv[0] == 400 and 150 < vv[1] < 250, vv)

        # singular-term forms
        sres = pg.evaluate("""([n,model])=>{const r=[]; for(let i=0;i<n;i++){ const s=makeSyllSingular(Math.random()<0.5,model);
            r.push([s.prem,s.concl,s.valid,s.kind]); } return r;}""", [6000, model])
        allv = pg.evaluate("""(model)=>[['a','F','G'],['a','b','F']].flatMap(t=>syllSingPools(model,t).valid.map(f=>[f.prem,f.concl]))""", model)
        need = {canon(p, c) for p, c in allv}
        seen_v = {canon(p, c) for p, c, v, k in sres if v}
        check(f'{model}: every valid singular form appears ({len(need)} kinds)', need <= seen_v, sorted(need - seen_v)[:4])
        seen_i = {canon(p, c) for p, c, v, k in sres if not v}
        tricky = {
            'affirming the consequent: x is Y; all X is Y; so x is X': 'is x X / all Y X / is x Y',
            'denying the antecedent: x is not X; all X is Y; so x is not Y': 'isnot x X / all X Y / isnot x Y',
            'two negatives: x is not X; no X is Y; so x is Y': 'isnot x X / no X Y / is x Y',
            'some-middle: x is X; some X is Y; so x is Y': 'is x X / some X Y / is x Y',
        }
        for name, form in tricky.items():
            check(f'{model}: tricky singular invalid appears — {name}', form in seen_i)
        sk = collections.Counter(k for *_, v, k in sres if not v)
        check(f'{model}: singular invalids mostly near misses', (sk['near'] + sk['exist']) / sum(sk.values()) >= 0.8, dict(sk))

    # ---------------- singular-term mix in generated sets ----------------
    # A clean 100-point run is 10 problems; misses make a set longer. Caps:
    # >=60% with no singular term, <=40% with any, <=15% (never >20%) with
    # more than one; no back-to-back singular items. Applies to symbolic
    # (letters), English, and the letter-form star drill.
    src = pg.evaluate("()=>[String(bSym),String(bEnglish),String(bStar)].join('\\n')")
    check('bSym, bEnglish and bStar all draw through makeBSyll',
          "makeBSyll({planKey:'sym'})" in src and "makeBSyll({planKey:'english'" in src and "makeBSyll({planKey:'star'})" in src,
          src[:240])
    MIX_JS = """([nSets, setLen, key, noIdent])=>{
      const count=s=>{const t=new Set(); [...s.prem,s.concl].forEach(st=>{
        if(/[a-z]/.test(st.a)) t.add(st.a); if(/[a-z]/.test(st.b)) t.add(st.b); }); return t.size; };
      const overall={none:0,one:0,multi:0}; const sets=[]; let adj=0, pairs=0;
      let nValid=0, nInvalid=0;
      for(let si=0;si<nSets;si++){
        session.syllPlan=null;
        const kinds=[];
        for(let i=0;i<setLen;i++){
          const s=makeBSyll({planKey:key, noIdent});
          const n=count(s);
          const k=n===0?'none':(n===1?'one':'multi');
          kinds.push(k); overall[k]++;
          if(s.valid) nValid++; else nInvalid++;
          if(i>0){ pairs++; if(kinds[i-1]!=='none' && k!=='none') adj++; }
        }
        const c={none:0,one:0,multi:0}; kinds.forEach(k=>c[k]++);
        sets.push({none:c.none, one:c.one, multi:c.multi, any:c.one+c.multi});
      }
      return {overall, adj, pairs, sets, nSets, setLen, nValid, nInvalid};
    }"""
    for key, noIdent, label in (('sym', False, 'symbolic (letters)'),
                                ('english', True, 'English'),
                                ('star', False, 'star drill')):
        for setLen in (10, 16, 20):
            nSets = 200 if setLen==10 else 120
            d = pg.evaluate(MIX_JS, [nSets, setLen, key, noIdent])
            tot = d['nSets'] * d['setLen']
            none = d['overall']['none'] / tot
            one = d['overall']['one'] / tot
            multi = d['overall']['multi'] / tot
            anyp = one + multi
            print(f'AFTER {label}, {d["nSets"]} sets of {setLen}: none={none:.1%} one={one:.1%} multi={multi:.1%} any={anyp:.1%}; adjacent singular pairs={d["adj"]}; valid={d["nValid"]} invalid={d["nInvalid"]}')
            bad_none = sum(1 for s in d['sets'] if s['none']/setLen < 0.60)
            bad_any = sum(1 for s in d['sets'] if s['any']/setLen > 0.40)
            bad_m15 = sum(1 for s in d['sets'] if s['multi']/setLen > 0.15)
            bad_m20 = sum(1 for s in d['sets'] if s['multi']/setLen > 0.20)
            check(f'{label}, {setLen}-problem sets: every set has ≥60% with no singular term', bad_none==0, bad_none)
            check(f'{label}, {setLen}-problem sets: no set has >40% with a singular term', bad_any==0, bad_any)
            check(f'{label}, {setLen}-problem sets: no set has >15% with more than one singular term', bad_m15==0, bad_m15)
            check(f'{label}, {setLen}-problem sets: never above 20% multi-singular', bad_m20==0, bad_m20)
            check(f'{label}, {setLen}-problem sets: no back-to-back singular-term items', d['adj']==0, d['adj'])
            if setLen==10:
                check(f'{label}, 10-problem sets: overall none in the 60–75% band (using the budget)', 0.60 <= none <= 0.75, none)
                check(f'{label}, 10-problem sets: still a mix of valid and invalid', 0.35 < d['nValid']/tot < 0.65, (d['nValid'], d['nInvalid']))
        if noIdent:
            # measured on the last (20-problem) batch
            check(f'{label}: English-style generation never uses two singular terms', d['overall']['multi']==0, d['overall'])

    # ---------------- scoring ----------------
    BOOT = r"""(want) => {
      const o=document.getElementById('overlay'); if(o) o.className='overlay';
      state.name='T'; state.level=2; state.sound=false; state.bImport='modern'; state.bMode='sym';
      session.set='B'; session.points=40; session.tries=0; session.lastAnswer=undefined;
      let p; do{ p=bSym(); } while(/[a-z] is/.test(p.prompt.replace(/<[^>]+>/g,'')) || p.choices.find(c=>c.correct).text!==(want?'Valid':'Invalid'));
      session.current=p; renderProblem(); return p.choices.map(c=>c.correct); }"""
    def pts(): return pg.evaluate('()=>session.points')
    for want in (True, False):
        pg.goto(BASE); pg.wait_for_function('()=>typeof bSym==="function"')
        corr = pg.evaluate(BOOT, want)
        wrong_i, right_i = corr.index(False), corr.index(True)
        p0 = pts()
        tag = 'valid' if want else 'invalid'
        if SHOTS: pg.screenshot(path=os.path.join(SHOTS, f'1-{tag}-start.png'), full_page=True)
        pg.click(f'.choice[data-i="{wrong_i}"]'); pg.wait_for_timeout(150)
        p1 = pts()
        if SHOTS: pg.screenshot(path=os.path.join(SHOTS, f'2-{tag}-wrong.png'), full_page=True)
        pg.click(f'.choice[data-i="{right_i}"]'); pg.wait_for_timeout(150)
        p2 = pts(); fb = pg.inner_text('#fb')
        if SHOTS: pg.screenshot(path=os.path.join(SHOTS, f'3-{tag}-right-after-wrong.png'), full_page=True)
        check(f'answer {tag}: wrong click costs the usual points ({p0}->{p1})', p1 == p0 - 2)
        check(f'answer {tag}: right click after a wrong one earns 0 ({p1}->{p2})', p2 == p1)
        check(f'answer {tag}: feedback says right, no points', 'No points this time' in fb and 'Next problem' in fb, fb[:120])
        check(f'answer {tag}: choices locked after the right answer', pg.evaluate("()=>[...document.querySelectorAll('.choice')].every(b=>b.onclick===null)"))
    # first-try right still +10
    pg.goto(BASE); pg.wait_for_function('()=>typeof bSym==="function"')
    corr = pg.evaluate(BOOT, True); p0 = pts()
    pg.click(f'.choice[data-i="{corr.index(True)}"]'); pg.wait_for_timeout(150)
    check('first-try right answer still +10', pts() == p0 + 10, (p0, pts()))
    # English and idiomatic arguments carry the same flag
    flags = pg.evaluate("()=>{state.bImport='modern'; return [bEnglish().noCreditAfterWrong, bIdiom().noCreditAfterWrong, bSym().noCreditAfterWrong];}")
    check('Set B symbolic, English and idiomatic valid/invalid all use the rule', all(flags), flags)

    # ---------------- the same rule in the other true/false sets ----------------
    OTHER = [('D', 'dEval({})', 'Set D truth evaluations'), ('E', 'eSym({})', 'Set E truth-assignment'),
             ('E', 'eEnglish({})', 'Set E English'), ('E', 'eIdiom({})', 'Set E idiomatic'),
             ('K', 'kGalactic()', 'Set K Galactic Travel'), ('M', 'mImp()', 'Set M imperative'),
             ('S', 'genS_laws({})', 'Set S Laws')]
    for setid, call, label in OTHER:
        pg.goto(BASE); pg.wait_for_function('()=>typeof renderProblem==="function"')
        corr = pg.evaluate("""([setid,call])=>{ const o=document.getElementById('overlay'); if(o) o.className='overlay';
            state.name='T'; state.level=2; state.sound=false; session.set=setid; session.points=40; session.tries=0;
            const p=eval(call); session.current=p; renderProblem();
            return {flag:!!p.noCreditAfterWrong, n:p.choices.length, c:p.choices.map(c=>c.correct)}; }""", [setid, call])
        check(f'{label}: binary, flagged', corr['flag'] and corr['n'] == 2, corr)
        pg.click(f'.choice[data-i="{corr["c"].index(False)}"]'); pg.wait_for_timeout(100); p1 = pts()
        pg.click(f'.choice[data-i="{corr["c"].index(True)}"]'); pg.wait_for_timeout(100); p2 = pts()
        check(f'{label}: wrong -2, then right earns 0 (40->{p1}->{p2})', p1 == 38 and p2 == 38 and 'No points this time' in pg.inner_text('#fb'))
    # Set D argument truth table: verdict after the table
    pg.goto(BASE); pg.wait_for_function('()=>typeof dArgTable==="function"')
    valid = pg.evaluate("""()=>{ const o=document.getElementById('overlay'); if(o) o.className='overlay';
        state.name='T'; state.level=2; state.sound=false; session.set='D'; session.points=40; session.tries=0;
        const p=dArgTable({}); session.current=p; renderProblem(); return /^<b>VALID/.test(p.explain()); }""")
    pg.evaluate("()=>document.querySelectorAll('.ttcell').forEach(b=>b.click())")
    for _ in range(2):
        if pg.query_selector('#atV'): break
        pg.click('#atCheck'); pg.wait_for_timeout(100)
    p0 = pts()
    pg.click('#atI' if valid else '#atV'); pg.wait_for_timeout(100); p1 = pts()
    pg.click('#atV' if valid else '#atI'); pg.wait_for_timeout(100); p2 = pts()
    check(f'Set D argument table verdict: wrong -2, then right earns 0 ({p0}->{p1}->{p2})', p1 == p0 - 2 and p2 == p1 and 'No points this time' in pg.inner_text('#fb'))
    check('no page errors', not errs, errs)
    br.close()

print(f"\n{sum(ok for _, ok in results)}/{len(results)} passed")
sys.exit(0 if all(ok for _, ok in results) else 1)
