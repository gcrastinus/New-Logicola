"""R2: completions are recorded per activity/difficulty, exported as signed v4,
and the instructor report shows them (plus older-format v3 files)."""
import json, os, sys
from playwright.sync_api import sync_playwright
BASE='http://localhost:8766/'
SHOTS='/workspace/logicola-work-shots'
res=[]
def check(name,cond):
    res.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(accept_downloads=True)
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE+'index.html'); pg.wait_for_timeout(600)
    # simulate finishing several activities exactly as completeSet does
    pg.evaluate("""()=>{
      state.name='Test, Student';
      const fin=(set,setup,lvl)=>{ Object.assign(state,setup); session.set=set; state.level=lvl; completeSet(); closeModal(); };
      fin('G',{gMode:'valid',gLevel:'harder'},5);
      fin('G',{gMode:'valid',gLevel:'harder'},7);
      fin('G',{gMode:'copi',gLevel:'easier'},3);
      fin('K',{kMode:'galactic',modalSystem:'S4'},4);
      fin('B',{bMode:'venn',bImport:'traditional'},2);
      fin('C',{cMode:'hard',type:true},6);
      fin('A',{harder:true,type:false},1);
    }""")
    st=pg.evaluate("JSON.parse(localStorage.getItem('logicola.v1'))")
    g=st['done']['G']['valid']['harder']
    check('G valid/harder recorded best 7, twice, typed', g['lv']==7 and g['n']==2 and g['ans']=='typed')
    check('K galactic recorded under system S4', st['done']['K']['galactic']['S4']['sys']=='S4')
    check('B records traditional reading', st['done']['B']['venn']['-']['sys']=='traditional')
    check('C typed answers noted', st['done']['C']['hard']['-']['ans']=='typed')
    check('A harder MC', st['done']['A']['-']['harder']['ans']=='MC')
    check('completed best kept', st['completed']['G']==7)
    pg.evaluate("scoresView()")
    with pg.expect_download() as dl: pg.evaluate("exportScores()")
    path='/tmp/v4-test.lgc'; dl.value.save_as(path)
    txt=open(path).read()
    check('export is LGC2 signed', txt.startswith('LGC2.'))
    # round-trip import into a clean app
    pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(500)
    pg.evaluate("scoresView()")
    pg.set_input_files('#impFile',path); pg.wait_for_timeout(800)
    st2=pg.evaluate("state.done")
    check('import restores done', st2 and st2['G']['valid']['harder']['lv']==7)
    check('app: no page errors', not errs)
    # report
    for w,h in [(1280,900),(390,844)]:
        rp=ctx.new_page(); rp.set_viewport_size({'width':w,'height':h}); rerr=[]
        rp.on('pageerror',lambda e:rerr.append(str(e)))
        rp.goto(BASE+'instructor.html')
        rp.set_input_files('#fileIn',[path,'/workspace/logicola-audit/sample.lgc']); rp.wait_for_timeout(800)
        body=rp.inner_text('#results')
        check(f'{w}: two students listed', 'Test, Student' in body and body.count('verified')>=1)
        check(f'{w}: older format flagged', 'Older format' in body)
        rp.screenshot(path=f'{SHOTS}/report-overview-{w}.png',full_page=True)
        rp.click('#exp0'); rp.wait_for_timeout(200)
        d=rp.inner_text('#det0')
        check(f'{w}: v4 detail shows level and date', '✔ level 7' in d and 'not done' in d and 'system: S4' in d and 'finished 2 times' in d)
        check(f'{w}: aria-expanded toggles', rp.get_attribute('#exp0','aria-expanded')=='true')
        rp.screenshot(path=f'{SHOTS}/report-v4-expanded-{w}.png',full_page=False)
        rp.click('#exp1'); rp.wait_for_timeout(200)
        d1=rp.inner_text('#det1')
        check(f'{w}: v3 detail says not recorded', 'activity and difficulty not recorded' in d1)
        rp.locator('#det1').screenshot(path=f'{SHOTS}/report-v3-expanded-{w}.png')
        small=rp.evaluate("""[...document.querySelectorAll('#app *')].filter(e=>e.offsetParent&&e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(getComputedStyle(e).fontSize)<16).length""")
        check(f'{w}: no visible text under 16px', small==0)
        if w==390:
            wide=rp.evaluate("document.documentElement.scrollWidth")
            check('390: no sideways scrolling', wide<=392)
        with rp.expect_download() as d2: rp.click('text=Download CSV summary')
        cp=f'/tmp/report-{w}.csv'; d2.value.save_as(cp)
        import csv
        hdr,r1,r2=list(csv.reader(open(cp)))[:3]
        cols=hdr
        check(f'{w}: CSV has per-activity columns', 'setG_valid_harder' in cols and 'setK_galactic_S4' in cols)
        check(f'{w}: CSV value', r1[cols.index('setG_valid_harder')]=='7' and r2[cols.index('setG_older_format_best_level')]=='7')
        check(f'{w}: no report errors', not rerr)
    b.close()
print(f"{sum(r for _,r in res)}/{len(res)} passed")
sys.exit(0 if all(r for _,r in res) else 1)
