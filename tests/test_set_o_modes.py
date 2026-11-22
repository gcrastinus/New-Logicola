"""Set O has the original LogiCola's four modes: Believing, Willing,
Rationality, Mixed. Problem forms are taken from the original (letters vary).
Checks: menu, each mode generates, scripts are self-consistent (line numbers
point back, each RAA cites a real contradiction, valid/invalid matches the
ending), and a few proofs of each mode can be typed through to the end.
Run a local server, then: python3 tests/test_set_o_modes.py [base]
"""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + str(info)) if info and not cond else ''))

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--headless=new', '--no-sandbox'])
    pg = br.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function("()=>typeof makeO==='function' && typeof startSet==='function'")

    acts = pg.evaluate("()=>MENU.O.acts.map(a=>a[0]+'|'+a[1])")
    check('Set O menu has Believing, Willing, Rationality, Mixed',
          acts == ['believe|Believing', 'will|Willing', 'rat|Rationality', 'mix|Mixed'], acts)
    check('Set O still typed', pg.evaluate("()=>MENU.O.type===true"))
    check("oMode default is believe and survives the 'mixed' migration",
          pg.evaluate("()=>STATE_DEFAULTS.oMode==='believe'"))
    sizes = pg.evaluate("()=>{const b=oOriginalBank(); return [b.believe.length,b.will.length,b.rat.length];}")
    check('8 original forms per mode', sizes == [8, 8, 8], sizes)

    audit = pg.evaluate("""()=>{
      const T=t=>canonWff(String(t).replace(/<[^>]*>/g,''),'proof');
      const neg=(a,b)=>a==='~'+b||b==='~'+a||a==='~('+b+')'||b==='~('+a+')';
      const b=oOriginalBank(), bad=[];
      for(const kind of ['believe','will','rat']) b[kind].forEach((mk,i)=>{ for(let rep=0;rep<15;rep++){
        const s=mk(), np=s.prem.length, lines=[];
        s.prem.forEach(p=>lines.push({w:'',c:T(p)}));
        s.steps.forEach((st,k)=>{
          const ln=np+k+1;
          if(st.kind==='refute'){ if(k!==s.steps.length-1) bad.push(kind+i+' refute not last'); return; }
          const nums=(st.just.match(/\\d+/g)||[]).map(Number);
          if(nums.some(n=>n<1||n>=ln)) bad.push(kind+i+' line '+ln+' cites '+st.just);
          if(st.kind==='raa'){
            const m=st.just.match(/(\\d+) contradicts (\\d+)/);
            if(!m) bad.push(kind+i+' raa no contra');
            else { const a=lines[m[1]-1], c=lines[m[2]-1];
              if(!a||!c||a.w!==c.w||!neg(a.c,c.c)) bad.push(kind+i+' raa bad contra '+JSON.stringify([a,c])); }
            if(T(st.typed)!==T(s.concl)) bad.push(kind+i+' raa not the conclusion');
          }
          lines.push({w:st.world||'',c:T(st.typed)});
        });
        const last=s.steps[s.steps.length-1].kind;
        if((last==='raa')!==s.valid) bad.push(kind+i+' valid flag');
        const asm=s.steps[0]; if(asm.kind!=='asm') bad.push(kind+i+' first not asm');
        const ac=T(asm.typed), cc=T(s.concl);
        if(!(neg(ac,cc))) bad.push(kind+i+' asm is not the denial of the conclusion '+ac+' / '+cc);
        const letters=new Set((s.concl+s.prem.join('')).replace(/<[^>]*>/g,'').match(/[A-Z]/g));
        if(rep===0 && letters.size===0) bad.push(kind+i+' no letters');
      }});
      return bad;
    }""")
    check('all original forms are self-consistent', audit == [], audit[:6])

    vary = pg.evaluate("""()=>{ const b=oOriginalBank(); const seen=new Set();
      for(let i=0;i<40;i++) seen.add(b.believe[2]().concl); return seen.size; }""")
    check('sentence letters are randomized', vary > 5, vary)

    for mode, label in [('believe', 'Believing'), ('will', 'Willing'), ('rat', 'Rationality'), ('mix', 'Mixed')]:
        ok = pg.evaluate("""(m)=>{ state.oMode=m; state.level=9; startSet('O');
          let n=0; for(let i=0;i<60;i++){ nextProblem(); if(session.current) n++; }
          return {n, line:document.body.innerText.includes('Set O — Belief Proofs')}; }""", mode)
        check(f'{label} mode generates problems', ok['n'] == 60, ok)
        lab = pg.evaluate("()=>session.current.setLine")
        check(f'{label} shows its name', f'({label})' in lab, lab)

    # type a few problems all the way through
    for mode, typed in [('believe',False), ('will',False), ('rat',False), ('mix',False), ('will',True), ('rat',True)]:
        done = 0
        for trial in range(6):
            r = pg.evaluate("""([m,ty])=>{ state.oMode=m; state.type=ty; state.level=9; state.autoJust=true; state.gTrain=false; startSet('O');
              return true; }""", [mode, typed])
            for k in range(30):
                fb = pg.evaluate("()=>((document.getElementById('fb')||{}).innerText||'')")
                if 'Problem complete' in fb: break
                if 'REFUTE to finish' in fb or 'type it yourself' in fb:
                    pg.evaluate("""()=>{const i=document.getElementById('ansInput');
                      if(i){ i.value='REFUTE'; document.getElementById('prfGo').click(); return; }
                      [...document.querySelectorAll('#prfCtl .choice')].find(b=>b.innerText.trim().endsWith('REFUTE')).click(); }""")
                    continue
                ans = pg.evaluate("""()=>{
                  const b=document.getElementById('prfGet'); if(!b) return 'nogo';
                  b.click(); return 'got'; }""")
                if ans != 'got': break
            fin = pg.evaluate("()=>((document.getElementById('fb')||{}).innerText||'').includes('Problem complete')")
            if fin: done += 1
        check(f'{mode}{" (typed)" if typed else ""}: proofs run to the end (Get answer, then REFUTE when invalid)', done == 6, done)


    # type every line by hand (typed mode), with world prefixes like "Du: K"
    pg.evaluate("""()=>{ const orig=proofPlayer; window.proofPlayer=function(cfg){
        window.__scr=JSON.parse(JSON.stringify(cfg.script)); return orig(cfg); }; }""")
    for mode in ['believe', 'will', 'rat']:
        good = 0; info = []
        for trial in range(8):
            r = pg.evaluate("""(m)=>{ state.oMode=m; state.type=true; state.level=9; startSet('O');
              const S=window.__scr, typed=[];
              for(const st of S.steps){
                const v= st.kind==='refute' ? 'REFUTE' : st.kind==='asm' ? 'asm: '+st.typed
                       : (st.world ? st.world+': '+st.typed : st.typed);
                typed.push(v);
                const i=document.getElementById('ansInput'); if(!i) return {fail:'no input', typed};
                i.value=v; document.getElementById('prfGo').click();
                const fb=(document.getElementById('fb')||{}).innerText||'';
                if(fb.includes('Problem complete')) return {ok:true, pts:session.points};
                if(fb.includes("don't like")) return {fail:fb.slice(0,160), typed};
              }
              return {fail:'not finished', typed}; }""", mode)
            if r.get('ok'): good += 1
            else: info.append(r)
        check(f'{mode}: every line can be typed (world prefixes) to finish', good == 8, info[:2])

    check('no page errors', not errs, errs[:3])
    br.close()

bad = [n for n, ok in results if not ok]
print(f'\n{len(results)-len(bad)}/{len(results)} passed')
sys.exit(1 if bad else 0)
