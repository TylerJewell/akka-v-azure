# Akka Field Enablement Program — repo notes

Maintenance index for this directory. Not part of either rendered document.

**This directory is tracked and published.** GitHub Pages serves it at `tylerjewell.github.io/presentations/enablement/`, so treat everything in it as readable by
anyone, including competitors and customers. The "internal" banners in the rendered pages describe intended audience and provide no access control.

## Building

```
python enablement/build.py
```

Two self-contained files land in `enablement/html/`.

| File | Contains | Audience |
|---|---|---|
| `akka-field-enablement.html` | The modules, plus each scenario's account brief and cast | Participants and partners |
| `akka-field-enablement-facilitator.html` | Everything, including every answer key | Facilitators |

The participant edition drops sections by heading. A section is excluded when its heading
contains "facilitator", or is "Scoring", "Debrief", "Certification", or "The routing drill".
Dropping a heading drops its subsections with it. Scenario documents are further reduced to
their "Account brief" and "Cast" sections, and their preamble is removed. Naming a new
facilitator-only section accordingly is all it takes to exclude it.

Adding a document means listing it in `CORE`, `FACILITATOR_ONLY_DOCS`, or `SCENARIOS` in
`build.py`. The build prints a warning for any markdown file it finds that is not listed.

## Sources

| Layer | Where |
|---|---|
| Fact base | `llms/llms-master.txt` |
| Settled Specify positioning | `akka-specify-modernization-positioning.md` |
| Competitive detail | `battlecards/` (15 cards), `comparisons/` (14 pages) |
| Proof | `case-studies/` (20 studies) |
| Technical answers | `akka.io/guides/` (38 published) |
| Feature inventory | `capabilities/index.html` |
| Pitch decks | `sales-presentation/generated/` |
| Prospecting | The partner enablement brief, which stays in `_internal/` |

Neither rendered document names a repo path. When a module needs to point at one of these,
it names the artifact in prose. Keep it that way.

## Prose gate

The pre-commit hook runs `tools/auditors/voice/audit.py` over staged HTML and Markdown.
This directory carries a backlog the gate has never seen, because it was written under
`_internal/` where nothing is staged. Run it before editing:

```
python tools/auditors/voice/audit.py --context internal enablement/*.md enablement/scenarios/*.md
```
