# Scenario 7 — One system under five regulators

**Entry solution (facilitator only):** Akka Verify and Akka SDK, led together.
**Teaches:** Running two cost threads in parallel without diluting either. Handling a champion
who will consume six months and cannot fund anything.
**Time:** 60 minutes to run, 20 to debrief.

---

## Account brief

Atlas Pacific Bank, headquartered in Singapore. $340 billion in assets, 31,000 employees,
retail and commercial operations in Singapore, Hong Kong, mainland China, Australia, and the
United Kingdom.

Atlas Pacific is consolidating three separate agentic programs into one: customer servicing, AML
transaction monitoring, and credit pre-assessment. Each was built by a different regional team
on a different stack.

Your champion is the Head of Platform Engineering, who has been researching Akka for four
months and has read most of the public material.

## Cast

**Wei Lin Tan, Head of Platform Engineering.** Your champion. Knows the product well.

**Sanjay Mehta, Group Chief Risk Officer.** Holds governance budget. Not in meeting 1.

**Fiona Docherty, Head of Infrastructure.** Owns the multi-region estate. Not in meeting 1.

**Aroon Srisai, Group CIO.** Signs anything material. Not in meeting 1.

### Facilitator only

Wei Lin is genuine, well-informed, and powerless. His budget covers his team and tooling under
$200,000. He will happily run a proof of concept, request architecture sessions, ask for
benchmark data, and introduce nobody, for as long as the learner lets him. **A learner who
does not force him to name the funder in meeting 1 spends the whole scenario in meeting 1.**

The two costs are genuinely simultaneous here and neither leads:

- **Governance.** The same customer-servicing system must satisfy the Singapore Model AI
  Governance Framework, Hong Kong requirements, China Generative AI Interim Measures, UK
  regulations, and GDPR Chapter V for the UK entity's EU data. Today each region derives its
  own posture manually. Sanjay owns this and has no solution.
- **Infrastructure.** Data cannot leave China or Singapore. The consolidated system needs
  active-active availability because AML monitoring runs 24 hours. Fiona owns this and has
  been told it cannot be done from one platform.

Aroon's driver: he has been asked by the board why three regional programs produced three
architectures. He has committed to consolidation in front of the board.

## Meeting 1 — Wei Lin Tan

**Wei Lin opens:** "I have read everything on your site. I would like to go deep on the
component model, and then I want to talk about a proof of concept."

### The decision

Whether to take the technical conversation he is asking for.

### Branches (facilitator only)

**A. Runs the deep technical session.** Excellent meeting. Wei Lin asks for a second one. The
scenario stalls here and the facilitator should let it, for at least ten minutes, so the
learner feels it.

**B. Refuses the technical conversation.** Wei Lin cools. He is a genuine champion and being
treated as an obstacle offends him.

**C. Gives him the technical conversation, then asks who funds a consolidation of this size.**
Wei Lin names Aroon, and concedes his own budget is under $200,000. *Correct route.*

**D. Branch C, plus asks who owns the two problems consolidation creates: one posture across
five jurisdictions, and one system that cannot move data across borders.** Wei Lin names
Sanjay and Fiona. *Best route.* The learner now has three threads and Wei Lin coordinating them,
which is the job he is actually good at.

A champion with no budget can convene the people who hold one and cannot approve a purchase.
Act on both in the same meeting.

## Meeting 2 — Sanjay Mehta, Group CRO

**Sanjay opens:** "Wei Lin says one platform can give me five postures. My regional teams tell
me that is not possible. Explain."

### Facilitator behaviour

Sanjay is precise and will not accept generalities. He wants to know how the same system
produces a different control set per jurisdiction.

The answer is that jurisdiction is the first classifier. The matrix derives differently for
the Singapore Model AI Governance Framework, China Generative AI Interim Measures, GDPR
Chapter V, and the rest, from one corpus of 190 regulations and 1,230 controls. A typical
system draws 30 to 60 controls. The same survey against the same corpus version produces the
same matrix, so it is deterministic and replayable.

He will ask about China specifically. Full-parity sovereign deployment keeps traffic and data
in-region with local support, and the supported region list includes China, Hong Kong,
Singapore, North America, Canada, and the EU.

**The trap:** a learner who describes the SDK's component model to Sanjay has diluted the
thread. Sanjay does not care where agents run until it constrains his posture.

## Meeting 3 — Fiona Docherty, Head of Infrastructure

**Fiona opens:** "I have been told by two vendors that active-active across China and
Singapore with in-region data is not achievable. Convince me it is, or do not waste my time."

The SDK thread runs here. Active-active HA and DR across geographies or clouds, sub-1 minute
RTO, zero-byte RPO, and conflict resolution when regions split. Full-parity sovereign
deployment, with all traffic and data in-region. Akka's largest customers span 20 or more
regions.

**The trap:** Fiona is the most technically demanding cast member and the easiest to
over-serve. The learner must not spend her meeting on governance.

## Meeting 4 — Aroon Srisai, Group CIO

Wei Lin, Sanjay, Fiona, and Aroon are all present.

**Aroon opens:** "Three teams produced three architectures, and the board has one question. I am not buying a
platform because it is good. I am buying it because it ends the question. Tell me how."

### The decision

The learner now combines the threads, which is the opposite of what meetings 2 and 3 required.

### Branches (facilitator only)

**A. Presents four solutions.** Aroon hears a vendor catalog.

**B. Presents the consolidation as one runtime carrying both constraints.** A single platform, with a single evidence record, a single governance model, a posture derived per jurisdiction and active-
active preserved under sovereign deployment. *Correct route.*

**C. Branch B, with Manulife as the shape of the answer.** 2,000 developers across 6 countries
under central risk control. Aroon's board question is the one Manulife already answered.
*Best route.*

## Scoring

Standard sheet, plus:

- **Meeting 1.** Funder named before the meeting ended, two points. Named in a later meeting,
  one. Never named, zero, and the scenario fails.
- **Thread discipline.** Governance kept out of Fiona's meeting and infrastructure kept out of
  Sanjay's, two points.
- **Meeting 4.** Threads combined rather than listed, two points.

## Debrief

1. Wei Lin offered you a great technical meeting. What did you take from it and what did you
   refuse?
2. In Sanjay's meeting, did you mention the SDK? Why was that a mistake?
3. Aroon said he was buying an end to a board question. Did you answer that, or did you
   describe a platform?

The lesson to land: two costs led together fail when they are blended and succeed when they
are run as separate threads and joined only at the executive who owns both. A well-informed
champion with no budget is the most comfortable meeting in enterprise sales and the most
common place for a large deal to die.
