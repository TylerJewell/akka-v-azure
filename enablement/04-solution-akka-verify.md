# Akka Verify — removes governance effort

## 1. The cost and who pays it

Akka Verify removes governance effort. Risk teams define policies once, and the runtime
enforces them across every agent, against 190 global regulations. Manulife rolled Akka out
to 2,000 developers in 6 countries under central risk control.

The people who pay this cost:

| Role | What they own | What they say |
|---|---|---|
| Chief Risk Officer | Regulatory exposure across every AI deployment. In governance-led deals the CRO is a primary budget holder alongside the CISO. | "I cannot tell the board how many AI systems we run or what they are allowed to do." |
| CISO, Security Lead | Policy enforcement, access control, audit trails | "We approve a system and then have no idea what it does in production." |
| Chief Compliance Officer, DPO | The regulatory deadline | "The EU AI Act applies to us in months and we have not classified anything." |
| Head of Model Risk | Model governance in a regulated institution | "Model risk management was built for models, and these are agents." |
| Head of Internal Audit | What gets handed to an examiner | "Our evidence is screenshots." |

## 2. The customer challenge

**Nobody can say which regulations apply.** An enterprise building AI across jurisdictions
has no repeatable way to derive the obligation set for a given system.

**Governance lives in a spreadsheet and a review board.** Controls are written down, approval
is a meeting, and nothing connects either to the running code.

**The approval cycle blocks delivery.** Each new AI system restarts the whole process, and
the process is negotiated from scratch every time.

**The evidence does not survive an examiner.** Screenshots, sampled traces, and mutable spans
are what most enterprises can produce today.

**Nothing can stop an agent.** By the time an observability tool's judge fires, the tool has
already executed and the response has already been sent.

**No one can prove that what runs is what was approved.** A system is signed off, and then it
changes.

## 3. Capabilities and core features

Verify evaluates, enforces, and governs.

**Evaluate.** Measure the agent against what good means, using LLM-as-judge and deterministic
evaluators, offline and online, against the interaction log.

**Enforce.** Run guardrails and policies at runtime, stop or redirect an action before it
happens, gate a deployment, and escalate to a human. Guardrails return a decision at a
boundary. Sanitizers redact, mask, or reshape content before it moves on. Safeguards are
driven by a policy matrix owned by compliance and enforced by the runtime, so compliance owns
governance and engineers do not hand-code it.

**Govern.** Keep the record an auditor asks for, map controls to regulations, and seal a
Governance Posture Package as evidence.

### The governance loop

1. **Define your risk.** Name, in plain language, what the AI system does, what it touches,
   what it decides, and what could go wrong.
2. **Identify your controls.** Translate the risk picture into the safeguards the system must
   implement and demonstrate. Verify maps the risk across 190 AI regulations.
3. **Enforce your posture.** Bind the signed controls into the running system and configure
   the test harnesses that verify each control behaves as expected.
4. **Improve your posture.** Detect changes that matter, to the system, the regulations, or
   the evidence, and use evaluation, testing, and replay to keep improving safety and
   accuracy.

### The signed Eval Matrix

The Risk Survey answers compile into one signed contract listing every safeguard the system
must implement and demonstrate. Rows come from regulations, corporate policy, and the project
itself. Each row carries its citation, its runtime binding, and its evidence event.

A typical system draws 30 to 60 controls from a corpus of 190 AI regulations and 1,230
controls, 742 of which carry financial penalties. The same survey against the same corpus
version produces the same matrix, so it is deterministic, reproducible, and replayable for
auditors.

### Jurisdiction is the first classifier

The matrix derives differently for the EU AI Act, China Generative AI Interim Measures,
Italian AI Law Article 4, Colorado AI Act, Texas TRAIGA, NYC Local Law 144, India DPDP, Japan
AI Promotion Act, Korea AI Act, California SB-942 and SB-53, NY RAISE, GDPR Chapter V, and
DORA. A platform team in Singapore, an actuarial team in Italy, and a frontier lab in
California each receive a posture derived from the same corpus.

### Runtime binding classes

Every control row compiles to one of these classes, and they are the vocabulary of the audit
trail. Learn the letters. An auditor asking for evidence of a control receives a specific event stream instead of a screenshot.

| Class | Binding | Behaviour | Event |
|---|---|---|---|
| **G** | Guardrail | Inline check at a tool, LLM, or agent-response boundary. Returns PASS, BLOCK, or ERROR before the action proceeds, and fails closed by default. | `GuardrailDecisionRecorded` |
| **H** | HITL boundary | Escalates to a reviewer queue and blocks until a human observation returns. | `HumanDecisionRecorded` |
| **W** | Workflow pause and resume | The orchestrating workflow durably suspends until a human resumes it, across crashes, deployments, and days. | `HumanDecisionRecorded` |
| **P** | Periodic evaluation | Scheduled aggregate evaluation over the interaction log. | `PeriodicEvaluationRecorded` |
| **E** | Event evaluation | Runtime-event-triggered evaluation that does not block. | `OnlineEvaluationRecorded` |
| **B** | Build and deploy gate | An evaluation harness runs at build and fails the deploy if the matrix is unmet. | Versioned, hash-chained report |
| **K** | Kill switch and system halt | Sits above per-call boundaries. All in-flight and future tool and LLM calls cease and the system moves to a defined safe state. | `HaltExercised` |

### Generation binds the matrix

The signed Eval Matrix is the input and a working agentic system with every safeguard bound
at the moment of generation is the output. Every row compiles to one or more runtime, build,
and review artifacts, and Akka wires each artifact back to the row that required it. The
signed and sealed result is the Governance Posture Package, a tamper-evident audit artifact
ready for regulatory handoff.

### The interaction log

Every interaction is saved into petabyte-scale, tamper-evident storage, indexed, queryable,
and cryptographically chained, so the records handed to an auditor are the records the
runtime emitted. The same record feeds replay testing, conformance reconstruction, drift
detection, audit evidence, test dataset generation, fine-tuning corpus curation, and incident
investigation. Akka Optimize trains on this same record, so governance and cost read one
record.

Retention is six explicit categories, each mapped to a regulatory floor and protected by
first-class legal hold: interaction log, trace tiers, Annex IV documentation, evidence
exports, held-execution archive, and audit and change log.

### The improvement loop

A review starts on a declared change, which is one of nineteen named change types in the AI events taxonomy; on a regulation update from the monthly corpus watch; on a scheduled review; or on runtime-detected drift. Verify then scopes the review to what actually changed. A prompt tweak is a half-day cycle. A foundation-model swap is
multi-week, pre-determined and pre-budgeted.

### Sign-off recipes

A declarative recipe engine routes change events to the right reviewers with dossiers, carry-forward rules, and quorum logic. No competitor sells this pre-production half of governance.

## 4. What observation cannot do

Observability and evaluation tools live outside the request path. Each capability below
requires the runtime that executes the agent. Reps should be able to recite them.

1. **Stop an action before it executes.** A guardrail returns PASS, BLOCK, or ERROR while the
   runtime holds the call, and required production guardrails fail closed.
2. **Durably suspend for human judgment.** Pause for seconds to days across crashes and
   deployments, then resume where it stopped. The EU AI Act requires that humans can pause,
   discontinue, override, review, or nudge an ongoing agentic process.
3. **Capture an authority snapshot at execution.** SPIFFE workload identity, the delegation
   chain from human to agent to sub-agent to tool, effective permissions, policy bindings,
   and governance version, all resolved at the moment of execution.
4. **Record whether a side effect executed.** The runtime gates the tool call, so the log records whether the tool ran. An observability tool sees only that an LLM said it would.
5. **Capture non-sampled, tamper-evident records.** Sampling is a cost lever for observability
   tools and it destroys a compliance record.
6. **Apply governance before deployment.** Classification, multi-persona change approval, and
   a sealed audit artifact, as a first-class product surface.

**Observation and enforcement stay separate.** Evaluations emit observations into the same
authoritative log and cannot change runtime state. Guardrails are the only primitive that
decides whether an action may proceed. That separation is what makes the audit trail
trustworthy.

## 5. The line to state precisely

Verify covers agents built on Akka and agents built elsewhere, and the coverage differs.
State the line precisely, because a technical buyer will find the seam.

- **Applies to any system, wherever it runs:** classification against the corpus, the derived
  obligation set, the signed Eval Matrix, sign-off recipes and multi-persona attestation, the
  Governance Posture Package, and evaluation against captured traffic.
- **Requires the agent to execute on the Akka runtime:** inline guardrail enforcement, durable
  HITL suspension, authority snapshots at execution, recording whether a side effect
  executed, the non-sampled hash-chained interaction log, and bidirectional conformance.

## 6. Differentiators

**Against observability and evaluation tools.** Those tools sample by design, have no authority in the request path, produce mutable and unchained traces, have no signed intent artifact to
compare against, treat retention as a billing tier instead of a regulatory mapping, and cannot record side-effect execution. Concede that they are useful for engineering
observability, then draw the line at the compliance record.

**Against GRC platforms (ServiceNow GRC, Archer, OneTrust).** Each holds the policy. Nothing connects the policy to the running system, so there is no runtime binding, no evidence event
per control, and no way to prove that what runs is what was approved. The two coexist: the GRC platform stays as the system of record for policy, and Verify supplies the binding and the evidence.

**Against hyperscaler governance.** Azure spreads governance across five services with no
inline enforcement and no human intervention for running agents. Bedrock guardrails run as a
separate evaluation layer after inference. Gemini runs safety filters and grounding as separate API calls outside the execution path.

**Against enterprise SaaS agent governance.** The Einstein Trust Layer governs Salesforce data. Cross-application agents fall outside it. Unity Catalog is data governance applied to agents, with no inline guardrails, no durable HITL suspension, and no runtime binding
taxonomy.

**The claim to lead with.** Akka covers governance from first classification through runtime
enforcement, across pre-production and production, in one system.

## 7. Use cases and quick wins

**Use cases that fit.** Financial services under DORA and the EU AI Act, with credit scoring
or AML monitoring classified high-risk. Insurance underwriting and claims triage requiring
explainability for adverse-action decisions. Healthcare clinical decision support with
clinical sign-off gates. Frontier labs under California SB-53 and NY RAISE needing a
non-sampled research record and a system-wide kill switch. Any enterprise operating the same
AI system across jurisdictions with different obligations.

**Quick wins that land in one meeting.**

- *Run the Risk Survey on one system.* The industry presets shorten time-to-matrix from weeks
  to a half day. Do it live on a system the customer names.
- *Show a guardrail block and the event it wrote.* The demo is the `GuardrailDecisionRecorded` event. Risk officers care about the record.
- *Pause an agent for three days.* Start a run, suspend it for a human decision, deploy over the top, resume it. The EU AI Act oversight requirement becomes concrete in that demo.
- *Reconstruct a conformance report.* Show the runtime rebuild an Eval Matrix from what the
  deployed code enforces and diff it against the signed one, with missing rows, orphan rows,
  and drift.

## 8. Discovery questions

1. How many AI systems do you have in production, and how many have a documented obligation
   set?
2. What happens today when an agent is about to take an action nobody approved?
3. What do you hand an examiner, and has it been tested against one?
4. How long does it take to get a new AI system approved here, and what drives the duration?
5. Who signs, and what exactly are they signing?
6. Can you prove the system running today is the system that was approved?
7. What is your retention obligation on AI interactions, and where does that data live?

Question 4 is the qualifier. A cycle measured in months is a funded problem.

## 9. Objections

**"We have a GRC platform already."** Keep it. Ask what connects a control in that platform
to the line of code that enforces it, and what evidence event proves the control fired.

**"Our observability tool captures everything."** It samples, and sampling is a cost lever
they configured. Ask what their sampling rate is, then ask whether an examiner accepts a
sampled record.

**"Legal reviews every AI system."** The review is manual and per system. Ask what a review
costs in elapsed weeks and how many systems are queued behind the current one.

**"The EU AI Act does not apply to us."** Jurisdiction is the first classifier, and there are
thirteen named regimes plus more. Name the one that does apply to them, from their industry
and their footprint.

**"Our agents run on Bedrock."** Use the line in section 5. Classification, the Eval Matrix,
sign-off, and the Governance Posture Package apply now. Inline enforcement follows the
workload.

**"This is a compliance tax on my engineers."** Safeguards are driven by a policy matrix
owned by compliance and enforced by the runtime. Engineers do not hand-code controls.

## 10. What to send after the call

- `akka.io/guides/which-regulations-apply`
- `akka.io/guides/what-evidence-an-auditor-asks-for`
- `akka.io/guides/stop-an-agent-before-it-acts`
- `akka.io/guides/prove-what-runs-was-approved`
- `akka.io/guides/who-is-accountable-for-an-agent`
- `akka.io/guides/agent-waits-for-a-human`
- `akka.io/guides/rules-that-differ-by-region`
- `akka.io/guides/agent-data-inside-a-jurisdiction`
- `akka.io/guides/reconstruct-what-an-agent-knew`
- Case study: Manulife, 2,000 developers, 6 countries, central risk control
- The Akka Verify overview and the Risk Survey
- The industry posture for their sector

## 11. Certification

Run a 20-minute discovery call against a facilitator playing a CRO at a European insurer with
a classification deadline and an agent estate running on Azure. Pass requires: the obligation
set framed before any Akka capability is described, the section 5 coverage line stated
accurately without overclaiming, three of the limits in section 4 recited correctly, and the
Risk Survey proposed as the next step with a date.
