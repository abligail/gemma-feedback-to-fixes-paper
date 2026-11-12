"""Render v0.4 figures and presentation tables from the frozen analysis.

Requires Matplotlib for Figure 2. Rebuilds the native Figure 1 SVG, verifies its
versioned PNG/PDF exports, and writes tables and a provenance manifest;
never invokes TeX, a repair model, a stored check, or the grader.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.text import Text

from public_inputs import IS_MONOREPO, PAPER, ROOT, resolve_input, verify_public_inputs
INPUTS = {}
INK = "#243746"
MUTED = "#536776"
CONTROL = "#32658A"
FEEDBACK = "#168477"
BLOCKED = "#B65325"
LINE = "#B9C6CE"
LIGHT = "#EDF1F4"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": INK, "axes.edgecolor": LINE,
    "svg.fonttype": "none", "svg.hashsalt": "gemma-paper-v04",
    "savefig.facecolor": "white", "figure.facecolor": "white",
})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(relative: str):
    path = resolve_input(relative)
    INPUTS[path.relative_to(ROOT).as_posix()] = sha(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def save(fig, stem, alt):
    """Record visible labels for an inclusive manuscript word count."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = []
    outside = []
    for item in fig.findobj(Text):
        if not item.get_visible() or not item.get_text().strip():
            continue
        # Axis-off tick labels exist as artists but are not drawn.
        if item.axes is not None and not item.axes.axison and item not in item.axes.texts:
            continue
        box = item.get_window_extent(renderer)
        if box.width == 0 or box.height == 0:
            continue
        labels.append(item.get_text())
        if (box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.width + 1
                or box.y1 > fig.bbox.height + 1):
            outside.append(item.get_text())
    assert not outside, f"Text outside figure canvas: {outside}"
    outputs = {}
    for extension in ("png", "svg"):
        path = PAPER / "figures" / f"{stem}.{extension}"
        metadata = {"Software": "Matplotlib; build_v04_visuals.py"} if extension == "png" else {
            "Date": None, "Creator": "Matplotlib; build_v04_visuals.py",
            "Description": alt,
        }
        fig.savefig(path, dpi=240, metadata=metadata)
        if extension == "svg":
            # Matplotlib emits trailing spaces in multiline path attributes.
            # Newlines retain the SVG token separators after trimming them.
            write(path, "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n")
        outputs[extension] = {"path": path.relative_to(PAPER).as_posix(), "sha256": sha(path)}
    outputs["png"]["pixels"] = [round(x * 240) for x in fig.get_size_inches()]
    plt.close(fig)
    return {"alt": alt, "visible_text": labels, "outputs": outputs,
            "canvas_text_bounds_check": "passed"}


def study_design(budget):
    """Regenerate the authored SVG and verify its approved PNG/vector-PDF exports."""
    from build_study_design_svg import build_svg
    record = read_json("paper/feedback-to-fixes/evidence/study-design-svg-v04.json")
    generator = Path(__file__).with_name("build_study_design_svg.py")
    assert sha(generator) == record["generator_sha256"], "Figure 1 generator changed; re-export the artwork."
    assert budget == record["budgets"], "Figure 1 export budget differs from the frozen R03/R04 plans."
    INPUTS["paper/feedback-to-fixes/scripts/build_study_design_svg.py"] = sha(generator)
    source = PAPER / "figures/study-design-v04.svg"
    labels = build_svg(source, budget)
    assert sha(source) == record["svg_sha256"], "Figure 1 SVG changed; run the optional export script."
    assert labels == record["visible_text"], "Figure 1 visible text differs from the approved export."
    outputs = {"svg": {"path": source.relative_to(PAPER).as_posix(), "sha256": sha(source)}}
    for extension, exported in record["exports"].items():
        path = PAPER / exported["path"]
        assert path.is_file() and sha(path) == exported["sha256"], f"Figure 1 {extension} export changed or is missing."
        outputs[extension] = exported
    return {
        "alt": "Study B (R03/R04): C/F share frozen draft D, public issue, check specification and expected outcome; both can inspect, edit and run checks, and only F receives the precomputed result or unavailable notice.",
        "visible_text": labels,
        "outputs": outputs,
        "canvas_text_bounds_check": "approved SVG v02; native PDF export and all visible labels checked",
        "renderer": "Authored native SVG; versioned PNG/PDF exports verified against the SVG fingerprint",
    }


def main_results(failed, failed_alloc, timelines, budget, counterevidence):
    fig = plt.figure(figsize=(11.0, 5.85))
    left = fig.add_axes([.155, .28, .285, .51])
    right = fig.add_axes([.61, .28, .355, .51])
    fig.text(.025, .94, "A  Failing-draft behavior & tool cap", fontsize=13.8, fontweight="bold")
    fig.text(.025, .885, f"R03/R04 · {failed['realizations']} failing drafts per arm", fontsize=11.5, color=MUTED)
    fig.text(.505, .94, "B  First source edit blocked at tool cap", fontsize=13.8, fontweight="bold")
    fig.text(.505, .885, f"6 of {len(counterevidence)} counterevidence F branches attempt edits: 2 pass, {len(timelines)} blocked", fontsize=11.2, color=MUTED)

    metrics = [
        ("Common-check\nreplay on D", failed["control_draft_replays"], failed["feedback_draft_replays"]),
        ("Exhaust\n8-tool cap", failed_alloc["control"]["budget_exceeded_branches"], failed_alloc["feedback"]["budget_exceeded_branches"]),
        ("Retained\nsource edits", failed["control_retained_source_changes"], failed["feedback_retained_source_changes"]),
        ("Confirmed\nnew passes", failed["control_new_passes_from_draft"], failed["feedback_new_passes_from_draft"]),
    ]
    for i, (_, c_val, f_val) in enumerate(metrics):
        y = 3 - i
        for offset, value, color in [(0.18, c_val, CONTROL), (-0.18, f_val, FEEDBACK)]:
            left.barh(y + offset, value, height=.29, color=color, zorder=3)
            left.text(value + 1.1, y + offset, str(value), va="center", fontsize=11.5,
                      fontweight="bold", color=color)
    left.set(yticks=[3, 2, 1, 0], yticklabels=[m[0] for m in metrics],
             xlim=(0, failed["realizations"] + 3), ylim=(-.55, 3.55), xticks=[0, 16, 32, 48, 64])
    left.set_xlabel("Branch count (out of 64)", fontsize=11.5, labelpad=7)
    left.tick_params(axis="both", length=0)
    left.tick_params(axis="y", pad=10, labelsize=11)
    left.grid(axis="x", color=LIGHT, lw=1, zorder=0)
    for s in ["top", "right", "left"]:
        left.spines[s].set_visible(False)
    fig.legend(handles=[Patch(facecolor=CONTROL, label="C · Ordinary"),
                        Patch(facecolor=FEEDBACK, label="F · Advance result")],
               loc="upper left", bbox_to_anchor=(.025, .205), frameon=False,
               fontsize=11, ncol=2, handlelength=1.1, columnspacing=1.6)
    c_run, f_run = failed_alloc["control"]["run_command"], failed_alloc["feedback"]["run_command"]
    c_read, f_read = failed_alloc["control"]["read_file"], failed_alloc["feedback"]["read_file"]
    fig.text(.025, .092,
             f"Tool shift (C→F): runs {c_run}→{f_run} (−29); reads {c_read}→{f_read} (+30).",
             fontsize=10.6, color=INK, fontweight="bold")
    fig.text(.025, .042,
             f"Normal grades: C {failed['control_normal_draft_pairs']}; F {failed['feedback_normal_draft_pairs']} (one unknown).",
             fontsize=10.5, color=MUTED)

    timelines = sorted(timelines, key=lambda t: t["first_source_edit_seconds"])
    names = []
    for i, t in enumerate(timelines):
        y = 3 - i
        when = t["first_source_edit_seconds"]
        remaining = t["nominal_seconds_remaining"]
        repo, issue = t["task"].split("_")
        names.append(f"{'FastAPI' if repo == 'fastapi' else 'Rich'} {issue}\n{t['batch']}")
        right.barh(y, budget["continuation_seconds"], height=.40, color=LIGHT, zorder=1)
        right.barh(y, when, height=.40, color=FEEDBACK, alpha=.24, zorder=2)
        event_times = [event["elapsed_seconds"] for event in t["eight_spent_events"]]
        assert len(event_times) == budget["continuation_calls"]
        assert max(event_times) < when < budget["continuation_seconds"]
        right.vlines(event_times, y - .17, y + .17, color=FEEDBACK, linewidth=1.1, zorder=3)
        right.scatter([when], [y], marker="X", s=75, color=BLOCKED, edgecolor="white", linewidth=.7, zorder=4)
        right.text(when, y + .34, f"{when:.1f} s", ha="center", fontsize=11, color=BLOCKED)
        right.text(when + remaining / 2, y, f"{remaining:.1f} s", va="center", ha="center", fontsize=11, color=INK)
    right.set(xlim=(0, budget["continuation_seconds"]), ylim=(-.55, 3.65),
              yticks=[3, 2, 1, 0], yticklabels=names, xticks=[0, 30, 60, 90, 120, 150])
    right.set_xlabel("Seconds from continuation start", fontsize=12, labelpad=7)
    right.tick_params(axis="both", length=0)
    right.tick_params(axis="y", pad=8, labelsize=11)
    right.grid(axis="x", color=LIGHT, lw=.8, zorder=0)
    for s in ["top", "left", "right"]:
        right.spines[s].set_visible(False)
    fig.legend(handles=[
        Line2D([0], [0], marker="|", markersize=11, color=FEEDBACK, linestyle="none", label="Tool opportunity"),
        Line2D([0], [0], marker="X", markersize=7, color=BLOCKED, linestyle="none", label="Rejected edit"),
        Patch(facecolor=LIGHT, edgecolor=LINE, label="Time remaining"),
    ], loc="upper left", bbox_to_anchor=(.51, .22), frameon=False, fontsize=11,
       ncol=3, handlelength=.9, columnspacing=1.0)
    fig.text(.505, .092, f"{budget['continuation_calls']} calls spent on read/probe · 0 left for first edit", fontsize=10.8, color=INK, fontweight="bold")
    fig.text(.505, .042, f"All {len(timelines)} blocked F branches return D unchanged; both arms fail.", fontsize=10.5, color=MUTED)
    return save(fig, "feedback-and-edit-budget-v04",
                f"Failing-draft comparison ({failed['realizations']} realizations): C/F replay "
                f"{failed['control_draft_replays']}/{failed['feedback_draft_replays']}, exhaust 8-tool cap "
                f"{failed_alloc['control']['budget_exceeded_branches']}/{failed_alloc['feedback']['budget_exceeded_branches']}, retain edits "
                f"{failed['control_retained_source_changes']}/{failed['feedback_retained_source_changes']}, and confirm new passes "
                f"{failed['control_new_passes_from_draft']}/{failed['feedback_new_passes_from_draft']}. "
                "Four counterevidence timelines show the first source edit rejected after all eight tool opportunities, despite 30–79 seconds remaining.")


def tables(process, review):
    final = process["summary"]["final_configuration"]
    coverage = final["coverage"]
    rows = [
        ("No execution output", "no_execution_output"),
        ("Python invoked on missing \\texttt{PY} file", "python_invoked_on_missing_PY_file"),
        ("Other failure before target behavior", "other_target_not_reached"),
        ("Peripheral behavior only", "peripheral_behavior"),
        ("Target reached; expectation insufficiently grounded", "target_reached_expectation_not_grounded"),
        ("Grounded target behavior", "supported_target_reached"),
    ]
    assert sum(coverage.values()) == final["task_realizations"] == 108
    header = "% Generated by scripts/build_v04_visuals.py from frozen v0.4 analysis.\n"
    body = [r"\begin{tabular}{lr}", r"\toprule", r"Check-construction outcome & Realizations \\", r"\midrule"]
    body += [f"{label} & {coverage[key]} " + r"\\" for label, key in rows]
    body += [r"\midrule", r"Total attempts & 108 \\", r"\bottomrule", r"\end{tabular}"]
    write(PAPER / "tables/construction-coverage-v04.tex", header + "\n".join(body) + "\n")

    body = [r"\begin{tabular}{lrrrrrrrr}", r"\toprule",
            r" & & \multicolumn{2}{c}{Replay} & \multicolumn{2}{c}{Retained edits} & & \multicolumn{2}{c}{F vs C} \\",
            r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){8-9}",
            r"Common result & N & C & F & C & F & Pairs & Gains & Losses \\", r"\midrule"]
    labels = {"grounded_target": "Grounded target", "other_output": "Other output", "no_output": "No output"}
    for row in review["summary"]["final_configuration"]:
        values = [labels[row["group"]], row["realizations"], row["control"]["draft_replays"],
                  row["feedback"]["draft_replays"], row["control"]["retained_source_changes"],
                  row["feedback"]["retained_source_changes"], row["normal_cf_pairs"],
                  row["feedback_gains"], row["feedback_losses"]]
        body.append(" & ".join(map(str, values)) + " " + r"\\")
    body += [r"\bottomrule", r"\end{tabular}"]
    write(PAPER / "tables/result-groups-v04.tex", header + "\n".join(body) + "\n")

    responses = final["responses"]
    all_alloc = next(r for r in review["tool_allocation_summary"] if r["scope"] == "all_final_108")
    measures = [
        ("Common-check replay on draft logic", "replay_on_draft_logic"),
        ("Common-check replay after a source change", "replay_after_source_change"),
        ("Retained executable-source changes", None),
        ("New passes from D", "new_passes"),
        ("Lost passes from D", "lost_passes"),
        ("Final passes on the complete list", "passes"),
    ]
    content = ["# Continuation process — R03/R04", "",
               "Complete process and tool-allocation table for the final configuration, retained here alongside the manuscript's focused Figure 2. Each arm has 108 realizations of the same 54 tasks.", "",
               "| Branch behavior, tool allocation, or outcome | C | F |", "|---|---:|---:|"]
    for label, key in measures:
        values = [responses[arm][key] if key else responses[arm]["source_categories"]["retained_executable_source_change"]
                  for arm in ("control", "feedback")]
        content.append(f"| {label} | {values[0]} | {values[1]} |")
    for label, key in [
        ("Branches starting with `read_file` at call 0", "event0_read_file_branches"),
        ("Executed `run_command` calls", "run_command"),
        ("Executed `read_file` calls", "read_file"),
        ("Malformed `read_file` key calls (e.g., `start_line\"`)", "malformed_read_key_calls"),
        ("Silent line-1 reset `read_file` calls", "silent_line1_reset_reads"),
        ("Executed `edit_file` calls", "edit_file"),
        ("Executed `write_file` calls", "write_file"),
        ("Malformed `edit_file` calls (missing `old_string`)", "missing_param_calls"),
        ("Missing-`old_string` calls with swallowed `old_string:`", "missing_param_swallowed_old_string"),
        ("Missing-`old_string` calls with split bogus keys", "missing_param_bogus_split_keys"),
        ("Branches exhausting 8-tool cap (`BudgetExceeded`)", "budget_exceeded_branches"),
    ]:
        content.append(f"| {label} | {all_alloc['control'][key]} | {all_alloc['feedback'][key]} |")
    content += ["", "Replay rows count branches and overlap. Post-edit replay includes documented invocation repairs and adapted diagnostics. Retained executable-source changes may be incomplete or harmful.", "",
                "D transitions use 104 normal D/C and 103 normal D/F pairs. D has 40 passes, 64 failures, three technical unknowns, and one unscored no-patch result. Direct C/F comparison has 103 normal pairs, with two F gains and three losses.", "",
                "Sources: [frozen process analysis](../evidence/process-analysis-v04.json), [draft-status breakdown](draft-status-breakdown-v04.csv), [tool allocation](tool-allocation-v04.csv), and [joined outcomes](result-action-outcome-v04.csv). Generated by [build_v04_visuals.py](../scripts/build_v04_visuals.py).", ""]
    write(PAPER / "supplement/continuation-process-v04.md", "\n".join(content))


def main():
    if not IS_MONOREPO:
        verify_public_inputs()
    process = read_json("paper/feedback-to-fixes/evidence/process-analysis-v04.json")
    review = read_json("paper/feedback-to-fixes/evidence/reviewer-analysis-v04.json")
    for relative, expected in review["sources"].items():
        path = resolve_input(relative)
        assert path.is_file(), f"Missing frozen input: {relative}"
        assert sha(path) == expected, f"Frozen input changed: {relative}"
        INPUTS[relative] = expected
    plans = [read_json(f"research/cycles/2026-10-14-feedback-refinement/plan-{batch}.json")
             for batch in ("R03", "R04")]
    budgets = []
    for plan in plans:
        arms = plan["arms"]
        assert arms[0]["eval"] == arms[1]["eval"]
        budgets.append({
            "draft_seconds": round(plan["draft_arm"]["eval"]["max_time_minutes"] * 60),
            "draft_calls": plan["draft_arm"]["eval"]["max_tool_calls"],
            "constructor_seconds": round(plan["checker_arm"]["eval"]["max_time_minutes"] * 60),
            "constructor_reads": plan["checker_arm"]["eval"]["max_tool_calls"],
            "execution_seconds": plan["probe_timeout_seconds"],
            "continuation_seconds": round(arms[0]["eval"]["max_time_minutes"] * 60),
            "continuation_calls": arms[0]["eval"]["max_tool_calls"],
        })
    assert budgets[0] == budgets[1]
    budget = budgets[0]
    assert budget["constructor_reads"] == 1 and budget["continuation_calls"] == 8 and budget["continuation_seconds"] == 150
    failed = next(r for r in review["final_configuration_draft_status_breakdown"] if r["value"] == "scored_failed")
    failed_alloc = next(r for r in review["tool_allocation_summary"] if r["scope"] == "failing_drafts_64")
    assert failed["control_nonnormal_returns"] == 0 and failed["feedback_nonnormal_returns"] == 1
    counterevidence = [r for r in review["counterevidence_comparison"] if r["batch"] in ("R03", "R04")]
    blocked = {(r["batch"], r["task"]): r for r in counterevidence
               if r["feedback_first_source_edit"] and r["feedback_first_source_edit"]["budget_rejected"]}
    timelines = process["budget_timelines"]
    assert len(counterevidence) == 7
    assert set(blocked) == {(t["batch"], t["task"]) for t in timelines}
    assert all(r["control_status"] == r["feedback_status"] == "scored_failed" for r in blocked.values())
    assert len(timelines) == 4 and all(t["delivered_equals_draft"] for t in timelines)
    for t in timelines:
        assert t["batch"] in ("R03", "R04")
        assert sum(t["spent_opportunities"].values()) == budget["continuation_calls"]
        assert abs(t["first_source_edit_seconds"] + t["nominal_seconds_remaining"] - budget["continuation_seconds"]) < 1e-6
        first = blocked[(t["batch"], t["task"])]["feedback_first_source_edit"]
        assert first["event"] == t["first_source_edit_event"]
        assert abs(first["seconds"] - t["first_source_edit_seconds"]) < 1e-6
    (PAPER / "figures").mkdir(exist_ok=True)
    figures = {
        "study-design-v04": study_design(budget),
        "feedback-and-edit-budget-v04": main_results(failed, failed_alloc, timelines, budget, counterevidence),
    }
    tables(process, review)
    outputs = [PAPER / f for f in ("tables/construction-coverage-v04.tex", "tables/result-groups-v04.tex",
                                  "supplement/continuation-process-v04.md")]
    manifest = {
        "version": "v0.4 native SVG figure 1", "date": "2026-11-12", "matplotlib": matplotlib.__version__,
        "renderer_sha256": sha(Path(__file__)), "input_sha256": INPUTS,
        "budgets": budget, "failed_draft_panel": failed,
        "budget_timelines": [{**{k: v for k, v in t.items() if k not in ("packet_path", "eight_spent_events")},
                              "eight_spent_events": [{k: e[k] for k in ("event", "tool", "category", "elapsed_seconds")}
                                                     for e in t["eight_spent_events"]]}
                             for t in timelines],
        "figures": figures,
        "other_outputs": {p.relative_to(PAPER).as_posix(): sha(p) for p in outputs},
        "scope": "R03/R04; existing frozen analysis only. Counts, not rate estimates. Timeline marks show first rejected edits within the nominal 150-second allocation, not branch termination. No manuscript PDF output; Figure 1 uses a verified vector PDF export.",
    }
    write(PAPER / "evidence/visuals-v04.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"figures": list(figures), "verified_inputs": len(INPUTS),
                      "formats": ["PNG", "SVG", "PDF (Figure 1 vector)"], "tables": 2, "pdf_generated": False}))


if __name__ == "__main__":
    main()
