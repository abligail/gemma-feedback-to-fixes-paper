# Knowing the Bug Is Not Landing the Fix: Why Execution Feedback Stalls Before Patch Delivery in Budget-Constrained Coding Agents

**Team xiakongxin** · Gemma 4 Good Hackathon — Paper Track Companion Repository

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

This repository provides the full manuscript, compiled PDF, figures, derived dataset tables, frozen analysis JSONs, and deterministic build/verification scripts for our empirical study of execution feedback and patch delivery in budget-constrained repository coding agents.

---

## Primary Deliverables

- **Compiled 5-Page PDF (NeurIPS-Style Single-Column)**: [`output/pdf/knowing-the-bug-is-not-landing-the-fix.pdf`](output/pdf/knowing-the-bug-is-not-landing-the-fix.pdf) (`SHA256: 4f9fb0b5ef26eeecff036bf728c022b9df460b05f231fb08604431dcd454da90`)
- **Readable Markdown Manuscript (Writeup Copy)**: [`manuscript.md`](manuscript.md) (`2,942` whitespace words / `2,993` word tokens excluding references, including all 3 tables, captions, and the 258 words drawn inside Figures 1 and 2; strictly $\le 3,000$ words)
- **LaTeX Source**: [`main.tex`](main.tex) and [`sections/`](sections/)
- **Figures (PNG & SVG; vector PDF for Figure 1)**:
  - **Figure 1** ([PNG preview](figures/study-design-v04.png), [editable SVG](figures/study-design-v04.svg), [vector PDF](figures/study-design-v04.pdf)): Study B shared inputs and expected outcome, equal-capability continuation arms, and the F-only precomputed-result route
  - **Figure 2** ([`figures/feedback-and-edit-budget-v04.png`](figures/feedback-and-edit-budget-v04.png)): Failing-draft continuation behavior, 8-tool cap exhaustion, action substitution (`run_command` $226 \to 197$, `read_file` $239 \to 269$), and counterevidence first-edit rejection timelines
- **Tables**:
  - **Table 1** ([`tables/construction-coverage-v04.tex`](tables/construction-coverage-v04.tex)): Check-construction outcomes across 108 R03/R04 realizations
  - **Table 2** ([`tables/result-groups-v04.tex`](tables/result-groups-v04.tex)): Continuations stratified by check quality (`Grounded target`, `Other output`, `No output`)
  - **Table 3** ([`tables/prompt-ablations-v04.tex`](tables/prompt-ablations-v04.tex)): Three 855-run follow-up prompt-only mitigation ablations across 95 tasks and 15 repositories (2,565 runs)

---

## Summary of Findings (3,517 Runs & Realizations Across 95 Tasks / 15 Repositories)

Across **Study A** (736 whole-workflow runs), **Study B** (216 shared-draft realizations / 864 model sessions / 648 graded endpoints), and **three follow-up prompt-mitigation ablations** ($3 \times 855 = 2,565$ runs), upstream diagnostic gains fail to increase final solve rates because downstream bottlenecks absorb freed budget across four stages:

1. **Stage 1 — Check Launch & Grounding**: In Study B's final configuration (R03/R04, 108 realizations), **38 of 108 generated checks (35%)** fail on CLI heredoc syntax (`python3 -B PY`, omitting `- <<` from `python3 -B - << 'PY'`), leaving 20 grounded target checks (13 expectations matched, 7 counterevidence on failing drafts).
2. **Stage 2 — Action Substitution & Silent `read_file` Resets**: On the 64 failing drafts, advance results halve pre-edit check replay from **46/64 (72%) in C to 22/64 (34%) in F**, yet F trades **29 saved `run_command` calls ($226 \to 197$)** for **30 extra `read_file` calls ($239 \to 269$)**. Furthermore, **58 executed `read_file` calls** emit a malformed optional key (`"start_line\"": "151"`), silently resetting to lines 1–150 in **56 of 58 calls**, and **89% of F branches (57/64)** hit `BudgetExceeded`. In `Grounded target` (20 realizations), advance results cut replay by **80% ($20/20 \to 4/20$)**, raise call-0 `read_file` starts from **$6/20 \to 16/20$**, and double edit-attempting branches (**$4/20 \to 8/20$**), yet 4 of 8 hit `BudgetExceeded`.
3. **Stage 3 — The Last-Centimeter Edit Wall**: Six of seven R03/R04 counterevidence F branches (7/8 across all four batches) issue a concrete `edit_file` call across four statically verified outcomes:
   - **Landed within cap (2/7 F, 3/8 overall; 100% pass)**: `Requests6592/R03`, `Rich3067/R03`, `FastAPI13537/R02`.
   - **Exact, uniquely matching fixes (`occurrences = 1`) preempted by 1 slot (2/7 F + 1 C)**: `Rich3518/R04` F/C (`highlight=self.highlight`) and `FastAPI13786/R04` F (`self.model.in_.value`).
   - **Multi-part tasks cut off mid-localization (2/7 F + 1 C)**: `FastAPI14986/R03` F and `FastAPI15800/R04` F/C emit truncated edits at event 9 immediately after hitting `BudgetExceeded` at event 8.
   - **Cut off at target-file entry (1/7 F)**: `FastAPI15589/R04` F has its first `read_file` on `fastapi/dependencies/utils.py` blocked at event 8.
4. **Stage 4 — Delimiter Corruption & Continuation Regression**: Across R03/R04, **93 `edit_file` calls across 11 branches** fail with `Missing mandatory parameters: old_string`; in **93/93 (100%)**, delimiter corruption fuses `,old_string:` into `new_string` (**82/93 split target code into bogus keys**). Meanwhile, **4 of 29 retained diffs** delete working draft logic, and prompt-only mitigations across **2,565 follow-up runs** (Table 3) confirm that runtime edit reservations, resilient tool adapters, and state-bound rollback are required.

---

## Repository Structure & Reproducibility

- [`supplement/reproducibility.md`](supplement/reproducibility.md): End-to-end guide mapping every figure, table, and claim in the manuscript to its primary CSV/JSON record.
- [`supplement/methods.md`](supplement/methods.md): Detailed experimental protocol, stage budgets, and measurement definitions.
- [`supplement/continuation-process-v04.md`](supplement/continuation-process-v04.md): Full 108-realization R03/R04 continuation process and tool-allocation companion table.
- [`supplement/*.csv`](supplement/): Derived realization-level, branch-level, and tool-allocation CSV datasets (`check-construction-v04.csv`, `check-phases-v04.csv`, `draft-status-breakdown-v04.csv`, `edit-opportunities-v04.csv`, `feedback-task-outcomes.csv`, `final-configuration-breakdown-v04.csv`, `result-action-outcome-v04.csv`, `source-delivery-v04.csv`, `tool-allocation-v04.csv`).
- [`evidence/*.json`](evidence/): Frozen process analysis (`process-analysis-v04.json`), joined reviewer analysis (`reviewer-analysis-v04.json`), figure provenance (`visuals-v04.json`), case evidence (`case-evidence.json`), and claim index ([`evidence/claims.md`](evidence/claims.md)).
- [`protocol/`](protocol/): Five stage prompts, frozen Study B plans/rubric, Study A/B and Table 3 reports/protocols, aggregate cycle exports, and [14 core case packets](protocol/packets/README.md); indexed in [protocol/README.md](protocol/README.md).

### Rebuilding Figures, Tables, Markdown Manuscript, and PDF

Use Python 3.11+ with the pinned [build dependencies](requirements-build.txt), Tectonic 0.17.0, PowerShell for the PDF wrapper, and Poppler (`pdftoppm`) for page rendering. From this repository's root:

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

The lightweight mode checks frozen LF-byte fingerprints, recomputes the complete 216-realization joins and eight counterevidence case analyses, and rebuilds the figures/tables/Markdown from the bundled records. Figure 1 is authored as native SVG; the default build regenerates it and verifies the bundled PNG/vector-PDF exports against the [export manifest](evidence/study-design-svg-v04.json). It does not require Node.js or a browser. Figure 2 retains its Matplotlib renderer. The [reproduction guide](supplement/reproducibility.md) documents the optional Playwright/Chromium export step for artwork edits. All-trace tool-allocation counts come from the frozen aggregate CSV; the seven final counterevidence traces are recomputed and matched to that aggregate. Full extraction of all 216 original packets requires the complete source archive.

The PDF wrapper writes `build/main.pdf` and freezes `SOURCE_DATE_EPOCH=1794441600` (12 November 2026 UTC) for reproducible metadata. It accepts an installed compiler path via `-Compiler`. On systems without PowerShell, use `SOURCE_DATE_EPOCH=1794441600 tectonic --keep-logs --outdir build main.tex` after creating `build/`. The checked release PDF is linked above.
