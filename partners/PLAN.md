# Partners — Applying the Case-Study Technique to akka.io/partners

## The problem with the current page

`https://akka.io/partners` today is a **directory, not a narrative**:

- Hero claim ("our partners are experts in agentic and distributed systems") with **zero proof**.
- A flat 14-logo card grid (AWS, GCP, Azure, Carahsoft, SHI, Infosys, VirtusLab, Scalac,
  Improving, AVOWS, Twoday, Far Networks, Peperina…), each with a one-sentence blurb and a
  "Learn More" link off-site.
- **No categories, no filtering, no tiers.**
- **No partner stories, testimonials, metrics, or outcomes.**
- **No "Become a Partner" CTA.**

Customers (Verizon, Renault, John Deere, Swiggy…) are named elsewhere on the site but are
**never connected to the partners who delivered them.** That disconnect is the whole opportunity.

## The core move

Our customer case studies work because they are **numbers-first narratives on a fixed skeleton**.
Apply the same machine to partners by reframing the partner from a *logo* into a
**proven delivery vehicle**:

> A customer story says "Company X achieved outcome Y with Akka."
> A partner story says "**Partner P + Akka** delivered outcome Y for real customers."

The connective tissue: **partner stories reuse the customer proof we already have.** Many of the
17 existing case studies were delivered with a partner. The same Speed / Cost / Scale numbers that
power `verizon.html` become the joint-delivery proof on the VirtusLab (or whoever) partner story.
Customer stories ↔ partner stories become a linked web of reinforcing proof.

## Two deliverables (mirrors `case-studies/`)

### 1. Partner gallery — upgrade the flat grid

Model on `case-studies/index.html`. Same dark hero, same proof-carrying cards, but:

- **Group partners by type** with `.sect` headings the current page lacks:
  *Cloud Platforms · System Integrators & Consultancies · Government & Resellers.*
- Each card carries **one joint-win stat** (e.g. "7.5× order throughput, delivered with X"),
  not just a logo + blurb.
- Add the missing **"Become a Partner" CTA band** at the bottom.

### 2. Individual partner story pages — one long-form page per strategic partner

Reuse `case-study.css` verbatim (dark hero → 820px white body → dark CTA). Adapt the fixed
8-section customer arc into a **partner arc**:

| # | Customer arc | Partner arc |
|---|---|---|
| 1 | Headline (outcome, gold `.hl`) | Joint headline — the outcome the partnership delivered |
| 2 | `Industry · Offering` meta | `Partner type · Region/Practice · Certified engineers` meta |
| 3 | Answer-first `.lead` capsule (40–60 wds, AEO-extractable) | Same — carries the joint headline numbers |
| 4 | ROI Scorecard: **Speed / Cost / Scale** | **Same three cards** — this is what the partner *delivered*, reused from the customer study |
| 5 | The challenge | What the partner does / the customer problem they solve |
| 6 | Why Akka (→ a platform pillar) | Why Akka + this partner together (→ same pillar) |
| 7 | The results (quantified) | The joint result — a real customer win, quantified |
| 8 | The agentic opportunity (2 paths) | The joint agentic opportunity + how to engage this partner |
|   | CTA: "Talk to Akka" | CTA: "Work with this partner" / "Become a partner" |

Keep every case-study rule: numbers over adjectives, the escalating data crescendo
(capsule → scorecard → `.pullstat`), one gold accent, CSS-only motion, no dates, no Sources.

## Why this specifically fixes what's broken

| Current gap (from page audit) | Fixed by |
|---|---|
| No proof behind the "experts" claim | Joint-win scorecard + `.pullstat` on every story |
| Flat, uncategorized logo grid | Typed `.sect` gallery groups |
| No partner stories / testimonials | Long-form partner story pages |
| No metrics or outcomes | Reused Speed/Cost/Scale from customer studies |
| No "Become a Partner" path | Dedicated CTA band on gallery + story pages |
| Partners disconnected from customer wins | Story pages cite the actual customer outcome |

## Build integration (already-solved plumbing)

Plugs straight into the existing pipeline — no new machinery:

1. Author `partners/<name>.html` + `.md` linking `../case-studies/case-study.css`
   (or a copied `partners.css` if we want divergence).
2. Add a `transform_dir('partners')` call in `build-all.py` → auto-generates the
   HubSpot fragment via `sales-presentation/builder/hubspot.py`.
3. Register the gallery in `build-index.py` as one landing-page entry
   (`{"link": "partners/", "title": "Akka Partner Stories", "sub": "PARTNERS"}`).
4. Pre-commit hook builds everything.

## Open question before building (needs real data — do NOT fabricate)

The technique's power depends on the **partner ↔ customer mapping**: which partner actually
delivered which customer win. That is not derivable from the repo and must come from Tyler /
the partner team. Pick 1–2 strategic partners with a known customer win to build the reference
implementation first (e.g. an SI that delivered one of the 17 existing case studies).
