# TASK (for Opus): Add Set T — Formal Languages & Metatheory to LogiCola

You are modifying **`logicola.html`** (single-file vanilla-JS app, ~8000 lines) in the New Logicola folder. `index.html` is a byte-for-byte copy. A parallel task adds Set S and a shared menu group; the wiring below is written so either task can run first.

**Do not reword any quoted content in this ticket.** Question text, correct answers, explanations, and distractor `why` diagnoses were authored for philosophical accuracy — several items live exactly on classic confusions (soundness vs completeness, Gödel 1930 vs 1931, "true but unprovable"), where small rewordings create errors. If you think something is wrong, add `// FLAG:` in a comment and keep the text.

## 1. Architecture crib sheet (verified against the file)

- `const SETS` (~5496): `id → {name, chapter, gen, hasHarder}`. Use free ID **T**.
- `const SET_GROUPS` (~5762): menu groups `[title, chapterLabel, [ids]]`.
- `function fileMenu()` (~7224): renders groups, then an "Explore · Non-Classical Logic" block.
- `const MENU` (~7272): per-set activity menu; entry shape `{key:'tMode', acts:[[value,label,desc],...]}`.
- `const STATE_DEFAULTS` (~5527): add mode keys here only.
- Help registries: `SET_TITLES`, `ABOUT` (~7817), `INFO` (~7875), `HELP_EX` (~7975).
- **Generator contract** — `SETS.T.gen(opts)` returns:
  ```js
  { setLine, prompt, instr, mode:'mc'|'tf'|'type',
    choices:[{text,correct,why}],            // mc/tf
    noKeyboard:true, scratch:true,           // optional
    explain:()=>'html' }
  ```
- Helpers: `pick, rand, shuffle, sampleDistinct, uniqStrings, cap`, `mc(correct, distractors)` (4-option builder; distractors `'text'` or `{text,why}`; dedups), `wff(s)` (styling span).
- **Logic engine to reuse** (~lines 298–2160): `parseProp(str)` → AST `{op:'var',name}` / `{op:'~',a}` / `{op:'&'|'|'|'>'|'=',a,b}`; `astRender(ast)` renders in the user's chosen notation via `SYM` (`SYM.not/and/or/horseshoe/threebar`); `astStr(ast)` canonical string; `astEval(ast, assignment)`; `allAssignments(letters)`; `astLetters(ast)`. Set T must respect the notation setting — always display formulas through `astRender`/`SYM`, never hardcode symbols in formula strings (hardcoding them in prose explanations via `${SYM.x}` template slots, as below, is fine).
- Quantifier rendering for the `reg` activity: `qU('x')` and `qE('x')` give `(x)`/`(∃x)` or `∀x`/`∃x` per the user's setting.

## 2. Wiring

**2a.** In `SETS` add:
```js
T:{name:'Formal Languages & Metatheory', chapter:'Supplement · syntax, semantics, the big theorems', gen:genT, hasHarder:false},
```
**2b.** `SET_GROUPS`: if a `'Sets and Metatheory'` group already exists, add `'T'` after `'S'`; otherwise append as **last** entry `['Sets and Metatheory','Supplement',['S','T']]`.
**2c.** If (and only if) the parallel task hasn't already: in `fileMenu()` change `ids.map(btn)` to `ids.filter(id=>SETS[id]).map(btn)`, and split the group rendering so the `'Sets and Metatheory'` group renders AFTER the Explore block:
```js
const gHtml=([title,ch,ids])=>
  `<h3 style="margin:18px 0 2px">${title} <span class="muted" style="font-weight:400;font-size:13px">· ${ch}</span></h3>
   <div class="grid">${ids.filter(id=>SETS[id]).map(btn).join('')}${ids.includes('G')?toolBtn:''}${ids.includes('I')?qtoolBtn:''}${ids.includes('K')?ktoolBtn:''}</div>`;
const groups   = SET_GROUPS.filter(g=>g[0]!=='Sets and Metatheory').map(gHtml).join('');
const smGroups = SET_GROUPS.filter(g=>g[0]==='Sets and Metatheory').map(gHtml).join('');
```
…and render `${groups} ${deviantBtn} ${smGroups}` in the modal template.
**2d.** `STATE_DEFAULTS`: add `tMode:'lang',`
**2e.** `MENU` add:
```js
T:{key:'tMode',
   acts:[['lang','Language & metalanguage','Use vs mention, object vs metalanguage, types & tokens'],
         ['gram','Grammar & wffs','Formation rules, wff or not, main connective, subformulas'],
         ['sem','Syntax vs semantics','Interpretations, tautologies, ⊨ vs ⊢'],
         ['meta','Metatheory','Soundness, completeness, decidability, Gödel'],
         ['reg','Regimented English','Scope made visible in English itself — Montague & Klima']]},
```
**2f.** `SET_TITLES`: `T:'Formal Languages & Metatheory'`. `ABOUT`:
```js
T:'Step back and study logical languages themselves: how a formal language is built from an alphabet and formation rules, how syntax differs from semantics and object language from metalanguage, what the great metatheorems say — and how a regimented fragment of English (Montague, Klima) can do a formal language\'s work.',
```
`INFO`:
```js
T:`<b>Syntax</b> is about shape (wff, proof, main connective); <b>semantics</b> is about truth under interpretations (tautology, validity, ${'⊨'}). The <b>object language</b> is the language studied; the <b>metalanguage</b> is the language we study it in — "wff," "valid," and "⊢" are metalanguage. To talk about an expression, quote it: Boston is a city, but 'Boston' has six letters. The grammar used here: (1) any capital letter is a wff; (2) if P is a wff so is its negation; (3) if P and Q are wffs so is (P # Q) for each binary connective, parentheses included; nothing else is a wff. In the <b>regimented English</b> activity, quantifier phrases are pulled to the front in scope order, each as "every/some … is such that …," and pronouns act as bound variables.`,
```
`HELP_EX`:
```js
T:()=>`Regimenting "Every critic reviewed some book" (reading: the book may vary):<br>
<b>Every critic is such that some book is such that he reviewed it.</b><br>
Same sentence, other reading (one book for all):<br>
<b>Some book is such that every critic is such that he reviewed it.</b><br>
The unregimented sentence is scope-ambiguous; each regimentation — like each wff — has exactly one reading.`,
```
**2g.** `instructor.html` `SET_TITLES` (~line 167): ensure `T:'Formal Languages & Metatheory'` is present (the parallel task may have added it).
**2h.** When done: `cp logicola.html index.html`.

## 3. Set T shared code (paste verbatim)

```js
/* ================= SET T — FORMAL LANGUAGES & METATHEORY ================= */
function genT(opts){
  const m=state.tMode||'lang';
  return m==='gram'?genT_gram(opts):m==='sem'?genT_sem(opts):m==='meta'?genT_meta(opts)
       :m==='reg'?genT_reg(opts):genT_lang(opts);
}
function tBankItem(bank, setLine, instr){
  const it=pick(bank);
  return { setLine, prompt:it.q, instr:it.instr||instr, mode:'mc', noKeyboard:true,
    choices:mc(it.a, it.d), explain:()=>it.x||it.a+'.' };
}
/* random wff AST over given letters */
function tRandAst(depth, letters){
  letters=letters||['A','B','C'];
  if(depth<=0||(depth<2&&Math.random()<0.4)) return {op:'var',name:pick(letters)};
  if(Math.random()<0.28) return {op:'~',a:tRandAst(depth-1,letters)};
  return {op:pick(['&','|','>','=']), a:tRandAst(depth-1,letters), b:tRandAst(rand(depth),letters)};
}
function tSubAsts(f,out){ out=out||[]; out.push(f); if(f.a)tSubAsts(f.a,out); if(f.b)tSubAsts(f.b,out); return out; }
```

## 4. Activity `lang` (bank verbatim; the first item is a template — implement `tMentionItem()` as described after the bank)

```js
const T_LANG=[
  {q:`Which of these is true?`,
   a:`'Boston' has six letters`,
   d:[{text:`Boston has six letters`,why:`Without quotes you're talking about the city — and cities don't have letters. To say something about the WORD, quote it.`},
      {text:`'Boston' is a large city`,why:`With quotes you're talking about the word — and words aren't cities. Use the name unquoted to talk about the city.`}],
   x:`'Boston' (in quotes) names the word, which has six letters; Boston (no quotes) is the city. Quotation forms a name of an expression — the standard device for MENTIONING rather than USING it.`},
  {q:`The object language / metalanguage distinction:`,
   a:`the object language is the language under study; the metalanguage is the language in which we study it`,
   d:[{text:`the object language is about objects; the metalanguage is about ideas`,why:`Nothing to do with subject matter — it's about which language is being TALKED ABOUT and which is doing the talking.`},
      {text:`the metalanguage must be a formal language`,why:`Usually it's the opposite: the object language is formal and the metalanguage is ordinary English (plus some mathematics).`}],
   x:`When this app states rules ABOUT wffs in English, the wff-language is the object language and English is the metalanguage.`},
  {q:`Which of these belong to the METALANGUAGE rather than the object language of propositional logic?`,
   a:`"is a wff," "is valid," "⊢" — vocabulary for talking about the formulas`,
   d:[{text:`the sentence letters A, B, C`,why:`Those are the object language's own vocabulary — the things talked about.`},
      {text:`the parentheses`,why:`Parentheses are object-language symbols, part of wffs themselves.`}],
   x:`Anything used to describe or evaluate the formulas — "wff," "valid," "provable," "⊢," "⊨" — is metalanguage.`},
  {q:`When a rule is stated as "from (P • Q) infer P," the letters P and Q are:`,
   a:`metavariables — metalanguage letters standing for arbitrary wffs of the object language`,
   d:[{text:`two particular sentence letters of the object language`,why:`Then the rule would only apply to the single wff (P • Q). It applies to (A • B), ((C ∨ D) • E), … because P, Q range over ALL wffs.`},
      {text:`abbreviations for English sentences`,why:`They abbreviate nothing — they're variables in the metalanguage ranging over object-language formulas.`}],
   x:`Rule statements are metalanguage generalizations about infinitely many object-language wffs — that's what metavariables achieve.`},
  {q:`A formal language, strictly speaking, is defined by:`,
   a:`an alphabet of symbols plus formation rules saying which strings of them are well-formed — nothing more`,
   d:[{text:`an alphabet, formation rules, and the meanings of the symbols`,why:`Meanings come later, with an interpretation — the LANGUAGE itself is pure syntax. That's what lets us study it mathematically.`},
      {text:`a dictionary and a grammar`,why:`A dictionary assigns meanings; a bare formal language has none until semantics is added.`}],
   x:`Language = alphabet + grammar. Interpretation is a further, separable step — the separation is the deep idea.`},
  {q:`The distinction between a sentence TYPE and its TOKENS:`,
   a:`the type is the repeatable pattern; a token is a particular physical inscription or utterance of it`,
   d:[{text:`types are written, tokens are spoken`,why:`Both written inscriptions and utterances are tokens; the type is what they're all instances of.`},
      {text:`a type is a kind of token found in formal languages only`,why:`English has types and tokens too — "the cat saw the cat" has 5 word tokens of 4 word types.`}],
   x:`Logic's laws are about types; ink and sound provide the tokens.`},
  {q:`Why do logicians bother with quotation marks when stating facts about expressions?`,
   a:`to form a NAME of the expression — otherwise the sentence would use the expression and talk about whatever it refers to`,
   d:[{text:`for emphasis`,why:`Quotation here is a naming device, not typography: 'snow' names a four-letter word.`},
      {text:`because expressions cannot appear inside sentences`,why:`They appear constantly — the issue is whether they're USED (doing their normal job) or MENTIONED (being talked about).`}],
   x:`Confusing use with mention collapses claims about words into claims about things — the source of many classical fallacies and paradoxes.`},
  {q:`Which sentence commits a use–mention confusion?`,
   a:`Chicago has seven letters`,
   d:[{text:`'Chicago' has seven letters`,why:`Correct as it stands — the quoted name names the word.`},
      {text:`Chicago has almost three million residents`,why:`Correct — the unquoted name is used, and the claim is about the city.`}],
   x:`Cities don't have letters; words do. The claim needs quotes: 'Chicago' has seven letters.`},
  {q:`Tarski argued that, on pain of paradox, a truth predicate for a language should live in:`,
   a:`a richer metalanguage — the language itself cannot consistently contain its own unrestricted truth predicate`,
   d:[{text:`the language itself, since speakers apply "true" to their own sentences`,why:`That's what generates the liar ("this sentence is false"). Tarski's hierarchy blocks it: truth-for-L is defined one level up.`},
      {text:`no language — truth is indefinable`,why:`Tarski showed truth for a given object language IS rigorously definable — in its metalanguage.`}],
   x:`The liar paradox is the pressure; the object/metalanguage hierarchy is Tarski's release valve.`},
  {q:`Ordinary English serves as its own metalanguage ("the word 'dog' has three letters"). For formal work logicians still separate the two because:`,
   a:`a sharp separation gives an exact, paradox-free setting for proving things ABOUT the language`,
   d:[{text:`English is not really a language`,why:`It is — the point is methodological control, not a defect in English's status.`},
      {text:`object languages are always incomplete`,why:`Incompleteness is a property of certain theories (a later topic), not the reason for the object/meta distinction.`}],
   x:`Self-application is where paradox breeds; regimenting WHO talks about WHOM keeps the metatheory clean.`},
];
function genT_lang(opts){
  if(Math.random()<0.3) return tMentionItem();
  return tBankItem(T_LANG,'Set T — Formal Languages · Language & metalanguage',
    `Use an expression to do its normal job; mention it — with quotes — to talk about the expression itself. "Wff," "valid," "⊢": metalanguage. Sentence letters, connectives, parentheses: object language.`);
}
/* tMentionItem(): pick w from ['logic','proof','valid','snow','seven','Aristotle'];
   ask: `Which is true?` with correct `'w' has ${w.length} letters` and distractors
   `w has ${w.length} letters` (why: use–mention — unquoted, you talk about the thing, not the word)
   and `'w' has ${w.length-1} letters` (why: count again — the quoted word has w.length).
   For 'seven' also offer `seven has five letters` with why: numbers don't have letters; the WORD does — quote it.
   explain: quoting names the word; the word has N letters. Same return shape as tBankItem. */
```

## 5. Activity `gram` (paste verbatim + implement the two marked functions)

The grammar to display (rendered with the user's SYM):

```js
function tGrammarBox(){
  return `<div class="muted" style="font-size:13px;margin:8px 0;border:1px solid var(--line);border-radius:8px;padding:8px 10px">
    <b>The grammar.</b> 1. Any capital letter is a wff. &nbsp;2. The result of prefixing ${SYM.not} to a wff is a wff.
    &nbsp;3. The result of joining two wffs with ${SYM.and}, ${SYM.or}, ${SYM.horseshoe}, or ${SYM.threebar} and enclosing the result in parentheses is a wff.
    &nbsp;<i>Nothing else is a wff.</i></div>`;
}
const T_GRAM_FIXED=[
  {q:`The clause "nothing else is a wff" does real work: it guarantees that`,
   a:`the wffs are EXACTLY the strings the rules generate — so properties can be proved of all wffs by induction on the rules`,
   d:[{text:`the language stays small enough to be useful`,why:`The language is infinite anyway. The closure clause fixes membership exactly, which is what proofs by induction need.`},
      {text:`no new connectives may ever be added`,why:`One may define richer languages freely; the clause closes THIS language's membership, nothing more.`}],
   x:`This closure clause is what makes "prove it for the letters, preserve it through rules 2 and 3, conclude it for every wff" a valid argument form — structural induction.`},
  {q:`Claim: every wff has equal numbers of left and right parentheses. The BASE CASE of the induction proves it for:`,
   a:`the sentence letters — which contain zero of each`,
   d:[{text:`the shortest formula containing parentheses`,why:`The base case handles the wffs the rules START from — letters — not the shortest parenthesized wff.`},
      {text:`the empty string`,why:`The empty string isn't a wff at all; induction starts from clause 1's letters.`}],
   x:`Base: letters have 0 and 0. Induction: rule 2 adds no parentheses; rule 3 adds one of each. Closure: every wff is reached this way. Hence balance always.`},
  {q:`Same claim, the INDUCTION STEP: assuming the parts are balanced, show the whole is. Rule 3 preserves balance because:`,
   a:`it adds exactly one left and one right parenthesis around already-balanced parts`,
   d:[{text:`parentheses always come in pairs in mathematics`,why:`That's the thing being PROVED — an induction step can't just assert it.`},
      {text:`rule 3 adds no parentheses`,why:`That's rule 2 (negation). Rule 3 adds one of each — which is why balance survives.`}],
   x:`Each rule application keeps the ledger even; the closure clause says there's no other way to be a wff. This is the simplest real metatheorem — a proof ABOUT the language, in the metalanguage.`},
  {q:`"Unique readability" is the metatheorem that every wff:`,
   a:`can be built by the formation rules in exactly one way — so it has one main connective and one parse`,
   d:[{text:`can be read aloud unambiguously`,why:`Pronunciation isn't the point; unique STRUCTURE is — one construction tree per wff.`},
      {text:`contains no ambiguous words`,why:`Formal symbols aren't the issue; the theorem rules out structural (grouping) ambiguity, the formal analogue of amphiboly.`}],
   x:`Compare English "old men and women," which parses two ways. The parentheses of rule 3 make that impossible here — that's a designed-in feature, and it's provable.`},
];
function genT_gram(opts){
  const kind=pick(['wffq','wffq','wffq','main','main','sub','clause','fixed']);
  if(kind==='fixed') { const r=tBankItem(T_GRAM_FIXED,'Set T — Formal Languages · Grammar & wffs',''); r.prompt=tGrammarBox()+r.prompt; r.instr='A metatheorem is a claim ABOUT the formal language, proved in the metalanguage — usually by induction on the formation rules.'; return r; }
  const ast=tRandAst(2+rand(2));
  const good=astRender(ast);
  if(kind==='wffq') return tWffOrNot(ast,good);
  if(kind==='main'){
    const root=ast.op==='var'?null:ast.op;
    if(!root) return genT_gram(opts);
    const names={'~':'the negation sign','&':`${SYM.and} (and)`,'|':`${SYM.or} (or)`,'>':`${SYM.horseshoe} (if-then)`,'=':`${SYM.threebar} (iff)`};
    const symOf={'~':SYM.not,'&':SYM.and,'|':SYM.or,'>':SYM.horseshoe,'=':SYM.threebar};
    const present=uniqStrings(tSubAsts(ast).filter(f=>f.op!=='var').map(f=>f.op));
    const ds=present.filter(o=>o!==root).map(o=>({text:symOf[o],
      why:`That occurrence lies inside the formula — within parentheses or inside a negated part. The main connective is the one applied LAST, governing the whole.`}));
    while(ds.length<2){ const extra=pick(['&','|','>','=','~'].filter(o=>o!==root&&!ds.some(d=>d.text===symOf[o]))); ds.push({text:symOf[extra],why:`That connective doesn't govern the whole formula${present.includes(extra)?'':' — it does not even occur here'}.`}); }
    return { setLine:'Set T — Formal Languages · Grammar & wffs',
      prompt:tGrammarBox()+`What is the MAIN connective of ${wff(good)}?`,
      instr:`The main connective is the one introduced by the LAST formation-rule application — the operator of the whole formula, outside every parenthesis pair (or the initial ${SYM.not} if the whole is a negation).`,
      mode:'mc', noKeyboard:true, choices:mc(symOf[root],ds),
      explain:()=>`The whole formula is ${names[root]==='the negation sign'?'a negation':'built with '+names[root]} — ${wff(symOf[root])} is applied last, so it's the main connective.` };
  }
  if(kind==='sub'){
    const subs=uniqStrings(tSubAsts(ast).map(astRender));
    if(subs.length<3) return genT_gram(opts);
    let fake=astRender({op:'~',a:pick(tSubAsts(ast).filter(f=>f.op!=='~'))});
    if(subs.includes(fake)) fake=astRender({op:'&',a:{op:'var',name:'A'},b:{op:'var',name:'Z'}});
    const others=sampleDistinct(subs.filter(s=>s!==good),Math.min(3,subs.length-1))
      .map(s=>({text:s,why:`That IS a subformula — it appears as a part built along the way to the whole.`}));
    return { setLine:'Set T — Formal Languages · Grammar & wffs',
      prompt:tGrammarBox()+`Which of these is NOT a subformula of ${wff(good)}?`,
      instr:`The subformulas of a wff are the wffs used in building it up by the rules — its parts, their parts, and so on, plus the whole itself.`,
      mode:'mc', noKeyboard:true, choices:mc(fake,others),
      explain:()=>`${wff(fake)} never occurs in the construction of ${wff(good)}.` };
  }
  // clause: which clause certifies the last step
  const forms=[{f:{op:'var',name:pick(['A','B','C'])},clause:'Clause 1 — it is a sentence letter',
                d:[{text:'Clause 2 — negation',why:'No negation sign was applied; the string IS one of the alphabet\'s letters, which clause 1 admits outright.'},
                   {text:'Clause 3 — binary connective',why:'No connective or parentheses here — clause 1 alone certifies bare letters.'}]},
               {f:{op:'~',a:tRandAst(1+rand(2))},clause:`Clause 2 — it prefixes ${SYM.not} to a wff`,
                d:[{text:'Clause 1 — sentence letter',why:'It is longer than a letter; the LAST step prefixed a negation sign, which is clause 2\'s business.'},
                   {text:'Clause 3 — binary connective',why:'The outermost operation is the initial negation sign, not a parenthesized binary compound — even if clause 3 was used earlier, the FINAL step is clause 2.'}]},
               {f:{op:pick(['&','|','>','=']),a:tRandAst(1),b:tRandAst(1)},clause:'Clause 3 — it joins two wffs with a binary connective inside parentheses',
                d:[{text:'Clause 2 — negation',why:'The whole string is a parenthesized compound; negations, if any, occur inside. The final step is clause 3.'},
                   {text:'Clause 1 — sentence letter',why:'Far more than a letter — the outer parentheses come from clause 3.'}]}];
  const pk=pick(forms);
  return { setLine:'Set T — Formal Languages · Grammar & wffs',
    prompt:tGrammarBox()+`Given that its immediate parts are wffs, which clause certifies that ${wff(astRender(pk.f))} is a wff?`,
    instr:`Read the formula from the outside in: what was the LAST rule applied?`,
    mode:'mc', noKeyboard:true, choices:mc(pk.clause,pk.d),
    explain:()=>pk.clause+'.' };
}
/* tWffOrNot(ast, good): with probability .5 present `good` (answer: wff);
   otherwise mutate `good` into a non-wff by ONE of these, chosen at random
   (retry with a fresh ast if a mutation accidentally yields a wff or a duplicate):
     dropParen  — delete one random parenthesis.               why:'Parentheses come only from rule 3, always as a matching pair around a binary compound — one is missing/extra here.'
     dupOp      — double a binary connective ("• •").          why:'No rule ever places two connectives side by side — rule 3 always puts a wff on each side.'
     dropOperand— delete the letter right after a binary op.   why:'Rule 3 needs a wff on BOTH sides of the connective; the right-hand one is missing.'
     bareBinary — strip the outermost parens of a binary compound whose parts contain another binary compound, e.g. turn ((A•B)∨C) into (A•B)∨C… actually strip ALL outer parens producing an ambiguous string like A•B∨C using the two top-level ops. why:'Without rule 3\'s parentheses this string could be grouped two ways — the grammar admits no ambiguous strings (unique readability).'
     lowercase  — lowercase one sentence letter.               why:'The alphabet has only CAPITAL letters as sentence letters; no rule introduces lowercase.'
   Question: grammar box + `Is this string a wff of the language?<br>` + wff(string)
   mode:'mc', choices: [{text:'Yes — a wff'},{text:'No — not a wff'}] with correct set appropriately;
   on the non-wff side attach the mutation's why to the WRONG option ('Yes') so a mistaken
   student sees the diagnosis; instr: 'Check it against the three clauses — can the string be
   built by them, in some order, with nothing left over?'
   explain: for wffs, 'It parses: built by the rules' + (optionally show astRender of parts);
   for non-wffs, the mutation why. */
```

## 6. Activity `sem` (paste verbatim; classification is computed live, so it is always right)

```js
const T_SEM=[
  {q:`An INTERPRETATION of the propositional language is:`,
   a:`an assignment of a truth value to each sentence letter — the connectives' tables then fix every wff's value`,
   d:[{text:`a translation of the formulas into English`,why:`Translation attaches English meanings; an interpretation in the logician's sense just supplies truth values — that's all the semantics of PL needs.`},
      {text:`a proof of the formula`,why:`Proof is syntax. Interpretation is the semantic side — no rules, just truth values.`}],
   x:`This is where semantics enters: symbols get truth values, and truth for compounds is computed. Before an interpretation, a wff is pure shape.`},
  {q:`A TAUTOLOGY is a wff that is:`,
   a:`true under every interpretation — every row of its truth table`,
   d:[{text:`true under at least one interpretation`,why:`That's SATISFIABILITY — much weaker.`},
      {text:`provable without premises`,why:`That's a syntactic notion (theoremhood). Extensionally they coincide in good systems — but by DEFINITION a tautology is a semantic creature. Keeping the notions apart is the whole game here.`}],
   x:`Tautology, satisfiable, contradiction: semantic classifications, defined by truth under interpretations.`},
  {q:`"Γ ${'⊨'} A" (A is a semantic consequence of the set Γ) means:`,
   a:`every interpretation making all members of Γ true makes A true`,
   d:[{text:`A can be derived from Γ by the rules`,why:`That's Γ ⊢ A — the syntactic counterpart. ⊨ mentions no rules at all, only truth.`},
      {text:`A and Γ are all true`,why:`⊨ doesn't say anything IS true — it says truth of Γ would guarantee truth of A, across all interpretations.`}],
   x:`⊨ = preservation of truth under all interpretations; ⊢ = derivability by rules. Soundness and completeness are about how the two line up.`},
  {q:`A COUNTEREXAMPLE to the claim Γ ${'⊨'} A is:`,
   a:`an interpretation making every member of Γ true and A false`,
   d:[{text:`a proof of the negation of A`,why:`That's syntax again — a counterexample is a truth-value assignment, not a derivation.`},
      {text:`an interpretation making A false`,why:`Not enough — it must ALSO make all of Γ true, or it refutes nothing.`}],
   x:`One such interpretation kills the entailment; none existing IS the entailment.`},
  {q:`The connectives of propositional logic are TRUTH-FUNCTIONAL, meaning:`,
   a:`the truth value of a compound is completely fixed by the truth values of its parts`,
   d:[{text:`they always produce true sentences`,why:`Truth-functionality is about DEPENDENCE on parts' values, not about being true.`},
      {text:`their meaning is given by examples`,why:`Their meaning is given by truth TABLES — the function from input values to output value.`}],
   x:`Contrast English "because": knowing the truth values of P and Q does not settle "P because Q." Not truth-functional — so PL doesn't try to capture it.`},
  {q:`Truth tables give propositional logic a DECISION PROCEDURE for validity because:`,
   a:`a formula with n letters has just 2ⁿ interpretations, and the table checks every one mechanically in finitely many steps`,
   d:[{text:`they make formulas easier to read`,why:`Legibility isn't the point — GUARANTEED mechanical verdicts in finite time is what "decision procedure" means.`},
      {text:`every formula is true in some row`,why:`False (contradictions aren't) — and irrelevant to decidability.`}],
   x:`Semantic question, mechanical answer: that's decidability, and it's special — quantificational logic has no such procedure (see the Metatheory activity).`},
  {q:`The pair {${'∼'}, ${'•'}} is EXPRESSIVELY COMPLETE (all truth-functions definable). The pair {${'•'}, ${'∨'}} is not, because:`,
   a:`any formula built from • and ∨ alone is true whenever all its letters are true — so negation can never be expressed`,
   d:[{text:`two connectives are never enough`,why:`{∼, •} is a pair and suffices; indeed the Sheffer stroke suffices ALONE.`},
      {text:`∨ can already be defined from •`,why:`It can't (without ∼) — and the real obstacle is different: nothing in {•, ∨} can turn all-true inputs into false.`}],
   x:`The all-true row is a trap: • and ∨ both output true on it, so anything built from them does too — but ∼A needs false there. An invariance argument, and a tiny metatheorem.`},
  {q:`That a single connective — the Sheffer stroke, "not both" — suffices to express ALL truth-functions shows:`,
   a:`our familiar five connectives are a convenience, not a necessity; the expressive power matters, not the inventory`,
   d:[{text:`the five connectives are ambiguous`,why:`Nothing ambiguous about them — they're just definable from a smaller basis.`},
      {text:`logic needs only one truth value`,why:`Two values throughout; ONE CONNECTIVE is what's economized.`}],
   x:`∼P := (P|P); (P•Q) := ((P|Q)|(P|Q)); and the rest follow. Economy of primitives is a recurring metatheoretic theme.`},
];
function genT_sem(opts){
  if(Math.random()<0.45){
    const ast=tRandAst(2+rand(2),['A','B'].concat(Math.random()<0.5?['C']:[]));
    const L=astLetters(ast);
    if(!L.length) return genT_sem(opts);
    let t=0,n=0;
    for(const a of allAssignments(L)){ n++; if(astEval(ast,a)) t++; }
    const cls= t===n?'tautology': t===0?'contradiction':'contingent';
    const disp=wff(astRender(ast));
    const D={
      tautology:[{text:'Contingent — true under some interpretations, false under others',why:'Check again: EVERY row comes out true.'},
                 {text:'A contradiction — false under every interpretation',why:'The opposite: every row is true.'}],
      contradiction:[{text:'A tautology — true under every interpretation',why:'The opposite: every row is false.'},
                 {text:'Contingent — true under some interpretations, false under others',why:'No interpretation makes it true — that is contradiction territory.'}],
      contingent:[{text:'A tautology — true under every interpretation',why:`Not all rows: it is false under ${n-t} of the ${n} interpretations.`},
                 {text:'A contradiction — false under every interpretation',why:`Not all rows: it is true under ${t} of the ${n} interpretations.`}]};
    const A={tautology:'A tautology — true under every interpretation',
             contradiction:'A contradiction — false under every interpretation',
             contingent:'Contingent — true under some interpretations, false under others'};
    return { setLine:'Set T — Formal Languages · Syntax vs semantics',
      prompt:`Classify ${disp} semantically.`,
      instr:`Run the truth table in your head (or the scratch space): ${L.join(', ')} give ${n} interpretations. True in all = tautology; in none = contradiction; otherwise contingent.`,
      mode:'mc', noKeyboard:true, scratch:true, choices:mc(A[cls],D[cls]),
      explain:()=>`${A[cls]} — true under ${t} of the ${n} interpretations.` };
  }
  return tBankItem(T_SEM,'Set T — Formal Languages · Syntax vs semantics',
    `Syntax: shape and rules (wff, proof, ⊢). Semantics: truth under interpretations (tautology, ⊨). The discipline is keeping the two columns separate — then studying how they correspond.`);
}
```

## 7. Activity `meta` (bank verbatim — the heart of the set; wire with `tBankItem`)

```js
const T_META=[
  {q:`SOUNDNESS of a proof system says:`,
   a:`whatever the system proves is valid — if ⊢ A then ${'⊨'} A`,
   d:[{text:`whatever is valid, the system proves — if ⊨ A then ⊢ A`,why:`That's COMPLETENESS, the converse. Soundness: the system never overreaches. Completeness: it never falls short.`},
      {text:`the system's axioms are self-evident`,why:`Self-evidence is epistemology; soundness is a precise mathematical relation between ⊢ and ⊨.`},
      {text:`no proof in the system contains errors`,why:`Individual proofs being checked correctly is proof-checking; soundness is a theorem about the SYSTEM: rules preserve validity.`}],
   x:`Sound = proves only valid things. The standard proof: axioms are valid, rules preserve validity, so by induction on proof length every theorem is valid — a metatheorem proved by induction.`},
  {q:`COMPLETENESS of a proof system (in the semantic sense) says:`,
   a:`every valid formula is provable — if ${'⊨'} A then ⊢ A`,
   d:[{text:`every provable formula is valid`,why:`That's SOUNDNESS. Completeness is the harder converse: the rules are strong enough to reach EVERYTHING valid.`},
      {text:`every formula is provable or refutable`,why:`That's "negation-completeness" of a THEORY — a different notion that happens to share the name. Semantic completeness relates ⊢ to ⊨.`},
      {text:`the system contains all the connectives`,why:`Expressive completeness is yet a third notion. The three "completenesses" are the great false friends of metatheory.`}],
   x:`Soundness + completeness together: ⊢ and ⊨ pick out exactly the same formulas — the rules capture the semantics precisely. For propositional and quantificational logic, both hold.`},
  {q:`A system is CONSISTENT when:`,
   a:`for no formula A are both A and its negation provable`,
   d:[{text:`everything it proves is true`,why:`That's soundness (given an interpretation). Consistency is purely syntactic — no contradiction derivable — and is weaker.`},
      {text:`it proves at least one formula`,why:`Backwards — an inconsistent system (classically) proves EVERYTHING; consistency is about not proving too much.`}],
   x:`Consistency is the minimal virtue: an inconsistent classical system proves every formula whatsoever, so distinctions collapse.`},
  {q:`Propositional logic is DECIDABLE. That means:`,
   a:`a mechanical procedure (e.g. the truth table) settles, for any formula, in finitely many steps, whether it is valid`,
   d:[{text:`every formula of it is either true or false`,why:`Bivalence is a semantic principle; decidability is about the existence of an ALGORITHM for validity.`},
      {text:`its formulas are all provable`,why:`Only the valid ones are (soundness!). Decidability says the valid/invalid boundary is mechanically computable.`}],
   x:`2ⁿ rows, finite check, guaranteed verdict. Slow, maybe — but always terminating with an answer.`},
  {q:`Church's theorem (1936) says that quantificational (first-order) logic is:`,
   a:`undecidable — no algorithm whatsoever settles validity for arbitrary formulas`,
   d:[{text:`incomplete — some valid formulas are unprovable`,why:`No — Gödel (1930) proved first-order logic COMPLETE. Undecidable and incomplete are different properties; FOL is complete yet undecidable.`},
      {text:`inconsistent`,why:`Nothing of the sort — FOL is consistent, sound, and complete. Only the DECISION problem is unsolvable.`},
      {text:`undecidable so far — no one has yet found the algorithm`,why:`The theorem PROVES none can exist, ever. That's the force of it — an impossibility result, not a report of failure.`}],
   x:`A landmark: for quantificational logic there is provably no analogue of the truth-table method.`},
  {q:`Though undecidable, first-order validity is SEMI-decidable: a proof-search procedure will`,
   a:`eventually confirm any valid formula — but on an invalid one it may run forever, never announcing invalidity`,
   d:[{text:`eventually classify every formula correctly`,why:`That would be full decidability, which Church refutes. The asymmetry — yes-answers guaranteed, no-answers not — is exactly semi-decidability.`},
      {text:`confirm invalid formulas but not valid ones`,why:`The other way round: completeness guarantees a proof EXISTS for each valid formula, and systematic search will find it.`}],
   x:`Enumerate all proofs; if A is valid, its proof turns up. If A is invalid, silence — and you never know if it's silence-so-far or silence-forever.`},
  {q:`"Gödel proved logic is incomplete" — what's wrong with this common slogan?`,
   a:`Gödel proved first-order LOGIC complete (1930); the incompleteness theorems (1931) concern formal THEORIES of arithmetic, not the logic itself`,
   d:[{text:`nothing — that is what Gödel proved`,why:`The slogan mixes 1930 and 1931. The logic captures all VALID formulas; what no adequate theory can capture is all arithmetic TRUTHS.`},
      {text:`it was Church, not Gödel`,why:`Church proved UNDECIDABILITY of FOL — a third result again. Three theorems, three properties: complete (logic), incomplete (arithmetic theories), undecidable (FOL validity).`}],
   x:`Same man, opposite-sounding theorems, one year apart — the standard test of whether someone keeps "logic" and "theory" distinct.`},
  {q:`Gödel's FIRST incompleteness theorem, carefully stated: any formal theory that is (i) consistent, (ii) effectively axiomatized, and (iii) strong enough for basic arithmetic`,
   a:`contains a sentence of its own language that it can neither prove nor refute`,
   d:[{text:`is inconsistent`,why:`The theorem ASSUMES consistency — it concludes incompleteness, not contradiction.`},
      {text:`proves some false sentences`,why:`Nothing about proving falsehoods; the theorem finds truths (in the standard model) that the theory cannot PROVE.`},
      {text:`shows human minds surpass machines`,why:`A contested PHILOSOPHICAL gloss (Lucas, Penrose), not the theorem. The mathematics concerns formal derivability only.`}],
   x:`All three hypotheses matter: drop effectiveness and true arithmetic is a counterexample; drop arithmetic strength and complete theories exist (e.g. of dense linear orders).`},
  {q:`In the first incompleteness theorem, "the Gödel sentence is true but unprovable" means:`,
   a:`true in the standard model of arithmetic, yet not derivable in the particular theory in question`,
   d:[{text:`true in a mystical sense beyond mathematics`,why:`Nothing mystical: "true" = true of the actual natural numbers, a perfectly definite (meta-level) notion.`},
      {text:`unprovable by any means whatsoever`,why:`Only unprovable IN THAT THEORY — a stronger theory proves it (and has its own new Gödel sentence). The result is relative to each theory.`}],
   x:`Each adequate theory has its own blind spot; strengthening the theory moves the blind spot, never removes it.`},
  {q:`Gödel's SECOND incompleteness theorem: such a theory, if consistent,`,
   a:`cannot prove its own consistency`,
   d:[{text:`cannot prove anything about itself`,why:`It proves plenty about itself — arithmetized syntax is the engine of the whole proof. Its own CONSISTENCY is the specific unprovable item.`},
      {text:`is probably inconsistent`,why:`No such conclusion — the theorem just locates one more sentence (the consistency statement) outside the theory's reach.`}],
   x:`This is what wrecked Hilbert's original program: a theory can't certify its own reliability by its own lights.`},
  {q:`The COMPACTNESS theorem for first-order logic:`,
   a:`if every finite subset of a set of sentences is satisfiable, the whole set is satisfiable`,
   d:[{text:`every satisfiable set is finite`,why:`False and not the theorem — infinitely many sentences can be satisfied together; compactness says finite checkability suffices.`},
      {text:`every proof uses finitely many premises`,why:`True, and it's WHY compactness holds (via completeness) — but the theorem itself is the semantic statement about satisfiability.`}],
   x:`Strange consequences flow: a theory with arbitrarily large finite models has an infinite one; nonstandard models of arithmetic exist. Finite proofs cast long semantic shadows.`},
  {q:`"Effectively axiomatized" in the Gödel theorems means:`,
   a:`an algorithm can decide, of any given string, whether it is one of the theory's axioms (and whether a given array is a proof)`,
   d:[{text:`the axioms are few`,why:`Infinitely many axioms are fine (axiom SCHEMES are standard) — what matters is mechanical recognizability.`},
      {text:`the axioms are obviously true`,why:`Epistemic obviousness is irrelevant; the condition is computational: axiomhood must be checkable.`}],
   x:`This is the hypothesis that makes "the set of theorems is effectively enumerable" true — and it's why "true arithmetic" (all truths of the standard model) escapes the theorem: it isn't effectively axiomatizable.`},
  {q:`The Church–Turing thesis — "the effectively computable functions are exactly the Turing-computable ones" — has the status of:`,
   a:`a bridge between an informal notion and a formal one — supported by converging evidence, not the kind of claim that admits ordinary mathematical proof`,
   d:[{text:`a theorem proved by Turing`,why:`Turing proved theorems ABOUT his machines; the thesis links them to the INFORMAL idea of effective procedure, and informal notions don't figure in theorems.`},
      {text:`a mere convention of terminology`,why:`More than convention: every proposed rival analysis (recursion, λ-calculus, register machines…) provably coincides with Turing computability — striking evidence, though still not proof.`}],
   x:`It matters here because undecidability results ("NO algorithm exists") inherit their sweep from the thesis.`},
  {q:`Gensler's propositional logic — the system practiced throughout this app — is:`,
   a:`sound, complete, consistent, and decidable: everything provable is valid, everything valid is provable, no contradictions, and truth tables decide validity`,
   d:[{text:`sound and complete but undecidable`,why:`Undecidability starts with QUANTIFICATIONAL logic; the propositional fragment has its truth-table decision procedure.`},
      {text:`incomplete, by Gödel's theorem`,why:`Gödel's incompleteness needs arithmetic-strength THEORIES; propositional logic is far below the threshold, and is complete.`}],
   x:`All the good properties at once — propositional logic is metatheoretic paradise. Each step up (quantifiers, then arithmetic) surrenders one: first decidability, then (for theories) completeness.`},
  {q:`The Löwenheim–Skolem theorem: a countable set of first-order sentences with an infinite model`,
   a:`also has a countable model`,
   d:[{text:`has models only of one fixed size`,why:`The reverse — first-order theories are strikingly BAD at pinning down infinite sizes.`},
      {text:`must be inconsistent`,why:`Having models is the OPPOSITE of inconsistency.`}],
   x:`Hence "Skolem's paradox": set theory proves uncountable sets exist, yet has a countable model. Resolution: "uncountable" inside the model means no bijection IN THE MODEL — the model lacks the pairing, not the sets. A vivid lesson in object/meta relativity.`},
  {q:`Soundness and completeness are METAtheorems. That means they are:`,
   a:`proved in the metalanguage, ABOUT the system — they are not derivations inside the system itself`,
   d:[{text:`especially important theorems of the system`,why:`They aren't theorems OF the system at all — the system proves wffs; these are English-and-mathematics results about the relation ⊢/⊨.`},
      {text:`unprovable assumptions`,why:`Fully proved — just one level up, with induction on proofs (soundness) or model constructions (completeness).`}],
   x:`The whole subject of this exercise set lives one level up: the formal language and system are the object; the reasoning about them is meta.`},
  {q:`Decidability and (semantic) completeness are independent properties. First-order logic itself is the standard example of a system that is:`,
   a:`complete but undecidable — every valid formula is provable, yet no algorithm separates the valid from the invalid`,
   d:[{text:`decidable but incomplete`,why:`Backwards on both counts for FOL.`},
      {text:`complete, hence decidable`,why:`The inference fails: completeness yields only SEMI-decidability (search finds proofs of valid formulas) — nothing ever certifies invalidity in general.`}],
   x:`Completeness guarantees proofs exist; decidability demands an always-terminating method. Existence without a guaranteed finding-procedure-with-verdict: the gap between the two.`},
];
function genT_meta(opts){
  const r=tBankItem(T_META,'Set T — Formal Languages · Metatheory',
    `Keep four properties separate: SOUND (proves only valid formulas), COMPLETE (proves all of them), CONSISTENT (never both A and not-A), DECIDABLE (an algorithm settles validity). Propositional logic: all four. First-order logic: all but decidable. Arithmetic theories: completeness falls too (Gödel).`);
  r.scratch=false; return r;
}
```

## 8. Activity `reg` — Regimented English (Montague & Klima)

Two parts: a fixed conceptual bank, and templated scope items. **The regimentation scheme** (also stated in `INFO.T`): quantifier phrases are fronted in scope order, each as "every/some NOUN is such that …"; pronouns pick up the nearest fronted phrase; "it is not the case that" marks negation scope.

```js
const T_REG=[
  {q:`Montague's famous thesis, opening "English as a Formal Language" (1970):`,
   a:`there is no important theoretical difference between formal and natural languages — both can be given exact syntax and semantics`,
   d:[{text:`natural language is too vague and ambiguous for exact treatment`,why:`Precisely the orthodoxy (Frege, Russell, Tarski leaned that way) that Montague was rejecting.`},
      {text:`artificial languages are unnecessary because English already is one`,why:`Montague built elaborate formal machinery; the claim is that English CAN BE TREATED with the same exactness, not that the machinery is idle.`},
      {text:`English speakers unconsciously use predicate logic`,why:`A psychological thesis Montague never advanced — his was a mathematical claim about describability.`}],
   x:`Montague backed it up: fragments of English with mathematically exact syntax and compositional semantics. This exercise set's regimented fragment is a low-tech descendant.`},
  {q:`COMPOSITIONALITY — the principle at the heart of Montague's program — says:`,
   a:`the meaning of a complex expression is determined by the meanings of its parts and the way they are combined`,
   d:[{text:`every sentence can be decomposed into words`,why:`Trivially true and not the principle — the principle is that meaning is computed FROM the parts by the mode of combination.`},
      {text:`meanings are conventional`,why:`A different thesis. Compositionality is about how complex meanings depend on simpler ones — what makes infinite understanding from finite means possible.`}],
   x:`The same principle you use computing a wff's truth value from its parts' values — semantics tracking syntax, clause by clause.`},
  {q:`Klima's point about the medieval logicians (Buridan, Ockham, and company):`,
   a:`they had no artificial symbolism — instead they regimented Latin itself, fixing word order and scope conventions until a disciplined fragment of the natural language did a formal language's work`,
   d:[{text:`they anticipated modern symbolic notation`,why:`Almost none — a handful of abbreviations aside, their technical instrument WAS regimented Latin, which is exactly Klima's point.`},
      {text:`they distrusted formal methods`,why:`The opposite: supposition theory and their scope-idioms were rigorous formal method, executed in a natural language.`}],
   x:`Klima's reconstructions render regimented Latin with restricted variables — the approach behind this app's Medieval Term Logic workbench (unlock it via Set I). Regimentation is an old, powerful road to rigor.`},
  {q:`What does REGIMENTING a fragment of English mainly buy, compared with English at large?`,
   a:`each regimented sentence has exactly one reading — scope is fixed by the order of the fronted quantifier phrases`,
   d:[{text:`shorter sentences`,why:`Usually LONGER ("every critic is such that…"). The gain is uniqueness of reading, not brevity.`},
      {text:`new expressive power English lacked`,why:`It expresses the readings English already had — but one at a time, unmistakably.`}],
   x:`Regimented English is to English what a wff is to a formula-sketch: same content, ambiguity engineered out.`},
  {q:`And what does a fully ARTIFICIAL language (like our wff-language) add beyond regimented English?`,
   a:`a mechanically checkable syntax — whether a string is well-formed is decidable by algorithm, with no judgment calls`,
   d:[{text:`the ability to express generality`,why:`Regimented English expresses generality fine ("every man is such that…"). The artificial language's edge is machine-checkable syntax and total explicitness.`},
      {text:`truth`,why:`Neither language is "truer" — interpretations confer truth in both cases.`}],
   x:`A trade: the symbolism maximizes rigor and checkability; regimented English keeps readability and stays close to the reasoning we actually give. Montague and Klima show the gap is smaller than it looks.`},
  {q:`Gensler's Loglish — "For all x: if x is F, then x is G" — compared with this activity's regimented English — "every F is such that it is G":`,
   a:`Loglish imports the symbolism's variables into English; regimented English instead uses restricted phrases ("every F") with pronouns doing the variables' work`,
   d:[{text:`they are the same fragment`,why:`Close cousins, not twins: Loglish says "x" out loud; the regimented fragment stays variable-free, binding pronouns to fronted phrases — the medieval (and Montagovian) route.`},
      {text:`Loglish is regimented Latin`,why:`Loglish is Gensler's English-symbol hybrid; regimented Latin is the medievals' instrument that Klima reconstructs.`}],
   x:`Two halfway houses between English and symbols, meeting from opposite sides.`},
  {q:`In the donkey sentence "Every farmer who owns a donkey beats it," the pronoun "it" functions as:`,
   a:`a bound variable — it varies with the donkeys, rather than naming any one donkey`,
   d:[{text:`a name for a particular donkey`,why:`No particular donkey is in view — different farmers, different donkeys. "It" covaries: the mark of a variable, not a name.`},
      {text:`a mere filler word with no logical role`,why:`Drop it and the sentence collapses — "it" carries the binding structure that makes the sentence say what it says.`}],
   x:`Pronouns-as-variables is a central discovery of both medieval supposition theory and modern semantics — natural language has binding machinery of its own.`},
  {q:`Regimenting the donkey sentence as "some donkey is such that every farmer who owns it beats it" FAILS because:`,
   a:`the sentence doesn't say one donkey is owned-and-beaten by all — it says each farmer beats whatever donkeys he owns; the indefinite "a donkey" here has universal, not existential, force`,
   d:[{text:`"a donkey" always means "some donkey," so the regimentation is right`,why:`The classic trap: inside "every farmer who ___," the indefinite's force flips. The accepted regimentation is "every farmer is such that every donkey he owns is such that he beats it."`},
      {text:`donkeys cannot be quantified over`,why:`They quantify fine — the subtlety is which quantifier the indefinite article contributes here.`}],
   x:`Donkey anaphora is the standard demonstration that surface form misleads — and that regimentation forces the hidden structure into the open. It vexed the medievals and still powers modern semantics.`},
  {q:`"Every senator admires himself" vs "Every senator is such that he admires him." The reflexive "himself":`,
   a:`must be bound by the local subject — the regimentation with two pronouns wrongly allows "him" to point at someone else`,
   d:[{text:`means the same as "him" in all contexts`,why:`English reflexives are obligatorily locally bound; plain "him" in that position resists exactly that reading. Binding is grammar, not just interpretation.`},
      {text:`is emphatic and logically idle`,why:`It fixes WHO is admired — hardly idle. Regimentation must preserve the binding: "…is such that he admires himself."`}],
   x:`Natural language wears some of its binding theory on its sleeve — regimentation has to respect it, not flatten it.`},
  {q:`"All that glitters is not gold" — as actually intended — regiments as:`,
   a:`it is not the case that every glittering thing is such that it is gold`,
   d:[{text:`every glittering thing is such that it is not gold`,why:`That says NOTHING glittering is gold — refuted by one gold ingot. The proverb denies the universal; it doesn't assert a universal denial.`},
      {text:`some glittering thing is such that it is gold`,why:`Compatible with the intended reading, but far weaker than what the proverb conveys: the FAILURE of "all that glitters is gold."`}],
   x:`Surface order puts "not" after the verb; the intended scope puts it over the whole universal. Regimentation makes the scope visible — the whole point of the fragment.`},
  {q:`"If anyone objects, the meeting stops" vs "if everyone objects, the meeting stops": "any" differs from "every" here in that:`,
   a:`"any" takes wide scope over the conditional — one objector suffices — while "every" stays inside the if-clause`,
   d:[{text:`they are interchangeable`,why:`Then a lone objector would either stop the meeting on both readings or on neither — but plainly the "any" version triggers on one objector and the "every" version needs unanimity.`},
      {text:`"any" is just more formal`,why:`Register isn't it — the two words have systematically different scope behavior, one of Gensler's own recurring translation warnings.`}],
   x:`Regimented: "every person is such that if he objects, the meeting stops" (any) vs "if every person is such that he objects, the meeting stops" (every). The fragment forces the choice English elides.`},
  {q:`Three kinds of ambiguity: LEXICAL ("bank"), STRUCTURAL/amphiboly ("old men and women"), SCOPE ("everyone loves someone"). A formal language eliminates:`,
   a:`all three by design — one meaning per symbol, unique readability for structure, explicit operator order for scope`,
   d:[{text:`only lexical ambiguity`,why:`Parentheses (unique readability) kill amphiboly, and operator order kills scope ambiguity — the design handles all three.`},
      {text:`none — ambiguity is unavoidable in any language`,why:`Avoiding it is precisely what formal languages are FOR; the cost is distance from natural idiom, which regimented English then tries to win back.`}],
   x:`Regimented English matches the formal language on structure and scope, and controls lexical ambiguity by fixing a small technical vocabulary.`},
  {q:`In the regimented fragment, quantifier phrases are RESTRICTED ("every critic," "some book"), while the classical symbolism uses UNRESTRICTED variables plus connectives. The correspondence:`,
   a:`"every A is such that it is B" matches ${'(x)(Ax ⊃ Bx)'}, and "some A is such that it is B" matches ${'(∃x)(Ax • Bx)'} — universal pairs with if-then, existential with and`,
   d:[{text:`both quantifiers pair with if-then`,why:`"Some A is such that it is B" as (∃x)(Ax ⊃ Bx) would be true whenever anything at all fails to be A — one of the most instructive translation errors there is.`},
      {text:`both quantifiers pair with and`,why:`(x)(Ax • Bx) says everything is BOTH A and B — far stronger than "every A is B."`}],
   x:`Restricted quantification is arguably the more natural primitive — medieval logic (and Klima's reconstruction, and this app's MTL workbench) builds the restriction into the variable itself.`},
];
```

**Templated scope items** (paste verbatim):

```js
const T_SCOPE=[
  {every:'critic', some:'book',    verb:'reviewed', E:'Every critic reviewed some book.',  L:['C','B','R'], pro:['he','it']},
  {every:'student',some:'question',verb:'answered', E:'Every student answered some question.', L:['S','Q','A'], pro:['he','it']},
  {every:'detective',some:'suspect',verb:'questioned', E:'Every detective questioned some suspect.', L:['D','S','Q'], pro:['he','him']},
  {every:'reporter',some:'scandal',verb:'covered',  E:'Every reporter covered some scandal.', L:['R','S','C'], pro:['she','it']},
  {every:'child',  some:'toy',     verb:'wanted',   E:'Every child wanted some toy.', L:['C','T','W'], pro:['he','it']},
];
function tRegScope(){
  const t=pick(T_SCOPE);
  const [P,Q,V]=t.L;
  const narrow=`Every ${t.every} is such that some ${t.some} is such that ${t.pro[0]} ${t.verb} ${t.pro[1]}.`;
  const wide  =`Some ${t.some} is such that every ${t.every} is such that ${t.pro[0]} ${t.verb} ${t.pro[1]}.`;
  const fNarrow=`${qU('x')}(${P}x ${SYM.horseshoe} ${qE('y')}(${Q}y ${SYM.and} ${V}xy))`;
  const fWide  =`${qE('y')}(${Q}y ${SYM.and} ${qU('x')}(${P}x ${SYM.horseshoe} ${V}xy))`;
  const kind=pick(['reading','reading','toFormula','fromFormula']);
  const instr=`In the regimented fragment, scope = left-to-right order of the fronted phrases: whichever "is such that" comes first has the whole rest in its scope. Each pronoun picks up the nearest fronted phrase of its kind.`;
  if(kind==='reading'){
    const narrowAsked=Math.random()<0.5;
    const gloss=narrowAsked?`on the reading where the ${t.some} may DIFFER from ${t.every} to ${t.every}`
                           :`on the reading where ONE ${t.some} is ${t.verb} by all of them`;
    const ans=narrowAsked?narrow:wide, other=narrowAsked?wide:narrow;
    return { setLine:'Set T — Formal Languages · Regimented English',
      prompt:`"${t.E}"<br>Regiment this ${gloss}:`,
      instr, mode:'mc', noKeyboard:true,
      choices:mc(ans,[
        {text:other, why:narrowAsked?`Fronting "some ${t.some}" first gives it widest scope — ONE ${t.some} for all — the other reading.`:`Fronting "every ${t.every}" first lets the ${t.some} vary from ${t.every} to ${t.every} — the other reading.`},
        {text:`Every ${t.every} is such that every ${t.some} is such that ${t.pro[0]} ${t.verb} ${t.pro[1]}.`, why:`Two "every"s — but the original says SOME ${t.some}.`},
        {text:`Some ${t.every} is such that some ${t.some} is such that ${t.pro[0]} ${t.verb} ${t.pro[1]}.`, why:`The original quantifies over ALL ${t.every}s, not just some.`}]),
      explain:()=>`${ans.replace(/\.$/,'')} — the first-fronted phrase takes widest scope.` };
  }
  if(kind==='toFormula'){
    const narrowAsked=Math.random()<0.5;
    const sent=narrowAsked?narrow:wide, ans=narrowAsked?fNarrow:fWide, other=narrowAsked?fWide:fNarrow;
    return { setLine:'Set T — Formal Languages · Regimented English',
      prompt:`${P} = ${t.every} · ${Q} = ${t.some} · ${V}xy = x ${t.verb} y.<br>"${sent}"<br>symbolizes as:`,
      instr:instr+` Universal restriction pairs with ${SYM.horseshoe}; existential with ${SYM.and}.`,
      mode:'mc', noKeyboard:true,
      choices:mc(ans,[
        {text:other, why:`Quantifier order is flipped — the regimented sentence fronts ${narrowAsked?`"every ${t.every}"`:`"some ${t.some}"`} first, so that quantifier goes outermost.`},
        {text:narrowAsked?`${qU('x')}(${P}x ${SYM.and} ${qE('y')}(${Q}y ${SYM.and} ${V}xy))`:`${qE('y')}(${Q}y ${SYM.horseshoe} ${qU('x')}(${P}x ${SYM.horseshoe} ${V}xy))`,
         why:narrowAsked?`"Every" pairs with ${SYM.horseshoe}, not ${SYM.and} — with ${SYM.and} it claims everything IS a ${t.every}.`:`"Some" pairs with ${SYM.and}, not ${SYM.horseshoe} — with ${SYM.horseshoe} it is true as soon as anything fails to be a ${t.some}.`}]),
      explain:()=>`${wff(ans)} — outermost quantifier = first-fronted phrase; every↦${SYM.horseshoe}, some↦${SYM.and}.` };
  }
  // fromFormula
  const narrowAsked=Math.random()<0.5;
  const ans=narrowAsked?narrow:wide, other=narrowAsked?wide:narrow, f=narrowAsked?fNarrow:fWide;
  return { setLine:'Set T — Formal Languages · Regimented English',
    prompt:`${P} = ${t.every} · ${Q} = ${t.some} · ${V}xy = x ${t.verb} y.<br>${wff(f)}<br>reads in regimented English as:`,
    instr, mode:'mc', noKeyboard:true,
    choices:mc(ans,[{text:other,why:`Scope order is flipped — the formula's outermost quantifier is ${narrowAsked?`the universal, so "every ${t.every}" must be fronted first`:`the existential, so "some ${t.some}" must be fronted first`}.`},
      {text:t.E, why:`That's the AMBIGUOUS original — the exercise is to give the regimentation that pins down this formula's one reading.`}]),
    explain:()=>`${ans.replace(/\.$/,'')} — regimented order mirrors the formula's quantifier order exactly.` };
}
function genT_reg(opts){
  if(Math.random()<0.45) return tRegScope();
  return tBankItem(T_REG,'Set T — Formal Languages · Regimented English',
    `The fragment: front the quantifier phrases in scope order, each as "every/some … is such that …"; pronouns act as bound variables; "it is not the case that" marks negation scope. One sentence, one reading — that's the contract.`);
}
```

## 9. Verification checklist

1. Menu shows Set T inside **Sets and Metatheory**, the LAST section on the Exercise Sets screen.
2. ≥15 problems per activity, no console errors. Switch notation in Options (Gensler ↔ standard ↔ arrow) and confirm `gram`/`sem`/`reg` formulas re-render in the chosen symbols, and quantifiers follow the (x)/∀x setting.
3. `gram`: confirm non-wffs are really non-wffs (spot-check each mutation type), main-connective answers match the outermost operator, and the NOT-a-subformula option is truly absent from the formula.
4. `sem`: spot-check three classifications by hand against truth tables.
5. Wrong answers surface the authored `why` texts.
6. Reach 100 points; Mastered badge for T appears; Help → Set T renders.
7. `cp logicola.html index.html`; confirm `instructor.html` has the T title.
