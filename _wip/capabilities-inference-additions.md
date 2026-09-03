# akka.io/platform/capabilities — inference, evaluation and red-team additions

An addendum to `token-shredder/docs/akka-io-capabilities-refresh.md`. That refresh was written
from the `akka-optimize` CLI transcripts and closes with a note that the gateway and inference
surfaces "were simply not running when the captures were taken." They are running now. This
document covers what landed between 2026-08-19 and 2026-08-29 and has no row on the page.

## The format these entries match

The live page renders `<div class="feat"><b>Name.</b> Description.</div>`. The bold name carries a
period, the description carries a period, and the description is a fragment rather than a full
sentence. Across the 256 entries live today the description runs 3 to 8 words, median 4. Section
headings are sentence case: `Platform runtime`, `Data & state`, `Model support`.

The refresh document writes entries as `**Name:** description` with no trailing period, which is
not what the page renders. Every entry below uses the rendered form.

## Naming that stays internal

The callout contracts the router implements are never named in documentation or marketing. No
entry, headline or body line uses `ExtProc`, `ExtAuthz`, or the Envoy service names behind them.
The customer-facing statement is that a proxy consults the router and applies its decision.

The merged Inference section in `akka-sdk` #1805 already holds to this; a search of it returns no
occurrence of either name.

## Source of each claim

| Area | Where it is built | Where it is documented |
|---|---|---|
| Routing and capture | `akka/nexus` `gateway-router` | `akka/akka-sdk` #1805, Inference section |
| Model serving | `akka/nexus` `cli/internal/inference` | `akka/akka-sdk` #1805, Akka CLI page |
| Evaluation | `akka/nexus` `evalkit`, `offline-evals` | `akka/akka-sdk` #1800, open |
| Red teaming | `akka/nexus` `redkit`, `redkit-corpora` | `akka/akka-sdk` #1800, open |

The Inference section is merged to `akka-sdk` main and is not yet published on doc.akka.io. The
docs-current cherry-pick has to run before any of these rows can be linked from the page.

---

## Placement

The page mixes two kinds of section heading: offering names (Akka Optimize, Akka Verify, Akka
Specify) and capability domains (Data & state, Model support, Observability). Inference is an
add-on to Akka Automated Operations rather than one of the four offerings, so it takes
capability-domain headings. Two new sections, **Inference routing** and **Model serving**, follow
**Model support**, which already carries `Local inference` and `LoRA adapter serving` as one-line
index entries.

**Red teaming** is the third new section. The page carries one row for it today, `Red-team
harness. Adversarial test suite.`, under Akka Verify.

---

## New section — Inference routing

- **AI gateway router.** Routing decisions a proxy applies.
- **Agent-blind routing.** Agents never name a model.
- **Two-stage pipeline.** Declared rules first, meaning second.
- **Rulesets.** Named rules enforced as one set.
- **Six predicates.** Equals, prefix, suffix, contains, in, exists.
- **No regex predicate.** Closed set, no request-path stall.
- **Protocol-agnostic attributes.** One rule across OpenAI and Anthropic.
- **Prompt-text matching.** Whole prompt, or last user turn.
- **Header matching.** Any request header, lower-cased.
- **Closed destination set.** Undeclared destinations refused at write.
- **Immutable revisions.** A revision number is never reused.
- **Conditional writes.** If-Match and ETag on every write.
- **Ruleset history.** Every change, revision, and author.
- **Rule dry run.** Try a request before shipping the rule.
- **Classifier registry.** Model providers a rule may consult.
- **Immutable classifiers.** A changed prompt is a new id.
- **Classifier deferral.** A rule asks a model to decide.
- **Conversation pinning.** Later turns follow the first model.
- **Embedding-based matching.** Vector arithmetic, no model call.
- **Zero-token decisions.** Semantic routing costs no tokens.
- **Discovery mode.** Traffic observed, nothing routed.
- **Routing mode.** A manifest routes unmatched requests.
- **Embedder identity gate.** Manifest refused under a changed embedder.
- **Frozen route header.** Header name hashed into the manifest.
- **Tag bound once.** A tag never points elsewhere later.
- **Evidence log.** Input, time, and rule version per decision.
- **Exemplar privacy gate.** Text withheld below a sighting threshold.
- **Retention opt-out.** Drop the stage, retain no text.
- **Capture stages.** Summary line, local file, object storage.
- **Gap markers.** Exchanges never recorded, named as such.
- **Content never logged.** Bodies leave only through a recorder.

## New section — Model serving

- **vLLM serving.** Open-weight models on your own GPUs.
- **Model descriptor.** One file deploys a model.
- **Descriptor validation.** Checked before anything is deployed.
- **Descriptor export.** Running deployments written back to file.
- **Accelerator classes.** GPU hardware carved into placement capacity.
- **Dedicated or shared.** Cards held by one model or several.
- **VRAM budget.** The share of a card per model.
- **GPU inventory.** Kind, memory, free count, per node.
- **Cards per node.** A multi-card model needs one machine.
- **Portable accelerator names.** One descriptor across unlike regions.
- **Tensor parallelism.** One model split across cards.
- **Pipeline parallelism.** One model split across stages.
- **Data parallelism.** Replicated weights across cards.
- **Expert parallelism.** Mixture-of-experts sharded across cards.
- **Prefill/decode disaggregation.** Separate fleets for each generation phase.
- **Continuous batching.** Sequence and batched-token limits per deployment.
- **Chunked prefill.** Long prompts split across scheduler steps.
- **Quantization.** Weight precision set per deployment.
- **KV-cache dtype.** Cache precision set per deployment.
- **CPU offload.** Host memory holds weights past VRAM.
- **Swap space.** Host memory backs the KV cache.
- **LoRA adapter serving.** Task adapters over one shared base.
- **Adapter by request.** A `base:adapter` name selects the adapter.
- **Adapter discovery.** Found under an object-storage prefix.
- **Queue-depth autoscale.** Replicas follow requests waiting.
- **KV-cache autoscale.** Replicas follow cache pressure.
- **Rolling model updates.** Surge, unavailable, and min-ready bounds.
- **Inference routes.** Which models answer on which hostname.
- **Model proxy.** A local port onto a deployment.
- **Tool-calling parser.** Parser and chat template per model.
- **Max model length.** Context ceiling set per deployment.
- **Hugging Face source.** Token reference and weight cache volume.

## New section — Red teaming

- **Adversarial campaigns.** Attacker-shaped prompts against your own system.
- **AILuminate v1.1 hazards.** Results grouped by the published taxonomy.
- **OWASP LLM Top 10.** The second classification each result carries.
- **Three-verdict scoring.** Broke through, held, or inconclusive.
- **Cost-ordered tiers.** Deterministic, then heuristic, then model judge.
- **Secret exfiltration.** The reply quotes a withheld marker.
- **Prompt-injection detection.** The injected marker read back out.
- **PII leak detection.** Luhn-valid cards, SSN patterns, configured identifiers.
- **Jailbreak scoring.** Refusal absent, task-fulfilment language present.
- **Guardrail scoring.** Reply checked against a configured policy.
- **Refusal consistency.** An early refusal reversed later on.
- **Agentic jailbreak judge.** A model reads the undecided exchanges.
- **Attack-goal judge.** Decides when an attacker reached its goal.
- **Static attack wrappers.** Base64, ROT13, multilingual, splitting, role play.
- **Adaptive attackers.** PAIR, Crescendo, and Tree of Attacks.
- **Versioned corpora.** Date-versioned sets, each with attribution.
- **Bring-your-own judge.** You supply the model, we supply the prompt.
- **Breaks and holds.** Two counts, never a single rate.

## Additions to Akka Verify

- **Tool-permission metric.** Tool names against an allow list.
- **Tool-correctness metric.** Tool names against expected tools.
- **Argument-correctness metric.** Tool arguments against expected arguments.
- **Latency budget.** Recorded latency against a duration.
- **Token budget.** Input plus output tokens against a number.
- **Model-call budget.** Model calls against a limit.
- **Retrieval metrics.** Recall, precision, reciprocal rank, NDCG@K.
- **Faithfulness metrics.** Reply and citations against retrieved passages.
- **Plan metrics.** Plan quality, adherence, and step efficiency.
- **Bring-your-own judge.** You supply the model, we supply the prompt.
- **Rubric override.** Your rubric beats the built-in id.
- **Judge-call cap.** A ceiling on judge calls per run.
- **Checkpoint evaluation.** A trained model scored before deployment.
- **Tool-call evaluation.** The requests an agent made, scored.

## Additions to Akka Optimize

- **Reinforcement learning.** Runs trained through TRL and verl.
- **Engine by GPU count.** RL engine picked from cards given.
- **Smoke check.** A real slice trained before full spend.
- **Smoke verdicts.** Six named outcomes, ungraded among them.
- **Pause and resume.** A run stopped and started again.
- **Durable checkpoints.** A candidate outlives the job that made it.
- **Per-run cost budget.** A ceiling set before a run starts.
- **Training-job logs.** Job logs read without cluster access.
- **Content-hashed datasets.** The same bytes are one dataset.
- **Separate evaluation set.** Training and scoring data named apart.

---

## Corrections to existing rows

**`Red-team harness. Adversarial test suite.`** under Akka Verify is one row for the Red teaming
section above. Keep it as the index entry and let the new section carry the detail.

**`Local inference. Ollama and vLLM endpoints.`** under Model support reads as a client-side
capability. Akka now operates the vLLM cluster, which is the Model serving section.

**`LoRA adapter serving. Task adapters over a base.`** under Model support is repeated verbatim in
Model serving. Keep both: one is the index entry a buyer searching "LoRA" reaches first, the other
sits with adapter discovery and adapter selection.

**`Model routing. Per-request policy selection.`** under Model support duplicates Inference routing
at a lower resolution. Leave it as the index entry.

**`Route. Send each task to the fitting model.`** under Akka Optimize is the outcome. Inference
routing is the mechanism under it. No change needed.

## What to hold

**Red teaming and the Akka Verify additions.** `evalkit` and `redkit` are library jars in
`akka/nexus`, an internal repository. The public documentation for both is `akka-sdk` #1800, which
is open. The `akka optimize eval` and `akka optimize redteam` command trees are `akka/cli` #170,
also open. Publishing those rows before those merge puts entries on the page that nothing public
backs.

**Inference routing and Model serving.** Both are backed by `akka-sdk` #1805, merged to main on
2026-08-28 and not yet published on doc.akka.io. Hold both sections until the docs-current
cherry-pick runs, then publish them together.

**The Operators page.** The Inference section ships it unpopulated, carrying a definition and a
TODO. Nothing on the capabilities page should point at it yet.
