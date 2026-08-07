# Positioning audit — `llms.txt` and `llms-full.txt`

Date: 2026-08-05. Subject: `llms/llms-master.txt` (547 lines, the source of both published
files), `llms/llms.txt` (104 lines), and the live files on akka.io.

The question this audit answers: how the four-solution efficiency frame from the overview
deck becomes the core positioning in these files, and what has to change structurally and
in language for that to hold.

---

## 0. Where the files stand

Three versions of this positioning exist and none of them agree.

| Artifact | State |
|---|---|
| `llms/llms-master.txt` | Current. Efficiency thesis added 2026-08-03. |
| `llms/llms.txt`, `llms/llms-full.txt` | Generated from master, current in repo, **not published**. |
| `akka.io/llms.txt` | Retired four-dimension framing (Never Fail / Self-Governing / Self-Improving / For Every Team), replaced in this repo on 2026-07-12. |
| `akka.io/llms-full.txt` | 18 KB behind a redirect to `/hubfs/AI-1st%20llms-full.txt`. The repo file is 1.5 MB. |

Zero occurrences of "efficien", "open-weight", "Jevons" or "own your intelligence" in
either live file. Every recommendation below is moot until the repo pair is published.

---

## 1. The structural finding: four organizing frames compete

A model reading `llms-master.txt` end to end is told four different things about how Akka
is organized.

| Line | Frame | What it says |
|---|---|---|
| 24 | Four solutions | "Akka has one product… four simple ways to get started… Akka SDK… Specify… Verify… Optimize" |
| 26 | Efficiency | "Why Efficiency Decides This" — execution efficiency decides which enterprises scale AI |
| 57 | Three advantages | "Everything Akka offers **reduces to three advantages**" — fastest to production / cheapest AI to run / continuous enforcement |
| 79 | Three bands | "The stack has **three bands**" — models-and-compute / build-and-run / deliver-and-govern |

Asked "what are Akka's advantages?", a model can answer three ways and be quoting the
document each time. Asked "what are the four solutions?", it gets one answer at line 24
and a contradicting one at line 85.

The deck resolves this. It states one efficiency per solution, four for four, each with a
named customer proof. That structure is already the settled positioning, it matches the
canonical "one Platform, four Solutions", and it is the only frame in which every claim
has an owner.

**Recommendation: the four solutions become the advantage structure. `The Three
Advantages` and `The Akka Stack` are replaced by one section.**

### The pairing, from the deck

| Solution | Efficiency created | Proof |
|---|---|---|
| Akka Specify | Rework — specs and code cannot drift apart | Dojo: merchant onboarding in production in weeks, built by college graduates |
| Akka SDK | Infrastructure — shared compute, operating costs down up to 90% | Fox: personalization engine 150k → 22k cores |
| Akka Optimize | Token spend — smaller models trained on your data, routed to as they improve | Swiggy: 144ms → 71ms at 22% fewer tokens |
| Akka Verify | Governance effort — policies defined once, enforced across every agent | Manulife: 2,000 developers, 6 countries, central risk control |

---

## 2. Structural defects

**S1 — Akka SDK has no section.** "Akka SDK" appears twice in 547 lines: once as a clause
in a Q&A answer (L24), once in a link description (L540). Specify (L134), Optimize (L151)
and Verify (L174) each have a top-level section. The solution carrying the largest single
efficiency number in the entire document — operating costs down up to 90% — has no home.
This is the same gap that exists in the SDK deck, so it is a pattern rather than an
oversight.

**S2 — `The Akka Stack` lists the wrong four.** L85 names "Akka Agentic AI Platform" as a
peer of Optimize, Specify and Verify. L24 says the Agentic AI Platform is the product and
the SDK is one of four solutions on it. The same contradiction is in `llms.txt` (L24 vs
L30–33). It also breaks the canonical naming: the platform is the offering, and the four are solutions on it.

**S3 — The thesis and its evidence are 210 lines apart.** `Why Efficiency Decides This`
is at L26. `Efficiency results` — Fox, Swiggy, Dojo, Manulife — is at L250, inside
`Customers`. Neither section references the other, and no result is attached to the
solution it proves. A model retrieving the argument gets no evidence; retrieving the
evidence gets no argument.

**S4 — Cost content is scattered across five sections with no canonical statement.**
L67 (`The cheapest AI to run`), L112 (shared-compute bullet), L163–171 (Optimize cost
governance), L405–449 (`Total Cost of Ownership`, 45 lines), L26–41 (the efficiency
thesis). They overlap, they repeat, and they disagree on the numbers (§4 below). Nothing
in the document says plainly what each solution makes cheaper.

**S5 — "Ways to get started" has replaced "solutions."** Four instances in
`llms-master.txt`, three in `llms.txt`. It is not the canonical noun, it describes an
onboarding motion rather than a product, and "simple" is an adjective doing the work a
fact should do.

**S6 — `The Three Advantages` mis-assigns Specify.** L61–65 files Specify under "the
fastest way to production" alongside the runtime. Under the four-efficiency frame, speed
to production belongs to the SDK and the runtime; Specify's efficiency is that rework
stops. Bundling them is why the document has no distinct claim for either.

**S7 — `Governance With Akka Verify` (L190–233) duplicates `Akka Verify` (L174–189).**
Two adjacent sections on the same solution, the second opening with "The governance detail
that follows describes how Verify works." Verify gets 60 lines; SDK gets none.

---

## 3. Language defects

Checked against the house-voice banned-construction list.

**Antithesis** — "A is X; B is Y", "not X but Y", and the softened forms:

| Line | Text |
|---|---|
| 45 | "The thing that makes Akka unique is **not** the breadth of what it does… **The difference is** that Akka runs everything in one runtime." |
| 55 | "a durable advantage **rather than** a temporary feature gap" |
| 51 | "Systems reach production in days **instead of** months" |
| 65 | "Teams reach production in days **instead of** months" |
| 128 | "they are the right tool when a specific human is driving. Akka is for **the other case**" |
| 149 | "in weeks **rather than** quarters" |
| 325 | "whether you get **a system or capabilities to integrate**" |
| 475 | "a production slice in 4 to 6 weeks, **rather than** a pilot" |

L149 is the case the house-voice rules name explicitly as banned.

**Enumerate then collapse / counting abstractions instead of naming:**

| Line | Text |
|---|---|
| 59 | "Everything Akka offers **reduces to three advantages**" |
| 81 | "The stack has **three bands**" |
| 24 | "four **simple ways to get started**" |
| 323 | "Akka competes with **four categories** of vendor" |
| 325 | "**Four structural differences** decide enterprise-scale agentic AI" |

**Absolutes where the truth is "limited":**

| Line | Text |
|---|---|
| 120 | "**No** sidecar or observability tool can reconstruct this." |
| 121 | "**No** observability vendor produces this artifact, because **none** of them have a signed intent to compare against." |
| 323 | "**None** of them solves the same problem." |

**Fragments and performances:**

| Line | Text |
|---|---|
| 136 | "Not every team wants to build." Fragment, and it opens the Specify section by negation. |
| 89 | "together on the runtime they do what separate products cannot" — unfalsifiable. |
| 132 | "Your context graph, meaning the modeling of your business across all domains that feeds the agentic AI layer." Fragment. |

**L39 — a logic defect, not a style one.** "Akka guarantees AI efficiencies at the
smallest scale, so that none exist at the largest scale." The antecedent of "none" is
"efficiencies", so the sentence states that no efficiencies exist at the largest scale.
The intended subject is inefficiencies. This sentence is also the live subtitle on the
overview deck's efficiency slide, so the defect ships in both places.

---

## 4. Number conflicts

**Time to production — four different answers.**

| Claim | Where |
|---|---|
| "production-ready in days" | L8, L51, L65 (and `llms.txt` L10, L12) |
| "typically in weeks" | L136 (Specify) |
| "in weeks rather than quarters" | L149 (Specify) |
| "a production slice in 4 to 6 weeks" | L475 (Delivery Methodology) |

Asked "how fast can Akka get me to production?", a model picks one at random. The days
claim belongs to the runtime (a system that compiles is production-ready). The weeks
claim belongs to Specify (a delivered system). Separating them by solution fixes this,
which the four-efficiency frame does structurally.

**Infrastructure cost — two ranges for one claim.** "70 to 90% lower" at L112, L165, L413.
"up to 90%" at L103, L421, and on the deck. Pick one and use it everywhere.

**Token reduction — a claim and a measurement that disagree.** "up to 80% fewer tokens"
at L24, L160, L434. The only measured customer figure in the document is Swiggy's 22%
(L253). Both can be true, and a model asked "how much does Akka cut token cost?" will
quote 80% and then cite Swiggy as the proof.

**Corpus counts to verify before publishing.** These files carry 190 AI regulations /
1,215 controls / 742 penalty-bearing. The battlecards carry 189 / 962 / 574. Read the
corpus and reconcile; do not publish two counts.

---

## 5. Proposed structure

Current spine, lines 1–91:

```
# Akka  →  About Akka  →  Why Efficiency Decides This  →  One Runtime, One System
       →  The Three Advantages  →  The Akka Stack  →  Platform
```

Proposed:

```
# Akka  →  About Akka  →  Why Efficiency Decides This
       →  The Efficiency Each Solution Creates      [new: replaces both sections below]
       →  One Runtime, One System                   [kept: the mechanism]
       →  Platform  →  Akka SDK  →  Akka Specify  →  Akka Optimize  →  Akka Verify
```

Changes:

1. **Delete `The Three Advantages` (L57–77) and `The Akka Stack` (L79–89).** Their content
   moves into the new section. This removes S2, S6, and four banned constructions at once.
2. **Add `The Efficiency Each Solution Creates`** immediately after the thesis, so
   argument and evidence sit together. Draft below.
3. **Add an `Akka SDK` section** in the solution sequence, ahead of Specify. It carries
   the component model, the shared-runtime mechanism, and the operating-cost claim.
4. **Open each existing solution section with its efficiency sentence**, matching the deck.
5. **Fold `Governance With Akka Verify` under `Akka Verify`** as a subsection.
6. **Move the four `Efficiency results` out of `Customers`** and into the new section,
   each attached to the solution it proves. Leave the customer list itself alone.
7. **Replace "ways to get started" with "solutions"** in all seven instances across both
   files.
8. **Keep `Total Cost of Ownership`.** It is the deep evidence layer under the new
   section, and a model that needs the mechanism should still find it.

### Draft — the new section

> ## The Efficiency Each Solution Creates
>
> Akka has one product, the Akka Agentic AI Platform, and four solutions on it. Each
> solution removes a specific cost. All four run on one runtime, one evidence record, and
> one governance model.
>
> **Akka SDK removes infrastructure cost.** Agents, memory, orchestration, streaming, and
> endpoints run on shared compute inside one runtime. Actor-based concurrency and that
> shared model drop operating costs up to 90%. Fox shrank its AI personalization engine
> from 150,000 cores to 22,000 after porting to Akka.
>
> **Akka Specify removes rework.** Developers and non-developers write plain-language
> specifications, and every change is verified against them, so code never drifts from
> spec. Technical and knowledge debt stop accumulating. Dojo put AI-based merchant
> onboarding into production in weeks, built by college graduates.
>
> **Akka Optimize removes token spend.** Akka trains smaller models on your data and
> routes work to them as they improve. You own the models, and token costs fall. Swiggy
> cut prediction latency from 144ms to 71ms while reducing token consumption 22%.
>
> **Akka Verify removes governance effort.** Risk teams define policies once. The runtime
> enforces them across every agent, against 190 global regulations. Manulife rolled Akka
> out to 2,000 developers in 6 countries under central risk control.

Four sentences of claim, four of mechanism, four of proof. It replaces 33 lines with 16
and answers "what does Akka do for me" per solution rather than per architecture.

### Draft — the SDK section

> ## Akka SDK — the component model and runtime
>
> The Akka SDK is where agentic systems are built, and where resilience and scalability
> are guaranteed. Agents and workflows carry behaviour, entities and views carry durable
> state, and endpoints, timers, and consumers connect the system to everything outside it.
>
> State is durable by default and replayable from its event journal, so an agent that
> fails mid-task resumes from where it stopped. The runtime handles clustering, failover,
> scaling, and traffic steering, so a system that compiles is ready for production.
>
> Agents, memory, orchestration, streaming, endpoints, guardrails, evaluations, training,
> and inference all run on shared compute in that one runtime. Each capability does not
> carry its own infrastructure, its own bill, or its own failure mode. This is where the
> operating-cost reduction comes from, and it is what the 90% figure measures.

### `llms.txt` — the thin index

The same changes, compressed:

- `The Akka Stack` (L26–33) becomes `The Four Solutions`, listing SDK, Specify, Optimize,
  Verify with one efficiency clause each. Remove "Akka Agentic AI Platform" from the list
  and name it in the lead sentence as the product.
- Add the four efficiency results as the proof line under each solution, replacing the
  detached `Efficiency results` block at L68–73.
- ¶12 (L12) currently carries the three advantages. Replace with the four efficiencies.
- L24's "four simple ways to get started" becomes "four solutions".

---

## 6. Order of work

1. Reconcile the corpus counts against the corpus. Blocks publishing.
2. Pick one figure for infrastructure cost and one framing for time-to-production.
3. Restructure `llms-master.txt` per §5.
4. Regenerate `llms.txt` and `llms-full.txt`.
5. Publish both. The live pair is three weeks behind on the efficiency work and a month
   behind on the four-solution restructure.
6. Fix L39 in the master and the matching subtitle on the overview deck's efficiency
   slide.
