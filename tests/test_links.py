"""LogiSkor rename: instructor.html (old link) and logiskor.html both load; links page links all load."""
import sys, urllib.request
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8766/'
Q=sys.argv[2] if len(sys.argv)>2 else ''
res=[]
def check(n,c,info=''):
    res.append(c); print(('PASS ' if c else 'FAIL ')+n+('' if c else '  -- '+str(info)))
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_page()
    # Old link: instructor.html is again a real page (the same LogiSkor report), not a redirect.
    pg.goto(B+'instructor.html'+Q+'#old')
    pg.wait_for_selector('.brand',timeout=15000)
    check('instructor.html is the LogiSkor page itself (no redirect)', pg.url.split('#')[0].endswith('instructor.html'+Q), pg.url)
    check('LogiSkor heading and title', 'LogiSkor' in pg.inner_text('.brand') and 'LogiSkor' in pg.title(), pg.title())
    a=urllib.request.urlopen(B+'instructor.html'+Q).read(); b2=urllib.request.urlopen(B+'logiskor.html'+Q).read()
    check('instructor.html is identical to logiskor.html (keep them in step)', a==b2)
    pg.goto(B+'logiskor.html'+Q)
    check('logiskor.html loads', 'LogiSkor' in pg.inner_text('.brand'))
    # Old Aug-Oct link: logicola-for-instructors.html is a real page too (same LogiSkor report).
    pg.goto(B+'logicola-for-instructors.html'+Q+'#h'); pg.wait_for_selector('.brand',timeout=15000)
    check('logicola-for-instructors.html is the LogiSkor page itself (no redirect)', pg.url.split('#')[0].endswith('logicola-for-instructors.html'+Q) and 'LogiSkor' in pg.inner_text('.brand'), pg.url)
    c=urllib.request.urlopen(B+'logicola-for-instructors.html'+Q).read()
    check('logicola-for-instructors.html is identical to logiskor.html', c==b2)
    # No white bands: html (canvas) and body are dark at top, bottom and in a tall/short page.
    for pageName in ('logiskor.html','instructor.html','logicola-for-instructors.html'):
        pg.set_viewport_size({'width':1280,'height':1400}); pg.goto(B+pageName+Q); pg.wait_for_selector('.brand')
        bg=pg.evaluate("[getComputedStyle(document.documentElement).backgroundColor,getComputedStyle(document.documentElement).backgroundImage!=='none',document.body.scrollHeight>=window.innerHeight]")
        check(pageName+' page background is dark and fills the window', bg[0]!='rgba(0, 0, 0, 0)' and bg[0]!='rgb(255, 255, 255)' and bg[1] and bg[2], bg)
        pg.screenshot(path='/tmp/logiskor-'+pageName.split('.')[0]+'.png')
    from PIL import Image
    for pageName in ('logiskor','instructor','logicola-for-instructors'):
        im=Image.open('/tmp/logiskor-'+pageName+'.png').convert('RGB'); w,h=im.size
        pts=[(2,2),(w-3,2),(2,h-3),(w-3,h-3),(w//2,h-3),(w//2,2)]
        bad=[im.getpixel(q) for q in pts if sum(im.getpixel(q))>300]
        check(pageName+' screenshot has no light band at edges', not bad, bad)
    pg.set_viewport_size({'width':1280,'height':720})
    pg.goto(B+'instructors-links.html'+Q)
    hrefs=pg.eval_on_selector_all('main a','els=>els.map(e=>e.getAttribute("href"))')
    check('links page has the 4 links', sorted(hrefs)==sorted(['index.html','instructors.html','logiskor.html','quizmaker.html']), hrefs)
    small=pg.evaluate("[...document.querySelectorAll('h1,p,a,a span')].filter(e=>parseFloat(getComputedStyle(e).fontSize)<16).length")
    check('links page text >= 16px', small==0, small)
    for h in hrefs:
        u=urljoin(B+'instructors-links.html', h)+Q
        try: code=urllib.request.urlopen(u).status
        except Exception as e: code=str(e)
        check(f'{h} returns 200', code==200, code)
    br.close()
print(f'\n{sum(res)}/{len(res)} passed')
