"""Underlining in typed answers, as in the original LogiCola: "_" right after a
letter underlines it ("A_" = underlined A; "Au_" = A with the small u underlined).
Wrong underlining gets "Incorrect underlining: edit your answer and try again."
with no points lost. Sets L and N can be typed; L, M, N, O tell students how.
Run a local server, then: python3 tests/test_underlining.py [base]
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
    pg = br.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function("()=>typeof ulCompare==='function' && typeof startSet==='function'")

    u = pg.evaluate("""()=>[ulText('O<u>A</u>'), ulText('(Au '+SYM.horseshoe+' B<u>u</u>)'), ulText('<u>u</u>:A<u>u</u>'),
        ulCompare('OA_','O<u>A</u>'), ulCompare('OA','O<u>A</u>'), ulCompare('Au_','A<u>u</u>'), ulCompare('A_u','A<u>u</u>'),
        ulCompare('Au','Au'), ulCompare('Au_','Au'), ulCompare('OB_','O<u>A</u>')]""")
    check('underlined letters read as "A_"', u[0] == 'OA_' and u[2] == 'u_:Au_', u)
    check('right underlining is accepted; wrong underlining is caught; wrong formula is wrong',
          u[3:] == ['ok', 'ul', 'ok', 'ul', 'ok', 'ul', False], u[3:])

    # Sets L and N, typed
    for sid, key, modes in [('L', 'lMode', ['imp', 'deon']), ('N', 'nMode', ['will', 'belief', 'rat'])]:
        for m in modes:
            got_ul = 0; got_ok = 0; tried = 0
            for t in range(30):
                r = pg.evaluate("""([sid,key,m])=>{ state[key]=m; state.type=true; state.level=9; startSet(sid);
                    const p=session.current; if(!/<u>/.test(p.answer)) return {skip:true};
                    const instr=document.body.innerText.includes('Put _ after a letter to underline it');
                    const i=document.getElementById('ansInput'); if(!i) return {fail:'no input'};
                    const before=session.points;
                    i.value=ulText(p.answer).replace(/_/g,''); answerType();
                    const fb=(document.getElementById('fb')||{}).innerText||'';
                    const ul=fb.includes('Incorrect underlining: edit your answer and try again.') && session.points===before && !i.disabled;
                    i.value=ulText(p.answer); answerType();
                    return {ul, ok: session.points>before, instr}; }""", [sid, key, m])
                if r.get('skip'): continue
                tried += 1
                if r.get('ul'): got_ul += 1
                if r.get('ok') and r.get('instr'): got_ok += 1
                if tried >= 5: break
            check(f'Set {sid} {m} typed: missing underline gets the retry message, no points lost ({got_ul}/{tried})', tried >= 3 and got_ul == tried)
            check(f'Set {sid} {m} typed: "_" underlining is accepted, and the tip is shown ({got_ok}/{tried})', tried >= 3 and got_ok == tried)

    # live preview
    pv = pg.evaluate("""()=>{ state.lMode='imp'; state.type=true; startSet('L'); const i=document.getElementById('ansInput');
        i.value='(Au > Bu_)'; i.dispatchEvent(new Event('input',{bubbles:true}));
        const d=document.getElementById('ulPreview'); return d?d.innerHTML:''; }""")
    check('typing "_" shows a real underline as you type', '<u>u</u>' in pv and 'Bu_' not in pv, pv)

    # generated deontic / belief proofs, typed: an imperative line needs its underline
    pg.evaluate("""()=>{ const orig=proofPlayer; window.proofPlayer=function(cfg){ window.__scr=JSON.parse(JSON.stringify(cfg.script)); return orig(cfg); }; }""")
    for sid, key, m in [('M', 'mMode', 'proof'), ('O', 'oMode', 'will')]:
        good = 0; tried = 0; info = []
        for t in range(60):
            r = pg.evaluate("""([sid,key,m])=>{ state[key]=m; state.type=true; state.level=9; state.gTrain=false; startSet(sid);
                const S=window.__scr; const st=S.steps[0];
                const body=String(st.disp).replace(/^asm:\\s*/,'');
                if(!/<u>/.test(body)) return {skip:true};
                const i=document.getElementById('ansInput'); const before=session.points;
                i.value='asm: '+ulText(body).replace(/_/g,''); document.getElementById('prfGo').click();
                const fb1=(document.getElementById('fb')||{}).innerText||'';
                const ul=fb1.includes('Incorrect underlining') && session.points===before;
                i.value='asm: '+ulText(body); document.getElementById('prfGo').click();
                const fb2=(document.getElementById('fb')||{}).innerText||'';
                const ok=!fb2.includes("don't like") && !fb2.includes('Incorrect underlining') && document.body.innerText.includes('asm:');
                const instr=document.body.innerText.includes('Put _ after a letter to underline it');
                return {ul, ok, instr, fb1:fb1.slice(0,90)}; }""", [sid, key, m])
            if r.get('skip'): continue
            tried += 1
            if r['ul'] and r['ok'] and r['instr']: good += 1
            else: info.append(r)
            if tried >= 6: break
        check(f'Set {sid} {m} typed proofs: underline checked on lines, retry without penalty ({good}/{tried})', tried >= 3 and good == tried, info[:2])

    check('no page errors', not errs, errs[:3])
    br.close()

bad = [n for n, ok in results if not ok]
print(f'\n{len(results)-len(bad)}/{len(results)} passed')
sys.exit(1 if bad else 0)
