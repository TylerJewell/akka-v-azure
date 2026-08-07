# Scenario 1 — The wrong door

**Entry solution (facilitator only):** Akka SDK, reached through a referral out of the first
meeting.
**Teaches:** An early meeting with someone who owns no cost is a routing problem. The move is to convert it into an introduction.
**Time:** 45 minutes to run, 20 to debrief.

---

## Account brief

Meridian Financial, a US regional bank with roughly $80 billion in assets. Twelve thousand
employees, headquartered in Charlotte, with operations in four states.

An inbound form fill came from their procurement portal. The subject line was "AI vendor
evaluation — fraud analytics." Procurement scheduled you with the Chief Information Security
Officer. You have 30 minutes.

Nothing else is known.

## Cast

**Dana Whitfield, CISO.** Fourteen years at the bank. Owns security architecture, third-party
risk, and the vendor review process.

**Marcus Bell, Head of Platform Engineering.** Not on the invite.

**Priya Raghavan, Chief Risk Officer.** Not on the invite.

### Facilitator only

Dana owns no AI budget and no AI mandate. She was assigned this evaluation because a fraud
triage project reached third-party review and nobody else volunteered. She is mildly
resentful about it and completely willing to say so if asked a direct question.

The real situation: Marcus Bell's team built an agentic fraud triage system on LangChain nine months ago. The system works, and it loses state when a node restarts, and analysts have to re-run cases.
There is no failover. Marcus has asked twice for headcount to fix it and been refused. His
budget is real and his frustration is high.

Priya has no idea any of this exists. She will matter in meeting 3.

Dana's hidden lines, delivered only if the learner asks something that earns them:

- If asked what she is being asked to secure: "Honestly? A thing Marcus's team built that I
  found out about in March."
- If asked who owns it: "Marcus Bell. Platform engineering. He is the one who should be in
  this meeting."
- If asked what would make this review easy: "SOC 2, your pen test summary, and a data flow
  diagram. That is not why you are here though."

Dana will not volunteer any of this. She will run a competent, polite security review for 30
minutes if the learner lets her.

## Meeting 1 — Dana Whitfield, CISO

**Dana opens:** "Thanks for coming in. I have a questionnaire I need to get through. Can you
start by telling me where our data would live and what your certifications look like?"

### The decision

The learner chooses what to lead with.

### Branches (facilitator only)

**A. Leads with Akka Verify.** Dana listens politely. Governance is adjacent to her job and
she has no AI governance mandate, so it does not land as her problem. She takes the material,
completes her questionnaire, and says she will circulate it. No second meeting. The deal
enters the vendor review queue and surfaces again in six weeks with no sponsor. *Learners pick this most often, and it looks like a good meeting while it happens.*

**B. Leads with Akka SDK.** Dana is not the audience for a runtime pitch. She redirects to the
questionnaire twice, then ends the meeting eight minutes early. No second meeting.

**C. Answers the security question briefly, then asks what she is being asked to secure and
who owns it.** Dana names Marcus and the fraud triage project. If the learner then asks for an
introduction, she gives it. *Correct route.*

**D. Delivers the 90-second platform statement, clears the certification question with 19+
InfoSec certifications including SOC 2 and ISO 42001, then asks C's questions.** Dana gives
the introduction and offers to attend. *Best. Dana attending meeting 2 accelerates everything
that follows.*

Learners on A or B get one recovery prompt from Dana at the 20-minute mark: "Look, I am not
the buyer here." If they take it, treat it as branch C with one point deducted.

## Meeting 2 — Marcus Bell, Head of Platform Engineering

Runs regardless of branch. On A or B, it happens five weeks later and Marcus has not been
briefed.

**Marcus opens:** "Dana said I should talk to you. I will be straight with you, we built this
already and it works. I do not need a platform. I need two more engineers."

### Facilitator behaviour

Marcus concedes nothing for the first five minutes. He will describe the system if asked. If
the learner asks what happens when it fails, he says: "The case restarts. Analysts re-key
about forty cases a week." If pushed for a number, he says a case takes an analyst eleven
minutes.

He does not volunteer the failover gap, which comes out only if he is asked what happens during a deployment or a node drain.

### The decision

Route Marcus, quantify the cost, and name the second cost.

### Branches (facilitator only)

**A. Pitches the platform.** Marcus disengages. "This is a rewrite. I do not have a rewrite in
me this year."

**B. Routes to SDK and quantifies.** Forty cases a week at eleven minutes each, plus the
re-run cost. Marcus engages. *Correct route.* He is not yet convinced this justifies a platform.

**C. Routes to SDK, quantifies, and proposes porting the single workflow that loses state.**
Marcus agrees to a scoped exercise. *Best route.* The quick win from `01-solution-akka-sdk.md`,
applied to his actual failure.

**D. Concedes that LangChain was the right choice for the prototype before contrasting.**
Add one point on any branch. Marcus's team chose LangChain and Marcus defends his team.

### The second cost

The correct second cost is governance, and the correct person is Priya Raghavan. The opening
sentence is in `05-routing.md`: "Once this is in production, someone has to prove what it is
allowed to do. Who owns that here?"

Marcus's answer: "Risk. Priya Raghavan. She does not know this exists, which is a conversation
I have been avoiding."

A learner who names infrastructure spend as the second cost has named something Marcus already
owns, which creates no meeting.

## Meeting 3 — Priya Raghavan, Chief Risk Officer

**Priya opens:** "Marcus tells me there is a system making fraud decisions that I have not
seen. Start there."

This meeting is Verify. The learner must not defend Marcus and must not describe Akka
capabilities before Priya has stated what she needs. Her actual need is an obligation set: she
cannot say what the system is required to do because nobody classified it.

**The win condition:** the Risk Survey proposed against the fraud triage system, with a date.

## Scoring

Use the standard sheet in `README.md`. Two scenario-specific additions:

- **Meeting 1 outcome.** Referral obtained, two points. Referral obtained after the recovery
  prompt, one point. Vendor review queue, zero.
- **Second cost.** Named Priya by name, two points. Named governance without a person, one.
  Named a cost Marcus already owns, zero.

## Debrief

Three questions for the learner, in order.

1. What in Dana's first three sentences told you she was not the buyer?
2. At what minute did you know, and what did you do with the remaining time?
3. Marcus said he needed two engineers. What did you do with that sentence?

The lesson to land: procurement routes AI vendors to security by default, so the wrong-door meeting is common. A security review with no sponsor behind it stalls. A security review that produces an introduction to the cost owner opens the account sooner than any other route, and Dana becomes a supporter because the learner solved her problem, which was being
handed an evaluation she did not want.
