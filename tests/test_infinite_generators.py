"""Every proof activity now makes new problems without end.
Generated items are checked before a student ever sees them:
  * proofs (Sets I, K quantified, M deontic, O belief/willing/rationality):
    every line cites earlier lines, every RAA cites a real contradiction in
    one world and derives the denial of its assumption, valid items end in
    RAA on the conclusion, invalid ones end in a checked REFUTE;
  * galactic travel (Set K): verdicts agree with the S5 proof engine and are
    monotone (valid in T => valid in S4, B, S5; S4 or B => S5);
  * Copi (Set G): each sample-proof line is re-checked by the Copi rule checker.
Then each activity is started in the app, and some proofs are played to the end.
Run a local server, then: python3 tests/test_infinite_generators.py [base] [N]
"""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 500
results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + str(info)) if info and not cond else ''))

AUDIT = """([name, N])=>{
  const T=t=>canonWff(String(t).replace(/<[^>]*>/g,''),'proof');
  const neg=(a,b)=>a==='~'+b||b==='~'+a||a==='~('+b+')'||b==='~('+a+')';
  const G={
    deontic:i=>genDeonticArg(i%2===0), believe:i=>genBeliefArg('believe',i%2===0),
    will:i=>genBeliefArg('will',i%2===0), rat:i=>genBeliefArg('rat',i%2===0),
    qmodal:i=>genQModalArg(i%2===0),
    'I-easier':i=>makeIScript('easier',i%2===0).script, 'I-harder':i=>makeIScript('harder',i%2===0).script,
    'I-rel':i=>makeIScript('rel',i%2===0).script, 'I-ident':i=>makeIScript('ident',i%2===0).script,
  };
  const bad=[], seen=new Set(); let nul=0, val=0, inv=0;
  for(let r=0;r<N;r++){
    const s=G[name](r); if(!s){ nul++; continue; }
    seen.add(s.prem.map(T).join('|')+'=>'+T(s.concl));
    const np=s.prem.length, lines=[]; s.prem.forEach(p=>lines.push({w:'',c:T(p)}));
    s.steps.forEach((st,k)=>{
      const ln=np+k+1;
      if(st.kind==='refute'){ if(k!==s.steps.length-1) bad.push('refute not last'); return; }
      const nums=(st.just.match(/\\d+/g)||[]).map(Number);
      if(nums.some(n=>n<1||n>=ln)) bad.push('line '+ln+' cites '+st.just);
      if(st.kind==='raa'){
        const m=st.just.match(/(\\d+) contradicts (\\d+)/);
        if(!m) bad.push('raa no contra');
        else { const a=lines[m[1]-1], c=lines[m[2]-1];
          if(!a||!c||(a.w||'').toUpperCase()!==(c.w||'').toUpperCase()||!neg(a.c,c.c)) bad.push('raa bad contra '+JSON.stringify([a,c])); }
      }
      lines.push({w:st.world||'',c:T(st.typed)});
    });
    const last=s.steps[s.steps.length-1];
    if((last.kind==='raa')!==s.valid) bad.push('valid flag');
    if(s.valid && T(last.typed)!==T(s.concl)) bad.push('final RAA is not the conclusion');
    if(s.steps[0].kind!=='asm' || !neg(T(s.steps[0].typed),T(s.concl))) bad.push('first line is not asm: not-conclusion');
    if(s.valid) val++; else inv++;
  }
  return {bad:bad.slice(0,5), nbad:bad.length, nul, val, inv, distinct:seen.size};
}"""

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--headless=new', '--no-sandbox'])
    pg = br.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function("()=>typeof WE==='object' && typeof genDeonticArg==='function' && typeof startSet==='function'")

    for name in ['deontic', 'believe', 'will', 'rat', 'qmodal', 'I-easier', 'I-harder', 'I-rel', 'I-ident']:
        n = N if not name.startswith('I-') else max(100, N // 4)
        r = pg.evaluate(AUDIT, [name, n])
        check(f'{name}: {n} generated proofs are all well-formed', r['nbad'] == 0, r)
        check(f'{name}: generator never gives up', r['nul'] == 0, r)
        check(f'{name}: both valid and invalid arguments appear', r['val'] > n * 0.2 and r['inv'] > n * 0.2, r)
        # Set I keeps about a quarter of its items from the old hand-built shapes, so a few repeats are expected
        check(f'{name}: problems keep changing ({r["distinct"]} different of {n})', r['distinct'] >= n * (0.6 if name.startswith('I-') else 0.8), r)

    g = pg.evaluate("""(N)=>{
      const conv=f=> f.op==='var'?WE.At(f.name): f.op==='~'?WE.Ng(conv(f.a)): f.op==='#'?WE.Box(conv(f.a)): f.op==='$'?WE.Dia(conv(f.a)): WE.Bn(f.op,conv(f.a),conv(f.b));
      let mono=0, dis=0, decided=0, nul=0, nocm=0; const seen=new Set(), kinds=new Set();
      for(let i=0;i<N;i++){ const x=genGalactic(); if(!x){nul++;continue;}
        const v=new Set(x.validIn); kinds.add(x.validIn.join('')); seen.add(x.prems.map(qRender).join('|')+qRender(x.concl));
        if(v.has('T')&&!(v.has('S4')&&v.has('B')&&v.has('S5'))) mono++;
        if((v.has('S4')||v.has('B'))&&!v.has('S5')) mono++;
        ['T','S4','B','S5'].forEach(s=>{ if(!v.has(s)&&!x.inv[s]) nocm++; });
        const r=WE.prove(x.prems.map(conv),conv(x.concl));
        if(r){ decided++; if(r.valid!==v.has('S5')) dis++; } }
      return {mono,dis,decided,nul,nocm,distinct:seen.size,kinds:kinds.size}; }""", N)
    check('galactic: verdicts are monotone across T, S4, B, S5', g['mono'] == 0, g)
    check('galactic: S5 verdicts agree with the proof engine', g['dis'] == 0 and g['decided'] > N * 0.9, g)
    check('galactic: every "invalid" verdict has a countermodel galaxy', g['nocm'] == 0, g)
    check('galactic: arguments that tell the systems apart appear', g['kinds'] >= 4, g)
    check(f'galactic: problems keep changing ({g["distinct"]} of {N})', g['distinct'] >= N * 0.8 and g['nul'] == 0, g)

    for lv in ['easier', 'harder']:
        c = pg.evaluate("""([lv,N])=>{ let bad=[], nul=0; const seen=new Set();
          for(let i=0;i<N;i++){ const x=genCopiRandom(lv); if(!x){nul++;continue;}
            seen.add(x.prem.map(astStr).join('|')+astStr(x.concl));
            const lines=x.prem.slice();
            for(const st of x.sample){ const f=parseProp(st.w.replace(/<[^>]*>/g,''));
              if(!f){ bad.push('unparsable '+st.w); break; }
              if(st.from.some(n=>n<1||n>lines.length)){ bad.push('cites forward'); break; }
              if(!copiStepOk(f,st.rule,st.from.map(n=>lines[n-1]))){ bad.push('rule fails '+st.rule+' '+st.w); break; }
              lines.push(f); }
            if(!astEq(lines[lines.length-1],x.concl)) bad.push('does not end in conclusion');
            const used=new Set(x.sample.flatMap(s=>s.from)); if(x.prem.some((p,i)=>!used.has(i+1))) bad.push('unused premise'); }
          return {bad:bad.slice(0,4), nbad:bad.length, nul, distinct:seen.size}; }""", [lv, N])
        check(f'Copi {lv}: every sample proof re-checks line by line', c['nbad'] == 0 and c['nul'] == 0, c)
        check(f'Copi {lv}: problems keep changing ({c["distinct"]} of {N})', c['distinct'] >= N * 0.8, c)

    # every activity starts and produces a stream of problems in the app
    acts = [('M', 'mMode', 'proof'), ('O', 'oMode', 'believe'), ('O', 'oMode', 'will'), ('O', 'oMode', 'rat'), ('O', 'oMode', 'mix'),
            ('K', 'kMode', 'quant'), ('K', 'kMode', 'galactic'), ('G', 'gMode', 'copi'),
            ('I', 'iKind', 'valid'), ('I', 'iKind', 'invalid'), ('I', 'iKind', 'both')]
    for sid, key, val in acts:
        r = pg.evaluate("""([sid,key,val])=>{ state[key]=val; state.level=9; startSet(sid); const seen=new Set(); let n=0;
          for(let i=0;i<40;i++){ nextProblem(); const c=session.current; if(c){ n++; seen.add(document.getElementById('app')? (c.prompt||'')+JSON.stringify((c.script||{}).prem||'')+document.body.innerText.slice(0,0):''); } }
          return {n, distinct:seen.size}; }""", [sid, key, val])
        check(f'Set {sid} {val}: 40 problems in a row', r['n'] == 40, r)

    # play generated proofs to the end with Get answer (and REFUTE when invalid)
    def play(sid, key, val, typed, trials):
        done = 0
        for t in range(trials):
            pg.evaluate("""([sid,key,val,ty])=>{ state[key]=val; state.type=ty; state.level=9; state.autoJust=true; state.gTrain=false; startSet(sid); }""", [sid, key, val, typed])
            for k in range(60):
                fb = pg.evaluate("()=>((document.getElementById('fb')||{}).innerText||'')")
                if 'Problem complete' in fb: break
                if 'REFUTE to finish' in fb or 'type it yourself' in fb:
                    pg.evaluate("""()=>{const i=document.getElementById('ansInput');
                      if(i){ i.value='REFUTE'; document.getElementById('prfGo').click(); return; }
                      [...document.querySelectorAll('#prfCtl .choice')].find(b=>b.innerText.trim().endsWith('REFUTE')).click(); }""")
                    continue
                if pg.evaluate("()=>{const b=document.getElementById('prfGet'); if(!b) return false; b.click(); return true;}") is False: break
            if 'Problem complete' in pg.evaluate("()=>((document.getElementById('fb')||{}).innerText||'')"): done += 1
        return done
    for sid, key, val in [('M', 'mMode', 'proof'), ('K', 'kMode', 'quant'), ('O', 'oMode', 'mix')]:
        for typed in [False, True]:
            d = play(sid, key, val, typed, 8)
            check(f'Set {sid} {val}{" (typed)" if typed else ""}: proofs run to the end', d == 8, d)

    # type every line by hand, world prefixes included, on freshly generated items only
    pg.evaluate("""()=>{ const orig=proofPlayer; window.proofPlayer=function(cfg){
        window.__scr=JSON.parse(JSON.stringify(cfg.script)); return orig(cfg); }; }""")
    for sid, key, val in [('M', 'mMode', 'proof'), ('K', 'kMode', 'quant'), ('O', 'oMode', 'believe'), ('O', 'oMode', 'will'), ('O', 'oMode', 'rat')]:
        good = 0; gen = 0; info = []
        for trial in range(25):
            r = pg.evaluate("""([sid,key,val])=>{ state[key]=val; state.type=true; state.level=9; startSet(sid);
              const S=window.__scr; if(!S.eng||S.eng.name!=='world') return {skip:true};
              for(const st of S.steps){
                const v= st.kind==='refute' ? 'REFUTE' : st.kind==='asm' ? 'asm: '+st.typed : (st.world ? st.world+': '+st.typed : st.typed);
                const i=document.getElementById('ansInput'); if(!i) return {fail:'no input'};
                i.value=v; document.getElementById('prfGo').click();
                const fb=(document.getElementById('fb')||{}).innerText||'';
                if(fb.includes('Problem complete')) return {ok:true};
                if(fb.includes("don't like")) return {fail:fb.slice(0,200), v};
              }
              return {fail:'not finished'}; }""", [sid, key, val])
            if r.get('skip'): continue
            gen += 1
            if r.get('ok'): good += 1
            else: info.append(r)
        check(f'Set {sid} {val}: every line of generated proofs can be typed ({good}/{gen})', gen >= 10 and good == gen, info[:2])

    check('no page errors', not errs, errs[:3])
    br.close()

bad = [n for n, ok in results if not ok]
print(f'\n{len(results)-len(bad)}/{len(results)} passed')
sys.exit(1 if bad else 0)
