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

**Raw sources / snapshots (reference):**

| File | Source | Notes |
|---|---|---|
| `llms-local-original.txt` | Local (this repo) | Original 445-line corporate-positioning superset, pre-merge. Kept as raw source. Uses the 3-dimension framing (Reliability / Risk Control / Repeatability). |
| `llms-update-approved-notes.md` | Local | Working notes on approved updates to the original local `llms.txt`. |
| `akka.io-llms.txt` | https://akka.io/llms.txt | Live concise index. Snapshot fetched 2026-07-11. |
| `akka.io-llms-full.txt` | https://akka.io/llms-full.txt | Live full overview. Snapshot fetched 2026-07-11. |

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
