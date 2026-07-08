# Akka for Financial Services

**Industry page** · Companion to `industry-financial-services.html`

---

## Hero

**Industries — Financial Services**

# Agentic AI for regulated finance.

Banking, insurance, and capital markets run on actions that are regulated, irreversible, and time-critical. The Akka Agentic AI Platform lets AI agents execute those actions — payments, credit decisions, claims, regulatory filings — with audit trails, authorization controls, and human oversight embedded within the platform.

| Stat | Label |
|---|---|
| **52** | FS orgs running in prod |
| **227** | FS AI controls supported |
| **19+** | InfoSec certifications |
| **SAFR** | Embedded within the platform |

---

## Why finance is different — from recommendation to execution

Financial institutions are deploying agents that initiate payments, submit trading orders, approve credit, file regulatory reports, and settle claims — at machine speed, without a human reviewing every action. That shift breaks control frameworks designed for human decision-making.

> "The volume and speed of agent decisions make traditional per-action oversight operationally impossible. What is needed is a governance layer that operates at the point of action."
> — SAFR — Safeguards for Agentic Finance at Runtime, v1.0 (2026)

- **Actions are irreversible.** A settled payment or executed order can't be recalled — the control has to happen *before* execution, not in a next-day audit.
- **Everything is regulated.** Prudential, conduct, operational resilience, AML/CFT, data protection, and consumer-protection obligations apply at once.
- **Systemic risk is real.** Correlated agent behaviour across institutions is a named FSB systemic vulnerability — bounded authority contains it.
- **Oversight must be provable.** Regulators expect evidence, reconstructable independent of the agent's own account — not dashboards.

---

## The platform, applied to finance — built for actions that cannot fail

- **Durable execution — No lost or double actions.** Every step survives failure, restart, and redeploy. A payment or decision runs exactly as intended, once — even when infrastructure fails mid-flight.
- **Event sourcing — Tamper-evident audit trail.** State changes are an append-only, replayable log by construction — the immutable record auditors ask for.
- **Guardrails + HITL — Control before execution.** Deterministic gates and human-in-the-loop escalation evaluate each proposed action against policy before it is applied — not after.
- **Multi-region — Residency & resilience.** Data residency and active-active operation across regions for workloads carrying regulatory and availability obligations.

---

## SAFR-aligned governance, embedded in the platform

SAFR (Safeguards for Agentic Finance at Runtime) is the emerging industry reference model for governing agents at the moment they act — developed with the Monetary Authority of Singapore's Project MindForge and BuildFin.ai, and aligned to NIST's AI Risk Management Framework. It defines a governance checkpoint between every agent decision and its execution.

The Akka Agentic AI Platform satisfies SAFR's four runtime components with capabilities embedded within the platform. Agent identity, authorization controls, the pre-execution decision gate, and the audit trail are all provided by the platform itself.

| SAFR component | What it requires | Embedded in the Akka Agentic AI Platform |
|---|---|---|
| **Governance Envelope** | A faithful record of what the agent intends and how it got there — the action trace, authenticated to origin. | A sealed, signed evidence bundle — the action and its decision trace transparently captured (including for third-party agents), bound by a reproducibility hash and authenticated to origin. |
| **Agent Identity** | Every action bound to a registered, verified agent before evaluation proceeds. | SPIFFE identity + ACLs + JWT — a stable, verifiable identity for every agent. |
| **Controls Repository** | A configurable rulebook of policy, regulation, and capability-based mandates. | The regulatory corpus and its controls — policy matrices automatically enforced against each proposed action. |
| **Disposition Engine** | A deterministic, pre-execution gate resolving each action to Deny / Escalate / Auto-Execute / Observe — re-run every step. | Enforcement of evaluations, sanitizers, guardrails, HITL escalations, HOTL escalations (halt switches), and testing gates. |
| **Audit Log** | An immutable, tamper-evident record, reconstructable independent of the agent. | Petabyte-scale logging — append-only and tamper-evident, with 10-year retention and legal hold. |

*Every SAFR component maps to a capability embedded within the Akka Agentic AI Platform.*

[Read the SAFR white paper →](https://www.mas.gov.sg/-/media/mas-media-library/development/fintech/ai-safr/safr.pdf)

---

## FINOS AI Governance Framework — implemented in the platform

FINOS AIGF is the financial-services industry's open standard for governing agentic AI, developed under the Fintech Open Source Foundation. It defines 23 agentic-AI risks and 23 mitigations — preventive and detective — and is the basis for the FINOS Common Cloud Controls adopted across banking, insurance, and capital markets.

Akka implements the FINOS mitigations as platform capabilities. The same runtime that enforces SAFR carries the preventive and detective controls FINOS specifies.

| FINOS AIGF mitigation | What it requires | Embedded in the Akka Agentic AI Platform |
|---|---|---|
| **Agent authority, least privilege** (AIR-PREV) | Each agent may act only within explicitly granted authority. | SPIFFE identity + capability-scoped mandates — an agent cannot widen its own authority. |
| **Tool-chain validation & sanitization** (AIR-PREV) | Tools and their inputs and outputs validated and sanitized before use. | Sanitizers + tool-call guardrails run in the decision path before any tool executes. |
| **Multi-agent isolation & MCP security** (AIR-PREV) | Agents isolated from one another; the MCP tool supply chain governed. | Each agent an isolated component; MCP endpoints governed and access-controlled. |
| **Model & data firewalling** (AIR-PREV) | Inbound and outbound filtering of model traffic and knowledge-base data. | Runtime guardrails filter prohibited content on the way in and out. |
| **Agent decision audit & explainability** (AIR-DET) | Every agent decision auditable and explainable after the fact. | Tamper-evident, hash-chained log + sealed, signed evidence bundles. |
| **Automated evaluation & human feedback** (AIR-DET) | Automated (LLM-as-a-judge) evaluation with a human feedback loop. | Evaluations (LLMs-as-judges) + HITL / HOTL escalation. |

[Explore the FINOS AI Governance Framework →](https://air-governance-framework.finos.org/)

---

## Controls & enforcement — how the platform enforces it

SAFR and the regulatory corpus are enforced by a two-layer control model embedded in the platform — a real-time check on every agent action, and periodic verification over time.

- **Guardrails — Block unsafe outputs.** Runtime filters catch prohibited or unsafe content before an agent can act on it.
- **Sanitizers — Strip sensitive data.** Personal and confidential data is automatically removed from what agents read and write.
- **Evaluations — Checked in real time.** Every agent action is checked inline as it happens — pass, block, or flag — so a non-compliant action never executes.
- **HITL / HOTL — People stay in control.** High-stakes actions escalate to a person for approval, and halt switches let a human stop an agent instantly.
- **Testing gates — Proven before it ships.** Scenario, replay, stress, and adversarial red-team tests gate every change before production.
- **Logging & retention — A record that holds up.** Every decision is written to a tamper-evident, hash-chained log, retained up to 10 years with legal hold.

---

## The regulatory corpus — your obligations, continuously mapped

Akka maintains a live corpus of the financial-services regulations that govern agentic AI — mapped to enforceable controls and monitored as they change. Governance runs against this corpus at the agent boundary, so obligations are enforced, not just reported.

| Stat | Label |
|---|---|
| **49** | financial-services AI regulations mapped to enforceable controls |
| **227** | AI controls governing agent actions in financial services |
| **46** | of those AI regulations carry direct financial penalties |

- **Prudential & operational resilience:** DORA, PRA SS1/23, APRA CPS 230, OSFI E-23, FSB AI in Finance
- **Model risk management:** SR 11-7, OCC Model Risk
- **Markets & conduct:** MiFID II, ESMA, IOSCO, FINRA, FCA Consumer Duty
- **Insurance:** Solvency II, NAIC AI, IAIS ICPs, EIOPA
- **AI governance for finance:** MAS FEAT, MAS AIRG, FINOS AIGF, HKMA GenAI, NY DFS 500
- **Consumer credit, privacy & data:** GDPR Art. 22, FCRA / ECOA, CFPB, GLBA

*A selection of the 49 financial-services regulations in the corpus, mapped across the EU, UK, US (federal and state), Singapore, Australia, Canada, Hong Kong, and Brazil. EU AI Act Art. 72 alone mandates 10-year retention with tamper-evident records.*

---

## Where agents act in financial services (use cases)

- **Payments orchestration & settlement** (Banking · Payments) — Initiate, sequence, and settle payments with per-action authority limits and full reconstructable traces.
- **Transaction monitoring & AML triage** (Risk · Compliance) — Surface, prioritize, and act on suspicious activity — with escalation gates before any customer-affecting action.
- **Credit assessment & underwriting** (Lending) — Real-time decisioning under model-risk governance. See Capital One — two-day batch to 200 ms.
- **Regulatory reporting & filing** (Compliance) — Assemble, validate, and file against the mapped control set, with the audit trail retained by construction.
- **Claims processing & settlement** (Insurance) — Straight-through claims with human-in-the-loop escalation on high-materiality or anomalous cases.
- **Underwriting & policy servicing** (Insurance) — Bounded agent authority over quotes, endorsements, and renewals — every action policy-checked pre-execution.
- **Fraud detection & response** (Fraud) — Detect and contain in real time; reversible actions auto-execute, irreversible ones escalate.
- **Next-best-action & servicing** (Customer) — Personalized, compliant interactions with conduct and data-protection controls enforced inline.
- **Order handling & post-trade** (Capital markets) — Agentic workflows across the trade lifecycle with deterministic containment and tamper-evident records.

---

## Proof — financial institutions already run on Akka

**Capital One · Banking / Lending — Auto-loan decisioning, from a two-day batch to real time.**
- **200 ms** to a financing decision
- **4.9×** application throughput
- **60%** lower cost per decision

Auto Navigator pre-qualifies buyers across ~4 million cars from 12,000+ dealers with no impact to their credit score — 486 applications per minute at 180–200 ms under load. [Read the story](https://akka.io/customers/capital-one)

**Manulife · Insurance — Operationalizing agentic AI on a secure, scalable foundation.**
- **Global** insurance leader
- **High-volume** trusted AI applications

Manulife selected Akka to build a high volume of trusted AI-powered applications on a secure and scalable foundation — the insurance proof point that anchors this vertical. [Read the story](https://akka.io/customers/manulife)
