# Competitive

Frameworks, hyperscalers, SaaS agents, observability tools, integrators, and GRC platforms all appear in Akka deals. Each solves a narrower problem, and each has
real ground that a rep should concede before drawing the line.

The battlecards and comparison pages carry the sourced detail. This module teaches the conversation.

---

## 1. Rules of engagement

**Concede first.** Every category is genuinely good at something. State it before the
contrast. A rep who concedes accurately is treated as an architect for the rest of the
meeting.

**Never insult a competitor.** Frame a limitation as what the customer owns or inherits.
"Azure AI Foundry is bad at HA" loses the room. "Microsoft's documentation states there is no
supported method for active-active multi-region replication, so multi-region failover is
yours to design" wins it.

**Never overstate.** Say "limited" when the truth is limited. Absolutes are how a technical
buyer catches a rep, and one catch costs the meeting.

**Cite the source.** Every competitive claim in the battlecards has a source. Know it before
using the claim, because the buyer will ask.

**Do not compete before the customer has a problem.** An architecture objection is not a
pain. Routing failure 8 in `05-routing.md` covers this.

## 2. Agentic frameworks

LangChain, LangGraph, CrewAI, Autogen, Letta, n8n, Pydantic AI, LlamaIndex, Vercel AI SDK,
Temporal, trigger.dev, Orkes.

**Concede.** Frameworks accelerate the prototype, and nothing gets an agent working on a laptop sooner. LangGraph has checkpoint persistence. Temporal, trigger.dev, and
LangGraph provide genuine durable execution. Never claim otherwise.

**What the customer inherits.** Getting from prototype to production means clustering,
resilience, identity, governance, evidence, and multi-region failover. The customer does that work. LangChain has no runtime, no HA or DR, no operational guarantees, and no built-in
governance. Temporal has no agents, no memory, no governance, and no AI-specific
capabilities. Letta solves agent memory alone. n8n has no clustering, no resilience
guarantees, and no compliance posture.

**The wedge: explicit against implicit durability.** Temporal and LangGraph make durability a programming model the developer opts into by
structuring code a certain way, declaring retry policies, and wiring backpressure and
circuit breakers. Akka makes durability and resilience properties of the runtime, so an agent gets retries, backpressure, throttling,
circuit breakers, durable memory, execution checkpointing, and a tamper-evident audit log by
running there. Akka also offers the explicit model through workflows and sagas.

**This question proves it.** "What is your availability commitment to the business on an
agentic workload, and who signed it?"

## 3. Hyperscaler agent services

Azure AI Foundry, AWS Bedrock, Gemini Enterprise Agent Platform, NVIDIA.

**Concede.** Hyperscalers offer comparable breadth of AI capability, the customer already has
the contract, and the enterprise agreement makes procurement trivial. Breadth is not the
differentiator to argue.

**What the customer inherits.** Each capability is a separately provisioned, separately billed
service, and the reliability of how they connect is the customer's design and the customer's
problem. The guarantee covers individual service uptime, and stops there.
Governance reads logs after the fact and cannot intervene in a running process. Everything is
coupled to one provider's cloud, identity, data, and compute. Separate evaluation and
observability products are often required, because the runtime provides no authoritative
evidence record.

**Per vendor, the sourced specifics.**

- **Azure AI Foundry.** Six to eight separately billed services composed into a workflow:
  Azure OpenAI, Cosmos DB, AI Search, Content Safety, API Management, Event Hubs, Monitor.
  Agent Service has no SLA. Microsoft's own documentation states that the recovery point for
  stateful content can be total loss and that there is no supported method for active-active
  multi-region replication. Governance spreads across five services with no inline
  enforcement and no human intervention for running agents. Lock-in is structural: Entra ID,
  Prompt Flow YAML, Cosmos DB, and Azure OpenAI fine-tuned models.
- **AWS Bedrock.** Agents run as stateless Lambda invocations. State and memory require
  separate provisioning through DynamoDB or Aurora at roughly 150 to 200ms retrieval. No
  built-in HA or DR for agentic workloads. Guardrails run as a separate evaluation layer
  after inference, so they cannot intervene in a running process. Lock-in comes through
  proprietary agent action schemas and IAM.
- **Gemini Enterprise Agent Platform.** Dialogflow-lineage primitives with Vertex AI Pipelines
  for batch workflows. No native active-active HA or DR for agents. Memory requires external
  Spanner or AlloyDB. Safety filters and grounding run as separate API calls outside the execution path. Lock-in comes through proprietary agent schema definitions and
  Vertex-specific APIs.

**The wedge.** Akka guarantees the workload at 99.9999% with sub-1 minute RTO and zero-byte
RPO, backed by indemnities. Every hyperscaler guarantees services at 99.9 to 99.99% and
leaves the composition to the customer.

**This question proves it.** "If a region goes down, what happens to the agents that are
mid-run, and which service's SLA covers that?"

**One structural point ends the debate.** Cloud providers sell separately provisioned,
separately billed services. Running everything as one system on one bill works against how
they are built, so this gap persists.

## 4. Enterprise SaaS agents

Salesforce Agentforce, ServiceNow AI Agents, Databricks Mosaic AI and Agent Framework,
Snowflake Cortex Agents, OpenAI Assistants API and Agents SDK.

**Concede.** Each is strong for an agent that lives inside its vendor's data perimeter.
Agentforce inside Salesforce, ServiceNow for ITSM, Databricks for data-and-model-centric
agents on the Lakehouse, Cortex over Snowflake data. When the whole use case falls inside one
of those perimeters, that vendor is the right answer and Akka should not fight for it. `00-foundation.md` lists the same case as a disqualifier.

**What the customer inherits.** None of these spans CRM, ITSM, the data warehouse, custom
systems, and external partners under a single runtime, with one governance contract and one evidence record. The Einstein Trust Layer governs Salesforce data, and cross-application agents fall outside it. Unity Catalog applies data governance to agents, with no inline guardrails, no durable HITL suspension, and no runtime binding taxonomy. OpenAI Assistants
has no HA or DR, no enterprise data-residency story, and no inline policy enforcement across
model vendors.

**The wedge.** Reach. The moment a process crosses two systems, the vendor's agent stops
being the answer.

**This question proves it.** "Which of your agentic processes stay entirely inside one
application, and which cross into another system?"

## 5. AI observability and evaluation tools

Arize, LangSmith, Langfuse, Galileo, Braintrust, Helicone, Fiddler, Datadog LLM
Observability, Honeycomb, Opik and Comet, Patronus, Humanloop, Portkey, Confident AI.

**Concede.** These tools are useful for engineering observability and model A/B testing. Most accounts have already deployed one, and it does its job well. Used alongside Akka they remain useful. Say this early, because attacking a tool the team chose attacks the team.

**What the customer inherits.** These observe from outside the request path. The limits that
follow matter for the compliance record:

- Sampling is on by design, and a compliance record cannot tolerate it.
- No authority exists in the request path, so nothing can block a tool call, fail-close a response, or durably suspend an agent for a reviewer.
- Their traces are mutable and unchained, so spans can be edited, dropped, or reshaped by
  ingestion settings.
- No signed intent artifact exists: no control corpus, no signed Eval Matrix, no jurisdiction-derived obligations, no runtime binding taxonomy.
- Retention is a billing tier with no regulatory mapping behind it. Thirty or ninety days is not
  EU AI Act Article 11 at ten years, Article 26 at a six-month floor, or DORA at five years
  or more.
- Side-effect execution goes unrecorded, because only the runtime that gates the tool call sees it.

**The wedge for Verify.** No tool outside the runtime can be the governance record, because the runtime is what produces the behaviour being governed.

**The wedge for Optimize.** Grading is where they stop. Nothing trains on the grade, nothing
serves the resulting model, and nothing routes traffic to it.

**This question proves it.** "What is your sampling rate, and would an examiner accept a
sampled record?"

## 6. Systems integrators and forward-deployed engineering

Deloitte, PwC, NTT Data, Accenture, and model-vendor forward-deployed engineering teams. Some
of these are also Akka partners, which changes the conversation from competition to
co-delivery. Check the partner list before positioning against a firm.

**Concede.** Integrators deliver. A forward-deployed engineering engagement produces a working bespoke system, and the customer gets senior people on site.

**What the customer inherits.** A bespoke system they then own and operate, plus a standing
integration team, plus the knowledge of how it works living in the vendor's staff.

**The wedge.** What the customer keeps at the end. Akka Specify reaches the same production
outcome through generation on the platform, in weeks, and what remains afterwards is a factory any team can use.

**This question proves it.** "At the end of the engagement, what do you own, and who
maintains it?"

## 7. GRC platforms

ServiceNow GRC, Archer, OneTrust.

**Concede.** A GRC platform holds the policy, the control library, and the audit workflow, and the customer is not replacing it.

**What the customer inherits.** Nothing connects a control in the GRC platform to the line of
code that enforces it. There is no runtime binding, no evidence event per control, and no way
to prove that what runs is what was approved.

**The wedge.** Coexistence. The GRC platform stays as the system of record for policy. Verify
supplies the binding, the evidence event, and the conformance proof.

**This question proves it.** "When a control in there says an agent must escalate to a
human, what makes that happen in the running system?"

## 8. Side-by-side

| Dimension | Frameworks | Hyperscaler AI | Enterprise SaaS Agents | Observability and Evaluation | Akka |
|---|---|---|---|---|---|
| Category | Developer library | 6-8 separately billed services | Agents bound to one app's data | Outside the request path | One runtime with shared compute |
| Availability | None, DIY | 99.9-99.99% per service; no SLA on Agent Service (Azure) | Vendor SaaS SLA | N/A | 99.9999% on the workload, with indemnities |
| HA/DR | DIY | None for agentic workload | Vendor's HA | N/A | Active-active, sub-1 min RTO, zero-byte RPO |
| Memory latency | DIY | 150-200ms via external stores | Vendor data only | N/A | Sub-10ms native |
| Cross-app reach | Code-only | Within one cloud | Within one app | N/A | CRM, ITSM, warehouse, custom, and partner, on one runtime |
| Governance | DIY | After the fact, per service | Per-vendor data only | Reads logs after the fact | Inline runtime, fail-closed, durable HITL |
| Pre-production governance | DIY | None | None | None | Sign-off recipe engine, sealed Governance Posture Package |
| Compliance record | None | Vendor telemetry, sampled | Vendor logs | Sampled, mutable | Non-sampled, hash-chained, authority snapshots |
| Model economics | DIY | Per-token inference, separate training | Vendor models | N/A | On-runtime inference, training, grading, scoring |
| Licensing | Mixed | Proprietary | Proprietary | Proprietary | BSL, self-host and modify, no managed-service lock-in |
| Model flexibility | Any | Provider-biased | Provider-tied | N/A | Any model, any vendor |
| Sovereign cloud | DIY | Feature-lagged | None | None | Full-parity deployment, all traffic and data in-region |

## 9. What competitors say about Akka

Seven objections, with the answer and the evidence.

**"Akka is a JVM actor library from 2009."** The open-source library is the lineage. The
platform is the product. Every reliability figure comes from that heritage: production since
2007, more than 100,000 deployments, 2 billion people touched daily, 1.4 million transactions
per second, 9ms latency.

**"BSL is not open source."** Correct. BSL gives the right to run, modify, and self-host the
runtime in the customer's own environment. The comparison is against a managed hyperscaler
service where self-hosting is not offered at all.

**"You are trading one lock-in for another."** Three answers: BSL self-hosting, any model from
any vendor under the customer's own policies, and native A2A, ACP, and MCP so agents and
tools interoperate across vendors. Specify's output is specifications, which carry to any deployment.

**"Nobody has heard of Akka."** One third of the Fortune 500 has deployed Akka technology. 52 financial services institutions run it in production. Dell Technologies is the largest shareholder, a customer, and a partner. Named customers include Manulife, Verizon, Swiggy,
Tubi, Morgan Stanley, RBC, Apple, Starbucks, Walmart, and Capital One.

**"It will be more expensive than what we have."** Akka is billed on platform tier and service cores. No line is priced per call, per token, or per service. The comparison is one invoice against
six to eight separately billed services that scale independently with usage.

**"We would have to rewrite everything."** Optimize grades agents running in third-party
harnesses including Cursor, Claude Code, and Copilot, with no migration. Verify's
classification, Eval Matrix, sign-off, and Governance Posture Package apply to systems built
anywhere. Tools integrate over MCP and agents hand off over A2A and ACP.

**"You are a small company."** Operating since 2007, profitable and growing, with Dell
Technologies as largest shareholder, and more than 19 InfoSec certifications including EU AI
Act, the Singapore Agent Framework, ISO 42001, and SOC 2.

## 10. Certification

Three role plays, 15 minutes each. Pass requires a concession before every contrast, one
sourced claim per role play, and no absolute that the source material does not support.

1. **LangChain incumbent.** A Head of Platform whose prototype has been four months from
   production. The team likes LangChain and will defend it.
2. **Azure mandate.** An Enterprise Architect who opens with "we are an Azure shop, why would
   we not use Foundry." No pain stated. The learner must find one before competing.
3. **Evaluation already solved.** A VP of AI Engineering who deployed LangSmith last year,
   considers evaluation handled, and reads any Verify pitch as an attack on their decision.
