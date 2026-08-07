# llms/ — Akka positioning `llms.txt` tracking

This folder tracks the Akka `llms.txt` positioning content and the live versions
published on akka.io, so divergence can be seen and reconciled deliberately.

## Files

**Canonical deliverables:**

| File | Source | Notes |
|---|---|---|
| `llms.txt` | Merged (this repo) | Thin, spec-compliant companion index — H1, blockquote, curated link sections, `## Optional`. Generated from `llms-master.txt`. All links verified 200 / no-redirect against the live site 2026-07-11. |
| `llms-master.txt` | Merged (this repo) | Full-content overview (the `llms-full.txt` equivalent). Restructured 2026-07-12 around the single-runtime differentiator, the three advantages (fastest way to production / cheapest AI to run / continuous enforcement), and the four-offering stack (Akka Agentic AI Platform, Akka Optimize, Akka Specify, Akka Verify). Retired the 4-dimension framing (Never Fail / Self-Governing / Self-Improving / For Every Team). Full prove/proof scrub applied; corpus numbers read live from the corpus on 2026-07-24: 190 regs / 1,215 controls / 742 penalty-bearing controls. Re-read from the corpus on every content edit before publishing. |
| `llms-full.txt` | Merged (this repo) + `doc.akka.io` | Generated 2026-07-13. The comprehensive machine-ingest file: the full corporate positioning (all of `llms-master.txt`) followed by the complete developer documentation content pulled from `doc.akka.io/llms-full.txt` (an index of every doc page plus the full text of each). ~1.5 MB, ~29,300 lines. Rebuild by concatenating `llms-master.txt` + a fresh `curl -sSL https://doc.akka.io/llms-full.txt`. This is the candidate for what `akka.io/llms-full.txt` should serve. |

### 2026-08-03 — the efficiency narrative

Audited all three files against the overview deck after its efficiency redesign. The
narrative was absent: zero occurrences of Jevons, "cost of intelligence", "efficient at
every scale", "own your intelligence", "open-weight" or "10x", and four of "efficienc*"
across 1.5 MB. The files were organised runtime-first, so a model asked why Akka matters
answered with architecture and never reached the market thesis.

Three changes, made in `llms-master.txt` and propagated:

1. New `## Why Efficiency Decides This` ahead of `## One Runtime, One System`. States the
   supply, demand and constraint argument with the deck's figures and sources. Efficiency
   is the subject; the single runtime stays the mechanism.
2. Akka Optimize renamed from "continuous AI intelligence" to "own your intelligence", and
   open-weight routing named — it is the first thing the deck's own definition says and it
   appeared nowhere.
3. An `Efficiency results` list under Customers: Fox 150k to 22k cores, Swiggy 144ms to
   71ms and 22% fewer tokens, Dojo onboarding in weeks by college graduates, Manulife 2,000
   developers in 6 countries. None of these figures were in any of the files.

Deliberately not done: mapping the four offerings to four costs. The three advantages are
about the runtime and were left as they are.

### 2026-08-05 — the four solutions become the positioning spine

Full audit in `positioning-audit-2026-08.md`. The file had four competing organizing
frames: four offerings (L24), efficiency (L26), "three advantages" (L57), "three bands"
(L79). A model asked for Akka's advantages could answer three ways and be quoting the
document each time.

Structural changes:

1. **`The Three Advantages` and `The Akka Stack` deleted.** Replaced by one section,
   `The Efficiency Each Solution Creates`, placed directly after the efficiency thesis so
   argument and evidence sit together. Each solution is introduced by the cost it removes:
   SDK/infrastructure, Specify/rework, Optimize/token spend, Verify/governance effort.
2. **`Akka SDK` section added.** "Akka SDK" previously appeared twice in 547 lines and had
   no section, while Specify, Optimize and Verify each had one. It carries the largest
   efficiency number in the document (operating costs up to 90%).
3. **The four efficiency results moved out of `Customers`** and attached to the solution
   each one proves: Fox/SDK, Dojo/Specify, Swiggy/Optimize, Manulife/Verify.
4. **`Governance With Akka Verify` folded under `Akka Verify`** as a subsection.
5. **Product model corrected.** One *offering* (the Akka Agentic AI Platform); four
   *solutions* on it, each usable independently, all delivered through the platform.
   "Ways to get started" removed from all seven instances across both files.

Numbers reconciled:

- **Corpus read from source 2026-08-05: 190 regulations, 1,230 controls, 742
  penalty-bearing.** Counted across 201 `controls*.yaml` files in
  `explainability/framework/regulations`. The published 1,215 was stale by 15 controls;
  penalty-bearing matched exactly. The battlecards' 189 / 962 / 574 is a separate,
  older count and is **not** reconciled.
- **Infrastructure cost standardised on "up to 90%"** (was "70 to 90%" in three places).
  Matches the deck and states a ceiling.
- **Time to production split by solution.** The days claim belonged to the runtime and now
  reads "a system that compiles is ready for production"; the weeks claim belongs to
  Specify. Four conflicting answers became two scoped ones.

Language: eight antitheses, five counting-abstraction constructions, and three absolutes
removed. `Akka guarantees AI efficiencies … so that none exist at the largest scale` had
"efficiencies" as the antecedent of "none" and stated the opposite of its intent; fixed in
both files. **The same sentence is still the live subtitle on the overview deck's
efficiency slide.**

Still unreconciled, flagged rather than changed: "up to 80% fewer tokens" sits alongside
Swiggy's measured 22%. Both are defensible, and a model asked "how much does Akka cut
token cost?" will quote 80% and then cite Swiggy as the proof.

**Live snapshots (the before-picture, kept until publish):**

| File | Source | Notes |
|---|---|---|
| `akka.io-llms.txt` | https://akka.io/llms.txt | Live concise index, fetched 2026-07-11. Re-verified byte-identical to live on 2026-08-05, so live has not moved since. |
| `akka.io-llms-full.txt` | https://akka.io/llms-full.txt | Live full overview, fetched 2026-07-11. Same re-verification. |

Both are the diff baseline for the pending publish. Refresh them from live with the curl
commands at the end of this file once the new pair ships.

**Publishing is out of scope for this repo.** The live `akka.io/llms.txt` and
`llms-full.txt` ship through a separate path, so a gap between the files here and what the
site serves is expected and is not a defect to re-report. This repo owns the content;
something else owns the deploy.

`llms-local-original.txt` (the 445-line pre-merge superset, 3-dimension framing) and
`llms-update-approved-notes.md` were deleted 2026-08-05, superseded by `llms-master.txt`.
Both are recoverable from git at 67532e3.

`akka.io/llms-all.txt` does not exist (404) as of 2026-07-11.

## Link inspection (2026-07-11)

Deep link check against the redone akka.io. Fixed in the merged pair; **still broken on the live published files** (flag for later):

- Tubi story: old long slug 404s → use `/customer-stories/tubi`.
- Llaama story: old long slug 404s → use `/customer-stories/llaama`.
- DeductiveAI story: old long slug 301-redirects → use `/customer-stories/deductive-ai`.
- `doc.akka.io/reference/release-notes/index.html` 404s → use `/reference/release-notes.html` (bug present in `llms-local-original.txt`).
- `akka.io/llms-full.txt` is served via a HubSpot redirect to `/hubfs/AI-1st%20llms-full.txt` — fragile path for a machine-read file.

## Known divergence (local vs. live), as of 2026-07-11

Not yet reconciled — captured here for a later decision:

1. **Framing model.** Local uses 3 dimensions (Reliability, Risk Control,
   Repeatability) and barriers (Production Gap, Liability, Specialist Trap).
   Web uses 4 dimensions (Never Fail, Self-Governing, Self-Improving, For Every
   Team) and barriers (Brittleness, Liability, Unevenness).
2. **Install commands conflict.** Local: `akka/ai-marketplace`,
   `akka-specify@ai-marketplace`, `/akka-specify:setup`. Web: `akka/claude-marketplace`,
   `akka@claude-marketplace`, `/akka:setup`. One is stale.
3. **Service tiers.** Local has 5 (Starter, Sandbox, Day 2 Ops, Business
   Continuity, Sovereign Cloud); web full has 4 (Fast Prod, Day 2 Ops, Business
   Continuity, Sovereign Cloud).
4. **Local-only sections:** User/Buying Personas, Governance That Scales (7
   runtime binding classes G/H/W/P/E/B/K), Industry Postures, full Competitive
   Landscape + table, Total Cost of Ownership, Delivery Methodology, Company,
   Partners & Ecosystem, Heritage.
5. **Web-only content:** dedicated "Akka Specify" section (six input specs),
   "governed service identity" bullet, desktop-agent/copilot exclusion, and the
   "Which Akka is this?" Lightbend disambiguation block.

## Refreshing the web snapshots

```
curl -sSL https://akka.io/llms.txt      -o llms/akka.io-llms.txt
curl -sSL https://akka.io/llms-full.txt -o llms/akka.io-llms-full.txt
```
