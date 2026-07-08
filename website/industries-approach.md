# Industry Pages — Approach & Financial-Services-First Outline

**Prepared:** 2026-07-08 · **Scope:** akka.io `/industries/` architecture, modeled on Palantir, leading with Financial Services.

---

## 0. Honest note on the current footer list

The Industries column in the mega-footer (Financial Services, Insurance, Telco, Retail, Manufacturing, Media, Public Sector) was **inferred from the customer logos** (Manulife → insurance, Verizon → telco, John Deere → manufacturing, Tubi → media, Swiggy/Walmart → retail). It is a plausible placeholder, **not** a map of where Akka has real depth, assets, or regulatory corpus. This doc replaces guesswork with an evidence-led approach.

**Evidence we should build the list around:**
- **Financial services is the deepest vertical** — 52 FS organizations worldwide, across multiple FS sub-segments (banking, insurance, capital markets, payments).
- **The regulatory corpus is heavily financial services** — the compliance/governance content we already own skews FS.
- **SAFR alignment** — Akka's runtime substrate inherently satisfies the SAFR agentic-finance governance model (see §4). No other vertical has an equivalent ready-made governance story.

→ **Recommendation:** don't ship 7 equal verticals. Ship **Financial Services as the flagship**, fully built, and treat the rest as a template rollout in priority order (§5).

---

## 1. What Palantir actually does (teardown)

Palantir runs a **three-layer** industry system — this is the SEO/authority engine, not a single page:

| Layer | URL pattern | Count (approx) | Purpose |
|---|---|---|---|
| **Industry offering** | `/offerings/<industry>/` | ~30 | The vertical landing page. Energy, Financial Services, Insurance, Life Sciences, Defense, Retail, Automotive/Mobility, Telecommunications, Consumer Goods, Utilities, Semiconductors, Health, Construction, Food & Beverage, Intelligence, Crypto, AML, Supply Chain… |
| **Sub-solutions** | `/offerings/<industry>/<solution>/` | many | Focused plays inside a vertical, e.g. `financial-services/applied-customer-intelligence`, `financial-services/government`, `anti-money-laundering`. |
| **Impact / use-case pages** | `/impact/<slug>/` | ~35+ | The keyword-rich outcome library — a mix of **named customers** (`swiss-re`, `sompo`, `axel-springer`) and **generic outcomes** (`transaction-monitoring`, `bank-digitization`, `compliance-acceleration`, `next-best-offer`, `customer-retention`, `pricing-optimization`). |

**The takeaway:** Palantir's SEO does not come from 30 landing pages — it comes from the **~35+ `/impact/` outcome pages**, each targeting a specific problem keyword and internally linked from the relevant industry page. The industry page is the hub; the impact pages are the spokes.

**Recurring page pattern per industry:** mission/why-this-matters narrative → the platform applied to this sector → 2–4 named use cases → outcome metrics → CTA (demo / contact). Consistent template, sector-specific content.

---

## 2. Proposed Akka IA (mirror the hub-and-spoke model)

```
/industries/                         ← index of all verticals
/industries/financial-services/      ← FLAGSHIP hub page
    ├─ use-case spokes (the SEO engine — see §3)
    └─ links to /customers/<name> proof + /compare where relevant
/industries/<next-vertical>/         ← templated rollout (§5)
```

Two choices to make deliberately:
- **Spokes = new `/use-cases/` pages, or reuse `/customers/<name>`?** Palantir does both. Recommendation: reuse existing customer stories as named proof, and add a small set of **generic outcome pages** (the real SEO win) only where we have substance to say. Don't mint empty outcome pages.
- **This needs the new template** (the blueprints-style build you flagged). The template is: hero + narrative + capability mapping + proof + use-case grid + governance block + CTA.

---

## 3. Financial Services hub page — detailed outline

**URL:** `/industries/financial-services/` · **Build first, fully.**

1. **Hero** — "The agentic AI platform for regulated finance." One line on the substrate: durable, auditable, governable by construction.
2. **Proof bar (above the fold)** — *52 financial-services organizations worldwide* · banking · insurance · capital markets · payments. (Anonymized count is a strong, honest headline even before named logos.)
3. **Why finance is different** — agents that *act* (initiate payments, submit orders, approve credit, file reports, settle claims) not just recommend. Regulated, irreversible, high-velocity. This is the SAFR thesis, in our words.
4. **Akka applied to finance** — map platform capabilities to FS needs:
   - Durable execution → no lost/duplicated transactions under failure
   - Event sourcing → complete, tamper-evident audit trail (see §4)
   - Guardrails + human-in-the-loop → pre-execution control
   - Multi-region → data residency / resilience for regulated workloads
5. **Governance: built-in SAFR alignment** — the differentiator (§4). A reusable content block.
6. **Use-case spokes** (the SEO engine — each a short section now, its own page later):
   - Transaction monitoring / AML triage
   - Credit assessment & underwriting
   - Payments orchestration & settlement
   - Compliance reporting & regulatory filing
   - Claims processing (insurance)
   - Fraud detection & response
   - Customer service / next-best-action
7. **Named proof** — Manulife (already in customers), plus other FS logos from the 52 as they clear approval.
8. **Regulatory corpus callout** — surface that we maintain a finance-weighted regulatory/governance knowledge base (differentiator vs generic agent platforms).
9. **CTA** — talk to a solutions architect / see the governance demo.

---

## 4. SAFR alignment — the FS differentiator (with capability mapping)

**SAFR = Safeguards for Agentic Finance at Runtime** (industry reference model, v1.0 July 2026; developed with MAS/Singapore's Project MindForge, BuildFin.ai, IMDA MGF; aligned to NIST AI RMF). It defines a **runtime governance checkpoint between every agent decision and its execution**, via four components + a "Governance Envelope."

Akka's substrate provides the primitives each SAFR component requires — this is an architectural fit, not a product claim:

| SAFR component | What it requires | Akka primitive that provides it |
|---|---|---|
| **Governance Envelope** (action + action trace + context, authenticated to origin) | A structured, faithful record of what the agent intends and *how it got there* | Durable execution + event-sourced journal capture the full action trace by construction |
| **Agent Identity** (verified against a registry before evaluation) | Stable, verifiable agent identity | Addressable components/entities + ACLs + JWT auth |
| **Controls Repository** (configurable rulebook; capability-based, bounded mandates) | Durable, machine-readable authority scoped per agent | State entities hold the mandate/rulebook; deterministic evaluation in workflows |
| **Disposition Engine** (deterministic eval → Deny / Escalate / Auto-Execute / Observe, per action) | A pre-execution decision gate, re-run each step | Akka Workflows (durable, deterministic orchestration) + declarative effects — the action is *proposed* and only applied after the gate; human-in-the-loop escalation via workflow pause/timers |
| **Audit Log** (immutable, append-only, tamper-evident, reconstructable independent of the agent) | An authoritative, unforgeable record of every decision | **Event Sourcing** — literally an append-only, tamper-evident log of every state change. Exact substrate match. |

**Honest framing (do not overclaim):** SAFR is a *reference model*, not a certification. Akka does not ship "SAFR-in-a-box." The claim is: **Akka gives you the infrastructure-grade primitives SAFR calls for — audit trail, bounded authority, deterministic pre-execution gating, per-step re-evaluation — so implementing SAFR on Akka is natural rather than bolted-on.** That is a substrate advantage generic agent frameworks (which lack durable execution + event sourcing) cannot match.

→ This block is reusable: SAFR is FS-specific, but the underlying "governable by construction" story generalizes to any regulated vertical (insurance, healthcare, public sector).

---

## 5. Templated rollout order (after FS)

Prioritize by evidence (logos + assets), not coverage:

1. **Financial Services** — flagship, full build (52 orgs, regulatory corpus, SAFR).
2. **Insurance** — Manulife; SAFR/claims-settlement story carries over. (Could sit *under* FS or stand alone — decide based on how we count the 52.)
3. **Telecommunications** — Verizon.
4. **Manufacturing / Automotive** — John Deere, Renault.
5. **Media & Streaming** — Tubi.
6. **Retail & E-commerce** — Walmart, Swiggy.
7. **Public Sector / Research** — CERN (and a governance angle via SAFR-adjacent frameworks).

Verticals without a logo or real asset **should not get a page yet** — an empty industry page is negative SEO and a weak sales artifact.

---

## Open questions for sign-off

- **Spokes:** mint generic `/use-cases/` outcome pages (Palantir's SEO engine), or start by reusing `/customers/`? (Rec: reuse first, add outcome pages where we have substance.)
- **Insurance:** its own vertical, or a sub-solution under Financial Services? (Depends how the "52 FS orgs" are segmented.)
- **SAFR paper:** can we cite/link it publicly and state alignment on the FS page, or is that gated pending review?
- **Template:** confirm this reuses the blueprints-style template build (shared with the docs blueprints work in pm-todos).
```
