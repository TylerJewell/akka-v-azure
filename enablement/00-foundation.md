# Foundation

Every role takes this module first, including partners. The module establishes the fact base the
rest of the program routes against.

---

## 1. What Akka is

Akka is an agentic AI platform for enterprises. The platform runs the whole agentic system in a single runtime: the agents, their memory, orchestration, guardrails, evaluations, training,
and inference. That runtime guarantees resilience and scalability, so a system that compiles
on Akka is ready for production.

Akka is distinct from the open-source Akka actor library and toolkit for the JVM. That
library, formerly maintained by Lightbend, is the lineage. The platform is the product. A
prospect who says "we used Akka years ago" is talking about the library, and the answer is
that the same runtime underneath that library now runs the platform.

The runtime has run in production since 2007 across more than 100,000 deployments. More
than 2 billion people touch an Akka-powered application every day. 52 financial services
institutions run Akka in production. One third of the Fortune 500 has deployed Akka
technology. Dell Technologies is the largest shareholder, a customer, and a partner.

## 2. The offering and the solutions on it

Akka has one offering: the Akka Agentic AI Platform. Four solutions run on it, over a shared runtime with a single evidence record and a single governance model. A customer can use any one of them
on its own.

- **Akka SDK** is the component model and runtime for building agentic systems.
- **Akka Specify** is spec-driven development and delivery of governed systems.
- **Akka Optimize** routes traffic to the best open-weight model and trains smaller ones on
  your data.
- **Akka Verify** is runtime-native evaluation, enforcement, evidence, and governance for
  agents built on Akka or elsewhere.

A customer builds on the platform, or Akka delivers and runs a production system for them. The delivered path is Akka Specify. Both paths run the same
runtime.

## 3. Why efficiency decides the market

The cost of intelligence is dropping up to 10x each year. Frontier capability that cost
thirty dollars per million input tokens in 2023 costs cents today at equivalent capability.

Demand rises as that price falls. Every capability release multiplies the AI use cases an enterprise can adopt. Jevons Paradox applies to intelligence: as the unit cost of
intelligence falls, enterprise AI demand accelerates.

When capability is cheap and demand is unlimited, execution efficiency decides which
enterprises scale AI adoption. Inefficiencies compound as deployments grow:

- AI applications spend 30 to 40% of revenue on cost of goods sold, against 10 to 15% for
  typical SaaS.
- GenAI projects that scale past pilot run 2x to 3x over cost.
- 20 to 40% of engineering capacity is lost to rework caused by earlier architectural
  choices.
- Switching cost off a first-choice runtime grows non-linearly with the size of the
  deployed base.

Akka removes those inefficiencies at the smallest scale, so none of them compound as a deployment grows.

Sources: vendor API pricing pages March 2023 through 2026; Stanford AI Index 2025 and Epoch
AI for cost-per-capability curves; Andreessen Horowitz for cost compression; McKinsey State
of AI 2024 and Deloitte for adoption; BCG and Deloitte for cost overruns; W. Brian Arthur
for path dependence.

## 4. The cost each solution removes

Everything in this program routes against this table. Learn it before anything else.

| Solution | Cost removed | Mechanism | Proof |
|---|---|---|---|
| **Akka SDK** | Infrastructure | Agents, memory, orchestration, streaming, and endpoints run on shared compute inside one runtime. Actor-based concurrency and that shared model drop operating costs up to 90%. | Fox shrank its AI personalization engine from 150,000 cores to 22,000 after porting to Akka. |
| **Akka Specify** | Rework | Developers and non-developers write plain-language specifications, and every change is verified against them, so code never drifts from spec. Technical and knowledge debt stop accumulating. | Dojo put AI-based merchant onboarding into production in weeks, built by college graduates. |
| **Akka Optimize** | Token spend | Akka trains smaller models on your data and routes work to them as they improve. You own the models. | Swiggy cut prediction latency from 144ms to 71ms while reducing token consumption 22%. |
| **Akka Verify** | Governance effort | Risk teams define policies once. The runtime enforces them across every agent, against 190 global regulations. | Manulife rolled Akka out to 2,000 developers in 6 countries under central risk control. |

## 5. Every capability is a property of one runtime

Akka runs every part of an agentic system in one runtime. Agents, memory, orchestration,
streaming, endpoints, guardrails, evaluations, training, and inference are properties of that
runtime, which handles clustering, resilience, failover, scaling, and traffic steering.

Hyperscalers offer comparable breadth of AI capability, delivered as separate services. The
customer provisions each service, connects them, and operates the result. The customer
configures failover, handles scaling, load-tests, and hardens the system before it carries
real traffic. The integration between those services belongs to the customer to build and to
keep working.

The single runtime produces the results below.

- A system that compiles is ready for production, because the runtime already provides the
  reliability and scale that otherwise take months to build and harden.
- AI costs come down over time, because inference, training, grading, and scoring run next
  to the agents. The loop that trains smaller, cheaper models stays inside one system.
- Guardrails and policies are enforced while the agent works, because the runtime that
  executes the agent is the same runtime that enforces the rules and keeps the record.

Cloud providers sell separately provisioned, separately billed services. Running everything
as one system on one bill works against that business model.

### Every problem has one correct form

The single runtime admits one correct form for durable state, one for orchestration, and one
for an endpoint. The constraint does not limit what a system can do or how far it scales, and
it keeps the SDK small. A small SDK with one form per problem is a golden path expressed as
an API.

Generated code works for the same reason. A model writing against an API that offers six
plausible ways to persist state picks one that compiles and does not survive a restart. An
API with one form gives the model one form to write.

Akka Specify extends those paths across the lifecycle. Specification, plan, tasks,
implementation, review, build, and deploy each run as a governed step, verified as it
completes. A team running the full sequence has an automated software factory, and work moves
from idea to production in hours. A developer with no distributed-systems background reaches
the same result, because the path is the one the runtime already enforces.

## 6. The guarantees that no other vendor offers

Know these by heart. Each is a claim a competitor cannot answer, and each carries contractual weight.

1. **99.9999% availability on the agentic workload**, with sub-1 minute RTO and zero-byte
   RPO, backed by indemnities. Cloud AI services offer per-service SLAs at 99.9 to 99.99%,
   and none guarantee the workload itself.
2. **Sub-10ms native agentic memory.** Most platforms expose memory as a roughly 200ms
   add-on requiring DynamoDB, Spanner, AlloyDB, Cosmos DB, or an equivalent store.
3. **Up to 90% lower infrastructure cost** through shared compute for orchestration, agents,
   memory, streaming, APIs, governance, and model economics.
4. **A non-sampled, hash-chained interaction log with authority snapshots**: SPIFFE workload
   identity, the delegation chain from human to agent to sub-agent to tool, effective
   permissions, and policy bindings resolved at execution and embedded in every event.
5. **Durable human-in-the-loop suspension** across crashes, deployments, and days. An agent
   paused for review resumes exactly where it stopped, with no state loss and no replay.
6. **BSL licensing on the runtime**, so the customer keeps the right to run, modify, and
   self-host the platform in their own environment.

Two more that matter in governance-led deals: full-parity sovereign cloud deployment that
preserves HA and DR across China, Hong Kong, Singapore, North America, Canada, and the EU;
and bidirectional conformance, where the runtime reconstructs an Eval Matrix from the
controls the deployed code enforces and compares it against the signed one.

## 7. What Akka is not

Reps lose credibility by claiming ground Akka does not hold. Concede these directly.

- **Not a desktop agent or workforce copilot.** Claude Code, Copilot, and Glean inherit a user's identity and stop when the session closes. Each is the right tool when a specific human is driving. Akka runs processes unattended, under their own governed service
  identity.
- **Not the open-source Akka actor library.**
- **Not a public model-serving marketplace or a foundation-model pretraining platform.**
  Akka Optimize does reinforcement learning, fine-tuning, and distillation against a
  customer's own agents and data.
- **Not a vector database or a standalone semantic knowledge layer.** When a system needs
  semantic knowledge, Akka Specify delivers and integrates that layer as part of the system
  it builds.
- **Not the customer's context graph**, meaning the modeling of their business across all
  domains that feeds the agentic AI layer.

## 8. Disqualifiers

Walk away, or park until the trigger arrives:

- A single-agent internal productivity tool with no production SLA and no compliance
  exposure.
- A team that has not yet built anything and has no funded use case. Send them to the docs.
- An account whose entire agent estate lives inside one SaaS vendor's data perimeter and
  never leaves it. Agentforce or Cortex is the right answer.
- A pure model-hosting or GPU-capacity requirement.
- A prospect who wants a chatbot on a website with no state, no tools, and no audit
  requirement.

## 9. The 90-second platform statement

Memorize and deliver this live. The delivery is the certification for this module.

> Akka is an agentic AI platform for enterprises. The platform runs every part of an agentic system in
> one runtime: the agents, their memory, orchestration, guardrails, evaluations, training,
> and inference. That runtime guarantees resilience and scalability, so a system that
> compiles on Akka is ready for production.
>
> Four solutions run on that platform, and each one removes a cost.
>
> Akka SDK removes infrastructure cost. Everything runs on shared compute, which drops
> operating costs up to 90%. Fox went from 150,000 cores to 22,000.
>
> Akka Specify removes rework. You write specifications in plain language and every change
> is verified against them, so the code cannot drift from the spec. Dojo put AI-based
> merchant onboarding into production in weeks, built by college graduates.
>
> Akka Optimize removes token spend. Akka trains smaller models on your data and routes work
> to them as they improve, and you own the models. Swiggy cut prediction latency from 144ms
> to 71ms at 22% fewer tokens.
>
> Akka Verify removes governance effort. Risk teams define policies once, and the runtime
> enforces them across every agent against 190 global regulations. Manulife rolled Akka out
> to 2,000 developers in 6 countries under central risk control.
>
> You can start with any one of them. Every solution shares the same runtime, the same
> evidence record, and the same governance model.

Delivery standard: 90 seconds or under, no notes, every number correct, and the four proofs
attached to the right solutions.

## 10. Fact check

Twenty questions. Eighteen correct to pass.

1. How many offerings does Akka sell, and what is it called?
2. Name the four solutions.
3. What cost does each solution remove?
4. Name the customer proof for each solution and the figure attached to it.
5. What is the availability guarantee, and does it cover the workload or each service?
6. What are the RTO and RPO figures?
7. What is Akka's memory latency, and what is the typical figure for an external store?
8. What licence covers the runtime, and what right does it give the customer?
9. How many AI regulations and controls are in the corpus, and how many controls carry
   financial penalties?
10. How many controls does a typical system draw from that corpus?
11. What are the six specifications that go into Akka Specify?
12. Name the seven runtime binding classes an Eval Matrix control row compiles to.
13. What is a Governance Posture Package?
14. What does Akka Optimize grade, and does it work for agents that do not run on Akka?
15. Name the five service tiers.
16. What is the first milestone of the delivery methodology, and how long does it take?
17. Name the things Akka is not.
18. What is the difference between Akka and the open-source Akka actor library?
19. Why can an observability tool not serve as the compliance record for an EU AI Act
    system? Give the reasons.
20. Which four inefficiencies compound as AI deployments grow?

Answers live in the Akka positioning reference. A learner who cannot find an answer there should
not be given it verbally.
