# Public study materials

This lightweight companion includes the stage system prompts, frozen Study B plans, study protocols, cycle reports, aggregate analysis exports, and selected case traces. The [release manifest](public-release-manifest.json) maps original source filenames and SHA256 fingerprints to the public exports and their separate LF-byte fingerprints.

## Stage prompts and Study B plans

| Stage | Exact system prompt used |
|---|---|
| Draft D, all four batches | [draft.md](prompts/draft.md) |
| Check constructor, R01 | [checker-R01.md](prompts/checker-R01.md) |
| Check constructor, R02 | [checker-R02.md](prompts/checker-R02.md) |
| Check constructor, R03/R04 | [checker-R03-R04.md](prompts/checker-R03-R04.md) |
| Control C and feedback F continuations | [revision.md](prompts/revision.md) |

The [Study B protocol](protocol.md), batch amendments ([R02](protocol-R02.md), [R03](protocol-R03.md), [R04](protocol-R04.md)), and [behavior rubric](behavior-rubric.md) preserve the intervention and annotation definitions. The plans contain fixed tasks, seeds, budgets, and original strategy/environment identifiers: [R01](plan-R01.json), [R02](plan-R02.json), [R03](plan-R03.json), [R04](plan-R04.json). Those original identifiers are provenance; the analysis rebuild uses the files included here.

## Study and ablation reports

| Role in the paper | Cycle report | Protocol |
|---|---|---|
| Study A, 736 whole-workflow runs | [Trigger validity](cycles/2026-10-12-trigger-validity/report.md) | [Protocol](cycles/2026-10-12-trigger-validity/protocol.md) |
| Study B, 216 realizations | [Feedback refinement](cycles/2026-10-14-feedback-refinement/report.md) | [Protocol](protocol.md) |
| Table 3, 855 schema/heredoc recovery runs | [Strong-baseline recovery](cycles/2026-10-15-strong-baseline-recovery/report.md) | [Protocol](cycles/2026-10-15-strong-baseline-recovery/protocol.md) |
| Table 3, 855 local-progress runs | [Local progress](cycles/2026-10-23-local-progress/report.md) | [Protocol](cycles/2026-10-23-local-progress/protocol.md) |
| Table 3, 855 subagent runs | [Local recursion](cycles/2026-10-25-local-recursion/report.md) | [Protocol](cycles/2026-10-25-local-recursion/protocol.md) |
| Precursor study, outside the paper's 3,517-run accounting | [Pre-edit checking](cycles/2026-10-12-pre-edit-check/report.md) | [Protocol](cycles/2026-10-12-pre-edit-check/protocol.md) |

Study A's accounting comes from `2026-10-12-trigger-validity`, rather than the precursor. The five paper cycles include their original batch aggregate analysis fields in `analysis-Rxx.json`. Task-level Study A/B outcomes remain available in the [derived CSV tables](../supplement/README.md).

## Core cases and reconstruction scope

The [case index](packets/README.md) lists 11 Study B packets and 3 Study A packets covering every case named in the current manuscript, including all eight Study B counterevidence realizations.

Case exports retain tool arguments, observations, checks, patch text/fingerprints, and source-identity facts. They omit task statements/hints, model messages, wire requests, and infrastructure metadata. Reports retain the original findings, seeds, budgets, and denominators; machine aliases and checkout paths are replaced. Links point to bundled materials; unbundled original sources are labeled as plain filenames. The manifest records each transformation and both fingerprints.

The [rebuild guide](../supplement/reproducibility.md) reconstructs the complete 216-realization joins from the frozen CSV/JSON and recomputes the eight core counterevidence event analyses. All-trace tool counts are taken from the frozen aggregate CSV, with the final seven counterevidence traces independently rechecked. Full extraction from all 216 original packets requires the complete source archive, which is outside this lightweight release.
