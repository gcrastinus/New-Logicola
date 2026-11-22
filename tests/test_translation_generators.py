"""Sets C (easier, harder), H (easier) and J (basic) now generate translation
problems without end. For 500 items per mode: the English reads back as exactly
the answer formula (Gensler's grouping rules: both/either/if open a group, a
comma marks the main break; idioms only if, unless, provided that, sufficient,
necessary, just if, neither-nor), every wrong choice differs in truth value from
the answer, and items keep changing. Then each mode runs in the app, multiple
choice and typed. Run a local server, then:
python3 tests/test_translation_generators.py [base] [N]
"""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 500
results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + str(info)) if info and not cond else ''))

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--headless=new', '--no-sandbox'])
    pg = br.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function("()=>typeof genCTrans==='function' && typeof startSet==='function'")

    for mode in ['easy', 'hard']:
        r = pg.evaluate("""([mode,N])=>{
          // independent truth-table check with the app's own parser and evaluator
          const tt=s=>{ const a=parseProp(renderC(s)); const L=[...new Set(s.match(/[A-Z]/g))]; const out=[];
            for(let m=0;m<(1<<L.length);m++){ const v={}; L.forEach((x,i)=>v[x]=!!(m>>i&1)); out.push(evalAst(a,v)); } return {L,out}; };
          const same=(s,t)=>{ const L=[...new Set((s+t).match(/[A-Z]/g))]; const a=parseProp(renderC(s)), b=parseProp(renderC(t));
            for(let m=0;m<(1<<L.length);m++){ const v={}; L.forEach((x,i)=>v[x]=!!(m>>i&1)); if(evalAst(a,v)!==evalAst(b,v)) return false; } return true; };
          let nul=0, rt=0, eq=0, four=0; const seen=new Set(), idioms={};
          for(let i=0;i<N;i++){ const q=genCTrans(mode); if(!q){nul++;continue;}
            seen.add(q.p);
            const back=trReadC(q.p,q.words); if(!back||trC(back)!==q.o[0]) rt++;
            if(q.o.slice(1).some(d=>same(d,q.o[0]))) eq++;
            if(new Set(q.o).size!==4) four++;
            (q.p.match(/only if|unless|provided that|sufficient|necessary|just if|if and only if|neither|not both|both|either/gi)||[]).forEach(w=>idioms[w.toLowerCase()]=1); }
          return {nul,rt,eq,four,distinct:seen.size,idioms:Object.keys(idioms).sort()}; }""", [mode, N])
        check(f'C {mode}: {N} items, none missing', r['nul'] == 0, r)
        check(f'C {mode}: every English sentence reads back as exactly its formula', r['rt'] == 0, r)
        check(f'C {mode}: every wrong choice really is wrong (truth table)', r['eq'] == 0, r)
        check(f'C {mode}: four different choices every time', r['four'] == 0, r)
        check(f'C {mode}: problems keep changing ({r["distinct"]} of {N})', r['distinct'] >= N * 0.8, r)
        if mode == 'hard':
            need = ['only if', 'unless', 'provided that', 'sufficient', 'necessary', 'just if', 'if and only if', 'neither', 'not both']
            check('C hard: all of Gensler\'s idioms appear', all(w in r['idioms'] for w in need), r['idioms'])

    r = pg.evaluate("""(N)=>{ let nul=0, rt=0, eq=0, few=0; const seen=new Set();
      for(let i=0;i<N;i++){ const q=genHTrans(); if(!q){nul++;continue;} seen.add(q.e);
        const back=trReadH(q.e,q.W); if(!back||trQStr(back)!==q.ans) rt++;
        if(q.dsQ.some(d=>trQEquiv(d,q.q,q.Ps))) eq++;
        if(new Set([q.ans].concat(q.ds)).size!==4) few++; }
      return {nul,rt,eq,few,distinct:seen.size}; }""", N)
    check(f'H easier: {N} items, none missing', r['nul'] == 0, r)
    check('H easier: every English sentence reads back as exactly its formula', r['rt'] == 0, r)
    check('H easier: every wrong choice differs in some model', r['eq'] == 0 and r['few'] == 0, r)
    check(f'H easier: problems keep changing ({r["distinct"]} of {N})', r['distinct'] >= N * 0.6, r)

    r = pg.evaluate("""(N)=>{ let nul=0, rt=0, eq=0, few=0; const seen=new Set();
      for(let i=0;i<N;i++){ const q=genJTrans(); if(!q){nul++;continue;} seen.add(q.e);
        const back=trReadJ(q.e); if(!back||trMStr(back)!==q.ans) rt++;
        if(q.dsF.some(d=>trMEquiv(d,q.f))) eq++;
        if(new Set([q.ans].concat(q.ds)).size!==4) few++; }
      return {nul,rt,eq,few,distinct:seen.size}; }""", N)
    check(f'J basic: {N} items, none missing', r['nul'] == 0, r)
    check('J basic: every English sentence reads back as exactly its formula', r['rt'] == 0, r)
    check('J basic: every wrong choice differs in some world (S5)', r['eq'] == 0 and r['few'] == 0, r)
    check(f'J basic: problems keep changing ({r["distinct"]} of {N})', r['distinct'] >= N * 0.6, r)

    # in the app: multiple choice has one right answer; typed accepts the answer
    for sid, key, val, extra in [('C', 'cMode', 'easy', ''), ('C', 'cMode', 'hard', ''), ('H', 'hMode', 'easy', ''), ('J', 'jMode', 'basic', '')]:
        r = pg.evaluate("""([sid,key,val])=>{ let mcOk=0, tyOk=0; const seen=new Set();
          for(let i=0;i<40;i++){ state[key]=val; state.type=false; state.level=9; startSet(sid); const p=session.current;
            seen.add(p.prompt); if(p.choices && p.choices.filter(c=>c.correct).length===1 && p.choices.length===4) mcOk++; }
          for(let i=0;i<20;i++){ state[key]=val; state.type=true; startSet(sid); const p=session.current;
            if(p.accept && p.accept(p.answer,p.answer) && !p.accept(p.answer.replace(/[A-Z]/,m=>m==='Z'?'Y':'Z'),p.answer)) tyOk++; }
          state.type=false; return {mcOk,tyOk,distinct:seen.size}; }""", [sid, key, val])
        check(f'Set {sid} {val}: 40 multiple-choice problems with exactly one right answer', r['mcOk'] == 40, r)
        check(f'Set {sid} {val}: typed mode accepts the answer and rejects a changed letter', r['tyOk'] == 20, r)
        check(f'Set {sid} {val}: the app shows varied problems ({r["distinct"]} of 40)', r['distinct'] >= 25, r)

    check('no page errors', not errs, errs[:3])
    br.close()

bad = [n for n, ok in results if not ok]
print(f'\n{len(results)-len(bad)}/{len(results)} passed')
sys.exit(1 if bad else 0)
