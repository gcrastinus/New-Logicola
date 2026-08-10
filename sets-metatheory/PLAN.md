# Sets and Metatheory — plan for two new LogiCola exercise sets

New section at the very bottom of the Exercise Sets menu, titled **Sets and Metatheory**, holding two new sets that use the two free set IDs:

- **Set S — Sets** (elementary set theory; not in Gensler; standard philosophy-course material through Cantor)
- **Set T — Formal Languages & Metatheory** (rudiments of formal languages, syntax vs semantics, the big metatheorems, plus one activity on regimented English à la Montague and Klima)

Both sets use the app's existing machinery unchanged: 100-point completion, level-based scoring, MC/type modes, the `mc()` distractor helper with per-distractor `why` diagnoses, the activity log, and the Help system.

## Set S — Sets (six activities, key `sMode`)

| Activity | Content | Mode |
|---|---|---|
| `basics` | Membership vs subset, ∈/∉/⊆, ∅ vs {∅}, roster ↔ set-builder, extensionality, nested sets, cardinality of small sets | MC / type |
| `ops` | Compute ∪ ∩ − ′ ∆ on displayed finite sets (universe shown for complement) | MC / type |
| `power` | Subsets, proper subsets, P(A) listed in full, \|P(A)\| = 2^\|A\|, A ∈ P(B) iff A ⊆ B | MC / type |
| `pairs` | Ordered pairs, A×B computed, \|A×B\|, (a,b) ≠ {a,b}, inclusion–exclusion counting | MC / type |
| `laws` | True/false over set identities and subset equivalences (De Morgan, distribution, A⊆B iff A∩B=A, …), each with an explanation | TF |
| `inf` | Infinity: bijections/equinumerosity, Hilbert's Hotel, countability of ℤ and ℚ, Cantor's diagonal argument, Cantor's theorem, ℵ₀, continuum hypothesis, Russell's paradox | MC |

Typed answers are set literals; a canonicalizer (written, in the ticket) accepts any member order, optional spaces, `∅` or `{}`, and nested sets/pairs, and the diagnoser names the operation the student actually computed ("that's A ∪ B — the question asks for A ∩ B").

## Set T — Formal Languages & Metatheory (five activities, key `tMode`)

| Activity | Content | Mode |
|---|---|---|
| `lang` | Use vs mention, object language vs metalanguage, metavariables, type vs token, what a formal language is (alphabet + formation rules) | MC |
| `gram` | A displayed 3-clause grammar; classify strings as wff/non-wff (non-wffs made by principled mutations, each with a diagnosis); main connective; subformulas; which clause certifies a wff; unique readability; the parenthesis-balance induction proof | MC |
| `sem` | Interpretations, tautology/contingent/contradiction (computed live from the app's own evaluator), ⊨ vs ⊢, counterexamples, truth-functionality, expressive completeness (harder items) | MC |
| `meta` | Soundness, completeness, consistency, decidability (PL decidable, FOL undecidable but semi-decidable), compactness, Gödel 1930 completeness vs 1931 incompleteness — distractors built from the classic confusions, each diagnosed | MC |
| `reg` | Regimented English (Montague, Klima): fixed scope-marking fragment ("Every A is such that some B is such that …"), scope disambiguation, pronouns as bound variables, donkey sentences, restricted vs unrestricted quantifiers, and conceptual items on natural vs artificial languages | MC |

The `reg` activity is deliberately one option among five — the set's core is formal languages; regimentation appears as a considered alternative, with explicit ties to Gensler's Loglish (already in the app) and to the app's Medieval Term Logic workbench (Klima-style restricted variables).

## Division of labor

- **TASK-GROK.md** — Set S plus all shared wiring (new menu group rendered at the very bottom, registries, instructor.html titles). Computational, fully specified; all quality-critical code (set-literal canonicalizer, diagnosers) and all item banks are written out verbatim in the ticket.
- **TASK-OPUS.md** — Set T. Subtler assembly (strict wff checker, mutation engine, live semantic classification, templated scope items); every conceptual item bank (lang/meta/reg and the fixed gram/sem items) is authored verbatim in the ticket, including distractor `why` texts. The ticket forbids rewording authored correct answers without flagging.

The tickets are order-independent (each creates the menu group only if the other hasn't) and self-contained — paste one file per model, no other context needed.

## After the models run

Have me review the diffs: the failure modes to expect are (1) silently "improving" authored wording and introducing philosophical errors, (2) canonicalizer edge cases (`{}` inside a set, pair vs set confusion), (3) forgetting `index.html` is a byte-for-byte copy of `logicola.html`, (4) missing the instructor.html `SET_TITLES` addition.
