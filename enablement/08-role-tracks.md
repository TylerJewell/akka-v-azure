# Role tracks

Everyone takes the foundation, the four solution modules, routing, mandate owners,
competitive, and the scenarios. The track adds what the role does that the others do not.

---

## Account executive

### Qualification

An opportunity is real when it carries all of the following. Missing any one, it is not a forecast.

1. **A named cost with a number the customer supplied.** Akka's percentages are not
   qualification.
2. **A person who owns that cost and holds budget.** A champion without budget is an
   organiser. `07-sovereign-insurer.md` is what happens when this is missed.
3. **A trigger event with a date.** From the table in `05-routing.md`.
4. **A second thread with a different budget owner.** Single-threaded enterprise deals close
   at a rate that does not justify the forecast.

Disqualifiers are in `00-foundation.md` §8. The 30-second qualifier and the seven discovery
questions in the partner enablement brief run before any of this.

### Service tiers

Starter and Sandbox are the entry tiers. Both progress as needs grow.

| Tier | Shape | Support | Use it when |
|---|---|---|---|
| **Starter** | Akka-hosted in Akka's public cloud with a private data link back to the customer environment. One production region, monthly billing in arrears, no invoices or POs. | Included | Fastest path to a production workload without a VPC install. |
| **Sandbox** | Single region in the customer's VPC, configured for low overhead. No HA or DR. Not for production. | 9x5 | Lowest-friction evaluation inside their environment. |
| **Day 2 Ops** | Two regions in their VPC, one development and one production. Elastic scale-to-zero, live CVE patching, no-downtime rolling updates, AI explainability tooling. | 24/7 SRE, quarter-time TAM/FDE | First production commitment. |
| **Business Continuity** | Three regions in their VPC, one development plus two in HA. Active-active across regions or clouds, sub-1 minute RTO, zero-byte RPO, conflict resolution on region split. | 24/7 SRE, half-time TAM/FDE | Availability is contractual to their business. |
| **Sovereign Cloud** | Country-isolated. Traffic and data stay in-region, with local SREs and a private federation plane. China, the EU, Singapore, the UK, Japan, Australia, and more. | 24/7 SRE, two dedicated TAM/FDEs | Regulatory or sovereign residency requirements. |

**Sandbox is not an upgrade path.** Sandbox regions are not SLA-backed, and moving to a higher tier means a rebuild. Say this at the time of sale, because
discovering it later costs trust.

**Cores.** In-VPC tiers are sized around platform cores, which are Akka's infrastructure
overhead, and service cores, which are the customer's workloads. Akka charges for service
cores only. Platform cores run on cloud infrastructure the customer provisions. Sandbox
minimises platform-core overhead.

Confidential tier detail is in the internal service-tiers battlecard. Do not
quote figures from memory.

### The business case

Build it from the customer's number, in this order.

1. **The cost they stated**, in their units. Manual interventions, delayed benefit, unrealised
   revenue, penalty exposure, engineering months.
2. **What the delay costs per month.** Nearly every scenario in the library turns on this
   figure, and nearly every customer has it and has not said it.
3. **The replaced spend.** Six to eight separately billed services, plus evaluation and
   observability tooling that Akka's workloads no longer need.
4. **The Akka price**, last.

Reversing this order produces a feature comparison. Five spend-predictability and cost-
reduction categories are detailed in the total cost of ownership reference.

### Process influencers

The CFO or VP Finance must approve multi-year pre-paid commitments and cares about TCO,
predictability, and ROI timeline. Procurement and legal scrutinise multi-year pre-paid deals
and care about contract terms, SLAs, and vendor viability. Neither role is a champion, and both can stop a deal in the last three weeks. Reach them before the quarter they will decide in.

### Track exercise

Take a live opportunity. Produce a one-page account plan naming the four qualification items,
the second thread with its budget owner, the tier and why, and the business case built in the
order above. Present it in ten minutes and defend the tier choice.

---

## Forward-deployed engineer

### The delivery methodology

Five phases move a team from AI idea to production system. The first milestone is a production
slice in 4 to 6 weeks.

| Phase | What it produces |
|---|---|
| **Frame** | The first production slice selected, with a use-case brief, system map, role map, success metrics, milestones, owners, and acceptance criteria. |
| **Govern** | Runtime controls, autonomy policy, risk model, decision rights, sign-off recipes, HITL gates, retention, audit plan, and policy record. |
| **Specify** | The functional AI implementation via Akka Specify: services, agents, integrations, ontologies, workflow models, API contracts, scenarios, eval criteria, and edge cases. |
| **Ship** | The production slice deployed, with release package, runbook, cutover plan, SLA view, metrics, alerts, dashboards, review queues, overrides, and feedback capture. |
| **Improve** | Feedback loops, behaviour metrics, token analysis, cache strategy, routing plans, tuning backlogs, and release cadence. |

Govern precedes Specify. A risk envelope defined after the system is built is a retrofit, and
the whole Verify argument is that safeguards are bound at generation.

### Scoping a production slice

A slice is production when it carries real traffic, has an owner who accepts it, and has its
controls bound. A slice that only demonstrates does not meet that definition.

Four questions size one:

1. What is the smallest complete path from a real input to a real business outcome?
2. Which of the six specifications is least defined today, and who owns defining it?
3. What controls does this slice's risk envelope produce, and which bind to G, H, W, or K?
4. Who accepts it, and against which acceptance criteria?

Question 3 is where slices go wrong. A slice whose controls require durable HITL is not a
two-week slice.

### The specifications in practice

The customer supplies goals and intent, functional requirements, risk envelope, knowledge
sources, operational envelope, and improvement policy. In practice the risk envelope and the
improvement policy arrive empty, and the FDE's job in Frame and Govern is to fill them with the customer in the room.

### Harnesses

`/akka:harnesses` generates project-adapted enterprise-configuration assets into `/harnesses`,
records them in the lock file, and surfaces each for approval. Know what this produces before
the Govern phase, because it is what the customer's InfoSec team will review.

### Track exercise

Take scenario 5 or 9 to the point of a signed engagement, then produce the Frame deliverable:
the slice selected, the acceptance criteria, the owner, and the milestone plan across four to six weeks. Defend the size of the slice.

---

## Field CTO and solution architect

### The whiteboards

Draw each from memory in under four minutes. These carry the technical conversation, and
slides are the fallback.

1. **One runtime against the per-service stack.** Eight boxes with eight bills and seams the
   customer owns, beside one box with shared compute. The claim underneath is that the guarantee applies to the whole system because the runtime is one system.
2. **The durability sequence.** An agent mid-task, a node dies, the journal replays, the run
   resumes at the last completed step. Extend it to a deployment and to a three-day human wait. `01-solution-akka-sdk.md` carries this demo.
3. **The guardrail boundary.** A tool call held by the runtime, the guardrail returning PASS,
   BLOCK, or ERROR, failing closed, and the `GuardrailDecisionRecorded` event written in the
   same transaction. Contrast with a mirror that fires after the side effect.
4. **Regulation to running code.** A regulation, a control row with its citation, its runtime
   binding class, and its evidence event, then the generated artifact and the event stream an
   auditor receives. The seven binding classes are the vocabulary.
5. **The optimization loop.** Trace, grade, train, shadow, promote, serve, grade again, on one
   record. Mark where a competitor's loop requires an export.
6. **Active-active and sovereign.** Two regions both taking writes, sub-1 minute RTO,
   zero-byte RPO, conflict resolution on split, and a country-isolated configuration with
   traffic and data in-region.

### The demo sequence

Assets are in the demo library and the deck library. Run them in this order:

1. **Kill something.** Durability first, because it is the claim no competitor can demo.
2. **Block something.** A guardrail decision and the event it wrote. Show the event, because risk officers care about the record.
3. **Wait.** Suspend for a human decision, deploy over the top, resume.
4. **Only then, build something.** Spec-driven generation lands after the audience believes
   the runtime.

Leading with generation invites the "AI wrote this code" objection before any credibility
exists.

### The technical win plan

Write it down before the proof of concept starts. A proof of concept with no written exit
criteria runs forever.

- The claims the customer needs proven, in their words.
- The measurement for each, and who reads it.
- What the customer commits to do if the claims hold.
- The date.

Refuse a proof of concept spread across several use cases. `09-transformation-
officer.md` covers why.

### The InfoSec review

The CISO or security lead is always involved and always runs a detailed review. Prepare:
19+ InfoSec certifications including EU AI Act, the Singapore Agent Framework, ISO 42001, and
SOC 2; deployment options across Akka's cloud, the customer's hyperscaler VPC, and their own
Kubernetes; zero-trust networking; SPIFFE workload identity and the delegation chain; and the
six retention categories with legal hold.

### Track exercise

Deliver whiteboards 1, 3, and 4 to a hostile technical audience in twelve minutes total, then
write a technical win plan for scenario 4 or 6.

---

## Partner

Partners take the foundation, every solution module, routing, mandate owners, and scenarios 8 and 9. This track replaces the AE track.

### Sourcing and qualifying

The partner enablement brief is the working document: ideal customer profile,
verticals that convert, trigger events, the seven discovery questions that qualify in fifteen
minutes, the persona map, outreach hooks by cost, disqualifiers, the 30-second qualifier, and
competitive landmines.

Routing is what this program adds to it. The brief tells a partner which accounts to call.
`05-routing.md` and `06-mandate-owners.md` tell them what to lead with once someone answers.

### Deal registration and handoff

Follow the process in the partner enablement brief. Register on the first qualified conversation. Registration protects the partner's position when a
second route into the account appears.

### Co-delivery

Three engagement models, with the customer-owned factory leading. A partner operating a
customer's factory is the model that produces the most follow-on work, and it is the frame
that converts an incumbent integrator from a blocker into an advocate. `05-integrator-
incumbent.md` runs this end to end.

Partners who resell: NTT Data embeds and resells Akka as the runtime under its Enterprise
Agentic Grid. Go-to-market partners include Deloitte, PwC, NTT Data, AVOWS, and BAE. Check the
partner list before positioning against any firm.

### Track exercise

Run scenario 8, then run scenario 5 from the other side of the table. Scenario 5 is where the
partner-conflict rule stops being theoretical.
