"""Set B deriving-conclusions mix.

Checks that bDerive, over many simulated 10-problem sets (a clean 100-point
run), balances conclusion types, includes singular-term items, shuffles
letters, covers the valid moods, and — on the traditional model — still
asks for the strongest (universal) conclusion when one follows.

Run a local server, then: python3 tests/test_derive_mix.py [base]
"""
import collections, re, sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
CHROME = '/usr/bin/google-chrome'
results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + str(info)) if info and not cond else ''))

LET = {'all':'A','no':'E','some':'I','somenot':'O'}
PRE_RX=re.compile(r'\b((?:all|no|some) [A-Za-z] is(?: not)? [A-Za-z]|[a-z] is(?: not)? [A-Za-z])\b')

def parse_ans(ans):
    if ans=='none': return {'t':'none','str':'none'}
    for rx,t in ((r'^all ([A-Za-z]) is ([A-Za-z])$','all'),
                 (r'^no ([A-Za-z]) is ([A-Za-z])$','no'),
                 (r'^some ([A-Za-z]) is not ([A-Za-z])$','somenot'),
                 (r'^some ([A-Za-z]) is ([A-Za-z])$','some'),
                 (r'^([A-Za-z]) is not ([A-Za-z])$','neg'),
                 (r'^([A-Za-z]) is ([A-Za-z])$','pos')):
        m=re.match(rx, ans)
        if m:
            if t in ('neg','pos'):
                small=m.group(1).islower() or m.group(2).islower()
                return {'t':'sing' if small else '?', 'str':ans, 'a':m.group(1), 'b':m.group(2)}
            return {'t':t,'str':ans,'a':m.group(1),'b':m.group(2)}
    return {'t':'?','str':ans}

def parse_prem(prompt):
    text=re.sub(r'<[^>]+>','\n', prompt)
    out=[]
    for s in PRE_RX.findall(text):
        m=re.match(r'^(all|no|some) ([A-Za-z]) is not ([A-Za-z])$', s)
        if m: out.append({'t':'somenot','a':m.group(2),'b':m.group(3)}); continue
        m=re.match(r'^(all|no|some) ([A-Za-z]) is ([A-Za-z])$', s)
        if m: out.append({'t':m.group(1),'a':m.group(2),'b':m.group(3)}); continue
        m=re.match(r'^([A-Za-z]) is(?: not)? ([A-Za-z])$', s)
        if m: out.append({'t':'sing','a':m.group(1),'b':m.group(2)}); continue
    return out[:2]

def mood_fig(prem,c):
    if c['t'] in ('none','sing','?') or any(st['t'] not in LET for st in prem): return None
    S,P=c['a'],c['b']
    mid=[t for t in {prem[0]['a'],prem[0]['b'],prem[1]['a'],prem[1]['b']} if t not in (S,P)]
    if not mid: return None
    M=mid[0]
    maj=next((x for x in prem if P in (x['a'],x['b'])), None)
    mn=next((x for x in prem if x is not maj), None)
    if not maj or not mn: return None
    fig={(True,True):3,(True,False):1,(False,True):4,(False,False):2}[(maj['a']==M, mn['a']==M)]
    return f"{LET[maj['t']]}{LET[mn['t']]}{LET[c['t']]}-{fig}"

JS="""([nSets,setLen,model])=>{
  state.bImport=model; const rows=[];
  for(let si=0;si<nSets;si++){
    session.derivePlan=null; session.syllPlan=null;
    for(let i=0;i<setLen;i++){ const p=bDerive(); rows.push({ans:p.answer, prompt:p.prompt}); }
  }
  return rows;
}"""

with sync_playwright() as pw:
    br=pw.chromium.launch(executable_path=CHROME, args=['--headless=new','--no-sandbox','--disable-gpu'])
    pg=br.new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function('()=>typeof bDerive==="function" && typeof derivePools==="function"')

    for model, nvalid in (('modern',15),('traditional',15)):
        rows=pg.evaluate(JS, [120, 10, model])
        n=len(rows)
        fam=collections.Counter(); strs=collections.Counter(); mfs=collections.Counter()
        letters=collections.Counter(); mids=collections.Counter(); nsmall=0
        sets=[]
        for i in range(0,n,10):
            kinds=[]; smalls=0
            for r in rows[i:i+10]:
                c=parse_ans(r['ans']); prem=parse_prem(r['prompt']); fam[c['t']]+=1; kinds.append(c['t']); strs[c['str']]+=1
                small=any(st['a'].islower() or st['b'].islower() or st['t']=='sing' for st in prem)
                if small: nsmall+=1; smalls+=1
                for st in prem:
                    letters[st['a']]+=1; letters[st['b']]+=1
                if len(prem)==2:
                    mf=mood_fig(prem,c)
                    if mf:
                        mfs[mf]+=1
                        mid=[t for t in {prem[0]['a'],prem[0]['b'],prem[1]['a'],prem[1]['b']} if t not in (c.get('a'),c.get('b'))]
                        if mid: mids[mid[0]]+=1
            sets.append((kinds,smalls))
        print(f'{model}: {dict(fam)}; singular-prem {nsmall}/{n}; mood-figures {len(mfs)}; letters {sorted(letters)}')
        tot=n
        check(f'{model}: about 40% "none"', 0.35 <= fam['none']/tot <= 0.45, fam['none']/tot)
        for k in ('all','no','some','somenot'):
            check(f'{model}: {k} conclusions at least 8%', fam[k]/tot >= 0.08, fam[k]/tot)
        check(f'{model}: singular conclusions at least 5%', fam['sing']/tot >= 0.05, fam['sing']/tot)
        check(f'{model}: no single non-none conclusion string over 5%', max((c for s,c in strs.items() if s!='none'), default=0)/tot < 0.05)
        check(f'{model}: letters are not stuck on A,B,C', len(set(letters) - set('ABC')) >= 4, sorted(letters))
        check(f'{model}: middle term varies', len(mids) >= 5, dict(mids))
        check(f'{model}: all 15 modern valid mood-figures appear among "all/no/some/some-not" items', len(mfs) >= nvalid, sorted(mfs))
        check(f'{model}: every 10-problem set has an "all" and a "no" conclusion', all('all' in k and 'no' in k for k,_ in sets))
        check(f'{model}: singular premises stay at or under ~40% of a set (allow 2 slips in 120)', sum(1 for _,s in sets if s/10 > 0.40) <= 2, sum(1 for _,s in sets if s/10>0.40))
        if model=='traditional':
            check('traditional: Barbara (AAA-1) is asked, with an "all" conclusion', mfs.get('AAA-1',0) > 0, dict(mfs))
            check('traditional: Darapti/Felapton-style strengthened moods appear', any(k in mfs for k in ('AAI-3','EAO-3','EAO-4')), sorted(mfs))

    check('no page errors', not errs, errs)
    br.close()

print(f"\n{sum(ok for _,ok in results)}/{len(results)} passed")
sys.exit(0 if all(ok for _,ok in results) else 1)
