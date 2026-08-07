# Scenario 6 — The architecture review board

**Entry solution (facilitator only):** Akka SDK, reached through the business owner.
**Teaches:** An architecture objection is not a pain. Competing before a business owner has a
number is unwinnable, and competing after they have one is straightforward.
**Time:** 45 minutes to run, 20 to debrief.

---

## Account brief

Vantage Communications, a US regional telecommunications carrier. 6.2 million subscribers,
$4.8 billion revenue, 14,000 employees, operating across nine states.

Vantage is building agentic order orchestration for business fiber: take an order, validate
serviceability, sequence provisioning across four legacy systems, and handle exceptions.

Their Enterprise Architecture Review Board mandated Azure for all new workloads eighteen
months ago. Your meeting is with the board's chair, arranged after she downloaded a comparison
page.

## Cast

**Priyanka Doshi, Chief Enterprise Architect.** Chairs the review board. Wrote the Azure
mandate.

**Ray Okonkwo, Director of Order Management.** Owns business fiber order fulfilment. Not in
meeting 1.

**Deborah Mensah, CIO.** Signed the Azure enterprise agreement. Not in meeting 1.

### Facilitator only

The Azure mandate exists to stop teams deploying unsupported stacks. An exception path exists, documented and almost never used, requiring a business case and Deborah's signature.

Priyanka has no pain. Her system works, her board works, and she downloaded the comparison
page to understand a technology her team asked about. **She will win any architecture debate,
because she is arguing on her own board's terms in her own building.** A learner who competes
against Foundry in this meeting loses and does not get a second one.

Ray has the pain. 22% of business fiber orders fall out of automated provisioning into manual
handling. Vantage processes roughly 11,000 business fiber orders a month, so that is about 2,400 manual interventions, each taking a provisioning specialist 40 minutes. Ray has been asking
for engineering help for two years. He does not know what Azure AI Foundry is and does not
care.

Deborah's exposure: business fiber carries contractual installation commitments. Missed
intervals cost credits. She does not know the fallout number in detail and will react to it.

The decisive fact, usable only in meeting 3: Azure AI Foundry's Agent Service has no SLA, and
Microsoft's documentation states there is no supported method for active-active multi-region
replication. Against Priyanka with no pain in the room, this is trivia. Against Priyanka after
Ray has quantified fallout and Deborah has named her credit exposure, it is the argument.

## Meeting 1 — Priyanka Doshi

**Priyanka opens:** "I read your comparison page. I will be direct. We are an Azure shop, we
have an enterprise agreement, and my board mandated it. Why would we not use Foundry?"

### The decision

Whether to answer the question.

### Branches (facilitator only)

**A. Answers the question and competes against Foundry.** Priyanka counters each point
competently. She is not wrong about any of them in the abstract, because no workload is on the
table. The meeting ends with mutual respect and no next step. *Learners pick this most often, and it feels like a good technical conversation.*

**B. Deflects without substance.** Priyanka reads it as evasion and disengages.

**C. Declines to compare, and asks what workload the board is deciding for.** Priyanka names
the business fiber order orchestration project. *Correct route.*

**D. Branch C, then asks who owns that workload's business outcome and what it is worth.**
Priyanka does not know the number and says so, which is itself useful. She names Ray. *Best route.*

The line that works, delivered plainly: comparing platforms with no workload attached produces
an opinion. Ask what the board is deciding for, and the comparison becomes answerable.

Priyanka will give the introduction. She has no reason not to, and a rep who declined an easy
argument registers as unusual.

## Meeting 2 — Ray Okonkwo

**Ray opens:** "Priyanka said to talk to you. I do not know what you sell. I know 22% of my
orders end up on somebody's desk."

### Facilitator behaviour

Ray gives numbers readily. He has been trying to get anyone to care about them for two years.
He will supply: 11,000 orders a month, 22% fallout, 40 minutes per intervention, eleven
specialists. He does not know what the fallout costs in credits and will point at Deborah.

He has never heard of Akka and does not need the platform statement. He needs someone to
believe the number matters.

### The decision

Quantify, propose a scoped win, and name the second cost.

### Branches (facilitator only)

**A. Delivers the platform pitch.** Ray listens and does not follow. No next step.

**B. Quantifies in Ray's numbers.** About 2,400 interventions a month at 40 minutes is roughly
1,600 specialist hours. *Correct route.*

**C. Branch B, plus the Verizon proof.** 750% increase in order processing capacity and
response times cut from 6 seconds to 2.4. Same industry, same problem shape. *Best route.*

The correct second cost is reliability commitments, and the correct person is Deborah, who
owns the SLA and the credit exposure.

## Meeting 3 — Priyanka, Ray, and Deborah

The architecture conversation becomes winnable in this meeting and in no earlier one.

**Deborah opens:** "Ray has a number I did not have. Priyanka has a mandate. I have to decide
whether this is an exception."

### The decision

Now the learner competes.

### Branches (facilitator only)

**A. Repeats the Foundry comparison from meeting 1.** Priyanka counters as before.

**B. Ties the guarantee to Deborah's exposure.** Agent Service has no SLA, and Microsoft's
documentation states there is no supported method for active-active multi-region replication.
Vantage's installation commitments carry credits. Akka guarantees the workload at 99.9999%
with sub-1 minute RTO and zero-byte RPO, backed by indemnities. *Correct route.*

**C. Branch B, framed as satisfying Priyanka's mandate.** The
exception path exists for workloads with commitments the standard stack cannot cover, and this
is one. Priyanka's board is used exactly as she designed it. *Best route.* Priyanka can now
support the exception without losing authority.

## Scoring

Standard sheet, plus:

- **Meeting 1.** Declined the comparison and got the workload named, two points. Competed and
  recovered, one. Competed and lost the meeting, zero.
- **Ray's numbers.** Quantified in his figures, two points. Quoted Akka's percentages, zero.
- **Priyanka's authority.** Framed the exception as using her process, two points. Framed it
  as overriding her, zero.

## Debrief

1. Priyanka asked a direct question in her first thirty seconds. Why was answering it the
   wrong move?
2. What changed between meeting 1 and meeting 3 that made the same Foundry facts persuasive?
3. Priyanka wrote the mandate. What did you do to let her support an exception to it?

The lesson to land: a comparison with no workload attached is an opinion, and the customer
always wins opinions in their own building. The same facts become decisive once a business
owner has quantified a problem and an executive has named their exposure. The route to an
architect runs through the business owner.
