"""Scoring matches Gensler's original LogiCola (measured 2020-12-07)."""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8767/index.html"
results = []

def check(name, cond, info=""):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), name, "" if cond else info)

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--headless=new", "--no-sandbox"])
    pg = br.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE)
    pg.wait_for_function("()=>typeof inferScoreKind===\"function\"")

    math = pg.evaluate("""()=>{
      const L=[1,5,7,9];
      const out={};
      for(const lv of L){
        state.level=lv;
        out[lv]={
          half2L:[firstWrongCost('half2L',lv), nextWrongCost('half2L', firstWrongCost('half2L',lv)),
                  nextWrongCost('half2L', nextWrongCost('half2L', firstWrongCost('half2L',lv)))],
          fourL:firstWrongCost('fourL',lv),
          threeL:firstWrongCost('threeL',lv),
          half3L:[firstWrongCost('half3L',lv), nextWrongCost('half3L', firstWrongCost('half3L',lv))],
          quarter:[firstWrongCost('quarter2L',lv), nextWrongCost('quarter2L', firstWrongCost('quarter2L',lv)),
                   nextWrongCost('quarter2L', nextWrongCost('quarter2L', firstWrongCost('quarter2L',lv)))],
          halfL:firstWrongCost('halfL',lv)
        };
      }
      return out;
    }""")

    def row(lv):
        return math.get(lv, math.get(str(lv)))

    check("MC / most misses: 2L then half, L1", row(1)["half2L"] == [2, 1, 0], row(1)["half2L"])
    check("MC / most misses: 2L then half, L5", row(5)["half2L"] == [10, 5, 2], row(5)["half2L"])
    check("MC / most misses: 2L then half, L7", row(7)["half2L"] == [14, 7, 3], row(7)["half2L"])
    check("MC / most misses: 2L then half, L9", row(9)["half2L"] == [18, 9, 4], row(9)["half2L"])
    check("two-choice 4L at 1,5,7,9", [row(l)["fourL"] for l in (1, 5, 7, 9)] == [4, 20, 28, 36])
    check("derive 3L at 1,5,7,9", [row(l)["threeL"] for l in (1, 5, 7, 9)] == [3, 15, 21, 27])
    check("inference first then half at L9", row(9)["half3L"] == [27, 13], row(9)["half3L"])
    check("how-to-star quarter at L9 is 18,4,1", row(9)["quarter"] == [18, 4, 1], row(9)["quarter"])
    check("missing asm / early REFUTE is L/2 at L9", row(9)["halfL"] == 4)

    kinds = pg.evaluate("""()=>{
      const pickp=(p)=>{ return {kind:inferScoreKind(p), right:rightPoints(p)}; };
      return {
        aMc:pickp({setLine:'Set A — Syllogistic Translations', mode:'mc'}),
        aTy:pickp({setLine:'Set A — Syllogistic Translations', mode:'type'}),
        vi:pickp({setLine:'Set B — Symbolic Arguments', mode:'tf', noCreditAfterWrong:true}),
        der:pickp({setLine:'Set B — Deriving Conclusions (modern)', deriveSlot:'all', mode:'type'}),
        star:pickp({setLine:'Set B — How to star the letters', mode:'custom'}),
        find:pickp({setLine:'Set B — Find the conclusion', mode:'custom'}),
        f:pickp({setLine:'Set F — Inference Rules', mode:'mc'}),
        q:pickp({setLine:'Set Q — Definitions', mode:'mc'}),
        r:pickp({setLine:'Set R — Fallacies', mode:'picklist'}),
        po:pickp({setLine:'Set P — Probability (odds)', mode:'mc'}),
        pr:pickp({setLine:'Set P — Probability (rules)', mode:'mc', scoreKind:'probMC'}),
        sl:pickp({setLine:'Set S — Sets · Laws', mode:'tf'}),
        sm:pickp({setLine:'Set S — Sets · Operations', mode:'mc'}),
        de:pickp({setLine:'Set D — Truth Evaluations', mode:'tf'}),
        pf:pickp({setLine:'Set G — Copi Proofs (easier)', mode:'custom', scoreKind:'proof'})
      };
    }""")
    expect = {
        "aMc": ("mcTrans", 5), "aTy": ("typeTrans", 7), "vi": ("twoChoice", 10), "der": ("derive", 10),
        "star": ("starHow", 5), "find": ("findConcl", 7), "f": ("infer", 7), "q": ("defs", 7), "r": ("fallacies", 8),
        "po": ("probOddsMC", 5), "pr": ("probMC", 10), "sl": ("twoChoice", 10), "sm": ("mcTrans", 5),
        "de": ("twoChoice", 10), "pf": ("proof", 20),
    }
    for k, (kind, right) in expect.items():
        got = kinds[k]
        check(f"profile {k} is {kind} +{right}", got["kind"] == kind and got["right"] == right, got)

    clamp = pg.evaluate("""()=>{
      const o=document.getElementById('overlay'); if(o) o.className='overlay';
      state.level=1; session.set='A'; session.points=-7; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set A — Syllogistic Translations', mode:'mc', explain:()=>''};
      awardCorrect('');
      return session.points;
    }""")
    check("negative score plus a +5 right answer clamps to 0, not -2", clamp == 0, clamp)

    mid = pg.evaluate("""()=>{
      state.level=9; session.set='B'; session.points=5; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set B — Symbolic', mode:'tf', noCreditAfterWrong:true, choices:[], explain:()=>''};
      penalizeWrong('no','no');
      return {pts:session.points, ended:!!session.scoreEnded};
    }""")
    check("two-choice miss at L9 from 5 goes negative then clamps to 0 at problem end", mid["pts"] == 0 and mid["ended"], mid)

    mc = pg.evaluate("""()=>{
      state.level=9; session.set='A'; session.points=40; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set A — Syllogistic Translations', mode:'mc',
        choices:[{text:'A',correct:false},{text:'B',correct:false},{text:'C',correct:true},{text:'D',correct:false}],
        explain:()=>''};
      const p0=session.points;
      penalizeWrong('1','1'); const c1=p0-session.points; const ended1=!!session.scoreEnded;
      const p1=session.points;
      penalizeWrong('2','2'); const c2=p1-session.points; const ended2=!!session.scoreEnded;
      awardCorrect('');
      return {costs:[c1,c2], ended1, ended2, final:session.points, ended3:!!session.scoreEnded};
    }""")
    check("MC at L9: first miss -18, still open", mc["costs"][0] == 18 and not mc["ended1"], mc)
    check("MC at L9: second miss -9, still open", mc["costs"][1] == 9 and not mc["ended2"], mc)
    check("MC at L9: later right still +5 (40-18-9+5=18)", mc["final"] == 18 and mc["ended3"], mc)

    fal = pg.evaluate("""()=>{
      state.level=5; session.set='R'; session.points=20; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set R — Fallacies', mode:'picklist', answer:'aa', options:['aa','ac'], explain:()=>''};
      penalizeWrong('1','1');
      const after1={pts:session.points, ended:!!session.scoreEnded, tries:session.tries};
      awardCorrect('');
      return {after1, final:session.points, ended:!!session.scoreEnded};
    }""")
    check("fallacies at L5: first miss -10, still open", fal["after1"]["pts"] == 10 and not fal["after1"]["ended"], fal)
    check("fallacies: a right after a miss earns 0 (10 stays 10)", fal["final"] == 10 and fal["ended"], fal)

    fal2 = pg.evaluate("""()=>{
      state.level=5; session.set='R'; session.points=20; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set R — Fallacies', mode:'picklist', answer:'aa', options:['aa','ac'], explain:()=>''};
      penalizeWrong('1','1');
      penalizeWrong('2','2');
      return {pts:session.points, ended:!!session.scoreEnded, tries:session.tries};
    }""")
    check("fallacies: second miss costs 0 and ends the problem (20-10=10)", fal2["pts"] == 10 and fal2["ended"] and fal2["tries"] == 2, fal2)

    der = pg.evaluate("""()=>{
      state.level=9; state.bImport='modern'; session.set='B'; session.points=40;
      session.tries=0; session.lastPenalty=undefined; session.scoreEnded=false; session.derivePlan=null;
      const p=bDerive(); session.current=p;
      const kind=p.deriveSlot;
      penalizeWrong('no','no');
      return {pts:session.points, ended:!!session.scoreEnded, kind, reviewed:!!(session.derivePlan&&session.derivePlan.reviews[kind])};
    }""")
    check("derive at L9: one miss costs 27 and ends the problem", der["pts"] == 13 and der["ended"], der)
    check("derive: that miss is queued for spaced review", der["reviewed"], der)

    typo = pg.evaluate("""()=>{
      state.level=9; session.set='A'; session.points=20; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set A — Syllogistic Translations', mode:'type', answer:'all A is B', accept:window.acceptSyll, explain:()=>''};
      renderProblem();
      const inp=document.getElementById('ansInput');
      inp.value='all A is';
      answerType();
      return {pts:session.points, ended:!!session.scoreEnded, tries:session.tries, fb:document.getElementById('fb').innerText};
    }""")
    check("typed translation: a non-wff costs nothing and you try again", typo["pts"] == 20 and not typo["ended"] and typo["tries"] == 0, typo)

    off = pg.evaluate("""()=>{
      state.level=0; session.set='B'; session.points=0; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set B — Symbolic', mode:'tf', noCreditAfterWrong:true, explain:()=>''};
      awardCorrect('');
      const right=session.points;
      session.scoreEnded=false; session.points=0;
      penalizeWrong('x','x');
      return {right, afterMiss:session.points};
    }""")
    check("level 0 (scoring off): a right answer and a miss both leave the score at 0", off["right"] == 0 and off["afterMiss"] == 0, off)

    prf = pg.evaluate("""()=>{
      state.level=9; session.set='G'; session.points=10; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      session.current={setLine:'Set G — Valid Proofs (easier)', mode:'custom', scoreKind:'proof', explain:()=>'done'};
      const c1=scoringOn()?2*state.level:0;
      applyDelta(-c1);
      const mid=session.points;
      applyDelta(20);
      endProblemScore();
      return {mid, final:session.points};
    }""")
    check("proof at L9: a wrong line can take the score negative mid-problem", prf["mid"] == -8, prf)
    check("proof at L9: finish +20 then 10-18+20=12", prf["final"] == 12, prf)

    deep = pg.evaluate("""()=>{
      state.level=9; session.set='G'; session.points=0;
      applyDelta(-52); const mid=session.points;
      applyDelta(20); endProblemScore();
      return {mid, final:session.points};
    }""")
    check("proof finished at -52 plus 20 clamps to 0", deep["mid"] == -52 and deep["final"] == 0, deep)

    letters = pg.evaluate("""()=>{
      state.level=9; session.set='A'; session.points=20; session.tries=0;
      session.lastPenalty=undefined; session.scoreEnded=false;
      const p=makeA('T lives in Florida.', 't is F', ['t is L','t is t','T is F'], {type:true, harder:true},
        '"F" stands for the general term "lives in Florida"');
      session.current=p; renderProblem();
      const inp=document.getElementById('ansInput'); inp.value='t is L';
      answerType();
      return {pts:session.points, ended:!!session.scoreEnded, tries:session.tries, fb:document.getElementById('fb').innerText};
    }""")
    check("typed translation: a wrong letter costs nothing and you try again", letters["pts"]==20 and not letters["ended"] and letters["tries"]==0, letters)
    check("typed translation: the wrong-letter hint mentions the place letter", "place" in letters["fb"].lower() and "F" in letters["fb"], letters)

    check("no page errors", not errs, errs)
    br.close()

passed = sum(ok for _, ok in results)
print(f"\n{passed}/{len(results)} passed")
sys.exit(0 if all(ok for _, ok in results) else 1)
