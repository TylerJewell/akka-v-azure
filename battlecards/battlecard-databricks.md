# Akka vs. Databricks (Mosaic AI / Agent Bricks)

**A comparison for teams building agentic AI — June 2026**

> **Databricks is a lakehouse with an agent layer attached — the data, feature, and model tier, not a governed agentic runtime.** Mosaic AI and Agent Bricks build agents that read your Lakehouse and run on stateless serving endpoints; their governance is *data* governance (Unity Catalog lineage, access control, and audit), not *runtime* EU AI Act enforcement. Akka is the governed agentic runtime: durable in-memory agent state, a six-nines platform SLA, and inline policy enforcement. The two fit together — Akka complements the lakehouse beneath it.

---

## At a Glance

| Dimension | Databricks (Mosaic AI / Agent Bricks) | Akka |
|---|---|---|
| What it is | A data intelligence platform (lakehouse) with an agent layer — Agent Bricks, Mosaic AI Agent Framework, Model Serving, Vector Search, Genie | A full-stack agentic systems platform — agents, orchestration, durable memory, streaming, APIs, and runtime governance on one runtime |
| Primary role | The data, feature, and model tier agents read from | The runtime agents *run on* |
| Agent state | Stateless serving endpoints; session/long-term memory externalized to Lakebase (managed Postgres), re-read each turn | Durable sharded in-memory state — 4ms reads / sub-10ms writes, replayable from the event journal |
| Availability SLA | 99.9% control-plane SLA; Model Serving rides the Databricks SLA, no published six-nines agent-tier number | 99.9999% across the entire platform, contractual, backed by indemnities |
| HA / DR | Customer-architected; typically active-passive; RTO < 1h, RPO < 15min for critical workloads; Model Serving endpoints not replicated in managed DR | Active-active HA/DR; sub-1-minute RTO; zero-byte RPO — Akka owns it |
| Governance | Data governance: Unity Catalog lineage, access control, audit; DAGF/DASF frameworks and guidance | Runtime EU AI Act enforcement: inline guardrails, hash-chained evidence, pre-deployment classification, sealed posture, Akka Verify |
| Coupling | Agents bound to the Lakehouse, Unity Catalog, and DBU-metered serving | Deploy anywhere — Akka cloud, your VPC, your Kubernetes, on-prem, sovereign cloud; portable specs |
| Cost model | DBU consumption metering (per-token + provisioned-throughput DBUs), scales with load | Shared compute on one runtime; up to 90% lower infrastructure for the same workload; fixed annual fee |
| Maturity | Agent Bricks beta Jun 2025; Supervisor Agent GA Feb 2026; rapidly evolving | 18 years, 100,000+ production deployments, 52 banks |

---

## A Data Platform With Agents, Not a Governed Agentic Runtime

Databricks is a lakehouse — Delta Lake storage, Unity Catalog governance, and Mosaic AI on top — with an agent layer attached. Agent Bricks, the Mosaic AI Agent Framework, Vector Search, and Genie build agents that read your governed data; Model Serving runs them. That is the data, feature, and model tier. It is not a runtime engineered to *run* an agentic system with guarantees.

The line is structural, not a matter of features. A lakehouse optimizes storage, retrieval, lineage, and model access. An agentic runtime optimizes durable execution, in-memory state, failover, and inline policy enforcement on running processes. Databricks delivers the first and attaches agents to it; Akka is the second. This is the wedge: a data platform with agents attached versus a governed agentic runtime.

| Capability | Databricks | Akka |
|---|---|---|
| Lakehouse / feature store / model serving | Yes — core strength | Not Akka's layer (complement) |
| Vector search / semantic retrieval | Yes — Mosaic AI Vector Search | Not Akka's layer (complement) |
| Native durable agents with in-memory state | Stateless endpoints; state externalized to Postgres | Built in — durable sharded in-memory |
| Six-nines platform availability SLA | Not published for the agent tier | 99.9999%, contractual |
| Active-active HA/DR, sub-1-min RTO, zero RPO | Customer-architected; serving endpoints excluded from managed DR | Built in — Akka owns it |
| Inline runtime EU AI Act enforcement | Data governance + frameworks/guidance | Built in — aspect-woven |

---

## Reliability: Agent State and the SLA That Covers It

Akka publishes a **99.9999%** availability SLA across the entire platform — contractual and backed by indemnities — with **sub-1-minute RTO**, **zero-byte RPO**, and **active-active HA/DR** that Akka owns and operates 24/7.

Databricks publishes a **99.9% control-plane SLA**; Model Serving is "backed by the Databricks SLA," but Databricks does not publish a six-nines availability number for the agent-serving tier. Disaster recovery on Databricks is **customer-architected** — the documented pattern is **active-passive**, with active-active described as "the most complex strategy." Databricks' own DR targets for critical workloads are **RTO under 1 hour and RPO under 15 minutes**, and **Model Serving endpoints are not replicated in Databricks managed disaster recovery** — the layer agents run on is explicitly outside managed failover.

The deeper difference is agent state. Databricks agent runtimes are **stateless by design**: "state cannot live in local memory and must be externalized to a durable store," so the **entire session history is retrieved from a central database (Lakebase managed Postgres) at the start of every turn.** Akka holds agent state in **durable sharded in-memory storage** — 4ms reads, sub-10ms writes, replayable from its event journal — so an agent's working memory survives failover without a per-turn database round trip.

| Metric | Databricks | Akka |
|---|---|---|
| Availability SLA | 99.9% control plane; no published agent-tier six-nines | 99.9999% — entire platform |
| Allowed downtime / year | ~8.7 hours (at 99.9%) | ~31 seconds |
| RTO | < 1 hour (customer-architected, critical workloads) | Sub-1 minute |
| RPO | < 15 minutes (customer-architected) | Zero byte |
| HA/DR posture | Typically active-passive; serving endpoints not in managed DR | Active-active, Akka-owned |
| Agent state | Stateless; externalized to Postgres, re-read each turn | Durable in-memory, 4ms / sub-10ms |

---

## Up to 90% Cheaper to Operate

AI systems built with Akka are **up to 90% cheaper to operate** than Python-based systems — a function of the infrastructure required to run the same agentic transaction volume, not list price. The drivers are actor-based concurrency (**~10 trillion tokens / core / year** versus ~2 trillion for comparable solutions; **~80% less compute** than Python-based frameworks), shared compute, and micro-checkpointing. Manulife reported up to **300% more concurrency** and **30–50% faster processing** after porting Python-based systems to Akka.

Databricks bills on **DBU consumption** — pay-per-token for Foundation Model APIs plus provisioned-throughput DBUs for hosted models and serving endpoints — so the meter moves with load, and the lakehouse, Vector Search, and serving each consume separately. Akka runs orchestration, agents, memory, streaming, APIs, observability, and governance on **one shared-compute runtime** for a **fixed annual fee** finance can forecast.

*Infrastructure footprint (compute to run the workload) is a separate dimension from list price; this section compares footprint.*

---

## Governance: Data Governance vs. Runtime EU AI Act Enforcement

Databricks' governance is **data governance**. Unity Catalog enforces access control, captures column-level lineage, logs activity for audit, and now governs agents, tools, and models as catalog assets with on-behalf-of access controls. Databricks also publishes responsible-AI guidance — the AI Governance Framework (5 pillars, 43 considerations) and the AI Security Framework — and states it is committed to EU AI Act compliance. These are governance *of the data and access*, plus frameworks and best practices. They are not inline enforcement on the running agent.

The EU AI Act expects enforcement at the runtime: prohibited practices blocked as they occur, immutable records witnessed as decisions happen, human override of running processes, pre-deployment classification, and a retained evidence trail. Akka embeds this in the runtime — inline guardrails, policies, LLMs-as-a-judge, and sanitizers; **hash-chained immutable evidence**; HITL/HOTL control; **pre-deployment classification against 189 regulations and 962 controls** (574 of which carry a financial penalty); multi-persona sign-offs; a sealed **Governance Posture Package**; and **Akka Verify**, which proves conformance from the running system.

### The penalties are enforceable now

| Violation | Maximum Fine |
|---|---|
| Prohibited AI practices (Art. 5) | €35M or 7% of global turnover |
| High-risk obligations (Art. 9–15) | €15M or 3% of global turnover |
| Incorrect / misleading information | €7.5M or 1.5% of global turnover |

High-risk AI carries a **10-year logging-retention** obligation (Art. 72), enforceable since Feb 2025 (prohibited practices) / Aug 2025 (high-risk).

---

## Two Lifecycles, One Certified System

Building agents on Databricks is a developer-and-data-team workflow: define an agent in Agent Bricks, wire it to Lakehouse context and Unity Catalog permissions, deploy to Model Serving, evaluate. Governance runs as a parallel data-governance and guidance track. There is no single platform where a risk officer authors and independently versions an enforceable safeguard contract alongside the functional one.

Akka runs two independent lifecycles on one platform via **Akka Specify**:

- **Build lifecycle** — a functional contract authored by product, developers, ML engineers, and domain experts ("Rank incoming ER patients by acuity and route the top three to a clinician"). Versioned and tested.
- **Govern lifecycle** — a safeguard contract authored by risk, security, and compliance ("Block prohibited practices under EU AI Act Article 5; notify regulators within 24h of any incident"). Versioned and tested **independently of the build**.

Both feed Akka Specify, which generates, tests, and runs **one certified AI service**: agents, tools, orchestration, memory, APIs, streaming, and UI, with guardrails, sanitizers, HITL/HOTL, evaluations, and halts, plus interaction, evidence, and causal logging. **Akka Verify** then validates the running system against both specs and fine-tunes the AI from production data.

---

## Real-Time Streaming at Petabyte Scale

Akka's streaming is built into the runtime — continuous, **backpressured**, **petabyte-scale in-memory**, with **no external broker** — powering both agent feedback loops and high-throughput data processing. **Tubi** runs real-time hyper-personalization on it at **5 billion tokens per second**. On Databricks, real-time data movement lives in the lakehouse (streaming tables, pipelines); feeding it into the agent layer is an integration the customer assembles across serving endpoints, Vector Search sync, and Lakebase, each metered and operated separately.

---

## For the Buyer: Product Maturity, Coupling, and Accountability

The Databricks lakehouse is mature and widely adopted. The question for an agentic-AI decision is the **agent product's** maturity and what standardizing on it commits you to — not Databricks' viability, which is not in question.

| Buyer concern | Databricks (Mosaic AI / Agent Bricks) | Akka |
|---|---|---|
| Agent product maturity | Agent Bricks announced beta Jun 2025; Supervisor Agent GA Feb 2026; capabilities and APIs evolving quickly | 18 years; 100,000+ production deployments; 52 banks |
| Coupling / lock-in | Agents bound to the Lakehouse, Unity Catalog, and DBU-metered serving; the value compounds the more of the estate sits in Databricks | Deploy anywhere — Akka cloud, your VPC, your Kubernetes, on-prem, sovereign cloud; portable specs; BSL licensing |
| Who owns the SLA | Customer architects HA/DR; serving endpoints excluded from managed DR | Akka owns the SLA, 24/7 SRE, one platform |
| Certifications | SOC 2 Type II, ISO 27001, ISO 27701, PCI DSS, HIPAA, HITRUST (Azure) | 19 standards — SOC 2 II + public SOC 3, ISO 27001/42001, HIPAA, PCI DSS, GDPR, CCPA, PIPEDA, NIS2, DORA, EU AI Act, NIST AI RMF — plus annual pen tests, SBOMs, 40+ policies (trust.akka.io) |
| Risk transfer | Standard cloud terms | Availability and data-integrity guarantees backed by contractual indemnities |
| Budget predictability | DBU consumption metering that scales with load | Fixed annual fee |

### Akka complements your lakehouse

Akka is explicitly **not** a vector database, a semantic knowledge layer, a model-serving / inference engine, or a context graph — those are exactly what the Databricks lakehouse, Unity Catalog, Vector Search, and Model Serving provide. For those layers Databricks sits **beneath** Akka, and the two are complementary: keep your governed data and feature/model tier in Databricks, and run the governed agentic system on Akka above it. The competitive overlap is narrow and specific — Agent Bricks and the Mosaic AI Agent Framework as the agent runtime and governance layer — and that is where the runtime-versus-data-platform line is drawn.

---

## Customers Running Agentic and Real-Time Systems on Akka

- **Manulife** — 2,000 developers across 100 projects on one governed platform; up to 300% more concurrency, 30–50% faster after porting from Python.
- **Tubi** — 5 billion tokens/sec real-time hyper-personalization engine.
- **Swiggy** — 71ms order-assignment AI, ~50% latency reduction.
- **John Deere** — 1,000+ tractor sensors turned into real-time insight.
- **Verizon** — 750% order-processing capacity gain; 6s → 2.4s response.

---

## Common Questions

**We already run Databricks. Why add Akka?**
Keep it. Databricks is a strong lakehouse, and Akka complements it — Akka is not a vector DB, model-serving, or semantic layer. The gap is the agentic runtime: durable in-memory agent state, a six-nines platform SLA, active-active failover, and inline EU AI Act enforcement. Run your governed data and models on Databricks and the governed agentic system on Akka above it.

**Agent Bricks is "governed." Isn't that the same governance?**
Agent Bricks governs agents, tools, and models as Unity Catalog assets — that is data governance: access control, lineage, and audit, with on-behalf-of permissions. The EU AI Act expects runtime enforcement: prohibited practices blocked inline, immutable records witnessed as decisions happen, human override of running processes, pre-deployment classification, and a sealed evidence trail. Akka enforces these in the runtime; Unity Catalog governs the data the agent reads.

**Doesn't Databricks have agent memory now?**
Databricks agents are stateless and externalize state to Lakebase (managed Postgres), re-reading session history from a central database at the start of every turn. Akka holds agent state in durable sharded in-memory storage — 4ms reads, sub-10ms writes, replayable from its event journal — so working memory survives failover without a per-turn database round trip.

**Is Databricks cheaper because we already pay for it?**
Databricks bills on DBU consumption — pay-per-token plus provisioned-throughput DBUs for serving — so the agent meter scales with load and each layer consumes separately. Akka runs the whole agentic system on one shared-compute runtime, up to 90% cheaper to operate for the same workload, on a fixed annual fee.

---

## Sources

**Agent Bricks (what it is / GA timeline):** databricks.com/blog/introducing-agent-bricks (beta, Jun 2025); databricks.com/blog/agent-bricks-supervisor-agent-now-ga-orchestrate-enterprise-agents (Supervisor Agent GA, Feb 10 2026); databricks.com/blog/agent-bricks-governed-enterprise-agent-platform; developers.databricks.com/docs/agents/overview — agents/tools/models governed via Unity Catalog and on-behalf-of access controls; context from the Lakehouse.
**Mosaic AI Agent Framework / Model Serving:** databricks.com/product/model-serving; docs.databricks.com/.../generative-ai/agent-framework/deploy-agent — agents deployed to serving endpoints; "Model Serving is backed by the Databricks SLA," highly available serverless.
**Agent state / memory:** learn.microsoft.com/.../oltp/projects/state-management; docs.databricks.com/.../agent-framework/stateful-agents — "agent runtimes are typically stateless," state externalized to a durable store (Lakebase Postgres) and session history retrieved at the start of every turn.
**Vector Search / Genie / Unity Catalog:** learn.microsoft.com/.../vector-search/vector-search; databricks.com/product/unity-catalog — Unity Catalog = centralized access control, lineage, audit, data discovery (data governance).
**Availability SLA / DR:** docs.databricks.com/.../reliability/best-practices — 99.9% control-plane SLA; docs.databricks.com/aws/en/admin/disaster-recovery and managed-disaster-recovery — typically active-passive, RTO < 1h / RPO < 15min for critical workloads, "Model serving endpoints are not replicated in Databricks managed disaster recovery."
**Pricing (DBU):** databricks.com/product/.../pricing; flexera.com/blog/finops/databricks-pricing-guide — DBU consumption; pay-per-token Foundation Model APIs + provisioned-throughput DBUs for hosted models/serving.
**Governance / EU AI Act:** databricks.com/trust/responsibleAI; databricks.com/blog/introducing-databricks-ai-governance-framework — DAGF (5 pillars, 43 considerations), DASF; "committed to responsible AI consistent with applicable laws, including the EU AI Act."
**Certifications:** databricks.com/legal/security-addendum; databricks.com/trust/compliance/soc — SOC 2 Type II, ISO 27001, ISO 27701, PCI DSS, HIPAA; HITRUST (Azure Databricks).
**Akka facts (per akka-facts.md, verified 2026-06-19):** 99.9999% availability, active-active HA/DR, sub-1-min RTO, zero-byte RPO, contractual indemnities; durable in-memory 4ms reads / sub-10ms writes, replayable event journal; ~10T vs ~2T tokens/core/year, ~80% less compute, up to 90% cheaper to operate; Manulife up to 300% more concurrency, 30–50% faster (akka.io/blog/go-slow-to-go-fast); 189 regulations / 962 controls / 574 with financial penalty (`../explainability/framework/regulations/`); 19 standards (trust.akka.io); 18 years, 100,000+ deployments, 52 banks; profitable, Dell Technologies Capital largest shareholder; Tubi 5B tok/s, Swiggy 71ms, John Deere 1,000+ sensors, Verizon 750%.

---

*Akka — Reliable AI for Every Industry. The Agentic Systems Platform. akka.io · June 2026*
