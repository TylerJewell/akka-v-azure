# Mandate owners, and the AI Transformation Officer

Some buyers own an AI outcome for the whole organisation. AI Transformation Officer is the common title, and Head of AI Enablement, Chief AI Transformation Officer, and Chief Digital Officer appear on the same charter. Such a person is increasingly the first meeting in an enterprise account, and the routing model in `05-routing.md` does not work on them.

---

## 1. Why cost routing fails here

Routing assumes the person pays one of the four costs from one budget. A mandate owner is
assigned an outcome instead: business transformation, identifying where AI can be used,
securing AI, and workforce transformation. Asked which cost they own, they name every one of them, or none.

The failure takes one of the shapes below, and both end the same way.

**Too little ownership.** The mandate arrives with no engineering team, no infrastructure budget, and no veto over the teams that would build. A mandate owner can convene a meeting and cannot fund one.

**Too much ownership.** A central AI budget arrives with an instruction to own AI. Every solution gets agreement and none gets bought, because a system still needs a business owner to accept it and an engineering team to run it.

A rep who routes on cost gets enthusiasm, a full portfolio briefing, and no next step.

## 2. The charter varies, and the measure is what differs

The title is new and each company wrote its own charter. What varies decides the play:

1. Whether they hold budget.
2. Whether that budget funds engineering headcount or funds other people's teams.
3. Whether they have authority over the teams that build.
4. What they are measured on at the end of the year.
5. Whether securing AI is theirs or the CISO's.

Item 4 decides the entry solution. Ask it directly.

## 3. The archetypes, named by what each is measured on

Most people are a blend. Classify on the measure.

### The portfolio holder

Measured on the count of AI use cases in production. Carries a list gathered from the
business. Has few or no engineers and is blocked on delivery capacity. The most common
archetype.

**Entry: Akka Specify.** The factory turns their list into delivered systems without hiring,
and it turns them from a person holding a list into the owner of how the company builds.
**Second cost: governance**, because the systems on their list need approval before any of
them ships.

### The safety officer

Securing AI dominates the charter. Appointed after an incident or ahead of a regulatory deadline, and sits beside or under the CISO or CRO. Measured on whether AI systems
can be approved to ship at all.

**Entry: Akka Verify.** **Second cost: rework**, because governing one system is a project
and governing everything the company builds is the actual assignment.

### The economist

Measured on AI return or on holding an AI spend envelope. Frequently the person who has to
justify last year's AI budget to the CFO this year.

**Entry: Akka Optimize.** Cost per verified task is the number they have been asked for and
cannot produce. **Second cost: infrastructure.**

### The workforce transformer

Measured on employee adoption and productivity. Wants copilots, assistants, licences, and
training programs.

**Treat this archetype as a disqualifier, because saying so wins more than pretending.** Akka is not a
desktop agent or workforce copilot. Claude Code, Copilot, and Glean inherit a user's identity
and stop when the session closes, and they are the right tool when a specific human is
driving. Find the part of the charter that covers systems running unattended. If there is none, ask who owns that and leave.

## 4. The classification questions

1. **"What does your scorecard look like at the end of the year?"** Reveals the measure, which
   selects the archetype.
2. **"Does your budget fund engineering headcount, or does it fund other people's teams?"**
   Reveals whether they can buy alone.
3. **"Whose team writes the code for the use case you just described?"** Names the actual cost owner, who is the person the second meeting is with.
4. **"Who can say no to this?"** Reveals the veto. A mandate owner who cannot name anyone is
   describing authority they do not have.

Ask every one of them in the first meeting. None reads as aggressive, because a mandate owner is relieved that someone understands the shape of the job.

## 5. The rule: sell to a use case, never to the mandate

A use case carries an owner, a profit and loss line, and a date, which is what a purchase
requires. A mandate carries none of those.

Every conversation with a mandate owner converges on one named use case in the first meeting.
One question gets there:

> "Of everything on that list, which one has a business owner who is already annoyed it has
> not happened?"

An annoyed business owner is already paying a cost and has a budget to stop paying it. Once
the use case is named, route on that owner's cost using `05-routing.md`, and keep the mandate
owner as the sponsor who opens the door.

Refuse the portfolio proof of concept. Propose one, delivered as a production slice in
four to six weeks, with the mandate owner's name on the outcome.

## 6. What Akka gives this persona that nothing else does

Each of the following maps to a pressure the role carries.

**Delivery capacity without hiring.** The scorecard counts systems in production, and the mandate owner controls no engineers. Akka Specify produces governed systems from plain-language
specifications, so their list stops being blocked on other teams' roadmaps.

**An answer to securing AI.** Nearly every charter includes it and almost none of them can
answer it. Akka Verify classifies a system against 190 regulations, derives its obligation
set, routes sign-off, and seals a Governance Posture Package. The CISO would otherwise use that question to stop them.

**A number when asked whether it is working.** Cost per verified task prices AI work on the
runs that passed their evaluations. Most mandate owners report activity counts because
nothing gives them an outcome number.

**One frame turns them into a champion.** A mandate ends when the person holding it
moves on. A platform that other teams build on outlives them. Position Akka as the thing that
converts their assignment into infrastructure the company depends on, and they will carry the
deal internally in a way a cost owner never does.

## 7. Traps

**Some briefings go nowhere.** Evaluating the market is part of the job, and a full
portfolio briefing lets them discharge it. Do not accept a second briefing. Make a named use
case the price of the second meeting.

**Believing the decision-maker claim.** Many will present as the decision maker. Question 4
resolves it. Never forecast on a mandate owner alone.

**Standardising before anything runs.** A mandate owner frequently wants a company-wide AI standard first. A standard with nothing running behind it is unenforceable. Propose one production
system that becomes the standard, which is also how Manulife reached 2,000 developers under
central risk control.

**Positioning centralisation in front of their peers.** Their peers often resent the role.
Never describe Akka as giving the mandate owner control over other teams' work while those
teams are in the room. Describe it as removing work from those teams, which is the framing
that survives the meeting.

**Some mandates are really a reorganisation.** If the charter appeared six weeks ago and no
budget followed, the account is not ready. Keep the relationship, and prospect the four cost
owners in parallel.

## 8. The sequence for a portfolio holder

The most common archetype, run end to end.

| Meeting | With | What happens |
|---|---|---|
| 1 | The mandate owner | Classify with the four questions. Extract the use-case list. Find the one with heat and name its business owner. Deliver the 90-second platform statement, and nothing more of the portfolio. |
| 2 | The business owner, sponsored by the mandate owner | Route on the business owner's cost. Quantify what the delay is costing them. Propose a production slice in four to six weeks. |
| 3 | The CISO or CRO, introduced by the mandate owner | Verify. Run the Risk Survey against the named use case. The obligation set is the deliverable. |
| 4 | All three | The factory, funded by the business owner's use case, sponsored centrally, approved by risk. |

The mandate owner never funds the first system and decides who does, which is the whole of their value here.

## 9. Certification

Run a 25-minute first meeting against a facilitator playing an AI Transformation Officer
appointed four months ago, holding a list of eleven use cases, a central budget that funds
nothing but their own team, and a charter that includes securing AI. Pass requires: every classification question asked, the archetype named correctly in the debrief, exactly one use
case extracted with its business owner named, no four-use-case proof of concept accepted, and
a second meeting agreed with someone other than the person in the room.
