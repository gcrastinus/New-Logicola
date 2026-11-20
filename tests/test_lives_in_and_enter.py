"""Syllogistic 'lives in' place letter, and Enter-to-next after a checked answer.
Run a local server, then: python3 tests/test_lives_in_and_enter.py [base] [shots-dir]
"""
import os, sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767/index.html'
SHOTS = sys.argv[2] if len(sys.argv) > 2 else ''
CHROME = '/usr/bin/google-chrome'

results = []
def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name + (('  -- ' + info) if info and not cond else ''))

BOOT_LIVES = r"""
(place) => {
  const o=document.getElementById('overlay'); if(o) o.className='overlay';
  state.name='T'; state.place=place; state.type=true; state.harder=true; state.level=0; state.sound=false;
  session.set='A'; session.points=0; session.tries=0; session.lastAnswer=undefined;
  const g=genASing('userGen');
  session.current=makeA(g.english, g.answer, g.D, {type:true, harder:true}, g.note);
  renderProblem();
  return {english:g.english, answer:g.answer, note:g.note, place:g.english};
}
"""

BOOT_MC = r"""
() => {
  const o=document.getElementById('overlay'); if(o) o.className='overlay';
  state.name='T'; state.place='Florida'; state.type=false; state.harder=false; state.level=0; state.sound=false;
  session.set='A'; session.points=0; session.tries=0; session.lastAnswer=undefined;
  session.current=makeA('All dentists are funny.', 'all D is F',
    ['all F is D','no D is F','some D is F','some D is not F'], {type:false, harder:false});
  renderProblem();
}
"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--headless=new','--no-sandbox','--disable-gpu'])
    pg = b.new_page(viewport={'width':1000,'height':800})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))

    def fresh():
        pg.goto(BASE)
        pg.wait_for_function('()=>typeof genASing==="function" && typeof renderProblem==="function"')

    fresh()
    # formalPlace
    fp = pg.evaluate("""() => ({
      FL: formalPlace('FL'), fl: formalPlace('fl'), Fl: formalPlace('Fl.'),
      MI: formalPlace('MI'), Michigan: formalPlace('Michigan'),
      empty: formalPlace(''), LA: formalPlace('LA'), NY: formalPlace('NY')
    })""")
    check('FL expands to Florida', fp['FL']=='Florida' and fp['fl']=='Florida' and fp['Fl']=='Florida')
    check('MI expands to Michigan', fp['MI']=='Michigan')
    check('full name is left alone', fp['Michigan']=='Michigan')
    check('blank place defaults to New York', fp['empty']=='New York')
    check('LA expands to Louisiana (USPS)', fp['LA']=='Louisiana')
    check('NY expands to New York', fp['NY']=='New York')

    info = pg.evaluate(BOOT_LIVES, 'FL')
    check('FL sentence spells out Florida', info['english']=='T lives in Florida.')
    check('expected answer is t is F (place letter)', info['answer']=='t is F')
    check('note names F and says the letter comes from the place',
          'Florida' in info['note'] and 'comes from the place' in info['note'] and 'not from' in info['note'],
          info['note'])
    if SHOTS:
        pg.screenshot(path=os.path.join(SHOTS, '02-lives-in-after.png'), full_page=True)

    # wrong letter L from "lives"
    pg.fill('#ansInput', 't is L')
    pg.press('#ansInput', 'Enter')
    pg.wait_for_timeout(150)
    fb = pg.inner_text('#fb')
    check('t is L is rejected with a place-letter hint',
          'Sorry' in fb and 'place' in fb.lower() and 'F' in fb and 'lives' in fb.lower(),
          fb)
    check('first wrong does not show Next problem', 'Next problem' not in fb)
    prompt1 = pg.inner_text('.prompt')

    # correct answer on the same problem (second try)
    pg.fill('#ansInput', 't is F')
    pg.press('#ansInput', 'Enter')
    pg.wait_for_timeout(150)
    fb = pg.inner_text('#fb')
    check('t is F is accepted', 'Correct' in fb or 'Right' in fb or 'Good' in fb or 'Yes' in fb or 'Nicely' in fb)
    check('Next problem button appears after a correct typed answer', 'Next problem' in fb)
    if SHOTS:
        pg.screenshot(path=os.path.join(SHOTS, '03-enter-to-next-feedback.png'), full_page=True)

    # Enter again, still focused in / around the answer field, goes next
    before = pg.inner_text('.prompt')
    pg.keyboard.press('Enter')
    pg.wait_for_timeout(200)
    after = pg.inner_text('.prompt')
    check('Enter after a checked typed answer loads the next problem', after!=before and 'Next problem' not in pg.inner_text('main'))

    # second-wrong then Enter-to-next
    fresh()
    pg.evaluate(BOOT_LIVES, 'Florida')
    pg.fill('#ansInput', 't is L')
    pg.press('#ansInput', 'Enter')
    pg.wait_for_timeout(80)
    pg.fill('#ansInput', 'all t is F')
    pg.press('#ansInput', 'Enter')
    pg.wait_for_timeout(150)
    fb = pg.inner_text('#fb')
    check('second wrong reveals the answer and shows Next problem',
          'Next problem' in fb and ('t is F' in fb or 't is F' in pg.inner_html('#fb')))
    before = pg.inner_text('.prompt')
    # focus still in the answer field
    pg.focus('#ansInput')
    pg.keyboard.press('Enter')
    pg.wait_for_timeout(200)
    check('Enter in the answer field after second wrong goes to the next problem',
          pg.inner_text('.prompt')!=before)

    # MC: after correct, Enter goes next
    fresh()
    pg.evaluate(BOOT_MC)
    # click the correct choice (all D is F)
    pg.evaluate("""() => {
      const btns=[...document.querySelectorAll('.choice')];
      const i=btns.findIndex(b=>/all D is F/.test(b.innerText));
      if(i>=0) answerMC(i);
    }""")
    pg.wait_for_timeout(150)
    check('MC correct shows Next problem', 'Next problem' in pg.inner_text('#fb'))
    before = pg.inner_text('.prompt')
    pg.keyboard.press('Enter')
    pg.wait_for_timeout(200)
    check('Enter after a checked MC answer loads the next problem', pg.inner_text('.prompt')!=before)

    # Show answer, then Enter
    fresh()
    pg.evaluate(BOOT_LIVES, 'FL')
    prompt1 = pg.inner_text('.prompt')
    pg.click('button.hintbtn')
    pg.wait_for_timeout(150)
    check('Show answer offers Next problem', 'Next problem' in pg.inner_text('#fb'))
    pg.keyboard.press('Enter')
    pg.wait_for_timeout(200)
    check('Enter after Show answer loads the next problem', pg.inner_text('.prompt')!=prompt1)

    # Enter in a scratch textarea must not skip (use a TF/MC set with scratch)
    # Set S T/F items can have scratch. Simpler: inject scratch onto current problem.
    fresh()
    pg.evaluate(BOOT_LIVES, 'FL')
    pg.evaluate("""() => {
      const p=session.current; p.scratch=true; renderProblem();
    }""")
    pg.fill('#ansInput', 't is F')
    pg.press('#ansInput', 'Enter')
    pg.wait_for_timeout(150)
    check('setup: correct answer with scratch showing Next', 'Next problem' in pg.inner_text('#fb'))
    before = pg.inner_text('.prompt')
    ta = pg.query_selector('textarea')
    check('scratch textarea is present', bool(ta))
    if ta:
        ta.focus()
        pg.keyboard.press('Enter')
        pg.wait_for_timeout(150)
        check('Enter in scratch textarea does not skip to the next problem',
              pg.inner_text('.prompt')==before and 'Next problem' in pg.inner_text('#fb'))

    check('no page errors', not errs, '; '.join(errs))
    b.close()

failed = [n for n,ok in results if not ok]
print(f'\n{len(results)-len(failed)}/{len(results)} passed')
sys.exit(1 if failed else 0)
