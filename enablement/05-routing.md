# Routing

Akka sells one offering. Which of the four solutions leads a conversation depends on which
cost the person in front of you pays. Routing is the skill this program exists to build.

---

## 1. The model

The cost a person owns and the sentence they said decide the entry solution. When the two
disagree, the sentence wins.

**Input one: the cost the person owns.** Title is the prior.

| Cost | Owner | Entry solution |
|---|---|---|
| Infrastructure, and the work of hardening to production | CTO, VP Engineering, Head of Platform, Enterprise Architect, SRE lead, CIO | Akka SDK |
| Rework, and delivery time across teams | CIO, Head of Delivery, VP Engineering, line-of-business owner, Head of Modernization | Akka Specify |
| Token spend | CFO, VP Finance, FinOps, CAIO, AI/ML engineering lead, Head of Data Science | Akka Optimize |
| Governance effort | CRO, CISO, Chief Compliance Officer, DPO, Head of Model Risk, Head of Internal Audit | Akka Verify |

**Input two: the sentence they said.** The stated pain is evidence, and it beats the title.

| What you hear | Entry solution |
|---|---|
| "It works in the demo and we cannot get it to production." | SDK |
| "We are paying for eight services to run one agent." | SDK |
| "When it fails, the work is gone." | SDK |
| "Forty teams are building forty different ways." | Specify |
| "Engineering has capacity for two of my nineteen ideas." | Specify |
| "Nobody left here knows what that system does." | Specify |
| "Our inference bill tripled." | Optimize |
| "We use the frontier model for everything." | Optimize |
| "We trained on our data and the vendor owns the model." | Optimize |
| "Legal will not let us ship." | Verify |
| "I cannot tell the board what our agents are allowed to do." | Verify |
| "Our evidence is screenshots." | Verify |

**The resolution rule.** When title and sentence disagree, lead with the sentence. A VP of
Engineering whose first sentence is about the inference bill is an Optimize conversation,
whatever the org chart says. People spend meetings on the thing they said out loud.

## 2. The second-cost rule

**Every first meeting ends by naming a second cost that belongs to someone who is not in the
room.** That person is the follow-up meeting.

One offering with four solutions becomes a structural advantage here. The four costs
have four different budget owners, so naming the second cost creates a reason for a second
meeting with a second budget. A rep who does this leaves every first meeting multi-threaded.

The pairs that work, and the sentence that opens the door:

| Led with | Name second | The sentence |
|---|---|---|
| SDK | Verify | "Once this is in production, someone has to prove what it is allowed to do. Who owns that here?" |
| SDK | Optimize | "The infrastructure number is one half. Who owns the model bill?" |
| Specify | Verify | "The risk envelope is one of the six specifications. Who signs off on what these systems are allowed to decide?" |
| Specify | SDK | "The systems this produces run on the platform. Who owns the runtime decision?" |
| Optimize | Verify | "Training on production traffic is a residency question. Who would need to approve that?" |
| Optimize | SDK | "The token number is one line. The infrastructure under it is the other. Who owns that budget?" |
| Verify | SDK | "Enforcement happens in the runtime that executes the agent. Who owns where these agents run?" |
| Verify | Specify | "Governing one system is a project. Governing every system your teams build is the actual problem. Who owns how they build?" |

Never name a second cost that belongs to someone already in the room, because no new meeting comes of it.

## 3. Routing in a multi-person meeting

Route to the cost owner whose budget carries the most exposure. Name every other attendee's cost
once, explicitly, so each person hears their own problem stated. Then return to the primary.

The failure is the platform pitch: giving SDK, Specify, Optimize, and Verify equal time. Everyone hears
something adjacent to their problem and nobody hears their problem, so nobody funds anything.

When a customer asks for the full portfolio walkthrough, give it in 90 seconds using the
foundation statement, then return to the cost the meeting is actually about.

## 4. Trigger events

Each event below creates a funded problem. Each maps to an entry solution. Use them
for prospecting as well as routing.

| Trigger | Entry solution |
|---|---|
| An AI pilot passed its demo and has not reached production after three months | SDK |
| A cloud bill review flagged AI services as the fastest-growing line | SDK or Optimize |
| An outage or incident involving an agentic workload | SDK |
| A new CIO, CTO, or Head of Platform in the first 120 days | SDK or Specify |
| A modernization program funded and then stalled | Specify |
| A funded budget line that expires before the project it was raised for can finish | Specify, as a wedge engagement |
| An internal estimate measured in quarters on a system operations needs sooner | Specify, as a wedge engagement |
| A systems integrator engagement ending, with the customer inheriting the system | Specify |
| A hiring freeze against a growing AI backlog | Specify |
| An inference contract renewal or a model vendor price change | Optimize |
| A FinOps mandate to attribute AI spend | Optimize |
| A regulatory deadline entering the board pack | Verify |
| A regulator letter, exam finding, or audit finding on AI | Verify |
| A newly appointed CRO, CISO, or AI risk lead | Verify |
| An AI incident that reached the press or the board | Verify |

## 5. Industry defaults

The industry sets the prior when nothing else is known. Full posture detail is in the
industry postures reference.

| Industry | Likely entry | Why |
|---|---|---|
| Banking and financial services | Verify | DORA and EU AI Act high-risk classification for credit scoring. 52 institutions already in production is the proof that opens the door. |
| Insurance | Verify | EU AI Act high-risk for life and health underwriting, NAIC bulletins, adverse-action explainability. Manulife is the reference. |
| Healthcare and life sciences | Verify | HIPAA, EU AI Act high-risk clinical decision support, GDPR Article 9. Durable HITL for clinical sign-off. |
| Frontier AI labs | SDK | Agent harness, multi-agent research, and red-teaming infrastructure. Verify follows on SB-53 and RAISE. |
| Consumer SaaS | SDK | Scale-to-zero economics and sub-10ms memory for chat latency. Optimize follows on volume. |
| Government and public sector | Verify | Sovereign deployment, hash-chained audit trail, multi-jurisdiction posture. |
| Telecom, logistics, retail, media | SDK | Throughput and reliability lead. Verizon, Tubi, and Swiggy are the proofs. |

## 6. The user personas behind the buyer

The person who signs is rarely the person who uses. Signers and users both matter, and they route differently.

**Builders.** Application developers, AI and ML engineers, product managers and business analysts evaluate the SDK and Specify. A product manager who discovers they can author
specifications becomes a champion, and they carry no budget.

**Operators.** Platform engineers, PlatformOps, SREs, and DevOps own the installation and the golden paths. Platform engineers are the most common champion in an SDK deal.

**Governance and oversight.** Risk officers, InfoSec engineers, FinOps. Risk officers route
to Verify. FinOps routes to Optimize. InfoSec engineers are always involved, always run a
detailed review, and become primary buyers in governance-led deals.

**Buying roles.** Decision makers with budget authority are the CAIO or CDO, CTO or VP
Engineering, CIO, and CRO. Champions who drive the deal internally are the Head of Platform
and the Enterprise Architect. The CISO influences every deal and buys in governance-led ones.
The CFO must approve multi-year pre-paid commitments, and procurement and legal scrutinise
them.

## 7. Routing failures

These mistakes recur, and each one has a name so it can be called in the moment.

1. **The platform pitch.** Giving each solution equal time leaves nobody hearing their own problem.
2. **Routing on title against the sentence.** The org chart is the prior, and the sentence is
   the evidence.
3. **Routing to the solution the rep knows best.** Reps who came from infrastructure sell SDK
   into governance meetings. Reps who came from GRC sell Verify to engineers.
4. **Naming a second cost owned by someone already present.** No new meeting is created.
5. **Selling the mechanism before the cost.** Describing shared compute, the Eval Matrix, or
   the six specifications before the customer has agreed they have the problem those
   mechanisms solve.

## 8. The routing drill

Fifteen cold opens. The learner names the entry solution, the second cost, and the signal
that decided it, in under 30 seconds each. Thirteen correct to pass.

| # | What they said | Entry | Second | Signal |
|---|---|---|---|---|
| 1 | *CISO:* "We have fourteen agent projects and I cannot tell you what any of them are allowed to do." | Verify | Specify | No obligation set exists, and fourteen projects means the real problem is how teams build. |
| 2 | *VP Engineering:* "Our inference bill is the biggest line in my budget now." | Optimize | SDK | Title says infrastructure, sentence says tokens. Sentence wins. |
| 3 | *CFO:* "We approved a two-year AI budget and we are eleven months in at 60% spend." | Optimize | Verify | Spend trajectory with a named owner. Governance is what stops the next overrun. |
| 4 | *Head of Platform:* "Every team writes their own retry logic." | SDK | Specify | Resilience as application code, and inconsistency across teams. |
| 5 | *CRO:* "Legal signed off on the pilot. The pilot is production now and nobody re-signed anything." | Verify | SDK | Conformance drift. Proving what runs was approved requires the runtime. |
| 6 | *CIO:* "We have had three AI programs and none of them shipped." | Specify | SDK | Delivery failure repeated three times is a rework problem. |
| 7 | *Chief Data Officer:* "We fine-tuned on our claims data and the vendor owns the model." | Optimize | Verify | Ownership of weights. Training on claims data raises residency. |
| 8 | *Enterprise Architect:* "We are an Azure shop. Why would we not use Foundry?" | None yet | — | An architecture objection with no stated pain. Ask what their agentic workload's availability commitment is before routing. |
| 9 | *SRE lead:* "We had an outage and the agents stopped. There was nothing to restart." | SDK | Verify | State loss on failure. |
| 10 | *Head of Claims:* "I have nineteen automation ideas and engineering has capacity for two." | Specify | Verify | Backlog against capacity. Claims decisions are high-risk under the EU AI Act. |
| 11 | *AI/ML lead:* "We use the frontier model for everything because we never had time to test alternatives." | Optimize | SDK | No evaluation loop, so no basis to route work down. |
| 12 | *Chief Compliance Officer:* "The EU AI Act deadline is in our board pack." | Verify | Specify | A dated regulatory obligation with board visibility. |
| 13 | *VP Engineering:* "We have been six months getting the prototype to production." | SDK | Specify | The production gap, stated in weeks. |
| 14 | *Head of Internal Audit:* "Our evidence for the last exam was a folder of screenshots." | Verify | SDK | The evidence record. Producing a real one requires the runtime. |
| 15 | *CTO:* "I have forty engineers and I need four hundred." | Specify | SDK | The constraint is build capacity, which the factory removes. |

Item 8 is the one most learners get wrong. An objection is not a cost, and routing on it
sells against a competitor before the customer has agreed they have a problem.

## 9. When the person owns a mandate instead of a cost

Some buyers own an AI outcome across the whole organisation and own none of the four
budgets, or claim all of them. AI Transformation Officers are the common case. Routing on
cost fails with them, and `06-mandate-owners.md` covers what to do instead.
