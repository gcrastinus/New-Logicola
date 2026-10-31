"""LogiSkor rename: instructor.html redirects; links page links all load."""
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
    pg.goto(B+'instructor.html'+Q); pg.wait_for_url('**/logiskor.html*',timeout=15000)
    check('instructor.html redirects to logiskor.html', 'logiskor.html' in pg.url, pg.url)
    check('LogiSkor heading and title', 'LogiSkor' in pg.inner_text('.brand') and 'LogiSkor' in pg.title(), pg.title())
    html=urllib.request.urlopen(B+'instructor.html'+Q).read().decode()
    check('redirect has meta refresh, JS redirect and visible link', 'http-equiv="refresh"' in html and "location.replace('logiskor.html'" in html and '<a href="logiskor.html">' in html)
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
