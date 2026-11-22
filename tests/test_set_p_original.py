"""Set P matches the original LogiCola's problem kinds.

Percent, Complex, Gamble: typed answers (whole number, one off accepted,
"unknown" where the problem leaves independence open). Odds: in your favor /
even / against, then type "x to y". Decide: type each option's value, then
the better option is named. Induction and Mill: name the kind of reasoning,
then correct or incorrect form, with flawed examples and the flaw named.
Scoring uses the shared hooks (values from the original):
  typed percent / dollars +10, miss 2L, one try
  odds step 1 +5, miss 2L halving; odds step 2 +5, miss 2L, one try
  decide each value +5, miss L, one try
  induction/Mill step 1 +5 (none after a miss), miss 2L halving; step 2 +5, miss 2L
Run a local server, then: python3 tests/test_set_p_original.py [base]
"""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + str(info)) if info and not cond else ''))

JS_HELPERS = """
window.__t = {
  start(mode, want){                       // start Set P in a mode; regenerate until want(p)
    state.level=9; state.pMode=mode; startSet('P');
    for(let i=0;i<400 && want && !want(session.current);i++) nextProblem();
    return !!session.current;
  },
  step(i){ return document.querySelector(`.pstep[data-step="${i}"]`); },
  pick(i, correct){
    const st=session.current.steps[i];
    const j=st.choices.findIndex(c=>!!c.correct===!!correct);
    this.step(i).querySelectorAll('.choice')[j].click();
  },
  type(i, val){
    const d=this.step(i); d.querySelector('.pstep-in').value=val; d.querySelector('.pstep-go').click();
  },
  pts(){ return session.points; },
  fb(){ const f=document.getElementById('fb'); return f?f.innerText:''; },
  next(){ return !!visibleNextProblemButton(); }
};
"""

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--headless=new', '--no-sandbox'])
    pg = br.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function("()=>typeof genP==='function' && typeof startSet==='function'")
    pg.evaluate(JS_HELPERS)

    # --- menu and generation ---
    acts = pg.evaluate("()=>MENU.P.acts.map(a=>a[0])")
    for m in ['percent','odds','complex','gamble','decide','varied','induct','mill','both','cards','dice','coins','rules']:
        check(f'menu has {m}', m in acts)
    gen = pg.evaluate("""()=>{
      const out={};
      for(const m of MENU.P.acts.map(a=>a[0])){
        state.pMode=m; let bad=null;
        for(let i=0;i<400;i++){ const p=genP();
          const typed=(p.steps||[]).filter(s=>s.kind==='type');
          if(!p||!p.prompt||/undefined|NaN/.test(p.prompt+(p.steps||[]).map(s=>s.q).join(' '))||typed.some(s=>s.answer==null||/NaN|undefined/.test(s.answer))){ bad=(p&&p.prompt||'').slice(0,160); break; } }
        out[m]=bad;
      }
      return out;
    }""")
    for m, bad in gen.items():
        check(f'{m}: 400 problems generate cleanly', bad is None, bad)

    # --- percent: whole number, one off either way, format errors free ---
    stats = pg.evaluate("""()=>{
      state.pMode='percent'; const dev={cards:0,dice:0,coins:0,stat:0}; let pctOk=true;
      for(let i=0;i<400;i++){ const p=genP(); const t=plainText(p.prompt);
        if(/deck/.test(t)) dev.cards++; else if(/die|dice/.test(t)) dev.dice++; else if(/coins/.test(t)) dev.coins++; else dev.stat++;
        const st=p.steps[0], a=+st.answer;
        if(!(st.accept(String(a)) && st.accept(String(a+1)) && st.accept(String(a-1)) && !st.accept(String(a+2)) && st.accept(a+'%'))) pctOk=false; }
      return {dev,pctOk};
    }""")
    check('percent mixes cards, dice, coins and stated facts', all(v > 20 for v in stats['dev'].values()), stats['dev'])
    check('percent accepts the answer and one off either way', stats['pctOk'])
    cx = pg.evaluate("""()=>{
      state.pMode='complex'; let unk=0, num=0, okUnk=true;
      for(let i=0;i<600;i++){ const p=genP(), st=p.steps[0];
        if(st.answer==='unknown'){ unk++; if(!st.accept('unknown')||st.accept('50')) okUnk=false; } else num++; }
      return {unk,num,okUnk};
    }""")
    check('complex includes "unknown" answers (dependence not stated)', cx['unk'] > 40 and cx['num'] > 300, cx)
    check('complex accepts "unknown" only when it is the answer', cx['okUnk'])

    # --- induction / Mill content ---
    ind = pg.evaluate("""()=>{
      const out={};
      for(const m of ['induct','mill','both']){ state.pMode=m; const seen={};
        for(let i=0;i<900;i++){ const p=genP(); const s0=p.steps[0];
          const k=s0.choices.find(c=>c.correct).text;
          const form=p.steps[1]? (p.steps[1].choices[0].correct?'ok':'bad') : 'onestep';
          seen[k]=seen[k]||{ok:0,bad:0,onestep:0,n:s0.choices.length}; seen[k][form]++; }
        out[m]=seen; }
      return out;
    }""")
    check('induction mode offers the three inductive kinds', set(ind['induct'].keys()) == {'Analogy syllogism','Sample-projection syllogism','Statistical syllogism'}, ind['induct'].keys())
    check('Mill mode offers the four methods', set(ind['mill'].keys()) == {'Agreement method','Difference method','Disagreement method','Variation method'}, ind['mill'].keys())
    check('Both mode offers all seven, with seven choices', len(ind['both']) == 7 and all(v['n'] == 7 for v in ind['both'].values()))
    for m in ('induct','mill'):
        for k, v in ind[m].items():
            if k == 'Disagreement method':
                check('disagreement is one step (always a correct form, as in the original)', v['onestep'] > 0 and v['ok'] == 0 and v['bad'] == 0, v)
            else:
                check(f'{k}: both correct and deliberately flawed forms occur', v['ok'] > 10 and v['bad'] > 10, v)
    flaw = pg.evaluate("""()=>{ state.pMode='both'; let missing=0;
      for(let i=0;i<500;i++){ const p=genP(); if(p.steps[1] && p.steps[1].choices[1].correct){
        const h=p.steps[1].answerHtml(); if(!/pflaw/.test(h)) missing++; } }
      return missing; }""")
    check('every incorrect form names its flaw', flaw == 0, flaw)

    # --- flows and scoring at level 9 ---
    def run(js):
        return pg.evaluate(js)
    pg.evaluate("__t.start('odds', p=>p.steps.length===2)")
    a = pg.evaluate("()=>{ const p0=__t.pts(); __t.pick(0,true); const p1=__t.pts(); __t.type(1, session.current.steps[1].answer); return [p0,p1,__t.pts(),__t.next()]; }")
    check('odds: step 1 right +5, step 2 right +5, problem ends', a == [0, 5, 10, True], a)
    pg.evaluate("__t.start('odds', p=>p.steps.length===2)")
    a = pg.evaluate("()=>{ session.points=50; __t.pick(0,false); const p1=__t.pts(); __t.pick(0,true); const p2=__t.pts(); __t.type(1,'1 to 99'); return [p1,p2,__t.pts(),__t.next()]; }")
    check('odds: step-1 miss −18, then +5; step-2 miss −18 and ends', a == [32, 37, 19, True], a)
    pg.evaluate("__t.start('odds', p=>p.steps.length===2)")
    a = pg.evaluate("()=>{ session.points=50; __t.pick(0,true); __t.type(1,'abc'); return [__t.pts(), /No points lost/.test(__t.fb()), __t.next()]; }")
    check('odds: a badly formed answer costs nothing', a == [55, True, False], a)
    pg.evaluate("__t.start('odds', p=>p.steps.length===1)")
    a = pg.evaluate("()=>{ __t.pick(0,true); return [__t.pts(), /even/i.test(__t.fb()), __t.next()]; }")
    check('odds: even odds end after step 1', a == [5, True, True], a)

    pg.evaluate("__t.start('percent')")
    a = pg.evaluate("()=>{ session.points=50; __t.type(0, String(+session.current.steps[0].answer+1)); return [__t.pts(),__t.next()]; }")
    check('percent: one off is right, +10', a == [60, True], a)
    pg.evaluate("__t.start('percent')")
    a = pg.evaluate("()=>{ session.points=50; __t.type(0, String(+session.current.steps[0].answer+5)); return [__t.pts(),__t.next(), /probability is/.test(__t.fb())]; }")
    check('percent: a miss costs 2L (18) and ends the problem', a == [32, True, True], a)
    pg.evaluate("__t.start('gamble')")
    a = pg.evaluate("()=>{ session.points=50; __t.type(0, session.current.steps[0].answer); return [__t.pts(),__t.next()]; }")
    check('gamble: typed dollars right +10', a == [60, True], a)
    pg.evaluate("__t.start('decide')")
    a = pg.evaluate("()=>{ session.points=50; __t.type(0, session.current.steps[0].answer); const p1=__t.pts(); __t.type(1, session.current.steps[1].answer); return [p1,__t.pts(),__t.next(), /better|equal/.test(__t.fb())]; }")
    check('decide: each value +5, then the better option is named', a == [55, 60, True, True], a)
    pg.evaluate("__t.start('decide')")
    a = pg.evaluate("()=>{ session.points=50; __t.type(0, String(+session.current.steps[0].answer+50)); const p1=__t.pts(); const st1=!!__t.step(1); __t.type(1, session.current.steps[1].answer); return [p1,st1,__t.pts(),__t.next()]; }")
    check('decide: a miss on A costs L (9) and moves on to B', a == [41, True, 46, True], a)

    pg.evaluate("__t.start('mill', p=>p.steps.length===2)")
    a = pg.evaluate("()=>{ session.points=50; __t.pick(0,true); const p1=__t.pts(); __t.pick(1,true); return [p1,__t.pts(),__t.next()]; }")
    check('Mill: name it +5, judge the form +5', a == [55, 60, True], a)
    pg.evaluate("__t.start('induct', p=>p.steps.length===2)")
    a = pg.evaluate("()=>{ session.points=50; __t.pick(0,false); const p1=__t.pts(); __t.pick(0,true); const p2=__t.pts(); __t.pick(1,false); return [p1,p2,__t.pts(),__t.next(), /form of the/.test(__t.fb())]; }")
    check('induction: miss −18, right after a miss +0, form miss −18 and the form is shown', a == [32, 32, 14, True, True], a)
    pg.evaluate("__t.start('mill', p=>p.steps.length===1)")
    a = pg.evaluate("()=>{ __t.pick(0,true); return [__t.pts(), __t.next(), /Correct form/.test(__t.fb())]; }")
    check('disagreement: one step, then "(Correct form.)"', a == [5, True, True], a)
    pg.evaluate("__t.start('induct', p=>p.steps.length===2)")
    a = pg.evaluate("()=>{ session.points=0; __t.pick(0,false); __t.pick(0,true); __t.pick(1,true); return [__t.pts(), __t.next()]; }")
    check('a negative score returns to 0 when the problem ends', a == [0, True], a)

    # rules mode keeps our multiple-choice fractions
    a = pg.evaluate("()=>{ state.pMode='rules'; let mc=0, op=0; for(let i=0;i<300;i++){ const p=genP(); if(p.mode==='mc') mc++; if(/odds are/.test(p.prompt)) op++; } return [mc,op]; }")
    check('rules (our addition) stays multiple choice and includes odds → probability', a[0] == 300 and a[1] > 10, a)

    check('no page errors', not errs, errs[:3])
    br.close()

bad = [n for n, ok in results if not ok]
print(f'\n{len(results)-len(bad)}/{len(results)} passed')
sys.exit(1 if bad else 0)
