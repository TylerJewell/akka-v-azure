# Akka Specify — Modernization Positioning and Specify Deck Recommendations

Internal working note. Not for publication. Written in the house voice
(`competitive/case-studies/case-study-rules.md`): direct statements of fact, no
flourishes, numbers over adjectives, no antithesis reveals, no hype words.

Purpose: capture the positioning we settled on for modernization, the
recommendations for the Specify sales deck, three customer stories to add, and the
open decisions to resolve when building the deck.

---

## 1. The positioning

Akka Specify guarantees your software stays free of technical and knowledge debt as
it ages.

Akka Specify is a system that builds and modernizes software. It defines each
system's intended behaviors, verifies them continuously, and enforces guardrails
that stop any change from drifting away from that intent. Technical and knowledge
debt do not accumulate, because the system enforces it, not the team.

This is a guarantee, the same class of contractual commitment Akka already makes for
resilience and scalability. It is a system the customer runs, not a practice teams
are taught.

## 2. The mechanism

Three parts, always on:

1. Define the system's behaviors as checks, not documents.
2. Verify those behaviors continuously.
3. Enforce guardrails that block any change that would drift from the intended
   behavior. A change that diverges fails a check before it ships.

Because the behaviors are written as checks and verified continuously, the
specification stays true to the running system. The knowledge of what the system
does cannot drift out of date, and the code cannot rot without failing a build.

## 3. What the mechanism produces

- Technical and knowledge debt stop growing as systems age.
- The customer runs an internal AI software factory that any team can use, including
  teams without deep engineering backgrounds. A team states the intended behavior;
  the factory builds the system and verifies it against that intent.
- The systems run on the Akka Agentic AI Platform, an architecture that guarantees
  resilience and scalability.

The name for these three held together is continuous modernization: one adoption,
and every system the factory produces or maintains stays true to intent, free of
debt, and resilient as it ages.

## 4. Two entry points, one system

Akka Specify builds new systems and modernizes existing ones through the same
system.

For an existing system, Akka recovers what the legacy code does and turns it into
checks the modern system must pass, including checks that the new system reproduces
the old behavior. The rebuilt system runs on the Akka Agentic AI Platform. Modernizing
one legacy system is the demonstration. The modernized software factory is what the
customer keeps.

Note on discovery: how Akka recovers what a legacy system does is not part of the
pitch. Discovery is a plain Akka step. Do not name discovery tools or partners.

## 5. Language and positioning decisions we settled

- Do not describe Akka Specify as a "structure and methodology." That sounds like a
  consulting process. It is a system that guarantees an outcome.
- Do not mention discovery partners or how discovery is done.
- Modernize the customer's software factory, not one project. The single-system
  result is the demonstration; the factory is the deliverable.
- "any team" is the phrasing, not "any stakeholder."
- The resilience-and-scalability guarantee is contractual and core. Debt prevention
  is framed the same way, as a guarantee.
- Voice: state facts. Numbers over adjectives. No antithesis reveals ("A is X; B is
  Y", "isn't just X, it's Y"). No hype words. No "load-bearing" or similar metaphors.

## 6. Specify deck — recommendation

Current arc: What is Akka Specify, Spec-driven delivery, Delivered in weeks, Where it
runs, Let Akka build your system for you, Let Akka deliver your system for you,
Price, Close. That spine sells fast delivery of new systems with Akka doing the work.

The positioning has grown past that spine. The recommendation is a strategic reframe,
not a couple of inserted slides. Most of the deck's substance stays; the framing at
the top, one mechanism slide, added modernization content, and a wider offer at the
engagement slides change.

### Engagement models (decided): three, customer-owned factory leads

The deck presents three engagement models, with the customer-owned factory as the
lead:

1. Your teams run the factory. The customer owns and operates Akka Specify inside
   their own repos, CI, scanners, and AI assistant. This is the primary model.
2. Akka builds for you.
3. Akka delivers for you.

Each model applies to building new systems and modernizing existing ones. The
customer-owned factory is the same story as governing the SDLC the customer already
has (section 10): the factory the customer owns is their existing toolchain, governed
by Akka Specify.

### Pricing

Pricing is the platform price, set by Akka and all-inclusive. It is nearly the same
across the three models. The customer pays slightly less when their own teams do all
the work, and slightly more when Akka does all the work. The choice between the
models is who operates the factory. The price is close to the same in all three.

### Slide-by-slide plan

| Slide | Action | What it becomes |
|---|---|---|
| sp-01 What is Akka Specify | Reset | The definition in section 1: a system that builds and modernizes software and guarantees it stays free of technical and knowledge debt as it ages. |
| sp-02 Spec-driven delivery | Reframe | The mechanism in section 2: define behaviors, verify continuously, enforce guardrails against drift. |
| sp-03 Delivered in weeks | Keep, broaden | Keep the speed claim. Add the second entry point: the same system modernizes an existing application, with checks that it behaves the same. |
| new, after sp-03 | Add | Continuous modernization and the software factory: debt stops growing as systems age; the factory keeps every system true to intent; any team can use it. Do not mention how discovery is done. |
| sp-04 Where it runs | Keep, sharpen | Runs on the Akka Agentic AI Platform, resilience and scalability guaranteed. Carry the guarantee as the contractual claim it is. |
| sp-05 / sp-06 engagement | Expand | Three models, led by the customer-owned factory: your teams run the factory; Akka builds for you; Akka delivers for you. Each applies to building new and modernizing existing. |
| sp-07 Close | Reframe | Modernize how you build software, and keep it modern. Cost and delivery options follow. |

### Reframed sp-01 content

Headline: Akka Specify guarantees your software stays free of technical and knowledge
debt as it ages.

Definition: Akka Specify is a system that builds and modernizes software. It defines
each system's intended behaviors, verifies them continuously, and enforces guardrails
that stop any change from drifting away from that intent. Technical and knowledge debt
do not accumulate, because the system enforces it, not the team.

Support:
- It defines a system's behaviors as checks, not documents.
- It verifies those behaviors continuously.
- It blocks any change that would drift from the intended behavior.
- The result is guaranteed and contractual, the same class of commitment as
  resilience and scale.

## 7. Modernization stories to add

Each proves one pillar of the positioning. Numbers are stated cleanly. Before these
go customer-facing, confirm the figures, decide attribution (Dojo is named; the bank
and grocer are anonymized), and give each the eight-section case-study treatment with
the ROI scorecard (Speed to Production, Cost to Operate, Scale).

**Dojo — any team can run the factory.**
Dojo hired college graduates with no enterprise experience. With Akka Specify they
built AI automation for merchant onboarding that runs 5,000 onboardings per month.
Proves: a team without an enterprise engineering background built and shipped
production automation. Maps to Speed to Production and to the "any team" claim.

**An Asian bank — modernize fast, at parity.**
An Asian bank modernized a 10-year-old mobile application. The work was budgeted for
3 years. It reached parity in 2 months. Proves: modernization speed and behavioral
parity with the original. Maps to Speed to Production and to behavioral equivalence.

**A North American grocer — replace expensive SaaS with owned software.**
A North American grocer replaced a retail-promotion SaaS system that cost $2M per
year. It moved to software it owns, built with Akka Specify, in 4 weeks. Proves: cost
removed, ownership gained, and speed. Maps to Cost to Operate and to the software the
customer owns.

## 8. Open decisions and checks before anything ships

- Engagement models and pricing are decided (section 6): three models at the same
  all-inclusive platform price, slightly lower when the customer does all the work and
  slightly higher when Akka does it all.
- Confirm the three stories' numbers and attribution; convert each to the eight-section
  case-study format with the ROI scorecard.
- Read any compliance counts (EU AI Act, IMDA, residency) live from the corpus
  (`C:\Users\tyler\explain`), never from memory.
- Run the marketing-brand audit (`tools/auditors/marketing-brand/audit.py`) over the
  deck output before committing.
- The behavioral-parity and debt-guarantee claims are strong. Confirm what legal and
  the case studies support before they appear in customer copy.

## 9. Cross-deck coherence

The Optimize deck is locked and is a separate part of the story. Even so, the three
sales stories share one spine: define behaviors, verify continuously, guard against
drift. Specify builds the system from intent and keeps it modern. Optimize runs it at
a governed cost. The platform guarantees resilience and scale under both. A single
line to that effect at the top of the Specify deck keeps it consistent with the rest.

## 10. Akka Specify governs the SDLC you already have

A deck thread and one slide. It answers the first question a large enterprise asks:
whether adoption means moving to Akka's platform or governing the tools the customer
already runs. The answer is that Akka Specify governs the tools the customer already
runs. This reinforces the customer-owned factory model (section 6): the factory is
the customer's existing toolchain, governed.

| SDLC element | How Akka Specify works within it | Status |
|---|---|---|
| Repos | Runs in your git repo; project state in `.akka/`; the commands operate on the repo you already have | Built and demonstrated |
| CI/CD | Generates a CI workflow into your repo and verifies it gates the merge; the coverage check reds if CI is missing or not enforcing | Built |
| Security scanning | SAST, secret, and dependency scanning are required surfaces; a central scanner is recorded by attestation | Built (provisioned); delegated case wired |
| Deployment | Deploy to the Akka platform, or record a receipt from your own deploy system | Platform path built; deploy-to-your-own-infrastructure is a delegated adapter, partially built |
| AI harnesses | The `/akka:specify` commands run inside your AI coding assistant (Claude Code, Cursor, Gemini, Codex) | Built for those assistants |

State the claim for the four surfaces that are built: repos, CI, scanning, and the AI
assistant. Mark deployment to your own infrastructure and the central-system adapters
(SIEM, vault, identity) as roadmap so the claim stays accurate.

Why it matters: it makes modernization a low-risk adoption. The customer keeps their
repos, CI, scanners, deployment, and AI assistant, and Akka Specify governs them and
keeps them free of debt. For a regulated enterprise, this is often the difference
between a pilot and a no.
