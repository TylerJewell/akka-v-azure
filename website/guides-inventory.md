# Guides — the question inventory

Working document. The candidate set for `akka.io/guides`, derived from what the platform
does differently rather than from a layout that looked balanced.

## The test each question has to pass

1. **Someone types it.** It is a question in the words a practitioner would use, not a topic
   heading.
2. **The answer differs.** Akka's answer is materially different from what a framework or a
   per-service stack gives you. Where the honest answer is "same as everyone," there is no
   page.
3. **No two questions share an answer.** Two pages with one answer compete with each other
   in search and split the citations.
4. **It is a pre-decision question.** Someone who already chose Akka is served by
   `doc.akka.io`. This corpus is for someone comparing approaches.

**Count: 49 questions across nine areas.** Thirty-eight are pre-decision. Six sit on the
line and are marked. Five are documentation.

---

## A. Durability and failure

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| A1 | What happens when an agent fails mid-task? | Durability is a runtime property, so a run resumes at the last completed step | **Guide** |
| A2 | What happens to in-flight work during a deployment or node drain? | Rescheduling and journal replay, with no maintenance window | **Guide** |
| A3 | How does an agent wait days for a human decision? | Durable HITL suspension across crashes and deployments, with no polling | **Guide** |
| A4 | How do you retry an agent step without repeating its side effect? | The runtime records whether a tool call executed, not only that it was requested | **Guide** |
| A5 | What happens when a model call hangs rather than fails? | Timeouts as a runtime concern rather than application code | Line call |

## B. State and memory

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| B1 | Where should an agent's memory live, and what does it cost per turn? | Sub-10ms native memory against a 150–200ms external store round trip | **Guide** |
| B2 | How do you reconstruct what an agent knew when it decided? | Event journal plus views, replayable rather than sampled | **Guide** |
| B3 | How do you stop context from growing without bound? | Memory compaction as a platform behaviour, and its effect on token spend | Line call |

## C. Streaming and flow control

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| C1 | What happens when an agent produces work faster than the consumer can take it? | Backpressure as a property of the runtime, propagated end to end | **Guide** |
| C2 | What happens when a model provider rate-limits you mid-run? | Upstream pressure absorbed by the runtime rather than by retry code in the agent | **Guide** |
| C3 | How do you apply a guardrail to a response that is still streaming? | Inline enforcement in the transactional path, before a partial response is emitted | **Guide** |
| C4 | How do you feed real-time data into an agent's context? | Stream processing in the same runtime that executes the agent | **Guide** |
| C5 | What happens to queued agent work when traffic spikes? | Elastic scaling with scale-to-zero, without a queue to operate | Line call |
| C6 | How do you stream a partial response while the agent is still working? | Streaming as a first-class component | Docs |

## D. Cost and scale

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| D1 | Why do agent costs rise faster than agent traffic? | Eight separately metered services against one shared runtime | **Guide** |
| D2 | What changes between 5 agents and 100? | Concurrency, partial failure, and retries that never surface in a prototype | **Guide** |
| D3 | How do you measure whether a cheaper model actually saved money? | Cost per verified task, priced on runs that passed their evaluations | **Guide** |
| D4 | What do you pay for when agents are idle? | Scale-to-zero against always-on service minimums | Line call |

## E. Models and routing

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| E1 | How does a request get routed to the right model? | Per-task routing across vendors under your own policies | **Guide** |
| E2 | When does routing to a smaller model make sense? | Evaluated production traffic identifies the work a smaller model can take | **Guide** |
| E3 | Where does the training data for a smaller model come from? | The trace that was graded is the trace that trains, with no export step | **Guide** |
| E4 | What does it take to train a smaller model on your own data? | Reinforcement learning and distillation from an open-weight base, in your environment | **Guide** |
| E5 | How do you know a smaller model is good enough to promote? | A candidate shadows live traffic and is promoted when quality holds and tokens drop | **Guide** |
| E6 | Who owns a model trained on your data, and can you take it elsewhere? | Tuned from an open-weight base in your own environment, so the weights are yours | **Guide** |
| E7 | Does training on production traffic create a compliance problem? | Sanitizers, residency, and the evidence record governance already uses | **Guide** |
| E8 | Can Akka optimize agents that do not run on Akka? | Grading works against third-party harnesses such as Cursor, Claude Code, and Copilot | **Guide** |
| E9 | What happens when a promoted model degrades later? | Online evaluation against the governance record, with the gate as the rollback point | Line call |

## F. Governance and control

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| F1 | How do you stop an agent before it acts? | Inline enforcement in the request path rather than observation after the fact | **Guide** |
| F2 | What evidence does an auditor actually ask for? | Non-sampled, hash-chained interaction log with authority snapshots | **Guide** |
| F3 | How do you prove the system running is the system that was approved? | Bidirectional conformance against a signed Eval Matrix, on demand | **Guide** |
| F4 | Who is accountable when an agent acts on a person's behalf? | Governed service identity with its own credentials and delegation chain | **Guide** |
| F5 | How do you know which regulations apply to what you are building? | Classification against 190 regulations and 1,230 controls | **Guide** |
| F6 | How do you test an agent against a policy before it ships? | Deploy gates bound to the control set rather than a review checklist | Docs |

## G. Operations and deployment

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| G1 | What does it take to run agents in more than one region? | Active-active with sub-1-minute RTO and zero-byte RPO | **Guide** |
| G2 | How do you keep agent data inside a jurisdiction? | Full-parity sovereign deployment that preserves HA and DR | **Guide** |
| G3 | How do you upgrade an agentic system without downtime? | No-downtime rolling updates and live CVE patching | Docs |
| G4 | What do you monitor on an agentic system that you do not monitor on a service? | Interaction-level capture rather than request-level metrics | Docs |

## H. Evaluation and quality

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| H1 | How do you evaluate an agent with no single right answer? | Deterministic evaluators for structured output, LLM judge for unstructured | **Guide** |
| H2 | How do you catch quality drift after deployment? | Online evaluation against the same record governance uses | Docs |

## I. Rollout and delivery

Every other area asks what the system does at runtime. This one asks what the organisation
does: who is allowed to build, how consistently, across how many teams and jurisdictions.

| # | Question | What makes the answer different | Intent |
|---|---|---|---|
| I1 | How do you let non-developers build agentic systems without losing control? | Plain-language specifications compile to the same governed system a developer would produce | **Guide** |
| I2 | How do you keep hundreds of developers across regions building the same way? | Golden paths and specifications as the contract, with central risk control | **Guide** |
| I3 | What stops code from drifting away from what was specified? | Every change is verified against the specification and blocked before it merges | **Guide** |
| I4 | How do you onboard a developer with no distributed-systems background? | The runtime provides the distributed-systems behaviour, so skill level stops gating delivery | **Guide** |
| I5 | What does a specification actually contain? | Goals, functional requirements, risk envelope, knowledge sources, operational envelope, improvement policy | **Guide** |
| I6 | How do you test a system that was generated rather than hand-written? | Scenarios, evaluation criteria, and edge cases each trace back to the requirement that produced them | **Guide** |
| I7 | Where does spec-driven delivery fit with the tools we already use? | It runs inside the repos, CI, and AI assistants the team already has | **Guide** |
| I8 | Who maintains the system after it is delivered? | You own and extend it on the platform, or it stays fully managed | **Guide** |
| I9 | How do you enforce different rules in different regions from one delivery model? | The risk envelope compiles to the safeguards enforced at runtime, per jurisdiction | **Guide** |
| I10 | What happens to technical debt over the life of the system? | Specifications live with the code, so debt prevention is a guarantee rather than a practice | Line call |


---

## Changes from the first pass

**Rollout and delivery was missing, and it is a different axis.** Areas A to H all ask what
the system does at runtime. Akka Specify is about who is allowed to build, how consistently,
across how many teams and jurisdictions. The first two passes had no category that could
hold that question, so none got written.

**Architecture is gone.** Agent-versus-workflow, multi-agent coordination, and exposing an
agent over MCP were all in the first list. They are post-decision questions, and
`doc.akka.io` already covers orchestration and MCP endpoints, so they were never gaps.

**Streaming and flow control is new, and it should have been there first.** Backpressure is
the oldest competence in the lineage and the first list reduced it to one line call. Five of
the six questions here have answers a framework cannot give, because flow control has to be
a property of the runtime that executes the work.

**Models and routing is new and is the largest area.** The first pass took its categories
from `/efficiency`, which compresses Akka Optimize into a single table row, and the
inventory inherited that compression.

**One merge.** "Test a prompt change without shipping it" and "know a smaller model is good
enough" have the same answer — shadow the candidate, gate on the metric — so they are one
page, E5.

## What I cannot tell you

No keyword volume, no ranking data, no Search Console access. Every intent judgment is from
what the question sounds like rather than evidence anyone searches it. Before committing to
thirty-eight, the list is worth checking against real query data, which would also surface
questions this inventory still misses.

## Suggested first batch

Eight, so the hub launches written rather than stubbed, with every area that carries weight
represented:

- **A1** What happens when an agent fails mid-task *(drafted)*
- **A3** How does an agent wait days for a human decision?
- **C1** What happens when an agent produces work faster than the consumer can take it?
- **C3** How do you apply a guardrail to a response that is still streaming?
- **D1** Why do agent costs rise faster than agent traffic?
- **E3** Where does the training data for a smaller model come from?
- **E6** Who owns a model trained on your data?
- **F2** What evidence does an auditor actually ask for?

Every one has an existing page to link from: all 14 compare pages discuss durability,
`/efficiency` carries the cost argument, `/platform/optimize` carries routing and training,
and `/platform/verify` carries governance.
