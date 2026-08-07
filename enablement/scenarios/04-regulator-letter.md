# Scenario 4 — The exam finding

**Entry solution (facilitator only):** Akka Verify, with Akka SDK arriving out of the Eval Matrix instead of out of a pitch.
**Teaches:** Stating the Verify coverage line precisely when the estate runs somewhere else.
The land-and-expand motion where the control bindings create the runtime deal.
**Time:** 45 minutes to run, 20 to debrief.

---

## Account brief

Rheinwerk Versicherung, a German life and health insurer. €14 billion in gross written
premium, 7,400 employees, operating in Germany, Austria, and Switzerland.

Rheinwerk put an underwriting decision support system into production eight months ago, running on AWS Bedrock.

BaFin conducted a supervisory review in June and raised a finding about AI system governance.
Separately, life and health underwriting is classified high-risk under the EU AI Act.

Your meeting was requested by the Chief Risk Officer. Sixty minutes, three people.

## Cast

**Dr. Katrin Sommer, Chief Risk Officer.** Requested the meeting. Holds budget. Has a
supervisory response due.

**Ilse Brandt, Head of Compliance.** Owns the BaFin relationship and wrote the response draft.

**Lars Pedersen, Head of Engineering.** Built the system on Bedrock. Committed to AWS, with
three years left on an enterprise agreement.

**Werner Klein, CFO.** Not present. Signs anything over €500,000.

### Facilitator only

The BaFin finding is specific: Rheinwerk cannot demonstrate which controls apply to the
underwriting system, cannot show that approved controls are enforced, and produced evidence
consisting of exported CloudWatch logs and screenshots. The response is due in eleven weeks.

Katrin's problem is the eleven weeks. She is not shopping for a platform and has no appetite
for a migration inside that window.

Lars is not hostile, and he is immovable on AWS in the near term. He has heard three vendors
this year claim they can govern Bedrock agents, and each claim fell apart under questioning.
**He will ask exactly how enforcement works on a Bedrock agent. If the learner claims inline
guardrails on Bedrock, Lars dismantles it and Katrin loses confidence in everything else said.** The scenario turns on that trap.

The underwriting system makes adverse decisions on natural persons. Under the EU AI Act it
carries human oversight obligations, and a correct Eval Matrix for it will contain control
rows binding to G, H, and K classes. None of those can be satisfied by a system Akka does not
execute. The customer discovers that fact instead of hearing it asserted, and the discovery creates the SDK deal.

## Meeting 1 — Katrin, Ilse, and Lars

**Katrin opens:** "We have eleven weeks to respond to BaFin. I am told you work on AI
governance. I do not want a rebuild. Tell me what you can do inside eleven weeks."

### The decision

What the learner commits to, and how precisely they state the boundary.

### Branches (facilitator only)

**A. Claims Verify governs their Bedrock agents.** Lars: "How? You are not in our request
path." The learner has no good answer. Katrin disengages from every subsequent claim. *This
fails the scenario.*

**B. Proposes migrating to Akka first.** Katrin: "In eleven weeks?" Meeting ends politely.

**C. States the coverage line accurately.** Classification against the corpus, the derived
obligation set, the signed Eval Matrix, sign-off recipes, and the Governance Posture Package
apply now, wherever the system runs. Inline enforcement, durable HITL, authority snapshots,
side-effect recording, and the hash-chained log require the agent to execute on the Akka
runtime. *Correct route.* Katrin's eleven-week problem is entirely in the first list.

**D. Branch C, then proposes the Risk Survey against the underwriting system as the first
deliverable.** Industry presets shorten time-to-matrix from weeks to a half day. Katrin has a
dated deliverable inside her window. *Best route.*

Lars respects branch C immediately. A rep who draws a boundary against their own product is
the first one he has met this year.

## Meeting 2 — the Eval Matrix review

Two weeks later. Same three people, plus Ilse's BaFin response draft.

The matrix for the underwriting system contains 41 control rows. Ilse reads them out. The
facilitator delivers this line when the group reaches the human oversight rows:

> **Ilse:** "This row says the system must escalate to a human underwriter and block until
> that person responds. And this one says we must be able to halt every in-flight call. How do
> we do those on what we have?"

### The decision

The learner answers Ilse's question.

### Branches (facilitator only)

**A. Pitches Akka SDK.** Lars hears a migration pitch arriving on schedule and pushes back.
The moment is lost.

**B. Answers factually and stops.** Those rows bind to the G, H, and K classes, which require
the runtime that executes the agent to hold the call. Then silence. *Correct route.* Katrin and Lars
work out the implication themselves, and Lars says it out loud, which is worth more than the
learner saying it.

**C. Branch B, then asks what the response to BaFin will say about those rows.** Ilse has to
write something. The honest options are a remediation plan with a date or an admission. This
converts the runtime question from a vendor preference into a supervisory commitment. *Best route.*

The learner must not be smug here. Lars made a reasonable decision eight months ago and the
obligations arrived afterwards.

## Meeting 3 — Werner Klein, CFO

Reached only from branch B or C.

**Werner opens:** "Katrin wants budget for a governance platform and now apparently a runtime
as well. What is the exposure if we do nothing?"

The answer is not a feature list. 742 of the 1,230 controls in the corpus carry financial
penalties. The specific exposure comes from the matrix Rheinwerk now holds and from BaFin's
remediation powers. A learner who quotes Akka's capability list here has misread the
question.

## Scoring

Standard sheet, plus:

- **The coverage line.** Stated accurately and unprompted, two points. Stated after Lars
  pushed, one. Overclaimed, zero, and the scenario fails.
- **Meeting 2.** Let Lars or Katrin draw the conclusion, two points. Pitched it, zero.
- **Deliverable inside eleven weeks.** Named with a date, two points.

## Debrief

1. Lars has heard three vendors claim this year that they can govern Bedrock agents. What did
   you do differently?
2. In meeting 2, who said out loud that the runtime had to change?
3. What did you tell Werner the exposure was, and where did that number come from?

The lesson to land: the honest boundary is the position that carries a governance deal, because a risk officer's job is assessing whether people are overstating. Drawing the
line yourself is the credibility that carries the rest of the conversation, and the Eval
Matrix then produces the runtime deal without a rep ever pitching it.
