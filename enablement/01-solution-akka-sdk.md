# Akka SDK — removes infrastructure cost

## 1. The cost and who pays it

Akka SDK removes infrastructure cost. Agents, memory, orchestration, streaming, and
endpoints run on shared compute inside one runtime, and that shared model together with
actor-based concurrency drops operating costs up to 90%.

The people who pay this cost:

| Role | What they own | What they say |
|---|---|---|
| CTO, VP Engineering | Technical architecture, build versus buy | "The prototype works and we cannot get it to production." |
| Head of Platform, PlatformOps | The internal platform every team builds on | "Every team is solving the same distributed-systems problems." |
| Enterprise Architect | Fit with the existing stack | "We are assembling seven services and we own every seam." |
| SRE, DevOps lead | Availability, HA and DR, incidents | "We cannot fail over an agent. There is nothing to fail over to." |
| CIO | Systems development and operational SLAs | "Who guarantees this stays up?" |

## 2. The customer challenge

Four problems bring this buyer to the market.

**The prototype-to-production gap.** An agent demo built on a framework works on a laptop. Production means clustering, resilience, identity, retries, backpressure,
circuit breakers, failover, and an audit trail. The work runs to months, and the customer's own engineers do it.

**The per-service bill.** A typical enterprise agentic deployment on Azure, AWS, or GCP
requires separately provisioned and billed services for model inference, agent
orchestration, memory and state storage, event streaming, an API gateway, observability and
logging, content safety and guardrails, and inter-service egress. Enterprise Agreements
reduce the per-service rate and do not change the architecture. Six to eight bills compound
with scale.

**State loss.** An agent that fails mid-task on a stateless invocation model starts over.
An agent that waits for a human decision cannot wait across a deployment. The customer
either builds durability themselves or accepts lost work.

**The specialist bottleneck.** Distributed-systems engineers are scarce, and every team
that builds agents needs one. Delivery is gated on hiring.

## 3. Capabilities and core features

**Components.** Agents and workflows carry behaviour. Event-sourced entities and key-value
entities carry durable state. Views are read-side projections queryable over gRPC or HTTP.
Endpoints expose HTTP, gRPC, and MCP. Timers schedule delayed and recurring work. Consumers
and streaming connect the system to event sources.

**Agentic features.** Multi-agent orchestration over A2A and ACP. Tool integration over MCP.
Autonomous and sequential agents with tools and handoffs. Real-time stream processing for AI
feedback loops. Durable memory with sub-10ms read and write.

**Durability.** State is durable by default and replayable from its event journal, with
snapshots. An agent that fails mid-task resumes from where it stopped. The runtime supplies execution checkpointing, retries, backpressure, throttling, and circuit breakers, so none of them are written into the application.

**Runtime.** Clustering, resilience, zero-trust networking, data sharding, and traffic
steering. Active-active HA and DR across geographies or clouds. Elastic scaling to 10
million agentic TPS with scale-to-zero. No-downtime rolling updates and live CVE patching.

**Deployment.** Akka's cloud, inside the customer's hyperscaler VPC, or on their own
Kubernetes. The runtime is BSL-licensed, so the customer keeps the right to run, modify, and
self-host it.

**Measured performance.** 99.9999% multi-region availability, 1.4 million transactions per
second, 9ms latency, sub-1 minute RTO, zero-byte RPO.

## 4. The mechanism

Every capability draws on the same compute and is billed once. There is no separate memory
charge, no streaming charge, and no observability charge, because they are properties of the
platform. Five mechanisms produce the cost reduction: shared compute in place of per-service
billing, sub-10ms native memory in place of per-query external stores, scale-to-zero in
place of always-on service minimums, no inter-service egress, and built-in evaluation,
guardrails, observability, governance, and model economics in place of separate tooling
purchases.

Fox is the measurement: an AI personalization engine that shrank from 150,000 cores to
22,000 after porting to Akka.

The single runtime also decides the shape of the SDK. One correct form exists for durable
state, one for orchestration, and one for an endpoint, so the SDK stays small. A developer
with no distributed-systems background writes the same code a specialist would, and a model
generating that code has one form to generate. Change velocity follows from that. Every team
ships along the same path, and the path is the one the runtime already enforces.

## 5. Differentiators

**Against agentic frameworks (LangChain, CrewAI, Autogen, Letta, n8n).** Frameworks
accelerate the prototype. Clustering, resilience, identity, governance, evidence, and
multi-region failover are the customer's work. LangChain has no runtime, no HA or DR, no
operational guarantees, and no built-in governance.

**Against durable-execution orchestrators (Temporal, trigger.dev, LangGraph).** Concede the
real ground first: these products do provide durable execution, and LangGraph has
checkpoint persistence. The distinction is explicit versus implicit. Temporal and LangGraph make durability a programming model the developer opts into by
structuring code a certain way, declaring retry policies, and wiring backpressure and
circuit breakers. Akka makes durability and resilience properties of the runtime, so an agent gets retries,
backpressure, throttling, circuit breakers, durable memory, execution checkpointing, and a
tamper-evident audit log by running there. Akka also offers the explicit model through
workflows and sagas when a developer wants it. Temporal has no agents, no memory, and no
governance.

**Against hyperscaler agent services.** Azure AI Foundry Agent Service has no SLA, and
Microsoft's own documentation states that the recovery point for stateful content can be
total loss and that there is no supported method for active-active multi-region replication.
AWS Bedrock runs agents as stateless Lambda invocations, with state and memory provisioned
separately through DynamoDB or Aurora at roughly 150 to 200ms retrieval. Gemini Enterprise
Agent Platform has no native active-active HA or DR for agents and requires external Spanner
or AlloyDB for memory.

**On code an AI assistant writes.** Frameworks expose several ways to do the same thing, and a
model writing against them produces code that compiles and fails under load. Akka's component
model gives a generator one form per problem, so generated Akka services reach production.
Raise this in any account already running Cursor, Claude Code, or Copilot against their
backend.

**The claim to lead with.** Akka guarantees the workload at 99.9999% with sub-1 minute RTO and
zero-byte RPO, backed by indemnities. Hyperscaler SLAs cover individual services, and the
reliability of how those services connect belongs to the customer.

## 6. Use cases and quick wins

**Use cases that fit.** High-throughput transaction processing with agents in the path.
Multi-agent orchestration spanning CRM, ITSM, warehouse, custom systems, and partners.
Real-time personalization and recommendation. Agentic workflows with human approval steps
measured in days. Systems that must run active-active across regions or inside a
jurisdiction.

**Quick wins that land in one meeting.**

- *Port one failing agent.* Start from the workflow that fails mid-task today.
  Rebuild that workflow on Akka and show it resume across a forced node kill.
- *Count the cores.* Take the customer's current agent workload and size it on shared
  compute. Fox is the reference point for the size of the answer.
- *Kill a region.* Show active-active failover with sub-1 minute RTO on a live workload. No
  competitor in the agentic category can run this demo.
- *Wait three days.* Start an agent, pause it for a human decision, deploy over the top of it, and resume it. The Bedrock conversation ends on this demo.
- *Generate a service in the meeting.* Have the customer's own AI coding assistant write an
  Akka service against the component model, then run it. Teams that have watched generated
  code fail on other stacks recognise the difference without being told.

## 7. Discovery questions

1. Walk me through what happens today when an agent fails halfway through a task.
2. How many separately billed services are in the path of one agent request right now?
3. Where does agent memory live, and what does a read cost you in milliseconds?
4. What is your availability commitment to the business on an agentic workload, and who
   signed it?
5. If a region goes down, what happens to agents that are mid-run?
6. How many people on your team can debug a distributed-systems failure, and how many teams
   are waiting on them?
7. What did the last prototype-to-production transition take in weeks?
8. What happens to the code your AI assistants generate between the pull request and
   production?

Question 7 is the qualifier. An answer over eight weeks means the deal is real.

## 8. Objections

**"We already have Kubernetes and we can build this."** They can. The question is what it
costs and how long it takes to reach the guarantees. Ask what their current availability
commitment on an agentic workload is and who signed it. Most have none, because nobody will
sign one.

**"We are standardised on LangChain."** Akka is not a replacement for how they write agent logic. Akka is where that logic runs. Agents on Akka use MCP for tools and A2A for handoffs,
so the integration surface stays open. Lead with the production gap.

**"Temporal already gives us durable execution."** Correct, and concede it. The gap is the
rest of the system: no agents, no memory, no governance, no evidence record. Ask what they run alongside Temporal for agents, memory, governance, and evidence, and count the bills.

**"BSL is not open source."** Correct. BSL gives the right to run, modify, and self-host in
their own environment, which is the property that matters for exit risk. The comparison is
against a managed hyperscaler service, where self-hosting is not offered at all.

**"Actors are legacy."** Actor-based concurrency is the mechanism behind the cost number,
and the runtime has been in production since 2007 across more than 100,000 deployments. The
customer is not buying an actor library, they are buying the runtime it produced.

## 9. What to send after the call

- `akka.io/guides/agent-fails-mid-task`
- `akka.io/guides/where-agent-memory-lives`
- `akka.io/guides/five-agents-to-a-hundred`
- `akka.io/guides/in-flight-work-during-deployment`
- `akka.io/guides/retry-without-repeating-side-effects`
- `akka.io/guides/agents-in-more-than-one-region`
- `akka.io/guides/developer-without-distributed-systems`
- Case studies: Fox, Verizon (750% order processing capacity, 6s to 2.4s), Tubi
- Comparison page matching the incumbent, and the battlecard for meeting preparation

## 10. Certification

Run a 20-minute discovery call against a facilitator playing a Head of Platform who has a
LangChain prototype four months from production. Pass requires: five of the seven discovery
questions asked, the production gap named before any Akka capability is described, one
quick win proposed with a date, and a second cost named that belongs to someone not in the
room.
