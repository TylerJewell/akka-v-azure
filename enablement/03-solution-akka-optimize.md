# Akka Optimize — removes token spend

## 1. The cost and who pays it

Akka Optimize removes token spend. Akka watches the work the customer's agents do, routes
each task to the model that handles it best, trains specialized models on their data, and
serves them, continuously. Inference, training, grading, and scoring run on the same runtime
as the agents, so the loop runs inside one system.

The people who pay this cost:

| Role | What they own | What they say |
|---|---|---|
| CFO, VP Finance | Total cost of ownership and spend predictability | "This line item tripled and nobody can tell me why." |
| FinOps | Attribution and unit economics | "I cannot break the inference bill down by team." |
| CAIO, CDO | AI strategy and the model relationship | "We are one price change away from a problem." |
| AI/ML engineering lead | Model selection and quality | "We use the frontier model for everything because we never proved a smaller one works." |
| Head of Data Science | Proprietary data and what it produces | "We train on our data and the vendor keeps the weights." |

## 2. The customer challenge

**The bill grows faster than the traffic.** AI applications spend 30 to 40% of revenue on
cost of goods sold, against 10 to 15% for typical SaaS. The cost per call falls every year
and the total rises anyway, because usage grows faster than price falls.

**Nobody can attribute the spend.** Token consumption arrives as one invoice from a model
vendor with no mapping to teams, use cases, or outcomes.

**Every task runs on the most expensive model available.** Teams default to a frontier model
because nothing tells them which work a smaller model could take, and nothing proves it
safely.

**The customer does not own what their data produced.** Fine-tuning inside a model vendor's
service produces weights the customer cannot take elsewhere.

**Training data has to leave the environment.** Building a training set from production
traffic means exporting traces to another system, which raises a residency and compliance
question the risk team then owns.

## 3. Capabilities and core features

**Routing.** Every task is routed to the best model from any vendor, under the customer's own policies. Routing gives leverage and choice across the whole market rather than one
vendor's catalog.

**Grading.** Optimize continuously evaluates traffic from the customer's agents. Grading is
deterministic for structured outputs such as SQL and JSON, and uses an LLM judge for
unstructured outputs. Grading works whether the agents run on Akka or in a third-party
harness such as Cursor, Claude Code, or Copilot.

**Training.** Grades train each smaller specialized model, prove it holds, and promote it,
and the loop grades again. Training is reinforcement learning and distillation from an
open-weight base, in the customer's own environment. Schemas from Akka agents feed the
reinforcement-learning training.

**Serving.** The specialized models are served on the same runtime, and traffic routes to
them as they improve.

**Cost governance.** Token tracking and cost reporting across teams and projects, built in,
without adding another ingestion-priced tool. Six mechanisms lower the bill: shared compute
for orchestration, agents, memory, streaming, APIs, and model economics, for up to 90% lower
infrastructure cost; sub-10ms native memory, which reduces redundant LLM calls; memory
compaction, which reduces tokens consumed per interaction; runtime guardrails, which stop
bad requests before they consume tokens; scale-to-zero; and the token tracking itself.

## 4. The mechanism

On Akka the loop closes by construction. The trace the agent emitted is the same record used
to grade, to train, and to serve. There is no export step, no separate training corpus, and
no second system holding a copy of production traffic.

That record is the same interaction log Akka Verify uses for governance, so cost and
compliance read the same record.

## 5. Handling the two token numbers

Two figures exist and they measure different things. Reps who blur them get caught.

- **22% is measured.** Swiggy cut prediction latency from 144ms to 71ms while reducing token consumption 22%. Lead with that figure, because a customer measured it.
- **Up to 80% is the claim for distilled specialized models against foundry models.** State
  it as what a specialized model trained on the customer's data can achieve, and never
  attach Swiggy to it as proof.

## 6. Differentiators

**Against observability and evaluation tools (Arize, LangSmith, Langfuse, Galileo,
Braintrust, Helicone, Fiddler, Datadog LLM Observability, Opik, Patronus, Humanloop,
Portkey, Confident AI).** Those tools grade from outside the request path and sample by design. Grading is where they stop. None of them trains a model, serves one, or routes traffic to it. Concede that they are useful for engineering observability and
model A/B testing, then ask what happens to the grade after it is produced.

**Against model-vendor fine-tuning.** Azure OpenAI fine-tuned models and comparable services
produce weights that are proprietary and non-portable. Akka tunes from an open-weight base
in the customer's own environment, so the customer owns the model and keeps improving it.

**Against building the loop themselves.** A do-it-yourself loop is four systems and a data
pipeline: trace export, training-set curation, training infrastructure, and a serving stack,
plus the evaluation harness that decides promotion. Each is a separate bill and a separate
failure mode, and production traffic ends up copied into all of them.

**The claim to lead with.** The customer owns intelligence that keeps improving, built on
their data, inside their environment, tuned from an open-weight base.

## 7. Use cases and quick wins

**Use cases that fit.** High-volume, repetitive agent work where the same task shape recurs
millions of times. Structured-output generation such as SQL, JSON, and classification, where
grading is deterministic. Organisations with an inference bill large enough to have a named
owner. Customers under data-residency constraints who cannot send training data to a model
vendor. Accounts already running agents on Cursor, Claude Code, or Copilot, where Optimize
enters without a migration.

**Quick wins that land in one meeting.**

- *Grade a week of their traffic.* Grading works on agents that do not run on Akka, which makes it the lowest-friction entry point in the whole portfolio. No migration, no code change,
  and the output is a report on which work a smaller model could take.
- *Compute cost per verified task.* Price the work on the runs that passed their
  evaluations. Customers who have only ever measured cost per call have never seen this
  number, and it reframes the entire budget conversation.
- *Shadow a candidate.* Run a smaller model against live traffic without serving it, and
  show quality holding while token count drops.
- *Attribute the bill.* Break their current spend down by team and use case in front of
  them.

## 8. Discovery questions

1. What is your monthly inference spend, and what was it six months ago?
2. Can you attribute that spend to teams and use cases today?
3. What share of your agent calls genuinely need a frontier model?
4. How would you prove a cheaper model was good enough to promote?
5. Who owns the weights of a model trained on your data right now?
6. Where does the data go when you build a training set?
7. What happens to your roadmap if your model vendor changes pricing next quarter?

Question 1 is the qualifier. A spend without a named owner is not yet a deal.

## 9. Objections

**"Our model vendor already offers fine-tuning."** Correct. Ask who owns the resulting
weights and whether they can be served somewhere else. The answer decides whether this is
model leverage or deeper lock-in.

**"We already use LangSmith for evaluation."** Concede that it grades well. Grading is the
input to the loop. Ask what happens to a grade after it is produced,
and whether anything trains on it.

**"Smaller models are not good enough for our work."** For some of it, correct. The
mechanism answers this: a candidate shadows live traffic and is promoted only when quality
holds and tokens drop. Nothing is promoted on an assumption.

**"We cannot train on production data."** Sanitizers, residency controls, and the same
evidence record governance already uses. This objection belongs to a risk officer who is not in the room, which makes it the multi-thread to Akka Verify.

**"Our agents do not run on Akka."** Grading works against third-party harnesses including Cursor, Claude Code, and Copilot. That answer keeps the deal alive with no migration attached.

**"Token prices are falling anyway."** Correct, up to 10x each year. Demand rises faster,
which is why the bill grows while the unit price falls.

## 10. What to send after the call

- `akka.io/guides/agent-costs-outrun-traffic`
- `akka.io/guides/did-a-cheaper-model-save-money`
- `akka.io/guides/routing-a-request-to-the-right-model`
- `akka.io/guides/when-a-smaller-model-makes-sense`
- `akka.io/guides/training-data-for-smaller-models`
- `akka.io/guides/who-owns-a-trained-model`
- `akka.io/guides/training-on-production-traffic`
- `akka.io/guides/optimize-agents-built-elsewhere`
- `akka.io/guides/promoting-a-smaller-model`
- Case study: Swiggy, 144ms to 71ms at 22% fewer tokens
- The Akka Optimize deck

## 11. Certification

Run a 20-minute discovery call against a facilitator playing a CFO who escalated a tripled
inference bill, with a defensive CAIO in the room. Pass requires: the spend quantified and
attributed, cost per verified task introduced, the 22% and 80% figures used correctly and
separately, one quick win proposed that needs no migration, and the CAIO left with something to win.
