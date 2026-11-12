# Reproducing the analysis

This guide connects the manuscript's claims to the configuration records, derived tables, and public-trace evidence in the project checkout. A task realization is identified by `(batch, task)`; branch-level records additionally identify D, C, or F. The four batches reuse 54 tasks, giving 216 realizations and 432 continuation branches.

## Configuration and inputs

The [method details](methods.md) specify the model, runtime, information supplied to each branch, stage budgets, and measurement definitions. The [original protocol](../protocol/protocol.md) and plans preserve the execution design:

| Batch | Draft seed | Check seed | Shared C/F seed | Plan |
|---|---:|---:|---:|---|
| R01 | 2026101401 | 2026101411 | 2026101421 | [R01](../protocol/plan-R01.json) |
| R02 | 2026101402 | 2026101412 | 2026101422 | [R02](../protocol/plan-R02.json) |
| R03 | 2026101403 | 2026101413 | 2026101423 | [R03](../protocol/plan-R03.json) |
| R04 | 2026101404 | 2026101414 | 2026101424 | [R04](../protocol/plan-R04.json) |

Each plan contains the fixed task list. R03/R04 share the final configuration. The [public-release manifest](../protocol/public-release-manifest.json) identifies bundled inputs, original-source fingerprints, public-export fingerprints, and declared unbundled original inputs. Stage prompts and cycle reports are indexed in [public study materials](../protocol/README.md). The analysis JSON files record hashes of their own inputs.

## Rebuild the current figures, tables, and reading copy

From the companion repository root, use Python 3.11+. The analysis, native Figure 1 SVG generator, and text scripts use the standard library; Figure 2 uses Matplotlib 3.11.1. Install the pinned [build dependencies](../requirements-build.txt); Tectonic 0.17.0 and Poppler are separate executables.

```powershell
python -m pip install -r requirements-build.txt
python -X utf8 scripts/verify_release.py
python -X utf8 scripts/build_v04_analysis.py
python -X utf8 scripts/build_v04_review_analysis.py
python -X utf8 scripts/build_v04_visuals.py
python -X utf8 scripts/build_text_manuscript.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1 -Compiler tectonic.exe
python -X utf8 scripts/verify_pdf.py --poppler pdftoppm --tag current-baseline
python -X utf8 scripts/verify_release.py --git-bytes
```

`build_v04_analysis.py` verifies the frozen inputs and reconstructs construction/replay/source summaries and endpoint accounting from the complete bundled CSV/JSON. It re-emits the verified process aggregate and two analysis tables. `build_v04_review_analysis.py` recomputes all 216 joined rows, group/batch/repository/draft-status summaries, the eight core counterevidence event analyses, and Table 3. Its all-trace tool counts come from the frozen `tool-allocation-v04.csv`; the final seven counterevidence packets are independently reprocessed and matched to that aggregate. The selected cycle analysis exports verify Study A and all three 855-run ablation totals. Both scripts print `lightweight-derived-inputs` mode in this repository. Full extraction from all 216 original packets is available only in the complete source checkout; unavailable original sources are explicitly listed in the release manifest.

The visual renderer checks every reviewer input hash and the R03/R04 budgets, regenerates the native Figure 1 SVG and verifies its bundled PNG/vector-PDF exports, and renders Figure 2 PNG/SVG with Matplotlib. It also builds two presentation tables and the complete process table. `build_text_manuscript.py` checks citations, tables, local links, and inclusive word counts; LaTeX embeds the Figure 1 vector PDF and Markdown uses its PNG preview. `build_pdf.ps1` writes the five-page PDF to `build/main.pdf`, with a fixed reproducible timestamp (`SOURCE_DATE_EPOCH=1794441600`). `verify_pdf.py` extracts text with two libraries and renders all pages for visual inspection. `verify_release.py` checks frozen input hashes, LF bytes, local links, excluded packet fields, and optional HEAD/working-file byte identity. These commands parse existing records without running agents, executing stored checks, or calling the grader.

Figure 1's [export manifest](../evidence/study-design-svg-v04.json) binds the SVG, generator, visible labels, and PNG/PDF fingerprints. The default rebuild verifies these versioned exports and needs no Node.js or browser. After editing [the SVG generator](../scripts/build_study_design_svg.py), the optional re-export step requires Node.js, Playwright/Chromium, and the pinned pypdf dependency:

```powershell
npm install --no-save --package-lock=false playwright
npx playwright install chromium
python -X utf8 scripts/build_study_design_svg.py
python -X utf8 scripts/export_study_design.py --node node
```

Then update the export-manifest fingerprint in `protocol/public-release-manifest.json` and rerun the normal visual, text, and PDF build. The bundled Figure 1 PDF embeds native vectors and searchable text with no raster images. Its metadata uses the fixed release timestamp; the optional export manifest records the browser and pypdf versions used.

## Locate a reported result

| Manuscript result | Primary record | What to inspect |
|---|---|---|
| Figure 1: shared-draft design | R03/R04 plans above; [visual manifest](../evidence/visuals-v04.json), [SVG export manifest](../evidence/study-design-svg-v04.json) | Equal C/F budgets and capabilities; shared draft, public issue, check specification and expected outcome; F-only precomputed-result route |
| Figure 2A: failing-draft comparison and action substitution | [Draft-status breakdown](draft-status-breakdown-v04.csv), [tool-allocation summary](tool-allocation-v04.csv) | All 64 failing realizations per arm; C/F replay 46/22, cap exhaustion 53/57, retained edits 8/8, confirmed passes 3/3; `run_command` 226→197 and `read_file` 239→269 |
| Figure 2B: counterevidence edit attempts and rejection timelines | [Edit opportunities](edit-opportunities-v04.csv), [process analysis](../evidence/process-analysis-v04.json) | 6 of 7 F branches attempt edits (2 land and pass; 4 have their first edit rejected at the 8-tool cap with 30.1–78.5s remaining) |
| Table 1: check construction | [216 construction records](check-construction-v04.csv) | Public grounding, target reach, command/stderr classification, and packet path |
| Table 2: result groups and paired outcomes | [216 joined realizations](result-action-outcome-v04.csv), [tool-allocation summary](tool-allocation-v04.csv) | Common-result group, separate C/F action columns, call-0 `read_file` shift (`6/20` to `16/20` in `Grounded target`), edit attempts (`4/20` to `8/20`), and paired gains/losses |
| Table 3: follow-up prompt-only ablations | [Joined analysis](../evidence/reviewer-analysis-v04.json) (`followup_prompt_ablations`, `program_scale_summary`), [cycle reports/protocols](../protocol/README.md#study-and-ablation-reports) | Three 855-run cycles across 95 tasks / 15 repositories (2,565 runs): subagent soft caps, schema/heredoc retry, and voluntary `keep`/`reject` gates |
| Silent `read_file` resets and `old_string:` delimiter corruption | [Tool-allocation summary](tool-allocation-v04.csv), [joined analysis](../evidence/reviewer-analysis-v04.json) | 56/58 silent line-1 resets on malformed `start_line"` keys; 93/93 missing-`old_string` rejections containing `old_string:` fused into `new_string` (82/93 bogus split keys) |
| Companion: [complete process table](continuation-process-v04.md) | [Replay phases](check-phases-v04.csv), [432 returned-source records](source-delivery-v04.csv) | All 108 realizations; draft versus post-edit replay; returned-source category; original label and source identity |
| Repetition and repository breakdowns | [Final-configuration breakdown](final-configuration-breakdown-v04.csv) | Realizations, distinct tasks, result groups, replay, retained edits, and normal-pair denominators |
| Continuation from passing and failing drafts | [Draft-status breakdown](draft-status-breakdown-v04.csv) | Existing D judgment, replay, retained edits, normal D/branch pairs, and new/lost passes |
| Final seven and all eight counterevidence cases | [Eight-case index](../evidence/counterevidence-slots.csv), [joined analysis](../evidence/reviewer-analysis-v04.json) | R03/R04 provide the main seven-case cohort; FastAPI13537/R02 supplies the additional case. Inspect D/C/F outcomes and both branches' first source-edit events |
| Rich3067/R03 successful repair | [Public packet](../protocol/packets/study-b/R03/rich_3067.json), [returned-source records](source-delivery-v04.csv) | C event 0 obtains the failing result but its edits lack a required argument; F events 4/5 fail argument validation, event 6 edits the source, and event 7 replays the unchanged common command successfully. R04 uses a separately generated draft |
| Four F first-edit rejections | [Edit opportunities](edit-opportunities-v04.csv) | The eight consumed ordinary opportunities, elapsed time, rejected edit, and unchanged returned draft |
| Final no-output losses | [Source review](../evidence/revision-public-review-v03.md), [case evidence](../evidence/case-evidence.json) | Requests7433/R03 draft-logic deletion and Rich3067/R04 temporary edit followed by restoration |
| Missing grades and empty patches | [All 648 endpoints](feedback-task-outcomes.csv), [unknown endpoints](../evidence/missing-endpoints.csv), [graded empty passes](../evidence/scored-empty-passes.csv) | Original status, denominator inclusion, and returned-patch identity |

The [claim index](../evidence/claims.md) gives additional links. Event indices are zero-based. Replay rows count branches and can overlap when a branch checks before and after an edit. A retained source change can be incomplete or harmful; it is distinct from a passing outcome. Normal paired outcomes require both branches to have a normal judgment. Batch, repository, and draft-status partitions each sum to the final 108 realizations; the partitions must not be added together. A repeated task can appear in different draft-status groups across batches.

Draft-status groups use the original judgments retrospectively. These judgments were not used to filter drafts or supplied to the continuations. F gains/losses compare the two continuation branches; new/lost passes from D compare each branch with its starting draft. This distinction separates damage to a passing draft from a correction achieved by only one continuation.

## Annotation and review

Gemma 4 31B QAT generated the repair and check-construction trajectories. Original behavior annotations were produced by AI agents using the [behavior rubric](../protocol/behavior-rubric.md); the [partition ledger](annotation-partitions.csv) preserves reviewer identifiers, hashes, and recorded score-access status. These labels were frozen before per-task score access.

The v0.3 semantic/source review and v0.4 process analysis were performed with Codex assistance after outcomes were known. They preserve original annotations and record later judgments separately. The v0.3 semantic review covers all 26 grounded target checks and 16 additional negative examples; v0.4 adds construction-failure classification, replay timing, comparison of all 432 returned continuation patches, and the linked summaries. Hash and arithmetic checks verify provenance and accounting; semantic decisions remain inspectable through their cited public traces. No independent human inter-rater reliability estimate is available.

## Companion repository availability

This lightweight companion contains all derived Study A/B CSV tables, frozen process analysis, recomputable joined reviewer analysis, five stage prompts, fixed plans/rubric, the five paper-cycle reports/protocols and a separately labeled precursor report, aggregate cycle exports, and 14 selected case packets. Original packet/source hashes remain provenance; the release manifest provides separate hashes for public projections and LF bytes. No full raw task payloads or 216-packet archive are included. The published five-page PDF and all four analysis/figure/text build commands can be verified from a clean clone with the documented dependencies.
