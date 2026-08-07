# Scenario 3 — The bill that tripled

**Entry solution (facilitator only):** Akka Optimize.
**Teaches:** Routing on the stated pain against the title. Handling a finance escalation with
the technical owner in the room, without making that owner an enemy.
**Time:** 45 minutes to run, 20 to debrief.

---

## Account brief

Cadence, a consumer SaaS company with $410 million in annual recurring revenue. Roughly 1,900
employees. Their product is a scheduling and workflow tool used by mid-market service
businesses in North America and the EU.

Cadence shipped AI features fourteen months ago: a drafting assistant, an automated scheduling
agent, and a support triage agent. Adoption was strong.

You were introduced by an investor. The meeting is with the CFO and the Chief AI Officer,
together, for 45 minutes.

## Cast

**Reid Callahan, CFO.** Called this meeting. Approved the AI budget last year.

**Dr. Amara Osei, Chief AI Officer.** Built the AI features. Reports to the CTO. Did not ask
for this meeting.

**Jules Fontaine, VP Engineering.** Owns the infrastructure budget. Not present.

**Sofia Reyes, General Counsel.** Not present.

### Facilitator only

The inference bill went from $180,000 a month to $610,000 a month over nine months. Revenue from AI features grew more slowly than the bill. Gross margin on the AI tier fell from 71% to
54%.

Reid's actual concern is the margin line in a board deck due in three weeks. He does not
understand the technology and does not want to. He wants a number he can commit to.

Amara's position: the growth is adoption, the architecture is fine, and she has been asked to
justify her budget three times this quarter. She is competent, tired, and expects this meeting
to be an ambush. **If the learner sides with Reid against Amara, Amara stops engaging and
kills the deal in the follow-up she is asked to run.** She is the person who would implement
anything sold here.

Amara's hidden facts, available if the learner earns them:

- Every agent call goes to a frontier model, because nobody had time to evaluate alternatives.
- Support triage is 62% of call volume and is a classification task.
- No way exists to attribute spend to the three features.
- She proposed routing work to smaller models in February and was told to focus on shipping.

That last fact is the key to the scenario. Amara already knows the answer and was overruled.
A learner who finds it gains a champion instead of an opponent.

## Meeting 1 — Reid and Amara, together

**Reid opens:** "Our AI costs went up three and a half times. Revenue did not. I need to
understand what we do about that before I stand up in front of the board."

Amara says nothing.

### The decision

Who the learner addresses first, and what they lead with.

### Branches (facilitator only)

**A. Answers Reid directly with Akka cost claims.** Amara hears a vendor promising savings on
a system she built and interprets it as a critique. She raises three technical objections in
the second half and the meeting ends inconclusive. Reid asks Amara to evaluate. She does not.

**B. Leads with Akka SDK infrastructure savings.** Wrong cost. Reid's number is the inference bill. The learner is talking about a different line item than the one on the board
deck.

**C. Asks Amara what drives the number before answering Reid.** Amara explains adoption growth
and frontier-model defaults. *Correct route.* The learner now has the mechanism from the person who
owns it, and Amara has been treated as the expert in front of her CFO.

**D. Branch C, then asks Amara what she would do with six months and no constraints.** Amara
describes routing support triage to a smaller model, and mentions she proposed it in February.
*Best route.* The learner is now advocating Amara's plan.

### The number to reach

Cost per verified task. Neither Reid nor Amara has ever seen it. Introducing it reframes the
board deck from a cost problem into a unit-economics story, which is the outcome Reid actually
needs. A learner who gets there has won the meeting whatever else happens.

### Discipline check (facilitator marks this)

If the learner uses the "up to 80% fewer tokens" figure, they must attach it to distilled
specialized models against foundry models. If they attach Swiggy's 22% to it as proof, mark it
wrong. Amara will not catch it. Jules will, in meeting 2.

## Meeting 2 — Jules Fontaine, VP Engineering

Reached by naming the second cost. The correct second cost is infrastructure, and the correct
person is Jules, who owns that budget and was not in meeting 1.

**Jules opens:** "Amara says you can cut the model bill. Fine. I want to know what happens to
my compute line, because every vendor who has cut one has grown the other."

### Facilitator behaviour

Jules is technical, skeptical, and fair. He will ask:

1. Where does grading run, and what does it cost?
2. Where does training run?
3. What do we have to migrate?

Question 3 is the one that matters. The correct answer is nothing yet. Grading works against
their existing agents with no migration. A learner who proposes a platform migration in
meeting 2 loses Jules.

He will also test the 80% figure if the learner used it in meeting 1 and Amara repeated it.

## Meeting 3 — Sofia Reyes, General Counsel

Optional, and available to a learner who identifies that training on production traffic raises
a residency question for their EU customers.

Sofia's need is narrow: written assurance about where training data goes and what is retained. The Verify thread starts here, and it opens a second budget.

## Scoring

Standard sheet, plus:

- **Amara's state at the end of meeting 1.** Advocate, two points. Neutral, one. Opponent,
  zero, and the scenario fails.
- **Cost per verified task introduced.** Worth two points.
- **Figure discipline.** The 22% and 80% numbers used correctly and separately, two points.
  Blurred, zero.
- **Migration.** Nothing proposed in meeting 2, two points.

## Debrief

1. Reid asked the question. Who did you answer first, and why?
2. Amara proposed this in February and was overruled. Did you find that out?
3. What did you say when Jules asked what they would have to migrate?

The lesson to land: in a finance escalation the technical owner is not the problem, they are
the person who already knows the answer and was not listened to. The rep who finds that out
converts the person most likely to block them into the person who implements them.
