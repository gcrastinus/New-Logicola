# TASK (for Grok): Add "Sets and Metatheory" section + Set S — Sets to LogiCola

You are modifying **`logicola.html`** (a single-file vanilla-JS web app, ~8000 lines) in the New Logicola folder. `index.html` is a byte-for-byte copy of it. There is also `instructor.html` (small; needs one tiny edit).

**Do not reword any quoted content in this ticket.** All question text, explanations, and distractor diagnoses below were authored for philosophical accuracy. If you believe something is wrong, add a code comment `// FLAG:` and keep the text as written.

## 1. Architecture crib sheet (verified against the file)

- `const SETS = {...}` (~line 5496): registry `id → {name, chapter, gen, hasHarder}`. IDs A–R are taken; **S and T are free**.
- `const SET_GROUPS = [...]` (~line 5762): the Exercise Sets menu groups, `[title, chapterLabel, [ids]]`.
- `function fileMenu()` (~line 7224): renders `SET_GROUPS`, then a hardcoded "Explore · Non-Classical Logic" block (`deviantBtn`).
- `const MENU = {...}` (~line 7272): per-set activity menus. Entry shape: `{key:'sMode', type:true, acts:[[value, label, description], ...]}`. `type:true` shows the "Multiple choice / Type the answer" toggle (`state.type`).
- `const STATE_DEFAULTS = {...}` (~line 5527): add new mode keys HERE (not in the `let state = load() || {...}` literal — a loop fills missing keys from defaults).
- `const SET_TITLES`, `const ABOUT` (~line 7817), `const INFO` (~line 7875), `const HELP_EX` (~line 7975): help-system registries. `helpMenu()` auto-lists any set with an `INFO` entry.
- **Generator contract** — `SETS[id].gen(opts)` is called with `opts = {harder, type}` and returns:
  ```js
  { setLine:'Set S — Sets · Operations',      // shown above the problem
    prompt:'html',                            // the question
    instr:'html',                             // instructions box under the answer area
    mode:'mc'|'tf'|'type',
    choices:[{text,correct,why}],             // for mc/tf (tf: exactly True/False)
    answer:'string', accept:(input,answer)=>bool,   // for type
    noKeyboard:true,                          // suppress the logic-symbol keypad
    scratch:true,                             // optional scratch textarea
    diagnose:(chosenOrTyped)=>string|null,    // optional targeted feedback
    explain:()=>'html shown on correct answer' }
  ```
- Helpers available globally: `pick(arr)`, `rand(n)`, `shuffle(arr)`, `sampleDistinct(arr,k)`, `uniqStrings(arr)`, `mc(correct, distractors)` (builds a 4-option shuffled choice list; distractors may be `'text'` or `{text, why}`; it dedups against the correct answer), `wff(s)` (styling span), `cap(s)`.
- Scoring, logging, level handling are automatic once the contract is met. Nothing to do.

## 2. Wiring (do this exactly)

**2a.** In `SETS`, add:
```js
S:{name:'Sets', chapter:'Supplement · elementary set theory, to Cantor', gen:genS, hasHarder:false},
```

**2b.** In `SET_GROUPS`, add as the **last** entry — but only if a `'Sets and Metatheory'` group doesn't already exist (a parallel task adds Set T; whichever runs second just inserts its ID into the existing group, S before T):
```js
['Sets and Metatheory', 'Supplement', ['S','T']],
```

**2c.** In `fileMenu()`, two changes. First, make `btn` skip unregistered IDs (so the group renders even before Set T lands): inside the `const groups=SET_GROUPS.map(...)` call, change `ids.map(btn)` to `ids.filter(id=>SETS[id]).map(btn)`. Second, the user wants this section at the **very bottom**, below the Explore block. Replace the single `groups` build with:
```js
const gHtml=([title,ch,ids])=>
  `<h3 style="margin:18px 0 2px">${title} <span class="muted" style="font-weight:400;font-size:13px">· ${ch}</span></h3>
   <div class="grid">${ids.filter(id=>SETS[id]).map(btn).join('')}${ids.includes('G')?toolBtn:''}${ids.includes('I')?qtoolBtn:''}${ids.includes('K')?ktoolBtn:''}</div>`;
const groups   = SET_GROUPS.filter(g=>g[0]!=='Sets and Metatheory').map(gHtml).join('');
const smGroups = SET_GROUPS.filter(g=>g[0]==='Sets and Metatheory').map(gHtml).join('');
```
and in the `openModal(...)` template change `${groups}\n    ${deviantBtn}` to `${groups}\n    ${deviantBtn}\n    ${smGroups}`. (If the parallel task already did 2b/2c, skip.)

**2d.** In `STATE_DEFAULTS`, add: `sMode:'basics',`

**2e.** In `MENU`, add:
```js
S:{key:'sMode', type:true,
   acts:[['basics','Membership & notation','∈ vs ⊆, ∅ vs {∅}, roster & set-builder, extensionality'],
         ['ops','Operations','Compute unions, intersections, differences, complements'],
         ['power','Subsets & power sets','⊆, ⊂, P(A), and how big P(A) is'],
         ['pairs','Pairs & products','Ordered pairs, A × B, counting with |A ∪ B|'],
         ['laws','Laws of sets','True or false: De Morgan, distribution, subset equivalences'],
         ['inf','Infinity','Bijections, countability, Cantor’s diagonal, Russell’s paradox']]},
```

**2f.** In `SET_TITLES` add `S:'Sets'`. In `ABOUT` add:
```js
S:'Learn the basics of sets — membership, subsets, operations, power sets, ordered pairs, and the sizes of infinite sets. Not in Gensler, but standard background for every branch of logic.',
```
In `INFO` add:
```js
S:`<b>∈</b> membership ("is one of") vs <b>⊆</b> subset ("every member of … is a member of …") — never confuse them: 1 ∈ {1,2} but {1} ⊆ {1,2}. <b>∅</b> is the empty set; ∅ ⊆ A for every A, and {∅} ≠ ∅. A set is fixed by its members alone (<b>extensionality</b>): order and repetition don't matter. Operations: A ∪ B (in either), A ∩ B (in both), A − B (in A but not B), A′ (in the universe U but not A). <b>P(A)</b> = the set of all subsets of A; |P(A)| = 2<sup>|A|</sup>. Ordered pairs (a,b) care about order; A × B = all pairs with first member from A, second from B. When typing a set, use braces and commas — {1, 3} — and ∅ or {} for the empty set; member order doesn't matter.`,
```
In `HELP_EX` add:
```js
S:()=>`U = {1,2,3,4,5,6}, A = {1,2,3}, B = {2,3,5}.<br>
A ∪ B = {1,2,3,5} · A ∩ B = {2,3} · A − B = {1} · A′ = {4,5,6}.<br>
P({1,2}) = {∅, {1}, {2}, {1,2}} — 2<sup>2</sup> = 4 subsets.<br>
{1,2} × {a} = {(1,a), (2,a)} — 2·1 = 2 pairs.`,
```

**2g.** In `instructor.html`, `SET_TITLES` (~line 167): add `S:'Sets', T:'Formal Languages & Metatheory'` (add both; harmless if T's code isn't in yet).

**2h.** When everything works: `cp logicola.html index.html`.

## 3. Shared Set-S code (paste verbatim, near the other gen* functions)

```js
/* ================= SET S — SETS ================= */
const SS={in:'∈',ni:'∉',sub:'⊆',psub:'⊂',cup:'∪',cap:'∩',diff:'−',comp:'′',empty:'∅',times:'×'};
/* Parse & canonicalize a set/pair/atom literal typed by the student.
   Accepts any member order, spaces, ∅ / Ø / {}, nested sets, pairs (a,b) or ⟨a,b⟩.
   Returns a canonical string, or null if malformed. */
function splitTop(s){
  const parts=[]; let d=0,cur='';
  for(const ch of s){
    if('{(⟨'.includes(ch)) d++;
    else if('})⟩'.includes(ch)) d--;
    if(d<0) return null;
    if(ch===','&&d===0){ parts.push(cur); cur=''; } else cur+=ch;
  }
  parts.push(cur);
  return d===0?parts.map(x=>x.trim()):null;
}
function canonSetElem(e){
  e=String(e).trim();
  if(e==='∅'||e==='Ø'||e==='{}'||/^\{\s*\}$/.test(e)) return '{}';
  if(e.startsWith('{')&&e.endsWith('}')){
    const inner=e.slice(1,-1).trim(); if(!inner) return '{}';
    const parts=splitTop(inner); if(!parts||parts.some(p=>!p)) return null;
    const els=parts.map(canonSetElem); if(els.some(x=>x===null)) return null;
    return '{'+uniqStrings(els).sort().join(',')+'}';
  }
  if((e.startsWith('(')&&e.endsWith(')'))||(e.startsWith('⟨')&&e.endsWith('⟩'))){
    const parts=splitTop(e.slice(1,-1)); if(!parts||parts.length!==2||parts.some(p=>!p)) return null;
    const els=parts.map(canonSetElem); if(els.some(x=>x===null)) return null;
    return '('+els.join(',')+')';          // pairs keep their order
  }
  return /^[A-Za-z0-9]+$/.test(e)?e:null;
}
function acceptSet(input,answer){ const a=canonSetElem(input); return a!==null&&a===canonSetElem(answer); }
function acceptNum(input,answer){ return String(input).trim()===String(answer).trim(); }
function fmtSet(a){ return a.length?'{'+a.join(', ')+'}':SS.empty; }
function fmtSetNest(a){ return '{'+a.join(', ')+'}'; }   // for sets whose members are sets
/* finite-set operations (arrays of atom strings) */
function sUnion(A,B){ return uniqStrings([...A,...B]).sort(); }
function sInter(A,B){ return A.filter(x=>B.includes(x)).sort(); }
function sMinus(A,B){ return A.filter(x=>!B.includes(x)).sort(); }
function sComp(U,A){ return U.filter(x=>!A.includes(x)); }
function sDelta(A,B){ return sUnion(sMinus(A,B),sMinus(B,A)); }
function sEq(A,B){ return fmtSet(A)===fmtSet(B); }
function sRandUAB(){
  const base=pick([['1','2','3','4','5','6','7'],['a','b','c','d','e','f','g']]);
  const U=base.slice(0,5+rand(3));
  const sub=()=>U.filter(()=>Math.random()<0.5);
  let A=sub(),B=sub();
  if(A.length<2)A=sampleDistinct(U,2).sort(); if(B.length<2)B=sampleDistinct(U,2).sort();
  return {U,A:A.sort(),B:B.sort()};
}
function powerList(A){       // all subsets, as formatted strings, ∅ first
  let out=[[]];
  for(const x of A) out=out.concat(out.map(s=>[...s,x]));
  return out.sort((p,q)=>p.length-q.length).map(s=>s.length?'{'+s.join(',')+'}':SS.empty);
}
function genS(opts){
  const m=state.sMode||'basics';
  return m==='ops'?genS_ops(opts):m==='power'?genS_power(opts):m==='pairs'?genS_pairs(opts)
       :m==='laws'?genS_laws(opts):m==='inf'?genS_inf(opts):genS_basics(opts);
}
```

## 4. Activity `ops` (paste verbatim)

```js
function genS_ops(opts){
  const {U,A,B}=sRandUAB();
  const T=[
    {q:`A ${SS.cup} B`,        val:sUnion(A,B),  name:'the union'},
    {q:`A ${SS.cap} B`,        val:sInter(A,B),  name:'the intersection'},
    {q:`A ${SS.diff} B`,       val:sMinus(A,B),  name:'A minus B'},
    {q:`B ${SS.diff} A`,       val:sMinus(B,A),  name:'B minus A'},
    {q:`A${SS.comp}`,          val:sComp(U,A),   name:'the complement of A'},
    {q:`(A ${SS.cup} B)${SS.comp}`, val:sComp(U,sUnion(A,B)), name:'the complement of the union'},
    {q:`(A ${SS.cap} B)${SS.comp}`, val:sComp(U,sInter(A,B)), name:'the complement of the intersection'},
  ];
  const t=pick(T);
  const answer=fmtSet(t.val);
  const others=T.filter(o=>o!==t&&fmtSet(o.val)!==answer)
                .map(o=>({text:fmtSet(o.val),why:`That is ${o.q} (${o.name}) — the question asks for ${t.q}.`}));
  const diagnose=(inp)=>{
    if(opts.type&&canonSetElem(inp)===null)
      return 'That isn’t a well-formed set literal — use braces and commas, e.g. {1, 3}; write the empty set as ∅ or {}.';
    for(const o of T) if(o!==t&&acceptSet(inp,fmtSet(o.val)))
      return `You computed ${o.q} (${o.name}) — the question asks for ${t.q}.`;
    return null;
  };
  return { setLine:'Set S — Sets · Operations',
    prompt:`U = ${wff(fmtSet(U))} &nbsp; A = ${wff(fmtSet(A))} &nbsp; B = ${wff(fmtSet(B))}<br>Compute ${wff(t.q)}.`,
    instr:`${SS.cup} union (in either) · ${SS.cap} intersection (in both) · ${SS.diff} difference (in the first but not the second) · ${SS.comp} complement (in U but not in the set). Order inside braces never matters; write ${SS.empty} or {} for the empty set.`,
    mode:opts.type?'type':'mc', noKeyboard:true, scratch:true, diagnose,
    choices:mc(answer, shuffle(others)),
    answer, accept:acceptSet,
    explain:()=>`${wff(t.q+' = '+answer)}.` };
}
```

## 5. Activity `power` (paste verbatim)

```js
function genS_power(opts){
  const kind=pick(['list','list','card','member','subq','subq']);
  if(kind==='list'){
    const {A}=sRandUAB(); const a=A.slice(0,2+rand(2));            // 2–3 members
    const P=powerList(a); const answer=fmtSetNest(P);
    const missEmpty=fmtSetNest(P.filter(x=>x!==SS.empty));
    const missFull =fmtSetNest(P.filter(x=>x!=='{'+a.join(',')+'}'));
    const elemsOnly=fmtSetNest(a.map(x=>'{'+x+'}'));
    return { setLine:'Set S — Sets · Power sets',
      prompt:`A = ${wff(fmtSet(a))}. What is P(A), the power set of A?`,
      instr:`P(A) is the set of ALL subsets of A — including ${SS.empty} and A itself. A set of n members has 2<sup>n</sup> subsets. When typing, nest braces: {${SS.empty}, {1}, …}.`,
      mode:opts.type?'type':'mc', noKeyboard:true, scratch:true,
      choices:mc(answer,[
        {text:missEmpty, why:`${SS.empty} is a subset of every set, so it always belongs to P(A).`},
        {text:missFull,  why:`Every set is a subset of itself, so A itself always belongs to P(A).`},
        {text:elemsOnly, why:`P(A) contains ALL subsets — not just the one-member ones. Don't forget ${SS.empty}, the larger subsets, and A itself.`}]),
      answer, accept:acceptSet,
      explain:()=>`P(${fmtSet(a)}) = ${wff(answer)} — 2<sup>${a.length}</sup> = ${P.length} subsets.` };
  }
  if(kind==='card'){
    const n=3+rand(3);   // 3–5: keeps 2ⁿ, n², and 2n all distinct
    return { setLine:'Set S — Sets · Power sets',
      prompt:`If |A| = ${n}, how many members does P(A) have?`,
      instr:`Each member of A is either in or out of a given subset — two choices each, so 2<sup>|A|</sup> subsets in all.`,
      mode:opts.type?'type':'mc', noKeyboard:true,
      choices:mc(String(2**n),[
        {text:String(n*n), why:'That’s n² — but each member contributes a factor of 2 (in or out), giving 2ⁿ.'},
        {text:String(2*n), why:'That’s 2n — but the choices multiply rather than add: 2ⁿ.'},
        {text:String(2**n-1), why:'Almost — but don’t forget the empty set is a subset too.'}]),
      answer:String(2**n), accept:acceptNum,
      explain:()=>`|P(A)| = 2<sup>${n}</sup> = ${2**n}.` };
  }
  if(kind==='member'){
    const b=['1','2','3'].slice(0,2+rand(2));
    const inn=Math.random()<0.5;
    const cand= inn ? fmtSet(b.filter(()=>Math.random()<0.6)) : fmtSet([...b.slice(0,1),'9']);
    const isIn = inn;
    return { setLine:'Set S — Sets · Power sets',
      prompt:`B = ${wff(fmtSet(b))}. &nbsp; Is ${wff(cand)} ${SS.in} P(B)?`,
      instr:`X ${SS.in} P(B) if and only if X ${SS.sub} B. So the question is just: is every member of ${cand} a member of B?`,
      mode:'mc', noKeyboard:true,
      choices:[{text:`Yes — ${cand} ${SS.sub} B, and the members of P(B) are exactly the subsets of B`,correct:isIn},
               {text:`No — ${cand} is not a subset of B, and P(B) contains exactly the subsets of B`,correct:!isIn}],
      explain:()=>isIn?`Yes: every member of ${cand} is in B, so ${cand} ${SS.sub} B, so ${cand} ${SS.in} P(B).`
                      :`No: ${cand} has a member not in B, so it isn't a subset of B, so it isn't in P(B).` };
  }
  // subq: subset judgments
  const {A,B}=sRandUAB();
  const isSub=A.every(x=>B.includes(x));
  return { setLine:'Set S — Sets · Power sets',
    prompt:`A = ${wff(fmtSet(A))} &nbsp; B = ${wff(fmtSet(B))}<br>Is A ${SS.sub} B?`,
    instr:`A ${SS.sub} B means: every member of A is a member of B. Check A's members one by one. (Note: this is about ${SS.sub}, not ${SS.in}.)`,
    mode:'mc', noKeyboard:true,
    choices:[{text:'Yes',correct:isSub},{text:'No',correct:!isSub}],
    explain:()=>isSub?`Yes — each of ${fmtSet(A)}'s members appears in B.`
      :`No — ${fmtSet(A.filter(x=>!B.includes(x)))} ${A.filter(x=>!B.includes(x)).length===1?'is':'are'} in A but not in B.` };
}
```

## 6. Activity `pairs` (paste verbatim)

```js
function genS_pairs(opts){
  const kind=pick(['prod','prod','count','incexc','pairfact']);
  if(kind==='prod'){
    const a=sampleDistinct(['1','2','3'],1+rand(2)).sort(), b=sampleDistinct(['x','y'],1+rand(2)).sort();
    const prod=[]; for(const p of a) for(const q of b) prod.push(`(${p},${q})`);
    const answer='{'+prod.join(', ')+'}';
    const flipped='{'+a.flatMap(p=>b.map(q=>`(${q},${p})`)).join(', ')+'}';
    const asSets='{'+a.flatMap(p=>b.map(q=>`{${p},${q}}`)).join(', ')+'}';
    return { setLine:'Set S — Sets · Pairs & products',
      prompt:`A = ${wff(fmtSet(a))} &nbsp; B = ${wff(fmtSet(b))}. Compute A ${SS.times} B.`,
      instr:`A ${SS.times} B is the set of all ORDERED pairs (a,b) with a from A and b from B — first coordinate from the first set. |A ${SS.times} B| = |A|·|B|.`,
      mode:opts.type?'type':'mc', noKeyboard:true, scratch:true,
      choices:mc(answer,[
        {text:flipped, why:`Those pairs run the wrong way — in A ${SS.times} B the FIRST coordinate comes from A.`},
        {text:asSets,  why:`Those are two-member sets, not ordered pairs: {1,x} = {x,1}, but (1,x) ≠ (x,1). The product is built from ordered pairs.`}]),
      answer, accept:acceptSet,
      explain:()=>`A ${SS.times} B = ${wff(answer)} — ${a.length}·${b.length} = ${prod.length} pairs.` };
  }
  if(kind==='count'){
    const m=2+rand(3), n=2+rand(3);
    return { setLine:'Set S — Sets · Pairs & products',
      prompt:`If |A| = ${m} and |B| = ${n}, what is |A ${SS.times} B|?`,
      instr:`Each of the |A| choices of first coordinate combines with each of the |B| choices of second coordinate.`,
      mode:opts.type?'type':'mc', noKeyboard:true,
      choices:mc(String(m*n),[
        {text:String(m+n), why:'That adds where you should multiply — every first coordinate pairs with every second coordinate.'},
        {text:String(2**(m+n)), why:'That’s the size of a power set, not of a product.'},
        String(m*n+n)]),
      answer:String(m*n), accept:acceptNum,
      explain:()=>`|A ${SS.times} B| = ${m}·${n} = ${m*n}.` };
  }
  if(kind==='incexc'){
    const i=1+rand(3), onlyA=1+rand(4), onlyB=1+rand(4);
    const a=onlyA+i, b=onlyB+i, u=onlyA+onlyB+i;
    return { setLine:'Set S — Sets · Pairs & products',
      prompt:`|A| = ${a}, |B| = ${b}, |A ${SS.cap} B| = ${i}. What is |A ${SS.cup} B|?`,
      instr:`Inclusion–exclusion: |A ${SS.cup} B| = |A| + |B| − |A ${SS.cap} B| — adding |A| and |B| counts the overlap twice, so subtract it once.`,
      mode:opts.type?'type':'mc', noKeyboard:true, scratch:true,
      choices:mc(String(u),[
        {text:String(a+b), why:'That counts the members of the overlap twice — subtract |A ∩ B| once.'},
        {text:String(a+b-2*i), why:'You subtracted the overlap twice; it was only double-counted once.'},
        String(u+1)]),
      answer:String(u), accept:acceptNum,
      explain:()=>`|A ${SS.cup} B| = ${a} + ${b} − ${i} = ${u}.` };
  }
  // pairfact: fixed conceptual items
  const F=[
    {q:`(1,2) = (2,1) — true or false?`, a:`False — ordered pairs care about order; (a,b) = (c,d) only when a = c and b = d`,
     d:[{text:`True — a pair is just a two-member collection`,why:`That's the SET {1,2}, which does equal {2,1}. Pairs are ordered precisely so that (1,2) ≠ (2,1).`}]},
    {q:`{1,2} = {2,1} — true or false?`, a:`True — a set is fixed by its members alone; order is irrelevant`,
     d:[{text:`False — the elements are listed in a different order`,why:`Order matters for ordered pairs, not for sets — extensionality says same members, same set.`}]},
    {q:`In general, does A ${SS.times} B = B ${SS.times} A?`, a:`No — the pairs point in opposite directions (unless A = B, or one of them is empty)`,
     d:[{text:`Yes — both contain the same coordinates`,why:`(a,b) ${SS.in} A ${SS.times} B but (a,b) ${SS.in} B ${SS.times} A would need a ${SS.in} B and b ${SS.in} A. Same coordinates, different pairs.`}]},
    {q:`A relation from A to B is, in set-theoretic terms:`, a:`a subset of A ${SS.times} B — the set of pairs it relates`,
     d:[{text:`a member of A ${SS.times} B`,why:`A single pair is one member; a relation collects all the pairs it relates, so it's a SUBSET of the product.`},
        {text:`a function from A to B`,why:`Backwards — a function is a special relation (one output per input), not the other way round.`}]},
    {q:`A function f from A to B is a relation such that:`, a:`each member of A is paired with exactly one member of B`,
     d:[{text:`each member of B is paired with exactly one member of A`,why:`That would make the INVERSE a function. A function gives one output per input — one B-member per A-member.`},
        {text:`no two members of A get the same value`,why:`That's what makes a function one-to-one (injective) — an extra property, not part of being a function.`}]},
  ];
  const f=pick(F);
  return { setLine:'Set S — Sets · Pairs & products', prompt:f.q,
    instr:`(a,b) is ordered; {a,b} is not. A relation is a set of ordered pairs; a function is a relation with exactly one output per input.`,
    mode:'mc', noKeyboard:true, choices:mc(f.a,f.d), explain:()=>f.a+'.' };
}
```

## 7. Activity `laws` (paste verbatim — bank + driver)

True/false with explanations. `v` = the truth value; `why` is shown as the explanation either way.

```js
const S_LAWS=[
  {s:`${SS.empty} ${SS.sub} A, for every set A`, v:true,  why:`Vacuously true: A subset claim fails only if some member of the left set is missing from the right — and ${SS.empty} has no members to be missing.`},
  {s:`${SS.empty} ${SS.in} A, for every set A`, v:false, why:`Membership isn't automatic: ${SS.empty} ${SS.in} A only if A happens to contain the empty set as a member — e.g. ${SS.empty} ${SS.in} {${SS.empty}} but ${SS.empty} ${SS.ni} {1,2}.`},
  {s:`{${SS.empty}} = ${SS.empty}`, v:false, why:`{${SS.empty}} has one member (namely ${SS.empty}); ${SS.empty} has none. A bag containing an empty bag isn't empty.`},
  {s:`A ${SS.sub} A, for every set A`, v:true, why:`Every member of A is a member of A. (That's why "proper subset," ${SS.psub}, exists as a separate notion.)`},
  {s:`If A ${SS.sub} B and B ${SS.sub} C, then A ${SS.sub} C`, v:true, why:`Subsethood is transitive: chase any member of A through B into C.`},
  {s:`If A ${SS.in} B and B ${SS.in} C, then A ${SS.in} C`, v:false, why:`Membership is NOT transitive: 1 ${SS.in} {1}, and {1} ${SS.in} {{1}}, but 1 ${SS.ni} {{1}} — its only member is {1}.`},
  {s:`A = B if and only if A ${SS.sub} B and B ${SS.sub} A`, v:true, why:`Extensionality: sets with the same members are the same set — and mutual subsethood says exactly "same members."`},
  {s:`{1, 2, 2, 3} = {1, 2, 3}`, v:true, why:`Listing a member twice adds nothing: a set is fixed by WHICH things are members, not by how often they're mentioned.`},
  {s:`(A ${SS.cup} B)${SS.comp} = A${SS.comp} ${SS.cap} B${SS.comp}`, v:true, why:`De Morgan: to be outside a union is to be outside both sets.`},
  {s:`(A ${SS.cap} B)${SS.comp} = A${SS.comp} ${SS.cup} B${SS.comp}`, v:true, why:`De Morgan: to be outside an intersection is to be outside at least one of the sets.`},
  {s:`(A ${SS.cup} B)${SS.comp} = A${SS.comp} ${SS.cup} B${SS.comp}`, v:false, why:`De Morgan flips the operation: the complement of a union is the INTERSECTION of the complements.`},
  {s:`A ${SS.cap} (B ${SS.cup} C) = (A ${SS.cap} B) ${SS.cup} (A ${SS.cap} C)`, v:true, why:`Distribution — mirror of "P and (Q or R)" ≡ "(P and Q) or (P and R)."`},
  {s:`A ${SS.cup} (B ${SS.cap} C) = (A ${SS.cup} B) ${SS.cap} (A ${SS.cup} C)`, v:true, why:`Distribution works both ways for sets, just as for "and"/"or."`},
  {s:`A ${SS.diff} B = B ${SS.diff} A, in general`, v:false, why:`Difference is directional: {1,2} ${SS.diff} {2} = {1}, but {2} ${SS.diff} {1,2} = ${SS.empty}.`},
  {s:`A ${SS.sub} B if and only if A ${SS.cap} B = A`, v:true, why:`If all of A lies inside B, intersecting with B keeps all of A; conversely, if intersecting loses nothing, all of A was in B.`},
  {s:`A ${SS.sub} B if and only if A ${SS.cup} B = B`, v:true, why:`Adding A to B adds nothing new exactly when A was already inside B.`},
  {s:`A ${SS.sub} B if and only if A ${SS.diff} B = ${SS.empty}`, v:true, why:`A ${SS.diff} B collects A's members that are NOT in B — there are none exactly when A ${SS.sub} B.`},
  {s:`A ${SS.cup} A${SS.comp} = U and A ${SS.cap} A${SS.comp} = ${SS.empty}`, v:true, why:`Everything in U is in A or out of it, and nothing is both — the set-shaped law of excluded middle and non-contradiction.`},
  {s:`(A${SS.comp})${SS.comp} = A`, v:true, why:`Double complement cancels, like double negation.`},
  {s:`|A ${SS.cup} B| = |A| + |B|, for all finite A, B`, v:false, why:`Only when A and B are disjoint — otherwise the overlap is counted twice. In general |A ${SS.cup} B| = |A| + |B| − |A ${SS.cap} B|.`},
  {s:`A ${SS.in} P(B) if and only if A ${SS.sub} B`, v:true, why:`P(B)'s members are exactly B's subsets — this equivalence is the whole point of the power set.`},
  {s:`P(${SS.empty}) = ${SS.empty}`, v:false, why:`P(${SS.empty}) = {${SS.empty}} — the empty set has exactly one subset, itself. Even "nothing" has a power set with something in it.`},
  {s:`If A ${SS.sub} B, then P(A) ${SS.sub} P(B)`, v:true, why:`Any subset of A is automatically a subset of B, so it's in P(B) too.`},
  {s:`{a} ${SS.in} {a, {a}}`, v:true, why:`{a, {a}} has two members: a, and {a}. So {a} is a member — and also a subset, since its only member a is in there. Both at once!`},
];
function genS_laws(opts){
  const it=pick(S_LAWS);
  return { setLine:'Set S — Sets · Laws', prompt:`True or false?<br>${wff(it.s)}`,
    instr:`Test identities with a small example or a two-circle diagram in the scratch space. Watch the ${SS.in}/${SS.sub} distinction like a hawk.`,
    mode:'tf', noKeyboard:true, scratch:true,
    choices:[{text:'True',correct:it.v},{text:'False',correct:!it.v}],
    explain:()=>`${it.v?'True':'False'}. ${it.why}` };
}
```

## 8. Activity `basics` (paste verbatim — bank + driver)

```js
const S_BASICS=[
  {q:`A = {1, {2}, 3}. &nbsp; Is 2 ${SS.in} A?`, a:`No — A's members are 1, {2}, and 3; the number 2 itself is not among them`,
   d:[{text:`Yes — 2 appears inside A`,why:`2 appears inside a MEMBER of A (the set {2}), but membership doesn't reach inside members. {2} ${SS.in} A; 2 ${SS.ni} A.`}]},
  {q:`A = {1, {2}, 3}. &nbsp; What is |A|?`, a:`3 — the members are 1, {2}, and 3`,
   d:[{text:`4`,why:`Don't count 2 separately — it's sealed inside the member {2}.`},{text:`2`,why:`{2} counts as one member, and so do 1 and 3 — three in all.`}]},
  {q:`Which is true of ${SS.empty} and {${SS.empty}}?`, a:`|${SS.empty}| = 0 and |{${SS.empty}}| = 1 — the second has the empty set as its one member`,
   d:[{text:`They are the same set`,why:`Different members: ${SS.empty} has none, {${SS.empty}} has one (namely ${SS.empty}). By extensionality they differ.`},
      {text:`Both are empty`,why:`{${SS.empty}} is not empty — it contains something, the empty set.`}]},
  {q:`Is a ${SS.in} {a}? And is a = {a}?`, a:`a ${SS.in} {a}, but a ≠ {a} — a thing is never identical to its own singleton`,
   d:[{text:`Both — braces around one thing change nothing`,why:`Braces change everything: {a} is a SET with one member. Socrates is a man; {Socrates} is a set. (If a = {a}, a set could be its own sole member — banned in standard set theory.)`}]},
  {q:`{x : x is an even number and 1 < x < 9} in roster notation is:`, a:`{2, 4, 6, 8}`,
   d:[{text:`{2, 4, 6}`,why:`8 satisfies the condition too: it's even and between 1 and 9.`},
      {text:`{1, 2, 4, 6, 8}`,why:`1 fails the condition — it isn't even (and isn't strictly between 1 and 9).`}]},
  {q:`Which set-builder description picks out {1, 3, 5, 7, 9}?`, a:`{x : x is an odd number and x < 10}`,
   d:[{text:`{x : x is a number and x < 10}`,why:`That includes the evens too.`},
      {text:`{x : x is an odd number}`,why:`Right start, but nothing stops it at 9 — set-builder needs the whole condition.`}]},
  {q:`{1, 2} and {2, 1, 1}:`, a:`are the same set — order and repetition are irrelevant to what a set is`,
   d:[{text:`are different sets`,why:`Extensionality: a set is fixed by which things are members. Both have exactly the members 1 and 2.`}]},
  {q:`B = {1, 2}. Which is correct?`, a:`{1} ${SS.sub} B and 1 ${SS.in} B`,
   d:[{text:`{1} ${SS.in} B and 1 ${SS.sub} B`,why:`Backwards on both: B's members are the numbers 1 and 2 (so 1 ${SS.in} B), and {1} is a subset because its member is in B. {1} would be a MEMBER only of a set like {{1},2}.`},
      {text:`1 ${SS.sub} B`,why:`Subsethood relates sets to sets; the number 1 isn't a set here. 1 ${SS.in} B is the right claim.`}]},
  {q:`How many members has {${SS.empty}, {${SS.empty}}}?`, a:`2 — the empty set, and the singleton of the empty set`,
   d:[{text:`0`,why:`It plainly contains things — two of them.`},{text:`1`,why:`${SS.empty} and {${SS.empty}} are different sets (0 vs 1 members), so they count as two members.`}]},
  {q:`"The set of prime numbers between 24 and 28" is:`, a:`${SS.empty} — a perfectly good set with no members (25 = 5·5, 26 = 2·13, 27 = 3³)`,
   d:[{text:`not a set at all`,why:`An unsatisfiable condition still defines a set — the empty one. There is exactly one empty set.`},
      {text:`{25, 27}`,why:`25 and 27 aren't prime.`}]},
  {q:`How many different empty sets are there?`, a:`Exactly one — sets with the same members are identical, and all empty sets have the same members (none)`,
   d:[{text:`One per kind of thing (an empty set of numbers, an empty set of people…)`,why:`Tempting, but extensionality forbids it: with no members, there's nothing to tell them apart, so they're one set.`}]},
  {q:`A = {n : n is a natural number}. Is A finite?`, a:`No — for any candidate largest member there's a larger one`,
   d:[{text:`Yes — every particular natural number is finite`,why:`Each MEMBER is finite, but the SET of all of them is infinite. Don't confuse properties of members with properties of the set.`}]},
];
function genS_basics(opts){
  const it=pick(S_BASICS);
  return { setLine:'Set S — Sets · Membership & notation', prompt:it.q,
    instr:`${SS.in} says "is a member of"; ${SS.sub} says "every member of the first is a member of the second." Braces build a set out of whatever is listed — including other sets. ${SS.empty} = the set with no members.`,
    mode:'mc', noKeyboard:true, choices:mc(it.a,it.d), explain:()=>it.a+'.' };
}
```

## 9. Activity `inf` (paste verbatim — bank + driver)

```js
const S_INF=[
  {q:`Two sets are "equinumerous" (the same size) when:`,
   a:`there is a one-to-one correspondence pairing each member of one with exactly one member of the other, none left over`,
   d:[{text:`they have the same members`,why:`Same members makes them the same SET. Same size is weaker — {1,2} and {a,b} differ in members but match in size.`},
      {text:`counting them gives the same number`,why:`Counting works only for finite sets. Correspondence is the definition that still makes sense for infinite sets — that's Cantor's key move.`},
      {text:`each is a subset of the other`,why:`Mutual subsethood is identity (extensionality), not sameness of size.`}]},
  {q:`The set of even natural numbers, compared with the set of ALL natural numbers, is:`,
   a:`the same size — n ↦ 2n pairs the naturals with the evens exactly`,
   d:[{text:`half the size`,why:`Finite intuition. For infinite sets, a proper subset can be equinumerous with the whole — that's practically the definition of "infinite."`},
      {text:`smaller, though both are infinite`,why:`The pairing 0↔0, 1↔2, 2↔4, 3↔6, … leaves nothing out on either side, so the sizes are equal.`},
      {text:`impossible to compare`,why:`Cantor's insight is that one-to-one correspondence DOES compare infinite sizes, and here it delivers a clear verdict: equal.`}]},
  {q:`Hilbert's Hotel has infinitely many rooms, all full. A new guest arrives. The manager:`,
   a:`moves each guest from room n to room n+1, freeing room 1 — an infinite hotel that's full can still take more`,
   d:[{text:`must turn the guest away — full is full`,why:`For FINITE hotels. The shift n ↦ n+1 relocates every current guest and opens room 1: full-but-roomy is the signature of the infinite.`},
      {text:`needs to build one more room`,why:`No construction needed — rearrangement alone frees a room.`}]},
  {q:`The set of integers (…, −2, −1, 0, 1, 2, …) is:`,
   a:`countable — list them 0, 1, −1, 2, −2, 3, −3, … and every integer shows up at some finite position`,
   d:[{text:`uncountable — it stretches to infinity in two directions`,why:`Direction doesn't matter; having SOME complete list does. Interleaving positives and negatives gives one.`},
      {text:`twice the size of the natural numbers`,why:`"Twice ℵ₀" is still ℵ₀ — the interleaved list is a bijection with ℕ.`}]},
  {q:`The rational numbers (all fractions) are:`,
   a:`countable — arrange fractions in a grid by numerator and denominator and snake through it diagonally, skipping repeats`,
   d:[{text:`uncountable — between any two rationals there's another`,why:`Density feels overwhelming but doesn't block listing: the diagonal walk through the grid reaches every fraction at a finite step. Density ≠ uncountability.`},
      {text:`the same size as the real numbers`,why:`Strictly smaller: ℚ is countable, and Cantor's diagonal argument shows ℝ is not.`}]},
  {q:`Cantor's diagonal argument shows the real numbers are uncountable. The core move: given ANY infinite list of reals,`,
   a:`build a real that differs from the n-th listed number at the n-th decimal place — so it's missing from the list, and no list is complete`,
   d:[{text:`show the list must repeat itself eventually`,why:`Nothing forces repetition. The argument constructs a MISSING number instead.`},
      {text:`show some real numbers can't be described`,why:`The diagonal number is described perfectly well — what fails is only its presence on the given list.`},
      {text:`derive a contradiction from the axioms of arithmetic`,why:`No contradiction in arithmetic — just a refutation of the assumption "this list contains every real."`}]},
  {q:`In the diagonal argument, the constructed number:`,
   a:`is a perfectly good real number — its crime is only that it differs from every entry on the given list`,
   d:[{text:`is not a genuine real number`,why:`It has a decimal digit at every place — as genuine as any real. Denying its reality is the classic wrong escape route.`},
      {text:`appears further down the list`,why:`It can't: it differs from entry n at digit n, for EVERY n.`}]},
  {q:`Cantor's theorem says: for EVERY set A,`,
   a:`|A| < |P(A)| — the power set is always strictly bigger, so there is an endless ladder of infinite sizes`,
   d:[{text:`|P(A)| = 2·|A|`,why:`For finite sets |P(A)| = 2^|A| (exponent, not product) — and the theorem's punch is that P(A) outruns A even when A is infinite.`},
      {text:`every infinite set is the same size`,why:`The exact opposite of the theorem: P(ℕ) is strictly bigger than ℕ, P(P(ℕ)) bigger still, without end.`}]},
  {q:`ℵ₀ (aleph-null) names:`,
   a:`the size of the natural numbers — the smallest infinite size`,
   d:[{text:`the largest infinite number`,why:`There is no largest: Cantor's theorem manufactures a bigger size from any given one.`},
      {text:`the size of the real numbers`,why:`ℝ is strictly bigger than ℵ₀ — that's what the diagonal argument establishes. The reals' size is called the cardinality of the continuum.`}]},
  {q:`The continuum hypothesis (CH) conjectures:`,
   a:`no set is strictly bigger than ℕ yet strictly smaller than ℝ`,
   d:[{text:`the real numbers are countable`,why:`Refuted by the diagonal argument. CH is about whether anything sits strictly BETWEEN ℕ and ℝ in size.`},
      {text:`every infinite set is the size of ℕ or of ℝ`,why:`Close, but CH concerns only the gap between ℕ and ℝ — Cantor's ladder keeps climbing above ℝ regardless.`}]},
  {q:`What did Gödel (1940) and Cohen (1963) together show about the continuum hypothesis?`,
   a:`the standard axioms of set theory can neither refute it (Gödel) nor prove it (Cohen) — CH is independent of them`,
   d:[{text:`that it is true`,why:`Neither proved it — Gödel showed the axioms can't refute it; Cohen showed they can't prove it either.`},
      {text:`that it is meaningless`,why:`Independence is a precise mathematical status, not meaninglessness — though philosophers dispute what it tells us about truth.`}]},
  {q:`Russell's paradox concerns R = {x : x is not a member of itself}. The problem:`,
   a:`R ${SS.in} R if and only if R ${SS.ni} R — a contradiction either way`,
   d:[{text:`R turns out to be empty`,why:`If R were empty, then R ${SS.ni} R, so R would satisfy its own defining condition and belong to R after all — the contradiction, not emptiness.`},
      {text:`R is simply too large to be a set`,why:`That's a DIAGNOSIS offered by later set theory (limitation of size), not the paradox itself. The paradox is the flat contradiction.`}]},
  {q:`The moral standardly drawn from Russell's paradox:`,
   a:`naive comprehension — "every condition determines a set" — must be abandoned; axiomatic set theory restricts how sets may be formed`,
   d:[{text:`mathematics is inconsistent`,why:`The contradiction springs from one naive principle, not from mathematics — ZF-style theories drop it and no paradox has surfaced there.`},
      {text:`the notion of a set is incoherent`,why:`Too strong: restricted set formation (e.g. separating subsets from a GIVEN set) works smoothly.`},
      {text:`some sets both are and are not members of themselves`,why:`Nothing true is a contradiction; the conclusion is that R does not exist as a set.`}]},
  {q:`A set is INFINITE, on Dedekind's elegant definition, exactly when:`,
   a:`it can be put in one-to-one correspondence with a proper part of itself`,
   d:[{text:`it has more than a trillion members`,why:`Any fixed bound leaves a finite set. Dedekind's mark: the whole matches a proper part — as ℕ matches the evens.`},
      {text:`its members go on without repeating`,why:`Vague — the correspondence-with-a-part criterion is the precise version of that intuition.`}]},
  {q:`Which pair differs in size?`,
   a:`ℕ and ℝ`,
   d:[{text:`ℕ and ℤ`,why:`Same size — interleave positives and negatives.`},
      {text:`ℕ and ℚ`,why:`Same size — snake diagonally through the grid of fractions.`},
      {text:`ℕ and the even numbers`,why:`Same size — pair n with 2n.`}]},
  {q:`P(ℕ), the set of ALL sets of natural numbers, is:`,
   a:`uncountable — by Cantor's theorem it is strictly bigger than ℕ itself`,
   d:[{text:`countable, since ℕ is`,why:`Cantor's theorem says the power set ALWAYS outruns the set: no list of sets of naturals can be complete (diagonalize: build the set of n's not in the n-th listed set).`},
      {text:`the same size as ℕ`,why:`Strictly bigger — in fact P(ℕ) is the size of ℝ.`}]},
];
function genS_inf(opts){
  const it=pick(S_INF);
  return { setLine:'Set S — Sets · Infinity', prompt:it.q,
    instr:`One idea runs through all of this: sizes are compared by one-to-one correspondence, not by counting. Everything else — countability, the diagonal argument, Cantor's theorem — unfolds from it.`,
    mode:'mc', noKeyboard:true, scratch:true, choices:mc(it.a,it.d), explain:()=>it.a+'.' };
}
```

## 10. Verification checklist (do all of it)

1. Open `logicola.html` in a browser. The Exercise Sets menu must show **Sets and Metatheory** as the LAST section (below "Explore · Non-Classical Logic"), containing Set S.
2. Do ≥15 problems in EACH of the six activities, in both MC and Type modes where offered. No console errors.
3. Typing tests for the canonicalizer: for an ops answer `{2, 3}`, all of `{3,2}`, `{ 3 , 2 }`, `{2,3,3}` must be accepted; for an empty answer, both `∅` and `{}`; for a power-set answer, member order fully scrambled including `{}` for the inner ∅; for a product, `{(1,x),(2,x)}` in any pair order but NOT with flipped coordinates.
4. Wrong answers must show the `why`/`diagnose` text, not generic feedback.
5. Earn 100 points in one activity; confirm the ✓ Mastered badge appears for Set S and Scores/export still work.
6. Help → Set S shows the guide with the example block.
7. `cp logicola.html index.html`, and confirm the `instructor.html` SET_TITLES edit.
