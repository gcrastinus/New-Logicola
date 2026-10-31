"""R1 regression tests: the proof checker accepts any legal Gensler proof.
Run:  python3 -m http.server 8766  (in the repo)  then  python3 tests/test_r1_proofs.py
Drives the real proofPlayer in headless Chromium."""
import sys
from playwright.sync_api import sync_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8766/index.html'

SETUP = r"""(a)=>{
  const [kind, prem, concl, mc] = a;
  let prems, c, s;
  if(kind==='prop'){ prems=prem.map(parseProp); c=parseProp(concl); s=provePropositional(prems,c);
    s.prem=prems.map(astRender); s.premAst=prems; s.concl=astRender(c); s.eng={name:'prop',prems,concl:c}; }
  else if(kind==='quant'){ prems=prem.map(qParse); c=qParse(concl); s=proveQuant(prems,c,LVLCFG.mixed||LVLCFG.easier);
    s.prem=prems.map(qRender); s.premAst=prems; s.concl=qRender(c); s.eng={name:'quant',prems,concl:c,opts:LVLCFG.mixed||LVLCFG.easier}; }
  else if(kind==='modal'){ prems=prem.map(qParse); c=qParse(concl); s=proveModal(prems,c);
    s.prem=prems.map(qRender); s.premAst=prems; s.concl=qRender(c); s.eng={name:'modal',prems,concl:c}; }
  else if(kind==='hand'){ // a hand-written script with no engine (like Sets M/O, quantified K)
    s={valid:true, prem:prem, concl:concl, steps:a[4]}; }
  else { s=window[kind](); s=s.__script||s; }
  let host=document.getElementById('T'); if(host) host.remove();
  host=document.createElement('div'); host.id='T'; document.body.prepend(host);
  if(!document.getElementById('fb')){const f=document.createElement('div');f.id='fb';document.body.prepend(f);}
  state.type = !mc;
  const pp=proofPlayer({setLine:'test',script:s,prompt:'x',forceType:!mc,stars:'auto'});
  pp.mount(host);
  return s.steps.map(x=>[x.kind, x.typed||'', x.world||'']);
}"""

results = []
LOG = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + info) if (info and not cond) else ''))
    if not cond: print('      typed:', LOG[-8:])
    LOG.clear()

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{const o=document.getElementById('overlay'); if(o) o.className='overlay'; state.level=0;}")

    def fresh():  # a clean page per problem, so no timer from the last one can fire
        pg.goto(BASE); pg.wait_for_function("()=>typeof proofPlayer==='function'")
        pg.evaluate("()=>{const o=document.getElementById('overlay'); if(o) o.className='overlay'; state.level=0;}")
    def mount(kind, prem, concl, mc=False, steps=None):
        fresh()
        return pg.evaluate(SETUP, [kind, prem, concl, mc, steps])
    def typ(v):
        if not pg.evaluate("()=>{const i=document.querySelector('#T #ansInput'); return !!(i&&i.offsetParent)}"):
            return 'NOINPUT ' + pg.inner_text('#fb')
        pg.fill('#T #ansInput', v); pg.press('#T #ansInput', 'Enter'); pg.wait_for_timeout(120)
        fb = pg.inner_text('#fb'); LOG.append((v, fb[:70].replace(chr(10),' '))); return fb
    def ok(fb): return not fb.startswith('NOINPUT') and ('✅' in fb or 'complete' in fb.lower() or 'Correct' in fb)
    def done(): return pg.evaluate("()=>{const i=document.querySelector('#T #ansInput'); return !(i&&i.offsetParent)}") and 'complete' in pg.inner_text('#fb').lower()
    def line(st):  # typed form of a script step
        k, t, w = st
        t = t.translate(str.maketrans({'∼':'~','•':'&','∨':'v','⊃':'>','≡':'=',' ':''}))
        if k == 'asm': return 'asm: ' + t
        if k == 'refute': return 'REFUTE'
        return (w + ': ' if w else '') + t

    def run_script(tag, kind, prem, concl):
        sc = mount(kind, prem, concl)
        good = True
        for st in sc:
            fb = typ(line(st))
            if not ok(fb): good = False; break
        check(f'{tag}: scripted route passes', good and done(), f'{sc} / {fb[:120]}')
        return sc

    # ---- G (propositional) ----
    mount('prop', ['A'], '(AvB)')
    a = ok(typ('asm: ~(AvB)')); b1 = ok(typ('~A')); c1 = ok(typ('(AvB)'))
    check('G (a) repro: asm ~(AvB), ~A, then RAA (AvB)', a and b1 and c1 and done())
    mount('prop', ['A'], '(AvB)'); typ('asm: ~(AvB)'); typ('~A'); c1 = ok(typ('AvB'))
    check('G F9: RAA conclusion typed without outer parentheses', c1 and done())
    run_script('G (b)', 'prop', ['(A>B)', '(B>C)'], '(A>C)')
    run_script('G (b) longer', 'prop', ['(A>(B&C))', '(~C v D)'], '(A>D)')
    mount('prop', ['(A>B)', '(B>C)'], '(A>C)'); typ('asm: ~(A>C)')
    check('G (c) illegal step rejected (C from nothing)', not ok(typ('C')))
    check('G (c) illegal step rejected (B from A>B alone)', not ok(typ('B')))
    check('G (d) RAA with no contradiction rejected', not ok(typ('(A>C)')))
    # off-script but legal order: derive ~C before A
    mount('prop', ['(A>B)', '(B>C)'], '(A>C)'); typ('asm: ~(A>C)')
    r1 = ok(typ('~C')); r2 = ok(typ('A')); r3 = ok(typ('~B')); r4 = ok(typ('B'))
    r5 = ok(typ('(A>C)'))
    check('G off-script legal order accepted through to RAA', r1 and r2 and r3 and r4 and r5 and done())
    # typed 'v' for or in a premise-derived line
    mount('prop', ['(AvB)', '~A'], 'B'); typ('asm: ~B'); r = ok(typ('A'))
    check('G I-rule from premises accepted', r)
    # (e) invalid needs full breakdown
    sc = mount('prop', ['(AvB)'], 'A'); typ('asm: ~A')
    early = ok(typ('REFUTE'))
    check('G (e) REFUTE before full breakdown rejected', not early, str(sc))
    mount('prop', ['(AvB)'], 'A'); typ('asm: ~A'); typ('B'); r = ok(typ('REFUTE'))
    check('G (e) REFUTE after full breakdown accepted', r and done())
    run_script('G (b) invalid', 'prop', ['((A&B)>C)', '~C'], '~A')
    # MC mode: 4 choices, picking a correct one advances
    mount('prop', ['A'], '(AvB)', mc=True)
    n = pg.evaluate("()=>document.querySelectorAll('#T .choice').length")
    pg.evaluate("()=>document.querySelector('#T .choice[data-ok=\"1\"]').click()"); pg.wait_for_timeout(60)
    check('G multiple-choice mode still works', n >= 2 and ok(pg.inner_text('#fb')))

    # ---- I (quantificational) ----
    run_script('I (b)', 'quant', ['(x)(Fx>Gx)', 'Fa'], 'Ga')
    run_script('I (b) existential', 'quant', ['(∃x)(Fx&Gx)'], '(∃x)Fx')
    mount('quant', ['Fa'], '(FavGa)'); a = ok(typ('asm: ~(FavGa)')); b1 = ok(typ('~Fa')); c1 = ok(typ('(FavGa)'))
    check('I (a) repro-style early RAA', a and b1 and c1 and done())
    mount('quant', ['(∃x)(Fx&Gx)'], '(∃x)Fx'); typ('asm: ~(∃x)Fx')
    s1 = ok(typ('(Fb&Gb)')); s2 = ok(typ('Fb')); s3 = ok(typ('(x)~Fx')); s4 = ok(typ('~Fb')); s5 = ok(typ('(∃x)Fx'))
    check('I off-script legal: drop existential with b, other order', s1 and s2 and s3 and s4 and s5 and done(), str([s1,s2,s3,s4,s5]))
    mount('quant', ['(x)(Fx>Gx)', 'Fa'], 'Ga'); typ('asm: ~Ga')
    check('I (c) illegal step rejected (Gb)', not ok(typ('Gb')))
    check('I (d) RAA with no contradiction rejected', not ok(typ('Ga')))
    sc = mount('quant', ['(∃x)Fx'], 'Fa'); typ('asm: ~Fa')
    check('I (e) REFUTE before full breakdown rejected', not ok(typ('REFUTE')), str(sc))
    run_script('I (b) invalid', 'quant', ['(∃x)Fx'], 'Fa')

    # ---- K (modal, S5 engine) ----
    run_script('K (b)', 'modal', ['☐A'], '☐(AvB)')
    run_script('K (b) diamond', 'modal', ['◊(A&B)'], '◊A')
    sc = mount('modal', ['☐A'], '☐(AvB)')
    seq = [line(s) for s in sc]
    # take scripted steps up to (and including) the first 'W ~A' line, then drop box early, then RAA
    out = []
    for s in sc:
        out.append(ok(typ(line(s))))
        if s[0] == 'derive' and s[2] and s[1].replace(' ', '') in ('~A', '∼A', '¬A'): break
    e1 = ok(typ('W: A')); e2 = ok(typ('☐(AvB)'))
    check('K (a) early RAA after off-script drop-box', all(out) and e1 and e2 and done(), f'{seq} {out} {e1} {e2}')
    mount('modal', ['☐A'], '☐(AvB)'); typ('asm: ~☐(AvB)')
    check('K (c) illegal step rejected (W B)', not ok(typ('W: B')))
    check('K (d) RAA with no contradiction rejected', not ok(typ('☐(AvB)')))
    sc = mount('modal', ['◊A'], '☐A'); typ(line(sc[0]))
    check('K (e) REFUTE before full breakdown rejected', not ok(typ('REFUTE')), str(sc))
    run_script('K (b) invalid', 'modal', ['◊A'], '☐A')

    # ---- hand-written scripts (Sets M, O, quantified K): standard route + early RAA ----
    hand = [['asm', '~(AvB)', ''], ['derive', '~A', ''], ['derive', '~B', ''], ['raa', '(AvB)', '']]
    steps = [{'kind': 'asm', 'typed': '~(AvB)', 'disp': '∼(A ∨ B)', 'just': 'asm'},
             {'kind': 'derive', 'typed': '~A', 'disp': '∼A', 'just': '{2}'},
             {'kind': 'derive', 'typed': '~B', 'disp': '∼B', 'just': '{2}'},
             {'kind': 'raa', 'typed': '(AvB)', 'disp': '(A ∨ B)', 'just': '{1, 3}'}]
    mount('hand', ['A'], '(A ∨ B)', False, steps)
    a = ok(typ('asm: ~(AvB)')); b1 = ok(typ('~A')); c1 = ok(typ('(AvB)'))
    check('M/O-style hand script: early RAA accepted', a and b1 and c1 and done())
    # real hand-written problems: walk the scripted route of several random problems per set
    for gen in ['makeM', 'makeO', 'kQuant']:
        good = 0; total = 8; bad = ''
        for trial in range(total):
            fresh()
            sc = pg.evaluate("""(g)=>{ state.type=true;
               const orig=proofPlayer; let cap=null; window.proofPlayer=(c)=>{ cap=c.script; return orig(c); };
               let host=document.createElement('div'); host.id='T'; document.body.prepend(host);
               if(!document.getElementById('fb')){const f=document.createElement('div');f.id='fb';document.body.prepend(f);}
               const pp=window[g](); pp.mount(host); window.proofPlayer=orig;
               return cap.steps.map(x=>[x.kind,x.typed||'',x.world||'']); }""", gen)
            allok = True
            for st in sc:
                if not ok(typ(line(st))): allok = False; break
            if allok and done(): good += 1
            elif not bad: bad = str(sc) + ' ' + str(LOG[-3:])
        check(f'{gen}: scripted route passes ({good}/{total} random problems)', good == total, bad)
    check('no page errors', not errs, '; '.join(errs[:3]))
    b.close()

passed = sum(1 for _, r in results if r); print(f'\n{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
