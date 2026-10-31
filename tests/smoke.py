"""Smoke: every set menu (and one problem from each) opens without errors;
instructor edition unlocks; Quiz Maker does not trip the single-instance lock."""
import sys
from playwright.sync_api import sync_playwright
B=(sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8766/'); res=[]
def check(n,c): res.append(bool(c)); print('PASS' if c else 'FAIL', n)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context()
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m: m.type=='error' and errs.append(m.text))
    pg.goto(B+'index.html'); pg.wait_for_timeout(700)
    ids=pg.evaluate("Object.keys(SETS)")
    for i in ids:
        n=len(errs)
        pg.evaluate(f"openSetMenu('{i}')"); pg.wait_for_timeout(150)
        check(f'set {i} menu opens', len(errs)==n and pg.locator('body').inner_text().count('Set '+i)>0)
    check('student: lock not shown', not pg.is_visible('#nlcLockOverlay'))
    check('student: designer credit visible', pg.is_visible('.designer-credit'))
    check('student title unchanged', pg.title()=='LogiCola (web edition)')
    check('no console errors (student)', not errs) or print(errs[:5])
    ins=ctx.new_page(); ie=[]
    ins.on('pageerror',lambda e:ie.append(str(e)))
    ins.goto(B+'instructors.html'); ins.wait_for_timeout(1500)
    fr=ins.frame_locator('iframe'); f=ins.frames[1]
    check('instructors: lock not shown in frame', not f.is_visible('#nlcLockOverlay'))
    check('instructors: brand says For Instructors', 'For Instructors' in f.inner_text('.brand'))
    check('instructors: tools unlocked', f.evaluate("INSTRUCTOR===true"))
    f.evaluate("openSetMenu('G')"); f.wait_for_timeout(200)
    t=f.inner_text('body'); print('   G menu text sample:', [l for l in t.split('\n') if 'uilder' in l or 'level 9' in l][:4])
    f.evaluate("fileMenu()"); f.wait_for_timeout(200)
    check('instructors: all four tools unlocked in File menu', f.locator('button.setbtn.tool').count()>=4 and f.locator('button.setbtn.tool:has-text("🔒")').count()==0)
    pg.evaluate("fileMenu()"); pg.wait_for_timeout(200)
    check('student (no level 9): tools still locked', pg.locator('button.setbtn.tool:has-text("🔒")').count()>=4)
    check('instructors: no errors', not ie) or print(ie[:5])
    pg.close(); ins.close()
    q=ctx.new_page(); qe=[]
    q.on('pageerror',lambda e:qe.append(str(e)))
    q.goto(B+'quizmaker.html'); q.wait_for_timeout(4000)
    s=ctx.new_page(); s.goto(B+'index.html'); s.wait_for_timeout(2500)
    check('Quiz Maker open: student tab not locked', not s.is_visible('#nlcLockOverlay'))
    check('Quiz Maker: no errors', not qe) or print(qe[:5])
    s2=ctx.new_page(); s2.goto(B+'index.html'); s2.wait_for_timeout(2500)
    check('second student tab IS locked (lock still works)', s2.is_visible('#nlcLockOverlay'))
    for w,h in [(1280,900),(390,844)]:
        sp=ctx.new_page(); sp.set_viewport_size({'width':w,'height':h}); sp.goto(B+'instructors.html'); sp.wait_for_timeout(1500)
        sp.screenshot(path=f'/workspace/logicola-work-shots/instructors-wrapper-{w}.png')
        sp.close()
    b.close()
print(f'{sum(res)}/{len(res)} passed'); sys.exit(0 if all(res) else 1)
