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
    # Old Aug-Oct link: logicola-for-instructors.html redirects to LogiSkor, keeping query and hash.
    pg.goto(B+'logicola-for-instructors.html'+Q+'#h'); pg.wait_for_url('**/logiskor.html*',timeout=15000)
    check('logicola-for-instructors.html redirects to logiskor.html', 'logiskor.html' in pg.url and 'LogiSkor' in pg.inner_text('.brand'), pg.url)
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
