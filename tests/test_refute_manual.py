"""R1 (Nov 2026): LogiCola never enters REFUTE for the student.
Once a refutation is possible the problem waits: wrong answers (however many)
and "Get answer" don't fill in REFUTE; the student must type/choose it.
Early REFUTE gets the normal wrong-answer feedback. Completion still counts.
Run:  python3 -m http.server 8766  (in the repo)  then  python3 tests/test_refute_manual.py [base] [shots-dir]"""
import sys, os
from playwright.sync_api import sync_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8766/index.html'
SHOTS = sys.argv[2] if len(sys.argv) > 2 else ''

MOUNT_GEN = r"""(a)=>{ const [gen,args,mc]=a; state.type=!mc;
  const orig=proofPlayer; let cap=null;
  window.proofPlayer=(c)=>{ cap=c.script; if(mc) c=Object.assign({},c,{forceType:false}); return orig(c); };
  let host=document.getElementById('T'); if(host) host.remove();
  host=document.createElement('div'); host.id='T'; document.body.prepend(host);
  if(!document.getElementById('fb')){const f=document.createElement('div');f.id='fb';document.body.prepend(f);}
  let pp; try{ pp=window[gen](...args); } finally { window.proofPlayer=orig; }
  if(!cap) return null;
  pp.mount(host);
  return {valid:!!cap.valid, steps:cap.steps.map(x=>[x.kind,x.typed||'',x.world||''])}; }"""

results = []; LOG = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + info) if (info and not cond) else ''))
    if not cond: print('      log:', LOG[-8:])
    LOG.clear()

def line(st):
    k, t, w = st
    t = t.translate(str.maketrans({'∼':'~','•':'&','∨':'v','⊃':'>','≡':'=',' ':''}))
    if k == 'asm': return 'asm: ' + t
    if k == 'refute': return 'REFUTE'
    return (w + ': ' if w else '') + t

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1100,'height':900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    def fresh():
        pg.goto(BASE); pg.wait_for_function("()=>typeof proofPlayer==='function'")
        pg.evaluate("()=>{const o=document.getElementById('overlay'); if(o) o.className='overlay'; state.level=0; session.points=0;}")
    def has_input(): return pg.evaluate("()=>{const i=document.querySelector('#T #ansInput'); return !!(i&&i.offsetParent)}")
    def fb(): return pg.inner_text('#fb')
    def typ(v):
        if not has_input(): return 'NOINPUT ' + fb()
        pg.fill('#T #ansInput', v); pg.press('#T #ansInput', 'Enter'); pg.wait_for_timeout(100)
        f = fb(); LOG.append((v, f[:80].replace('\n', ' '))); return f
    def ok(f): return not f.startswith('NOINPUT') and ('✅' in f or 'complete' in f.lower())
    def complete(): return 'complete' in fb().lower()
    def refute_shown(): return pg.evaluate("()=>!!document.querySelector('#T .refutebox')")

    def mount_until(gen, args, mc=False, tries=40):
        for _ in range(tries):
            fresh(); r = pg.evaluate(MOUNT_GEN, [gen, args, mc])
            if r and not r['valid'] and r['steps'] and r['steps'][-1][0] == 'refute': return r
        return None

    def typed_case(tag, gen, args, shot=None):
        r = mount_until(gen, args)
        if not r: check(f'{tag}: got an invalid problem', False); return
        steps = r['steps']; pre = steps[:-1]
        early_ok = True
        # early REFUTE (not everything broken down yet) -> normal wrong-answer feedback
        if len(pre) >= 1:
            ok(typ(line(pre[0])))
            if len(pre) >= 2:
                f = typ('REFUTE'); early_ok = (not ok(f)) and 'Sorry' in f and not complete() and has_input()
            for st in pre[1:]:
                if not ok(typ(line(st))): early_ok = False; break
        check(f'{tag}: early REFUTE rejected normally, scripted lines accepted', early_ok and not complete())
        waiting = has_input() and not complete() and not refute_shown()
        check(f'{tag}: all lines in, REFUTE waits for the student (not auto-entered)', waiting)
        if shot and SHOTS: pg.screenshot(path=os.path.join(SHOTS, shot + '-1-waiting.png'), full_page=True)
        # three wrong answers in a row: never "added for you"
        for w in ['Z', 'asm: Z', '~Z']: typ(w)
        check(f'{tag}: 3 wrong answers at the REFUTE point do not enter REFUTE',
              has_input() and not complete() and not refute_shown() and "won't enter REFUTE" in fb() and 'added for you' not in fb())
        # Get answer names it but does not enter it
        pg.click('#T #prfGet'); pg.wait_for_timeout(80)
        check(f'{tag}: Get answer names REFUTE but does not enter it',
              has_input() and not complete() and not refute_shown() and 'REFUTE' in fb())
        if shot and SHOTS: pg.screenshot(path=os.path.join(SHOTS, shot + '-2-after-wrong-and-get-answer.png'), full_page=True)
        f = typ('refute')
        check(f'{tag}: student types REFUTE -> refutation shown, problem complete (INVALID)',
              complete() and 'INVALID' in f and refute_shown() and not has_input())
        if shot and SHOTS: pg.screenshot(path=os.path.join(SHOTS, shot + '-3-after-student-refute.png'), full_page=True)

    # a fixed, readable case first (for screenshots): (A v B) ∴ A
    fresh()
    pg.evaluate("""()=>{ const prems=[parseProp('(AvB)'),parseProp('(C>~A)')], c=parseProp('A'); const s=provePropositional(prems,c);
      s.prem=prems.map(astRender); s.premAst=prems; s.concl=astRender(c); s.eng={name:'prop',prems,concl:c};
      let host=document.createElement('div'); host.id='T'; document.body.prepend(host);
      if(!document.getElementById('fb')){const f=document.createElement('div');f.id='fb';document.body.prepend(f);}
      state.type=true; proofPlayer({setLine:'Set G — Invalid Proofs (easier)',script:s,prompt:'Refute this argument.',forceType:true,stars:'auto'}).mount(host); }""")
    for v in ['asm: ~A', 'B']: typ(v)
    check('fixed (AvB),(C>~A) ∴ A: after asm ~A and B, REFUTE waits', has_input() and not complete() and not refute_shown())
    if SHOTS: pg.screenshot(path=os.path.join(SHOTS, 'fixed-1-refute-waiting.png'), full_page=True)
    typ('C'); typ('~C')
    check('fixed: two wrong answers -> still waiting (this used to auto-enter REFUTE)', has_input() and not complete() and not refute_shown())
    if SHOTS: pg.screenshot(path=os.path.join(SHOTS, 'fixed-2-after-two-wrong.png'), full_page=True)
    f = typ('REFUTE')
    check('fixed: student enters REFUTE -> complete', complete() and refute_shown())
    if SHOTS: pg.screenshot(path=os.path.join(SHOTS, 'fixed-3-after-student-refute.png'), full_page=True)

    for i in range(3): typed_case(f'G invalid easier #{i+1}', 'gProof', ['easier', 'invalid'], shot='G-easier' if i == 0 else None)
    for i in range(3): typed_case(f'G invalid harder #{i+1}', 'gProof', ['harder', 'invalid'], shot='G-harder' if i == 0 else None)
    for i in range(2): typed_case(f'G valid&invalid (invalid one) #{i+1}', 'gProof', ['mixed', 'both'])
    for i in range(3): typed_case(f'I quantificational invalid #{i+1}', 'makeI', ['easier', 'invalid'], shot='I-quant' if i == 0 else None)
    typed_case('I quantificational harder invalid', 'makeI', ['harder', 'invalid'])
    for i in range(2): typed_case(f'K modal invalid #{i+1}', 'kProof', ['easier', 'invalid'], shot='K-modal' if i == 0 else None)

    # multiple-choice mode: wrong choices and Get answer never enter REFUTE
    r = mount_until('makeI', ['easier', 'invalid'], mc=True)
    good = bool(r)
    if r:
        for st in r['steps'][:-1]:
            pg.evaluate("()=>{const b=[...document.querySelectorAll('#T .choice')].find(b=>b.dataset.ok==='1'); if(b) b.click();}"); pg.wait_for_timeout(80)
        wrongs = pg.evaluate("()=>[...document.querySelectorAll('#T .choice')].filter(b=>b.dataset.ok!=='1').length")
        for k in range(min(3, wrongs)):
            pg.evaluate(f"()=>{{const b=[...document.querySelectorAll('#T .choice')].filter(b=>b.dataset.ok!=='1')[{k}]; if(b) b.click();}}"); pg.wait_for_timeout(80)
        pg.click('#T #prfGet'); pg.wait_for_timeout(80)
        waiting = not complete() and not refute_shown() and pg.evaluate("()=>document.querySelectorAll('#T .choice').length>0")
        pg.evaluate("()=>{const b=[...document.querySelectorAll('#T .choice')].find(b=>/REFUTE/.test(b.innerText)); if(b) b.click();}"); pg.wait_for_timeout(80)
        good = wrongs >= 1 and waiting and complete() and refute_shown()
    check('multiple-choice: wrong choices + Get answer leave REFUTE to the student; choosing it completes', good)

    # real app flow + score: finishing invalid proofs by typing REFUTE still completes the set and records it
    fresh()
    rec = pg.evaluate("""async ()=>{
      state.gMode='invalid'; state.gLevel='easier'; state.level=1; session.set='G'; session.points=90;
      const orig=proofPlayer; let cap=null; window.proofPlayer=(c)=>{ cap=c.script; return orig(c); };
      nextProblem(); window.proofPlayer=orig;
      const steps=cap.steps; const inp=()=>document.querySelector('#ansInput');
      const tx=t=>t.replace(/[∼¬]/g,'~').replace(/•/g,'&').replace(/∨/g,'v').replace(/⊃/g,'>').replace(/≡/g,'=').replace(/ /g,'');
      for(const st of steps){ const v= st.kind==='refute'?'REFUTE' : st.kind==='asm'?'asm: '+tx(st.typed): tx(st.typed);
        if(!inp()) return {err:'no input', at:v};
        inp().value=v; inp().dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'})); await new Promise(r=>setTimeout(r,60)); }
      const d=JSON.parse(localStorage.getItem('logicola.v1')||'{}');
      return {pts:session.points, modal:document.body.innerText.includes('Exercise Complete'), done:d.done&&d.done.G&&d.done.G.invalid};
    }""")
    check('score: manual REFUTE in Set G invalid completes the set and records it for LogiSkor',
          rec.get('modal') and rec.get('done') and rec['done'].get('easier', {}).get('lv') == 1, str(rec))
    check('no page errors', not errs, '; '.join(errs[:3]))
    b.close()

passed = sum(1 for _, r in results if r); print(f'\n{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
