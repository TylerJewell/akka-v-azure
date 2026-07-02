# Akka vs. Azure AI Foundry

**A comparison for teams building agentic AI**
**July 2026**

---

**Azure AI Foundry (now Microsoft Foundry) Agent Service is a collection of Azure services you integrate and operate — not an integrated platform — and its Agent Service carries no availability or state-durability SLA.** Microsoft's own documentation states the Agent Service has no SLA, no automatic failover, and that the recovery point for agent state "can be total loss." Akka delivers agents, memory, streaming, APIs, and governance as one runtime with a contractual 99.9999% availability SLA, sub-1-minute RTO, and zero-byte RPO — and, through Akka Specify, that governed system can be delivered and operated for you as a guaranteed outcome, in weeks, for one fixed price.

| Stat | |
|------|--|
| **99.9999%** | Akka Availability SLA |
| **Weeks** | Akka Specify Delivery |
| **Fixed** | One All-In Price |
| **90%** | Less Infrastructure |

---

## At a Glance

| Dimension | Azure AI Foundry (Microsoft Foundry) | Akka |
|-----------|--------------------------------------|------|
| What it is | An agent service that orchestrates a set of separately provisioned Azure services | A full-stack agentic systems platform — build on it yourself, or have it delivered and operated for you |
| Scope | Agent runtime + bring-your-own Cosmos DB, AI Search, Storage, Key Vault, OpenAI, API Management, Monitor — you integrate and operate each | Agents, memory, streaming, APIs, orchestration, observability, and governance on one runtime |
| How you reach production | Self-integrate the services, or contract a systems-integration engagement | Build with spec-driven development, or **Akka Specify** delivers and runs it |
| Commercial model | Per-service metering across every service in scope, plus integration and operations labor | One fixed price — platform, infrastructure, tokens, training, delivery, and operations |
| Outcome guarantee | Effort only; the outcome is not guaranteed | The delivered outcome is guaranteed |
| Availability SLA | **No SLA** on Agent Service availability or state durability | **99.9999%** — entire platform, backed by indemnities |
| HA/DR | No automatic failover; no built-in DR; no active-active multi-region replication | **Active-active** HA/DR; sub-1-min RTO; zero-byte RPO |
| Recovery point | "Can be total loss"; cross-region state lost on failback | Zero-byte RPO; state fully preserved |
| Governance / EU AI Act | Assessment and mapping across Purview, Content Safety, API Management, Monitor, Entra — multiple services, not inline enforcement | Aspect-woven runtime enforcement + full pre-production governance |
| Portability | Azure identity, gateway, and data services; moving off means rebuilding | Any cloud, on-prem, or Akka cloud; portable specs; sovereign cloud |
| Cost model | Per-token / PTU on OpenAI + per-RU Cosmos + per-tier AI Search + gateway + per-GB logging | Shared compute; up to 90% lower infrastructure for the same workload; one fixed price |
| Improves after go-live | Not provided | Continuous evaluation, reinforcement learning, and distillation — up to 80% lower token cost over time |
| Certifications | Inherited Azure certifications + Purview templates | 19 standards — SOC 2 II + public SOC 3, ISO 27001/42001, HIPAA, PCI DSS, GDPR, NIS2, DORA, EU AI Act, NIST AI RMF |

---

## 1. A Collection of Services to Integrate, Not a Platform

A production agent on Azure AI Foundry is assembled from multiple, separately provisioned, separately billed Azure services. In the Agent Service Standard deployment mode, Microsoft's own setup documentation requires the customer to bring and operate an Azure Cosmos DB account (minimum 3,000 RU/s), an Azure AI Search resource, an Azure Storage account, and an Azure Key Vault — and a realistic production agent also needs Azure OpenAI, an API Management gateway, and Azure Monitor / Application Insights. ([Standard agent setup](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/standard-agent-setup))

| Azure service | Role in an agent | What the customer owns |
|---------------|------------------|------------------------|
| Azure OpenAI | Model inference | Per-token billing or PTU capacity reservation |
| Azure Cosmos DB | Agent state / thread memory | Per-RU billing; ≥3,000 RU/s; backup, replication, failover |
| Azure AI Search | Vector store / retrieval | Per-tier billing; index rebuild on recovery |
| Azure Storage | Uploaded files, attachments | Redundancy and failover configuration |
| Azure Key Vault | Secrets | RBAC and purge protection |
| Azure API Management | Generative AI gateway, load balancing, circuit breaker | Multi-region gateway deployment and policy |
| Azure Monitor / App Insights | Observability | Per-GB ingestion; multi-region instances |

Microsoft's documentation is explicit that the customer operates the durability of these stateful dependencies: "Microsoft and you jointly operate the Foundry Agent Service. Microsoft runs the control plane and capability host platform. You own the durability of stateful dependencies (Azure Cosmos DB, Azure AI Search, Azure Storage)." ([HA/DR for Foundry](https://learn.microsoft.com/en-us/azure/foundry/how-to/high-availability-resiliency)) The integration, the reliability, and the recovery across these seams are the customer's responsibility.

Akka delivers agents, durable memory (4ms reads / sub-10ms writes), real-time streaming, an HTTP/gRPC API layer, orchestration, observability, and governance on one runtime — provisioned once, operated as one system, under one SLA.

---

## 2. Two Ways to Production — Integrate the Services, or Have Them Delivered

Reaching production on Azure AI Foundry means integrating and operating the services in §1 yourself, or contracting a systems-integration engagement to assemble them — and in either case, no single vendor is accountable for the assembled result. Akka offers a second path: **Akka Specify** takes your specifications and delivers and operates the entire governed system for you as a guaranteed outcome — in weeks, for one fixed price.

| | With Azure AI Foundry | With Akka Specify |
|---|---|---|
| Model | Self-integrate the services in §1, or a systems-integration engagement | You provide the specifications |
| Who does the work | Your engineers, or a systems-integration engagement | Akka generates, governs, delivers, and runs the system |
| Timeline | Months, assembling and testing multiple services | Weeks, not quarters |
| Billing | Per-service metering across OpenAI, Cosmos DB, AI Search, Storage, the gateway, and logging, plus integration labor | One fixed price |
| Afterward | You own the integration and its ongoing operation across every service | Kept up, safe, and improving — operated by Akka |
| Guarantee | Effort is guaranteed; the outcome is not, and no single vendor owns it | The delivered outcome is guaranteed — one accountable owner |

By Microsoft's own shared-responsibility model, the customer owns the durability of every stateful dependency (Cosmos DB, AI Search, Storage) and the integration across them; no single vendor is accountable for the assembled result. A team that cannot self-integrate contracts a systems-integration engagement — billed for time and materials, guaranteeing effort rather than the outcome, and handing back a system the team then owns and operates. Akka Specify inverts that: you provide a handful of plain-language specifications, and Akka generates, tests, governs, deploys, and runs the system — then keeps it available, safe, and improving under one agreement, with one accountable owner.

---

## 3. The Agent Service Has No HA/DR Availability SLA

This is stated in Microsoft's own current documentation (HA/DR pages last updated April–May 2026):

> "Agent Service has no availability or state durability Service Level Agreement (SLA)." ([HA/DR for Foundry](https://learn.microsoft.com/en-us/azure/foundry/how-to/high-availability-resiliency))

> "Foundry itself doesn't provide automatic failover or disaster recovery." ([HA/DR for Foundry](https://learn.microsoft.com/en-us/azure/foundry/how-to/high-availability-resiliency))

> "Agent Service doesn't provide built-in disaster recovery capabilities. It doesn't replicate state, create backups, or support point-in-time restore… The service doesn't have any supported method for active-active, multi-region replication." ([Agent Service disaster recovery](https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-disaster-recovery))

> "The recovery point for stateful content can be total loss." ([Agent Service disaster recovery](https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-disaster-recovery))

| Metric | Azure AI Foundry Agent Service | Akka |
|--------|--------------------------------|------|
| Availability SLA | **No SLA** on Agent Service availability or state durability | **99.9999%** — contractual, backed by indemnities |
| HA/DR mode | Warm-standby reconstruction; no automatic failover | **Active-active**, automatic |
| RTO | "30 or more minutes per project" (reconstruction, not promotion) | **Sub-1 minute** |
| RPO | "Can be total loss" | **Zero byte** |
| Multi-region | "No supported method for active-active, multi-region replication" | Active-active across regions |
| State on failover | "Standby-region state is permanently lost" after failback | Fully preserved |
| Who operates it | The customer, or a systems-integration engagement | **Akka SREs, 24/7** |

Microsoft documents that recovery on Azure is reconstruction, not failover: "Warm standby environments start mostly empty. Recovery is reconstruction, not promotion of a hot replica," and after a regional outage, recovered agents "have no access to prior threads," with "no state… transferable between regions." ([Agent Service platform outage recovery](https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-platform-disaster-recovery))

Akka owns the SLA. With Foundry, the availability of the assembled agent is the customer's responsibility — and the Agent Service layer itself carries none.

### Azure platform outages are a documented reality

- **Oct 29, 2025** — An Azure Front Door global configuration fault broke routing and authentication across Azure-fronted services for hours. ([Azure status history](https://azure.status.microsoft/en-us/status/history/))
- **May 29, 2026** — Azure OpenAI Service experienced a multi-region outage (failures, timeouts, and 5XX errors) with pronounced impact across Europe and Australia East; root cause was retry amplification from an upstream rollout that cascaded across regions. ([Azure status history](https://azure.status.microsoft/en-us/status/history/))

For an agent with no availability SLA and a documented "total loss" recovery point, a regional event is not a tail risk the customer can ignore.

---

## 4. Cost: Many Meters vs. One Shared-Compute Fee — and It Keeps Getting Cheaper

AI systems built on Akka are up to **90% cheaper to operate** than Python-based systems — a function of the infrastructure required to run the same agentic transaction volume, not list price. On Azure AI Foundry, cost is the sum of independent meters across every service in §1: per-token or PTU-reserved Azure OpenAI, per-RU Cosmos DB (≥3,000 RU/s minimum), per-tier AI Search, gateway units, and per-GB log ingestion.

Provisioned-throughput (PTU) reservations on Azure OpenAI carry a substantial monthly floor; independent 2026 pricing analyses put a single minimum PTU reservation in the low thousands of dollars per month before any of the surrounding services are counted ([CloudZero](https://www.cloudzero.com/blog/azure-openai-pricing/), [OpsLyft](https://www.opslyft.com/blog/azure-openai-pricing)). Each meter scales independently with load, which makes the total bill difficult for finance to forecast.

Akka runs orchestration, agents, memory, streaming, APIs, observability, and governance on **shared compute** for **one fixed price**. The efficiency is structural: actor-based concurrency delivers ~10 trillion tokens per core per year versus ~2 trillion for comparable solutions, and ~80% less compute than Python-based frameworks. Manulife reported up to **300% more concurrency** and **30–50% faster processing** after porting Python-based systems to Akka. ([akka.io/blog/go-slow-to-go-fast](https://akka.io/blog/go-slow-to-go-fast))

### And the cost falls after go-live

Akka Verify runs continuous evaluation, reinforcement learning on production and synthetic data, and distillation to smaller specialized models — cutting token cost up to 80% while raising accuracy over time. Azure AI Foundry's evaluation tooling detects and scores quality; it does not retrain, distill, or ship the improvement. The spend is also predictable: **one fixed price** finance can forecast — covering platform, infrastructure, tokens, training, delivery, and operations — rather than the independent per-service meters in §1 that move with load, plus separate integration labor.

---

## 5. Governance and the EU AI Act: Assessment vs. Inline Enforcement

The penalties make governance a procurement gate, not a feature:

| Violation | Maximum fine |
|-----------|--------------|
| Prohibited AI practices (Art. 5) | EUR 35M or 7% of global annual turnover |
| High-risk obligations (Art. 9–15) | EUR 15M or 3% of global annual turnover |
| Supplying incorrect information | EUR 7.5M or 1.5% of global annual turnover |

Prohibited-practice penalties have been enforceable since February 2025 and high-risk obligations since August 2025; high-risk AI carries a 10-year logging-retention obligation (Art. 72).

Microsoft has invested in AI governance, and the current capability should be stated accurately. Microsoft Purview Compliance Manager now ingests regulations such as the EU AI Act, uses AI to extract controls, maps them to improvement actions, and syncs evaluation results from Azure AI Foundry into Compliance Manager. ([Purview + Foundry](https://learn.microsoft.com/en-us/purview/ai-azure-foundry)) Azure also provides Content Safety filters, an API Management gateway, Entra identity, and Monitor logs.

The line is architectural. Azure's governance is **assessment and mapping spread across several services** — Compliance Manager improvement actions, Content Safety, API Management policies, Monitor logs, Entra logs — that observe, score, and document. They are not a single enforcement plane woven into the agent's execution.

| Requirement | Azure AI Foundry approach | The gap |
|-------------|---------------------------|---------|
| Real-time policy enforcement | Content Safety + API Management policies | Multiple enforcement points across services; not a unified inline engine |
| Decision explainability | Evaluations + Responsible AI dashboard | Post-hoc scoring, not an inline record of why a running decision was made |
| Immutable interaction log | Azure Monitor / Purview audit logs | Standard audit logs, not a hash-chained, purpose-built ledger |
| Human pause / override of a running agent | Not a built-in capability | A log reader cannot stop or redirect a running process |
| Authorization capture at execution time | Correlate Entra + RBAC + gateway logs | Reconstructed across 3+ log sources, not captured atomically |
| PII scrub with explainability | PII detection exists | No single atomic scrub-and-explain operation |
| Pre-deployment classification + sign-off | Compliance Manager checklists / improvement actions | Self-assessment workflow, not a runtime-gating classification + multi-persona attestation engine |
| Sealed audit artifact | Assembled from reports | No single sealed, tamper-evident posture package emitted per deployment |

Akka's governance is **aspect-woven into the runtime**: inline guardrails, policies, LLMs-as-a-judge, and sanitizers execute within the agents; evidence is hash-chained and immutable; humans can pause, override, or nudge a running process; PII is scrubbed and explained atomically. Before a system ships, Akka classifies it against **186 regulations and 877 controls (288 carrying financial penalties)** to derive the obligation set, routes change events to the right reviewers, and emits a sealed Governance Posture Package. **Akka Verify** proves conformance from the running system, not from a dashboard.

---

## 6. One Certified System — Built, Governed, Delivered, and Run

Building on Azure AI Foundry means developers assembling agents against a set of Azure SDKs and portals; there is no first-class lifecycle for a risk officer or compliance reviewer to author and independently version the safeguard contract. Akka runs two independent lifecycles on one platform via **Akka Specify**:

```
BUILD LIFECYCLE                                          ONE CERTIFIED AI SERVICE
Functional contract                                      Built, governed, delivered & run
"Rank incoming ER patients by acuity                     - Agents, tools, orchestration,
 and route the top three to a clinician."                  memory, APIs, streaming, UI
Product · developers · ML · domain experts               - Guardrails, sanitizers,
v1.4 · versioned · tested                                  HITL/HOTL, evaluations, halts
                              --> Akka Specify -->        - Delivered, deployed, and
GOVERN LIFECYCLE                  (generates · tests ·      operated for you
Safeguard contract                 governs · runs ·
"Block prohibited practices under  operates)
 EU AI Act Article 5; notify
 regulators within 24h of any incident."
Risk · security · compliance
v2.1 · versioned & tested independent of the build

Akka Verify ↻ validates the running system against both specs and fine-tunes the AI from production data.
```

Akka generates, tests, governs, **runs, and operates** one certified service from both specs, which are versioned and tested independently by different audiences. Through Akka Specify, that certified system is delivered and operated as a guaranteed outcome — a delivery model and an independent governance lifecycle Azure AI Foundry has no equivalent for.

---

## 7. Real-Time Streaming at Petabyte Scale

Azure AI Foundry has no built-in streaming engine; real-time pipelines are provisioned separately (for example, Event Hubs or Service Bus) and operated by the customer. Akka's streaming is built into the runtime — continuous, backpressured, **petabyte-scale, in-memory**, with no external broker — powering both agent feedback loops and high-throughput data processing. It is the engine behind Tubi's real-time hyper-personalization at **5 billion tokens per second**.

---

## 8. For the Buyer: A Recent, Renamed Product vs. an 18-Year Platform

Microsoft is a durable company; the question is the maturity of the **product**. Foundry Agent Service reached general availability at Build in May 2025, and the product is mid-rebrand from "Azure AI Foundry" to "Microsoft Foundry," with its RBAC roles renamed from "Azure AI User/Owner/Project Manager" to "Foundry User/Owner/Project Manager" as the change rolls out. ([HA/DR for Foundry](https://learn.microsoft.com/en-us/azure/foundry/how-to/high-availability-resiliency)) It is a young, evolving agent layer assembled over a set of Azure services — and that layer ships today with no availability or state-durability SLA.

| Buyer concern | Azure AI Foundry | Akka |
|---------------|------------------|------|
| Product maturity | GA May 2025; active rebrand (Azure AI Foundry → Microsoft Foundry) and RBAC rename in progress | 18 years; 100,000+ production deployments; 52 banks; 2B+ people reached daily |
| Delivery & outcome | Self-integrate the services, or a systems-integration engagement; effort is guaranteed, the outcome is not | Akka Specify delivers and operates the system for one fixed price; the outcome is guaranteed |
| Scope of accountability | Customer integrates and operates Cosmos DB, AI Search, Storage, gateway, OpenAI; Agent Service has no SLA | One platform, one SLA, 24/7 SRE — Akka owns the running system |
| Risk transfer | Standard Azure terms; no Agent Service availability/durability SLA | Availability and data-integrity guarantees backed by contractual indemnities |
| HA/DR | No automatic failover; "total loss" recovery point | Active-active; sub-1-min RTO; zero-byte RPO |
| Certifications | Inherited Azure certifications + Purview Compliance Manager templates | 19 standards (SOC 2 II + public SOC 3, ISO 27001/42001, HIPAA, PCI DSS, GDPR, NIS2, DORA, EU AI Act, NIST AI RMF); annual pen tests, SBOMs, 40+ policies (trust.akka.io) |
| Budget predictability | Several independent meters that scale with load | One fixed price on shared compute |

The decision is scope and accountability: Azure AI Foundry gives you an agent service to wire your Azure estate around; Akka gives you the integrated platform with the SLA on the whole thing — and, through Akka Specify, will deliver and run the whole system for you.

---

## Customers Running Agentic and Real-Time Systems on Akka

- **Manulife** — selected Akka (March 2026) to operationalize agentic AI within its enterprise AI platform, citing the speed, predictability, and governance required in highly regulated environments, plus energy-efficient AI that requires less infrastructure. ([akka.io/blog/manulife-selects-akka-to-operationalize-agentic-ai](https://akka.io/blog/manulife-selects-akka-to-operationalize-agentic-ai))
- **Tubi** — 5 billion tokens/sec real-time hyper-personalization engine.
- **Swiggy** — 71ms order-assignment AI, ~50% latency reduction.
- **John Deere** — 1,000+ tractor sensors turned into real-time insight.
- **Verizon** — 750% order-processing capacity gain; 6s → 2.4s response.

---

## Common Questions

**We don't have a team to integrate this — what are our options?**
Two. Build it on the platform with spec-driven development, or have Akka Specify deliver and operate it for you. You provide plain-language specifications; Akka generates, governs, delivers, and runs the system as a guaranteed outcome, for one fixed price. With Azure AI Foundry, production means self-integrating the services in §1 or contracting a systems-integration engagement you then own.

**How is Akka Specify different from a systems-integration engagement to assemble Azure AI Foundry Agent Service into a system?**
A systems-integration engagement sells effort — time-and-materials over months — and hands back a system you own and operate across every service; the outcome is not guaranteed and no single vendor is accountable for it. Akka Specify sells the outcome: a governed system delivered in weeks for one fixed price, then kept up, safe, and improving by Akka. You own the specifications, not the operational burden.

**We're already on Azure. Why add Akka?**
Akka deploys inside your Azure VPC. You keep your Azure infrastructure, your Entra ID, and your networking — Akka runs alongside them and adds the integrated runtime, the active-active HA/DR, the 99.9999% SLA, and the inline governance that the Foundry Agent Service does not provide on its own.

**Won't Microsoft close the HA/DR gap soon?**
Microsoft's current documentation (updated April–May 2026) states the Agent Service has no availability or state-durability SLA, no automatic failover, no built-in DR, and that the recovery point "can be total loss." Until that changes in the product, the availability of an assembled Foundry agent is the customer's responsibility. Akka delivers active-active HA/DR with a contractual SLA today.

**Doesn't Microsoft already cover the EU AI Act?**
Microsoft has real assessment tooling: Purview Compliance Manager extracts EU AI Act controls and maps improvement actions, and syncs Foundry evaluation results. That assesses and documents; it does not enforce inline. The EU AI Act expects immutable records witnessed as they happen, human override of a running process, authorization capture at execution time, and pre-deployment classification that gates a release. Akka enforces these in the runtime and produces a sealed posture package.

**Isn't Foundry cheaper because we have an Enterprise Agreement?**
EA discounts apply to individual Azure services, but a production agent still meters across Azure OpenAI, Cosmos DB, AI Search, Storage, the gateway, and logging — each scaling independently. Akka's shared-compute model runs all of it on one runtime for one fixed price, and is up to 90% cheaper to operate for the same agentic transaction volume.

---

## Sources

- **Foundry HA/DR — no SLA, no automatic failover:** learn.microsoft.com/en-us/azure/foundry/how-to/high-availability-resiliency (updated 2026-04-15) — "Agent Service has no availability or state durability Service Level Agreement (SLA)"; "Foundry itself doesn't provide automatic failover or disaster recovery"; joint-operation / customer owns durability of Cosmos DB, AI Search, Storage.
- **Foundry Agent Service disaster recovery:** learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-disaster-recovery (updated 2026-05-12) — "doesn't replicate state, create backups, or support point-in-time restore… no supported method for active-active, multi-region replication"; "recovery point for stateful content can be total loss."
- **Foundry platform outage recovery:** learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-platform-disaster-recovery (updated 2026-05-12) — RTO "30 or more minutes per project"; "Recovery is reconstruction, not promotion of a hot replica"; "Standby-region state is permanently lost."
- **Standard agent setup (required services):** learn.microsoft.com/en-us/azure/foundry/agents/concepts/standard-agent-setup — Cosmos DB (≥3,000 RU/s), AI Search, Storage, Key Vault required; plus Azure OpenAI, API Management gateway, Monitor.
- **Foundry Agent Service GA:** techcommunity.microsoft.com — Announcing General Availability of Azure AI Foundry Agent Service (Build, May 2025).
- **Purview + Foundry governance:** learn.microsoft.com/en-us/purview/ai-azure-foundry — Compliance Manager extracts EU AI Act controls, maps improvement actions, syncs Foundry evaluation results (assessment/mapping).
- **Azure OpenAI / PTU pricing (third-party analyses):** cloudzero.com/blog/azure-openai-pricing, opslyft.com/blog/azure-openai-pricing — PTU minimum reservations and multi-meter cost.
- **Azure outages:** azure.status.microsoft/en-us/status/history — Oct 29, 2025 Azure Front Door global configuration fault; May 29, 2026 Azure OpenAI multi-region outage (Europe / Australia East).
- **Akka platform & performance:** akka.io/blog/go-slow-to-go-fast — Manulife up to 300% more concurrency, 30–50% faster; ~10T vs ~2T tokens/core; ~80% less compute than Python. 99.9999% availability, active-active HA/DR, sub-1-min RTO, zero-byte RPO (contractual indemnities); 186 regulations / 877 controls / 288 with penalties; 100,000+ deployments / 18 years; profitable; Dell Technologies Capital.
- **Akka trust center:** trust.akka.io — 19 compliance standards; SOC 2 II + public SOC 3; annual pen tests, SBOMs, 40+ policies.
- **Akka Specify (spec-driven delivery):** akka.io / akka.io/llms.txt (you provide the specifications; Akka generates, tests, governs, delivers, and operates the system as a guaranteed outcome; one fixed price covering platform, infrastructure, tokens, training, delivery, and operations; delivered in weeks; continuous improvement via reinforcement learning and distillation, up to 80% lower token cost with higher accuracy).
- **Manulife:** akka.io/blog/manulife-selects-akka-to-operationalize-agentic-ai (March 10, 2026).

---

*A comparison for teams building agentic AI. All Azure claims cite Microsoft's own documentation or Azure's status history; Akka figures per akka.io and trust.akka.io. July 2026.*
