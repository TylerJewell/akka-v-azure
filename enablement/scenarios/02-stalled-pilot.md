# Scenario 2 — The pilot that will not ship

**Entry solution (facilitator only):** Akka SDK.
**Teaches:** Conceding accurately to a framework the team chose and defends. The
explicit-against-implicit durability argument, delivered without overclaiming.
**Time:** 45 minutes to run, 20 to debrief.

---

## Account brief

Nordhaven Logistics, a European freight forwarder. €3.1 billion revenue, 9,000 employees,
operations across fourteen countries.

Eleven months ago they started building an agentic system that reads customs documentation,
extracts declarations, and routes exceptions to human brokers. The system demoed successfully to the board in March. Five months later it is still not in production.

Your champion, Head of Platform Engineering, took a meeting after reading a comparison page.
The CTO will join for the last fifteen minutes.

## Cast

**Ingrid Halvorsen, Head of Platform Engineering.** Your champion. Wants this shipped and has
been told twice that it is nearly ready.

**Tomas Bergqvist, Lead Engineer.** Built the system. Chose LangChain and LangGraph. In the room and unhappy about it.

**Rafael Mendes, CTO.** Joins at minute 30. Approved the project, has now been asked about it
by the board twice, and is out of patience.

**Anneke Visser, CFO.** Gates any new vendor over €250,000. Not in this meeting.

### Facilitator only

The system works. Tomas is a strong engineer and the architecture is reasonable. What is
missing is production hardening: multi-region, failover, backpressure against the customs
authority API that rate-limits them, and an audit trail their compliance team asked for in
June and has not received.

Tomas has read the Akka comparison pages. He knows LangGraph has checkpoint persistence and
he is waiting for the learner to claim otherwise so he can correct them in front of Rafael.
**If the learner says LangGraph has no durable execution, Tomas corrects them, and the room turns. The scenario turns on that trap.**

Tomas's real position, which surfaces only if he is treated as an expert: he has spent four
months writing retry logic, backpressure handling, and circuit breakers. He does not enjoy
this work and does not consider it his job. He will not say this unprompted, and he will say
it if asked what he has actually been doing since March.

Rafael's number: the customs automation was funded on €4.2 million of annual broker cost.
None of it has been realised. Every month of delay costs €350,000 in unrealised benefit.

## Meeting 1, first 30 minutes — Ingrid and Tomas

**Ingrid opens:** "We are close. I think we need help with the last mile. Tomas can walk you
through what we built."

Tomas then gives a competent eight-minute architecture walkthrough. He will mention LangGraph
checkpointing without emphasis.

### The decision

How the learner responds to the walkthrough decides the scenario.

### Branches (facilitator only)

**A. Claims frameworks have no durable execution.** Tomas: "LangGraph checkpoints state. We
persist to Postgres and resume." Ingrid goes quiet. Every subsequent claim is now
challenged. Recovery is possible and expensive.

**B. Concedes the architecture is sound, then pitches the platform.** Tomas defends. The
meeting becomes a technology comparison with no cost attached, and Rafael arrives to find two
engineers arguing.

**C. Concedes, then asks what Tomas has been building since March.** Tomas describes four
months of retry logic, backpressure against the rate-limiting customs API, and circuit
breakers. *Correct route.* The learner now has the argument in the customer's own words.

**D. Branch C, then draws the explicit-against-implicit line.** Durability on LangGraph is a
programming model Tomas opts into by structuring code a certain way and declaring retry
policies. On Akka it is a property of the runtime. Tomas has just spent four months proving
the first half of that sentence. *Best route.*

The learner must not claim Akka writes no code. Akka offers the explicit model through
workflows and sagas too. Tomas will test this.

## Meeting 1, last 15 minutes — Rafael Mendes joins

**Rafael opens:** "I have been asked about this twice by the board. Tell me when it ships."

### Facilitator behaviour

Rafael does not care about frameworks. He asks three questions and each one is about time or
money:

1. "When does this run in production?"
2. "What does it cost me to get there?"
3. "Why is this different from what we already tried?"

He knows the €350,000 monthly figure and will state it if the learner asks what the delay is
costing.

### The decision

Route Rafael, quantify in his numbers, propose a next step.

### Branches (facilitator only)

**A. Repeats the technical argument.** Rafael: "I asked when it ships." Meeting ends without a
next step.

**B. Answers with a date and a scoped exercise.** Port the workflow that carries the
rate-limit problem, show it survive a forced failure and a deployment. Rafael agrees to a
two-week exercise. *Correct route.*

**C. Branch B, and asks what the delay has cost.** Rafael states €350,000 a month and the
€4.2 million business case. The learner now has a number that dwarfs any platform price, and
Anneke Visser becomes reachable. *Best route.*

## Meeting 2 — Anneke Visser, CFO

Happens only if the learner reached branch B or C with Rafael.

**Anneke opens:** "Rafael wants to spend money on a project that has already spent money.
Convince me."

The correct frame is unrealised benefit against elapsed time. Every
month of delay is €350,000 against a €4.2 million case. The second cost to name here is token
spend, and the person is whoever owns the model bill, which Anneke will identify as Rafael.

A learner who opens with infrastructure savings has led with Akka's number instead of
Nordhaven's.

## Scoring

Standard sheet, plus:

- **The LangGraph trap.** Avoided entirely, two points. Recovered after correction, one.
  Uncorrected overclaim, zero, and the scenario fails regardless of other scores.
- **Concession.** Named what Tomas built well before any contrast, two points.

## Debrief

1. What did Tomas say in his walkthrough that you could have used, and did you use it?
2. When Rafael asked why this is different from what they already tried, what did you say?
3. You had the €350,000 figure available. Did you ask for it, or did you quote Akka's numbers?

The lesson to land: the person who chose the incumbent is in the room in most competitive
deals, and their four months of unglamorous work carries the argument. The argument reaches only a rep who treats them as an expert first.
