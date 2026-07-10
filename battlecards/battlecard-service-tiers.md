# Akka Service Tiers — Choosing Your On-Ramp to Production Agentic AI

**A guide to Akka's five service tiers, and the two ways to reach them, for enterprise buyers, architects, and partners**
**July 2026**

---

## The Bottom Line

Every Akka deployment runs on one of five service tiers, from a low-overhead evaluation sandbox to a fully sovereign, country-isolated production environment. Every tier can be built and operated by the customer's own team, or delivered and operated by **Akka Specify** as a guaranteed outcome — in weeks, for one fixed price covering the platform, the infrastructure, every inference and training token, delivery of the system, and 24/7 operations.

---

## TL;DR — The Five Tiers at a Glance

| Tier | Where It Runs | QoS | Best For | TCO Headline |
|------|---------------|-----|----------|--------------|
| **Starter** | Akka's public cloud | Fully resilient, 24/7 SRE | Customers who want a running production workload without the BYOC commitment | Monthly billing, no POs, no invoices — spend scales with usage |
| **Sandbox** | Customer's own VPC | Non-resilient, 9x5 support, no SLA | Customers who want to build and evaluate in their own environment before committing | Lowest possible cloud footprint — ~5 platform cores vs 20–25 for production tiers |
| **Day 2 Ops** | Customer's own VPC | Fully resilient, 24/7 SRE | Customers running real workloads that don't yet need cross-region failover | Consolidates orchestration, memory, streaming, evals, guardrails, logging, and governance onto shared compute — up to 90% infrastructure reduction plus avoided eval-tool spend |
| **Business Continuity** | Customer's own VPC | Fully resilient + active-active HA/DR | Workloads that cannot tolerate a regional outage | Managed HA/DR with sub-1 min RTO and zero-byte RPO — no customer-built failover infrastructure |
| **Sovereign Cloud** | Customer's own VPC, country-isolated | Fully resilient + HA/DR + local SREs | Regulated industries, data residency mandates, sovereign requirements | Full feature parity with commercial tiers — no lagged capabilities or restricted model access |

---

## Two Ways to Reach Any Tier: Build It, or Have Akka Specify Deliver It

Two commercial models sit on top of the five tiers above. A customer can build and operate the system with **spec-driven development** — provisioning whichever tier fits the workload and running it with their own team — or have **Akka Specify** deliver and operate the entire system as a guaranteed outcome: the customer provides the specifications, and Akka generates, governs, deploys, and operates the system in weeks, for one fixed price.

| Dimension | Self-Build (Spec-Driven Development) | Akka Specify (Delivered & Operated) |
|---|---|---|
| Model | The customer provides requirements and builds on the platform | The customer provides the specifications |
| Who does the work | The customer's engineering team | Akka generates, governs, delivers, and runs the system |
| Timeline | As fast as the customer's team can ship | Weeks, not quarters |
| Billing | Service-core license, plus the customer's own platform-core infrastructure, plus the customer's build-and-operate time | One fixed price — platform, infrastructure, every inference and training token, delivery, and operations |
| Improves after go-live | Static once deployed, unless the customer invests in retraining | Continuous evaluation, reinforcement learning, and distillation — up to 80% lower token cost with higher accuracy over time |
| Tier it runs on | Any of the five tiers, the customer's choice | Typically Day 2 Ops or above |
| Afterward | The customer owns ongoing operations | Kept up, safe, and improving — operated by Akka |
| Guarantee | The customer controls execution; the outcome depends on their team | The delivered outcome is guaranteed |

Every tier at Day 2 Ops and above already includes the personnel an Akka Specify engagement draws on: TAM/FDE (Technical Account Manager / Field Delivery Engineer) time scales from quarter-time at Day 2 Ops, to half-time at Business Continuity, to two dedicated FDEs at Sovereign Cloud. Akka Specify does not add a separate team to the deal — it uses the one already built into the tier.

---

## The Two Starting Paths

Every deployment begins by answering one question: does the customer want Akka-hosted or their-cloud-hosted? The answer routes to one of two on-ramps, both of which progress into Day 2 Ops, Business Continuity, or Sovereign Cloud as needs grow.

### Path A: Starter (Akka's Cloud)

A fully resilient Akka region installed in Akka's public cloud, with a private data link back to the customer's environment. Monthly billing in arrears. No POs, no invoices, no procurement cycle. The customer never installs anything.

**Who it's for:**
- Customers with a real workload but no appetite for a BYOC commitment yet
- Customers who haven't built cloud infrastructure maturity in-house
- Fast-moving lines of business that need to ship without waiting on central IT
- Proofs-of-value where the success criterion is "did the workload run?"

Starter buys a running Akka region, not infrastructure — billed monthly for actual usage, with no invoicing cycle, no capex, and no cloud architecture review before the first workload ships. Migrating to Day 2 Ops is available whenever the customer is ready to bring the workload in-house.

### Path B: Sandbox (Customer's VPC)

A single Akka region installed in the customer's own cloud, deliberately configured for low overhead. No HA/DR. 9x5 support. Not SLA-backed. Designed as a low-friction on-ramp for customers who want to evaluate Akka in their own environment without committing to a production footprint.

**Who it's for:**
- Engineering teams who want Akka in their cloud before committing to a production tier
- Enterprises whose procurement process requires a successful in-house pilot before larger contracts
- Customers who need to see Akka running alongside their existing cloud services
- Architecture teams doing fit-for-purpose evaluation

**Migration is a rebuild, not an upgrade.** Sandbox is intentionally cheap because it strips the resilience infrastructure; moving to a higher tier is a rebuild from scratch, not an in-place upgrade. The word "Sandbox" signals throwaway, experimental, not the destination — a distinction worth setting at sign-up, not at upgrade time.

Sandbox is the lowest-cost way to run Akka in a customer's own cloud — roughly a quarter of the platform-core footprint of a production-grade region. It prices evaluation, not production; outgrowing it means rebuilding on Day 2 Ops or Business Continuity, on a tier engineered for the workload just proven out.

---

## Quality of Service: The Sandbox vs. Production Distinction

Sandbox and Akka's production tiers are not versions of the same thing at different price points — they are different quality-of-service tiers, built on different infrastructure configurations. Treating them as interchangeable is the most common source of confusion: Sandbox strips out the resilience layer to minimize overhead while building or evaluating; Day 2 Ops and above include fully resilient infrastructure, 24/7 SRE, and no-downtime operations because production workloads require it.

| Dimension | Sandbox | Day 2 Ops, BC, Sovereign |
|-----------|---------|--------------------------|
| HA/DR | None | Day 2 Ops: none. BC + Sovereign: active-active |
| Rolling updates | None — platform downtime during updates | No-downtime rolling updates |
| SRE coverage | 9x5 monitoring | 24/7 SRE monitoring and management |
| SLA | Not SLA-backed | Contractual 99.9999% availability, backed by indemnities |
| CVE patching | Requires downtime | Live CVE patching, no downtime |
| Platform core footprint | ~5 platform cores | ~20–25 per region (varies by tier) |
| Intended workloads | Evaluation, learning, early development | Production, customer-facing systems, anything that matters |
| Upgrade path | Rebuild on a higher tier | In-place progression to higher tiers |

The question is not which tier is "better" — it is which one matches what the workload is actually doing right now.

---

## Platform Cores vs. Service Cores: The TCO Transparency Model

**If a buyer learns one thing from this document, it should be this.** The platform-core / service-core distinction is Akka's TCO transparency story, and the one that, if skipped, creates sticker shock at contract time.

### The Two Core Types

| Core Type | What It Runs | Who Pays |
|-----------|--------------|----------|
| **Platform cores** | Akka's own runtime, clustering, resilience layer, data sharding, traffic steering, zero-trust networking | Customer, as part of their own cloud infrastructure bill — Akka does NOT charge a license fee for platform cores |
| **Service cores** | The customer's agentic workloads — their agents, workflows, endpoints, entities, views | Customer, as part of their Akka license — Akka charges per service core |

### Why This Matters

**Resilience isn't free.** A fully resilient Akka region in the customer's VPC needs platform cores to run clustering, active-active replication, zero-trust networking, and the resilience layer that delivers Akka's 99.9999% availability guarantee. Those platform cores run on cloud infrastructure the customer provisions — they're part of the customer's cloud bill, not the Akka license.

**Sandbox is cheap because it has fewer platform cores.** That's the engineering tradeoff: strip the resilience infrastructure, drop the platform core count, cut the customer's cloud footprint by roughly 4-5x. The customer's total cost drops not because the license is cheaper, but because their cloud infrastructure bill drops.

**The TCO argument this unlocks:** Akka is the only agentic platform that separates and discloses this. Every other platform hides infrastructure overhead inside a single opaque price, or forces customers to stand up separate services (vector DB, memory layer, streaming, evaluation, guardrails, logging, governance) each with their own infrastructure bill. Akka discloses platform-core overhead up front, charges license fees only for service cores, and runs orchestration + memory + streaming + evaluation + guardrails + logging + governance + APIs on shared compute.

### The Third Dimension: One Fixed Price

Platform cores and service cores describe what a self-built deployment costs to run. An Akka Specify engagement replaces both lines — plus every inference and training token, delivery of the system, and 24/7 operations — with one fixed price. Rather than reconciling a license bill, a cloud infrastructure bill, metered token consumption, and a separate build-and-operate labor cost, the customer sees a single number covering the platform, the infrastructure, the tokens, the training, and the operations.

### Seven Questions That Expose the Hidden TCO Gap

These questions, asked by any buyer evaluating Akka against a hyperscaler agent product, an orchestration framework, or a DIY stack, surface the cost most vendors hide:

1. *"How many separately billed services are you stitching together today, and what's the combined monthly spend on them?"* → Exposes Azure's 6-9 service sprawl
2. *"What are you paying for agent memory today, and what's the read/write latency?"* → Exposes the ~200ms bolt-on memory penalty
3. *"What's your cloud spend on observability and tracing for your AI workloads?"* → Exposes App Insights / Datadog cost balloon
4. *"Are you budgeting for Arize, LangSmith, Phoenix, or another eval/observability product?"* → Exposes duplicated evaluation, trace storage, and audit-reconciliation cost
5. *"When a regulator or customer asks why an agent made a decision, which system is the evidence of record?"* → Exposes the gap between post-hoc dashboards and runtime-native interaction logs
6. *"When you need to patch a CVE in your runtime, how much downtime does that cost you?"* → Exposes the lack of live CVE patching
7. *"Have you priced out what it would cost to build active-active HA/DR yourself — and to staff, deliver, and operate the whole system?"* → Exposes the hidden cost of DIY failover, delivery, and operations, all of which Akka Specify folds into its one fixed price

---

## Matching Your Workload to the Right Tier

A five-step decision tree:

**Step 1. Where do they want Akka to run?**
- Akka's public cloud → **Starter**
- Their own VPC → continue to Step 2

**Step 2. Are they running something real, or exploring?**
- Exploring, learning, proving fit → **Sandbox**
- Running something real → continue to Step 3

**Step 3. Can their workload tolerate a regional outage?**
- Yes → **Day 2 Ops**
- No → continue to Step 4

**Step 4. Do they need country-level data isolation for regulatory or sovereign reasons?**
- No → **Business Continuity**
- Yes → **Sovereign Cloud**

**Step 5. Confirm the upgrade path.**
- Sandbox → higher tier is a rebuild
- Day 2 Ops → BC → Sovereign is in-place progression

**Step 6. Build it, or have it delivered?** Both paths land on the same tier — the choice is who does the work and how it is billed, not which tier the workload needs. A customer can build on any of the five tiers themselves, or have Akka Specify deliver and operate the whole system for one fixed price.

---

## TCO Arguments by Tier

### Starter

**Primary argument: time-to-value and procurement friction.** Customers choose Starter when the cost of *not starting* is higher than the per-month run rate. There is no procurement cycle, no PO, no architecture review, no cloud infrastructure project — they're buying a running workload.

**TCO angle:** Avoided costs dominate. No capex, no cloud architecture project, no multi-month deployment timeline. The business case is shipping in days instead of quarters.

### Sandbox

**Primary argument: lowest-friction evaluation in the customer's own environment.** Sandbox exists to make the cost of *trying Akka in your own cloud* smaller than the cost of *not trying.* Customers who evaluate Akka in their own VPC before committing to production convert at much higher rates than customers who evaluate from documentation alone.

**TCO angle:** Opportunity cost reduction. The customer gets hands-on with Akka running alongside their existing cloud services, reduces architecture uncertainty, and builds internal conviction before a larger commitment — against the cost of a failed production rollout after a doc-based decision.

### Day 2 Ops

**Primary argument: shared compute + live CVE patching + rolling updates + runtime evidence.** This is where the core Akka TCO story lands. Customers running real workloads on Day 2 Ops replace 6-9 separately billed services (orchestration + memory + streaming + APIs + evaluation + guardrails + logging + governance + observability) with a single platform running on shared compute.

**TCO angle:** Up to 90% infrastructure cost reduction vs a stitched stack on Azure AI Foundry, LangChain, or Temporal. No maintenance windows, no downtime during patching, no lost revenue during deployments, and no required Arize-class eval/observability purchase for Akka workloads.

### Business Continuity

**Primary argument: managed HA/DR with contractual guarantees.** Customers on BC are avoiding the cost of building and operating their own failover infrastructure — which for most enterprises is a multi-million-dollar, multi-year project that is never actually complete.

**TCO angle:** Avoided cost of DIY failover. Compare BC's fully managed active-active HA/DR (sub-1 min RTO, zero-byte RPO, backed by indemnities) against the headcount, infrastructure, and operational complexity of building it in-house.

### Sovereign Cloud

**Primary argument: full feature parity in a country-isolated configuration.** Competing sovereign offerings lag commercial offerings by 3-6 months and restrict AI service availability. Akka's Sovereign Cloud delivers full feature parity with no lagged capabilities, no restricted model access, and a private federation plane with local SREs.

**TCO angle:** Avoided compliance remediation cost. Inherit Akka's 19+ InfoSec certifications (EU AI Act, ISO 42001, SOC 2, Singapore Agent Framework, and more) rather than building a compliance posture from scratch. Runtime-native interaction logs, evaluation checkpoints, guardrail verdicts, legal hold, retention, and evidence export make Akka the evidence of record. Every EU AI Act violation is up to 7% of global annual turnover — the cost of getting governance wrong dwarfs the cost of getting it right.

### The System Gets Cheaper After Go-Live, Too

Beyond the one-time, up to 90% infrastructure reduction described above, Akka Verify runs continuous evaluation, reinforcement learning on production and synthetic data, and distillation to smaller specialized models — cutting token cost up to 80% while raising accuracy over time. This is a second, compounding saving, distinct from the infrastructure number: one describes what the system costs to run today, the other describes what it costs to run a year from now. Where Akka Specify delivers and operates the system, this self-improvement is part of the operated outcome, not a project the customer runs later.

### One Fixed Price, Regardless of Tier

Whichever tier a system runs on, an Akka Specify engagement folds the platform, the infrastructure, every inference and training token, delivery, and 24/7 operations into one fixed price — a single line item finance can forecast, rather than a license fee, a separately provisioned infrastructure bill, metered token consumption, and a separate build-and-operate labor cost.

---

## Common Questions

**Can we just run production workloads on Sandbox to save money?**
Sandbox is stripped of the resilience layer. There is no HA/DR, no 24/7 SRE, no SLA, and platform updates require downtime. Any workload with production characteristics — customers depending on it, data that matters, revenue tied to uptime — needs Day 2 Ops at minimum. Sandbox exists to evaluate Akka at the lowest possible cost, not to run production on the cheap.

**Why is there no in-place upgrade from Sandbox?**
Sandbox runs on a fundamentally different infrastructure configuration — fewer platform cores, no resilience layer, no HA/DR primitives. Retrofitting all of that onto a running environment would either force the same footprint as a production tier, defeating the purpose of Sandbox, or create an unreliable upgrade path. The rebuild is a feature: build in Sandbox, prove out the design, then stand up the production tier the workload actually needs.

**Why are platform cores charged on top of the license?**
They are not charged on top of the license — platform cores are part of the customer's own cloud infrastructure bill, not a line item on the Akka license. Akka charges only for service cores, where workloads actually run. Platform cores are disclosed up front so the customer sees the full picture before committing; most platforms hide this inside one opaque price.

**Azure AI Foundry has one bill — isn't that simpler than Akka?**
Azure AI Foundry is 6-9 separately billed services underneath a single brand — Azure OpenAI, Cosmos DB, AI Search, Event Hubs, API Management, App Insights, Content Safety, Private Endpoints, and often a separate eval/observability product. Each has its own pricing model and its own cost traps, and the full bill arrives at the end of the month, after consumption has happened. Akka runs orchestration, agents, memory, streaming, APIs, evaluation checkpoints, guardrails, interaction logging, and governance on one platform with shared compute, and discloses platform-core overhead before commitment. Simpler is not one bill; simpler is one platform.

**We already use Arize for evals and AI observability. Do we still need it?**
Keep Arize for legacy workloads if it is already embedded, but it is not required for Akka. Akka captures non-sampled interaction logs, evaluation checkpoints, guardrail verdicts, LLM calls, tool calls, token cost, authority snapshots, causal lineage, legal holds, retention, and evidence exports as part of the runtime. The question is whether to pay for a second evidence plane and reconcile it with the runtime of record.

**Can we start with Starter and migrate to Day 2 Ops later?**
Yes — Starter is designed as an on-ramp. The common pattern is to prove the business case on Starter for one or two quarters, then bring the workload in-house to Day 2 Ops once architecture, security, and procurement have signed off. Akka's field team helps migrate with continuity of the running workload.

**Do we really need 24/7 SRE on day one?**
Every tier above Sandbox includes 24/7 SRE because production-grade infrastructure without 24/7 coverage is a contradiction. If a customer-facing workload goes down at 2am, someone needs to be watching. A workload that genuinely doesn't need 24/7 coverage isn't a production workload yet — which makes Sandbox the right fit, and its low-overhead configuration reflects that.

**We don't have a team to build this — what are our options?**
Two. Build it with spec-driven development on whichever tier fits the workload, or have Akka Specify deliver and operate it. The customer provides plain-language specifications; Akka generates, governs, delivers, and runs the system as a guaranteed outcome, for one fixed price.

**How is Akka Specify different from hiring an integrator to build this?**
A labor-led integration engagement sells effort — time-and-materials, typically months — and hands back a system the customer then owns and operates; the outcome is not guaranteed. Akka Specify sells the outcome: a governed system delivered in weeks for one fixed price, then kept up, safe, and improving by Akka. The customer owns the specifications, not the operational burden.

---

## Glossary

| Term | Definition |
|------|------------|
| **Akka region** | A deployment unit of Akka — a single installation running on either Akka's cloud (Starter) or the customer's VPC (all other tiers) |
| **Platform core** | Cloud CPU capacity that runs Akka's own infrastructure — clustering, resilience, networking, sharding. Customer-provisioned, not license-billed |
| **Service core** | Cloud CPU capacity that runs the customer's agentic workloads. License-billed by Akka |
| **TAM/FDE** | Technical Account Manager / Field Delivery Engineer — dedicated Akka personnel included at the Day 2 Ops tier and above, scaling from quarter-time to two dedicated FDEs at Sovereign Cloud |
| **QoS (Quality of Service)** | The SLA, support tier, and resilience posture of a service tier. Sandbox is a distinct QoS from the production tiers |
| **HA/DR** | High Availability / Disaster Recovery. Only Business Continuity and Sovereign Cloud include active-active HA/DR |
| **RTO / RPO** | Recovery Time Objective / Recovery Point Objective. Akka's BC and Sovereign tiers deliver sub-1 minute RTO and zero-byte RPO |
| **In-place upgrade** | Moving from one tier to the next without rebuilding. Available between Day 2 Ops, BC, and Sovereign. **Not** available from Sandbox |
| **Akka Specify** | Akka's delivery offering: the customer provides specifications, and Akka generates, governs, delivers, deploys, and operates the finished system as a guaranteed outcome, for one fixed price |
| **Spec-driven development** | The self-build path: the customer's own team builds and operates the system on the platform, describing it in plain-language specifications that Akka's tooling generates from |

---

## Sources

- Akka Specify (spec-driven delivery) — akka.io / akka.io/llms.txt (one fixed price covering platform, infrastructure, tokens, training, delivery, and operations; delivered in weeks; continuous improvement via reinforcement learning and distillation, up to 80% lower token cost with higher accuracy)
- Akka service tiers & TCO model — akka.io/llms.txt (five-tier on-ramp; platform-core / service-core disclosure; up to 90% infrastructure cost reduction; managed HA/DR at sub-1 min RTO / zero-byte RPO; live CVE patching; TAM/FDE staffing scaling by tier)
- Akka trust center — trust.akka.io (19+ compliance standards: SOC 2 Type II + public SOC 3, ISO/IEC 27001 & 42001, HIPAA, PCI DSS, GDPR, NIS2, DORA, EU AI Act, NIST AI RMF)
- For detailed TCO modeling: `akka-tco-analysis.md`
- For competitive positioning against Azure AI Foundry: `battlecard-azure-ai-foundry.md`

*A guide for teams evaluating Akka's service tiers and delivery options. Pricing depends on workload size and tier — contact Akka for a quote.*
