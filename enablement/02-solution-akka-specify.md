# Akka Specify — removes rework

## 1. The cost and who pays it

Akka Specify removes rework. Teams write plain-language specifications, and every change is verified against them. A change that drifts from intent fails a check before it ships, so technical and knowledge debt stop accumulating. Akka guarantees this, in the same class of contractual commitment it makes for resilience and scalability.

The people who pay this cost:

| Role | What they own | What they say |
|---|---|---|
| CIO | Systems development and delivery commitments | "Every release costs more than the last one." |
| Head of Platform, PlatformOps | Consistency across every team | "Forty teams are building forty different ways." |
| VP Engineering | Engineering capacity | "Half my team maintains what the other half shipped." |
| Line-of-business owner | The backlog waiting on engineering | "I have eighteen months of requests and no engineers." |
| Head of Modernization | A legacy estate nobody wants to touch | "Nobody left here knows what that system does." |

## 2. The customer challenge

**Rework consumes capacity.** 20 to 40% of engineering capacity is lost to rework caused by
earlier architectural choices. That figure grows as a system ages, because the knowledge of
what the system does drifts out of date faster than the code does.

**Specifications go stale the day they are written.** A requirements document describes
intent at a moment. Code changes afterwards. Nothing enforces the relationship, so the
document becomes fiction and the only description of the system is the source.

**Engineering is the bottleneck on who can build.** Product managers and business analysts
know what the system should do and cannot express it in a form that produces a system.

**Modernization stalls on unknown behaviour.** A legacy system cannot be replaced until somebody establishes what it actually does. The expense of that work is why modernization programs get funded and then quietly stop.

**Delivery engagements hand back systems the customer then owns.** A months-long
forward-deployed engineering engagement produces a bespoke system, and the customer inherits
it along with a standing integration team.

## 3. Capabilities and core features

**Behaviours as checks.** A system's intended behaviours are defined as checks, verified continuously, with guardrails that block any change that drifts from
intent. Because the behaviours are checks and the checks run continuously, the specification
stays true to the running system.

**Six specifications produce a delivered system.**

| Specification | What it contains | What it compiles to |
|---|---|---|
| Goals and intent | Purpose, success metrics, decision rights | Acceptance criteria |
| Functional requirements | Agents, tools, orchestration, memory, APIs, UI | The system's components |
| Risk envelope | What could go wrong, industry, jurisdiction | Safeguards enforced at runtime and verified by testing |
| Knowledge sources | What the system must know | An integrated semantic layer with a knowledge graph, hybrid retrieval, multi-hop reasoning, and durable shared memory |
| Operational envelope | SLA, regions, latency, token budget | Deployment topology and token economics |
| Improvement policy | What to optimize toward, how far it may tune itself | The reinforcement-learning and self-improvement loops |

One governed system comes out, with agents, safeguards, evidence, the semantic layer, tests,
and deployment. Every part traces back to the specification that required it.

**Akka Specify governs the SDLC the customer already has.** A large enterprise asks first whether adoption means moving to Akka's platform or governing the tools they already run, and this is the answer.

| SDLC element | How Akka Specify works within it | Status |
|---|---|---|
| Repos | Runs in the customer's git repo, with project state in `.akka/` | Built and demonstrated |
| CI/CD | Generates a CI workflow into the repo and verifies it gates the merge; the coverage check reds if CI is missing or not enforcing | Built |
| Security scanning | SAST, secret, and dependency scanning are required surfaces; a central scanner is recorded by attestation | Built, with the delegated case wired |
| Deployment | Deploy to the Akka platform, or record a receipt from the customer's own deploy system | Platform path built; deploy to the customer's own infrastructure is a delegated adapter, partially built |
| AI harnesses | The `/akka:specify` commands run inside Claude Code, Cursor, Gemini, and Codex | Built for those assistants |

Claim the four built surfaces. Mark deployment to the customer's own infrastructure and the
central-system adapters (SIEM, vault, identity) as roadmap.

**The governed steps compose into a factory.** Specification, plan, tasks, implementation,
review, build, and deploy each run as a step that is verified as it completes. A team running
the full sequence moves work from idea to production in hours, and every step leaves a record
of what was checked. The steps work because the runtime underneath admits one correct form
for each problem, so a generated system has one target form. Akka Specify is
how that property is carried across the whole lifecycle instead of stopping at the SDK.

**Modernization uses the same system.** For an existing system, Akka recovers what the
legacy code does and turns it into checks the replacement must pass, including checks that
the replacement reproduces the old behaviour. Modernizing one legacy system is the
demonstration. The modernized software factory is what the customer keeps.

Do not name discovery tools or discovery partners. How Akka recovers legacy behaviour is not
part of the pitch.

**Portability.** The customer's investment is in specifications instead of vendor-proprietary primitives, so systems stay portable across deployments and Akka
versions.

## 4. Engagement models

Three models. The customer-owned factory leads.

1. **The customer's teams run the factory,** operating Akka Specify inside their own repos, CI, scanners, and AI assistant. Lead with this model.
2. **Akka builds for the customer.**
3. **Akka delivers for the customer.**

Each model applies to new systems and to modernization. Pricing is the platform price, set
by Akka and all-inclusive, and it is close to the same across the three models. The customer pays
slightly less when their own teams do all the work and slightly more when Akka does all of
it. The choice between models is who operates the factory.

The delivered model is an all-inclusive managed engagement: the platform, the
infrastructure, the AI tokens, any model training, the delivery of the system, and 24/7 SRE
operations, under a single agreement.

## 5. The wedge engagement

Akka will build a system a customer needs, agentic or not, to get the platform installed and
carrying production traffic. The engagement is consulting and is priced as consulting. What
it buys is an installed platform, a production reference inside the account, and a team that
has watched delivery run at the speed the platform allows.

**The use case does not have to involve AI.** A claims intake rewrite qualifies. So does an order-promising system that has to become real-time, a batch job the business has outgrown, or a legacy service nobody left can maintain. The platform is installed either way, and every cost in the routing table is still there to route on afterwards.

**What makes a use case a good wedge.** The work is funded from a budget that already exists and is small enough to reach production in weeks. Someone inside the account has already estimated it in quarters or years. The system carries real traffic once it ships. A named business owner will
accept it and say so afterwards.

**This question finds one.**

> "What is on next year's roadmap that you wish were finished next month?"

Ask it of an operations leader. Engineering owns the estimate and will defend it. Operations owns the delay and resents it.

**The account remembers the estimate gap.** A customer who has been told a system takes a year, and then watches it carry traffic in six weeks, has learned more about the platform than any demo teaches. The engagement returns nothing else, and it does not need to.

**Quote weeks only when the six specifications can be filled.** The estimate is the promise
the account will hold Akka to, and a wedge that runs long installs nothing and costs the
expansion. Agree the production slice, the acceptance criteria, and the owner before the
engagement starts.

**Never win the estimate argument in front of the person who made it.** The fourteen-month
figure was produced honestly, on a stack where fourteen months is correct. Say that, and let
the difference come from the platform instead of from the estimator.

## 6. Differentiators

**Against a forward-deployed engineering engagement or a systems integrator.** The common
alternative for a team that would rather not build is a months-long engagement that hands
back a bespoke system the customer then owns and operates. Spec-driven delivery reaches the
same production outcome through generation on the platform, in weeks, without a standing
integration team. What the customer keeps afterwards is a factory any team can use.

**Against AI coding assistants.** Copilot, Cursor, and Claude Code generate code, and none of them verifies that code against a specification or blocks a change that drifts from intent. Akka Specify runs inside those assistants and adds the verification. Saying so early wins credibility with an engineering audience, because the tools are a complement.

**Against a platform team with golden paths.** A golden path depends on every team
remembering to follow it. A style guide, a platform team, and a review board all depend on a
person applying them. Specify enforces the same intent as a check that fails a build.

**Against low-code and workflow automation.** n8n and comparable tools do not scale to
enterprise agentic workloads and carry no clustering, no resilience guarantees, and no
compliance posture. Specify produces systems on a runtime that guarantees both.

**The claim to lead with.** Debt prevention is contractual. Akka guarantees the customer's
software stays free of technical and knowledge debt as it ages, because the system enforces it and the team does not have to.

## 7. Use cases and quick wins

**Use cases that fit.** A backlog of line-of-business AI systems that engineering cannot
reach. A legacy estate blocking a modernization program. An organisation standardising how
hundreds of developers across regions build. Regulated systems where the safeguards must
trace back to a requirement. Teams whose specifications and code have already diverged.

**Quick wins that land in one meeting.**

- *Write one requirement and watch it compile.* Take a real requirement from the customer's
  backlog, in their words, and generate the specification and a running skeleton live.
- *Point it at their repo.* Run the drift check against an existing service and show which
  behaviours no longer match what was written down.
- *Recover one legacy service.* Turn what the legacy code does into checks the replacement must pass. That demonstration unblocks a stalled modernization program.
- *Hand the keyboard to the product manager.* A non-engineer states an intended behaviour and the factory produces the system. The line-of-business owner becomes the champion at that moment.

## 8. Discovery questions

1. What share of your engineering capacity goes to rework?
2. How many teams build agentic systems here, and how many different ways do they do it?
3. When a requirement changes, how do you find every place in the code that implements it?
4. Who is allowed to build today, and who wants to?
5. What does your CI gate on right now?
6. What stalled the last modernization program?
7. If we delivered a production slice in four to six weeks, who signs off that it is done?

Question 7 is the qualifier. If nobody can answer it, there is no funded outcome.

## 9. Objections

**"We already use Cursor and Copilot."** Correct, and Specify runs inside them. Those tools
generate code. Ask what stops a generated change from drifting away from what was specified,
and let the silence do the work.

**"We have a platform team and golden paths."** Ask how compliance with the golden path is
measured today. The answer is review, and review depends on a person remembering.

**"We are not putting AI-generated code into production."** The generated system is verified
against a specification and every safeguard traces back to the requirement that produced it.
Offer the drift check against their existing hand-written code first, which is a lower-risk first step and produces a finding in most estates.

**"We already signed a systems integrator."** Two responses. The customer-owned factory
model works alongside an SI, because the SI's team can operate it. And ask what the SI hands
back at the end and who owns it afterwards.

**"Our specs always go stale."** Written specifications do. Specify defines behaviours as
checks that run continuously, so a specification that stopped being true fails a build.

**"This sounds like a methodology."** It is a system the customer runs. Do not describe Akka
Specify as a structure and methodology.

## 10. What to send after the call

- `akka.io/guides/code-drifting-from-spec`
- `akka.io/guides/what-a-specification-contains`
- `akka.io/guides/non-developers-build-agents`
- `akka.io/guides/many-developers-one-way`
- `akka.io/guides/spec-driven-in-existing-tools`
- `akka.io/guides/testing-a-generated-system`
- `akka.io/guides/technical-debt-over-time`
- `akka.io/guides/who-maintains-the-system`
- Case study: Dojo, merchant onboarding in production in weeks, built by college graduates
- The Akka Specify deck

## 11. Certification

Run a 20-minute discovery call against a facilitator playing a CIO who has funded a
modernization program that stalled twice. Pass requires: the rework cost quantified in the
customer's own numbers, the correct engagement model proposed and justified, one quick win
proposed with a date, and no use of the words "methodology" or "process".
