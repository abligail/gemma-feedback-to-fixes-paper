"""Join existing v0.4 check, action, and outcome records and describe their scope.

Post-hoc descriptive analysis only. No model, execution, grading, or PDF calls.
Original v0.3/v0.4 annotations and result files are inputs, never overwritten.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re

from public_inputs import (IS_MONOREPO, PAPER, ROOT, resolve_input,
                           verify_original_identity, verify_original_sources,
                           verify_public_inputs)
INPUTS = {}
NORMAL = {"resolved", "scored_failed"}
GROUPS = ("grounded_target", "other_output", "no_output")


def read(path):
    raw = path.read_bytes()
    INPUTS[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
    return raw.decode("utf-8")


def csv_rows(name):
    return list(csv.DictReader(io.StringIO(read(PAPER / name))))


def write(path, text):
    (PAPER / path).write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_csv(path, rows):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    write(path, buf.getvalue())


def describe_scope(rows, dimension, value):
    result = {"dimension": dimension, "value": value,
              "realizations": len(rows), "distinct_tasks": len({r["task"] for r in rows}),
              "grounded_target": sum(r["group"] == "grounded_target" for r in rows),
              "other_output": sum(r["group"] == "other_output" for r in rows),
              "no_output": sum(r["group"] == "no_output" for r in rows),
              "normal_cf_pairs": sum(r["normal_cf_pair"] for r in rows),
              "feedback_gains": sum(r["feedback_gain"] for r in rows),
              "feedback_losses": sum(r["feedback_loss"] for r in rows)}
    for arm in ("control", "feedback"):
        result[arm + "_draft_replays"] = sum(r[arm + "_draft_replay"] for r in rows)
        result[arm + "_postedit_replays"] = sum(r[arm + "_postedit_replay"] for r in rows)
        result[arm + "_retained_source_changes"] = sum(
            r[arm + "_source_category"] == "retained_executable_source_change" for r in rows)
    return result


def describe_draft_status(rows, status):
    result = describe_scope(rows, "draft_status", status)
    for arm in ("control", "feedback"):
        result[arm + "_normal_draft_pairs"] = sum(
            r["draft_status"] in NORMAL and r[arm + "_status"] in NORMAL for r in rows)
        result[arm + "_new_passes_from_draft"] = sum(
            r["draft_status"] == "scored_failed" and r[arm + "_status"] == "resolved" for r in rows)
        result[arm + "_lost_passes_from_draft"] = sum(
            r["draft_status"] == "resolved" and r[arm + "_status"] == "scored_failed" for r in rows)
        result[arm + "_passes"] = sum(r[arm + "_status"] == "resolved" for r in rows)
        result[arm + "_nonnormal_returns"] = sum(r[arm + "_status"] not in NORMAL for r in rows)
    return result


def is_repo_source(path):
    return (path.startswith(("fastapi/", "rich/", "requests/", "src/requests/", "httpx/", "src/httpx/"))
            and path.endswith(".py"))


def reconstruct_read_text(packet, target_path):
    lines_map = {}
    stdouts = []
    for arm in ("control", "feedback"):
        for ev in packet["stages"][arm]["official_tool_events"]["events"]:
            for call in ev.get("tool_calls", []):
                args = call.get("arguments") or {}
                try:
                    obs = json.loads(ev.get("observation", {}).get("content", "{}"))
                except (ValueError, TypeError):
                    obs = {}
                if call["function_name"] == "read_file":
                    p = args.get("filepath", args.get("path", ""))
                    if p == target_path and obs.get("status") == "ok" and "content" in obs:
                        s_line = obs.get("start_line", 1)
                        for idx, line in enumerate(obs["content"].splitlines()):
                            lines_map[s_line + idx] = re.sub(r"^\d+:\s?", "", line)
                elif call["function_name"] == "run_command" and obs.get("stdout"):
                    stdouts.append(obs["stdout"])
    if lines_map:
        return "\n".join(lines_map.get(ln, "") for ln in range(1, max(lines_map) + 1))
    return "\n".join(stdouts)


def branch_interface_stats(packet, arm):
    events = packet["stages"][arm]["official_tool_events"]["events"]
    silent_resets = 0
    missing_params = 0
    event8_cap_tool = None
    for idx, ev in enumerate(events):
        obs_raw = ev.get("observation", {}).get("content", "")
        for call in ev.get("tool_calls", []):
            fn = call["function_name"]
            args = call.get("arguments") or {}
            if idx == 8 and "BudgetExceeded" in obs_raw:
                event8_cap_tool = {
                    "tool": fn,
                    "path": args.get("filepath", args.get("path", "")),
                    "start_line": args.get("start_line"),
                    "end_line": args.get("end_line"),
                    "seconds": call.get("extra", {}).get("elapsed_s"),
                }
            if "mandatory input parameters are not present" in obs_raw:
                missing_params += 1
            elif fn == "read_file" and "BudgetExceeded" not in obs_raw:
                bad_keys = [k for k in args if k not in ("filepath", "start_line", "end_line")]
                if bad_keys:
                    try:
                        obs = json.loads(obs_raw)
                    except (ValueError, TypeError):
                        obs = {}
                    if obs.get("start_line") == 1:
                        silent_resets += 1
    return {
        "silent_line1_reset_reads": silent_resets,
        "missing_param_calls": missing_params,
        "event8_cap_rejected_call": event8_cap_tool,
    }


def first_source_edit(packet, arm):
    events = packet["stages"][arm]["official_tool_events"]["events"]
    for index, event in enumerate(events):
        for call in event.get("tool_calls", []):
            args = call.get("arguments") or {}
            path = args.get("filepath", args.get("path", ""))
            if call["function_name"] in ("edit_file", "write_file") and is_repo_source(path):
                content = event.get("observation", {}).get("content", "")
                old_s = args.get("old_string", "")
                new_s = args.get("new_string", "")
                read_text = reconstruct_read_text(packet, path) if old_s else ""
                occurrences = read_text.count(old_s) if (old_s and read_text) else None
                anchor_preserved = None
                if old_s.lstrip().startswith("def "):
                    anchor_line = old_s.splitlines()[0].strip()
                    anchor_preserved = anchor_line in new_s
                has_contextual_target = bool(
                    old_s
                    and re.search(r"[A-Za-z_]{3,}", old_s.replace("True", "").replace("False", ""))
                    and anchor_preserved is not False
                )
                post_cap_ev9 = bool(
                    index == 9
                    and len(events) > 8
                    and "BudgetExceeded" in events[8].get("observation", {}).get("content", "")
                )
                return {"event": index, "seconds": call.get("extra", {}).get("elapsed_s"),
                        "budget_rejected": "BudgetExceeded" in content,
                        "immediate_post_cap_event9": post_cap_ev9,
                        "missing_parameter": "mandatory input parameters are not present" in content,
                        "tool": call["function_name"], "path": path,
                        "old_string_lines": len(old_s.splitlines()) if old_s else 0,
                        "new_string_lines": len(new_s.splitlines()) if new_s else 0,
                        "occurrences_in_read_window": occurrences,
                        "preserves_anchor_def": anchor_preserved,
                        "has_contextual_target": has_contextual_target,
                        "observation": content}
    return None


def summarize_tool_allocation(rows, packets, scope_name):
    out = {"scope": scope_name, "realizations": len(rows)}
    for arm in ("control", "feedback"):
        tools = Counter()
        schema_calls = 0
        swallowed_old_string_calls = 0
        bogus_split_key_calls = 0
        schema_branches = 0
        malformed_read_calls = 0
        silent_reset_reads = 0
        event0_read_branches = 0
        event0_run_branches = 0
        budget_branches = 0
        src_attempt_branches = 0
        src_budget_rej_branches = 0
        for r in rows:
            p = packets[(r["batch"], r["task"])]
            events = p["stages"][arm]["official_tool_events"]["events"]
            if events and events[0].get("tool_calls"):
                fn0 = events[0]["tool_calls"][0]["function_name"]
                if fn0 == "read_file":
                    event0_read_branches += 1
                elif fn0 == "run_command":
                    event0_run_branches += 1
            has_schema = False
            has_budget = False
            has_src_attempt = False
            has_src_budget = False
            for ev in events:
                for call in ev.get("tool_calls", []):
                    fn = call["function_name"]
                    if fn == "submit_patch":
                        continue
                    args = call.get("arguments") or {}
                    path = args.get("filepath", args.get("path", ""))
                    src = fn in ("edit_file", "write_file") and is_repo_source(path)
                    if src:
                        has_src_attempt = True
                    obs = ev.get("observation", {}).get("content", "")
                    if "BudgetExceeded" in obs:
                        has_budget = True
                        if src:
                            has_src_budget = True
                    elif "mandatory input parameters are not present" in obs:
                        schema_calls += 1
                        has_schema = True
                        if ("old_string" in str(args.get("new_string", ""))
                                or any("old_string" in str(k) or "old_string" in str(v) for k, v in args.items())):
                            swallowed_old_string_calls += 1
                        if any(k not in ("filepath", "old_string", "new_string") for k in args):
                            bogus_split_key_calls += 1
                    else:
                        bucket = "code_navigation" if fn in ("get_code_neighbors", "search_similar_code") else fn
                        tools[bucket] += 1
                        if fn == "read_file":
                            if any(k not in ("filepath", "start_line", "end_line") for k in args):
                                malformed_read_calls += 1
                                try:
                                    obs_json = json.loads(obs)
                                except (ValueError, TypeError):
                                    obs_json = {}
                                if obs_json.get("start_line") == 1:
                                    silent_reset_reads += 1
            if has_schema:
                schema_branches += 1
            if has_budget:
                budget_branches += 1
            if has_src_attempt:
                src_attempt_branches += 1
            if has_src_budget:
                src_budget_rej_branches += 1
        out[arm] = {
            "executed_calls_total": sum(tools.values()),
            "run_command": tools["run_command"],
            "read_file": tools["read_file"],
            "edit_file": tools["edit_file"],
            "write_file": tools["write_file"],
            "get_status": tools["get_status"],
            "code_navigation": tools["code_navigation"],
            "event0_run_command_branches": event0_run_branches,
            "event0_read_file_branches": event0_read_branches,
            "malformed_read_key_calls": malformed_read_calls,
            "silent_line1_reset_reads": silent_reset_reads,
            "missing_param_calls": schema_calls,
            "missing_param_swallowed_old_string": swallowed_old_string_calls,
            "missing_param_bogus_split_keys": bogus_split_key_calls,
            "missing_param_branches": schema_branches,
            "budget_exceeded_branches": budget_branches,
            "source_edit_attempt_branches": src_attempt_branches,
            "source_edit_budget_rejected_branches": src_budget_rej_branches,
        }
    return out


def main():
    if not IS_MONOREPO:
        verify_public_inputs()
    original = json.loads(read(PAPER / "evidence/process-analysis-v04.json"))
    provenance = verify_original_sources(original["sources"])
    checks = csv_rows("supplement/check-construction-v04.csv")
    source = {(r["batch"], r["task"], r["branch"]): r
              for r in csv_rows("supplement/source-delivery-v04.csv")}
    phase = {(r["batch"], r["task"], r["branch"]): r
             for r in csv_rows("supplement/check-phases-v04.csv")}
    counterevidence = csv_rows("evidence/counterevidence-slots.csv")
    joined = []
    for check in checks:
        k = (check["batch"], check["task"])
        dc, df = source[k + ("control",)], source[k + ("feedback",)]
        assert dc["draft_status"] == df["draft_status"]
        assert dc["draft_patch_sha256"] == df["draft_patch_sha256"]
        group = ("grounded_target" if check["category"] == "supported_target_reached"
                 else "no_output" if check["category"] == "no_execution_output" else "other_output")
        row = {"batch": k[0], "task": k[1], "group": group, "draft_status": dc["draft_status"],
               "construction_category": check["category"], "semantics": check["execution_semantics"],
               "packet_path": check["packet_path"]}
        for arm in ("control", "feedback"):
            s, ph = source[k + (arm,)], phase.get(k + (arm,), {})
            row[arm + "_draft_replay"] = ph.get("replay_on_draft_logic") == "True"
            row[arm + "_postedit_replay"] = ph.get("replay_after_source_change") == "True"
            row[arm + "_source_category"] = s["source_category"]
            row[arm + "_status"] = s["returned_status"]
        c, f = row["control_status"], row["feedback_status"]
        row["normal_cf_pair"] = c in NORMAL and f in NORMAL
        row["feedback_gain"] = row["normal_cf_pair"] and c == "scored_failed" and f == "resolved"
        row["feedback_loss"] = row["normal_cf_pair"] and c == "resolved" and f == "scored_failed"
        joined.append(row)
    assert len(joined) == len({(r["batch"], r["task"]) for r in joined}) == 216
    summaries = {}
    for scope, batches in (("final_configuration", ("R03", "R04")),
                           ("all_configurations", ("R01", "R02", "R03", "R04"))):
        summaries[scope] = []
        for group in GROUPS:
            selected = [r for r in joined if r["batch"] in batches and r["group"] == group]
            summary = {"group": group, "realizations": len(selected),
                       "distinct_tasks": len({r["task"] for r in selected}),
                       "normal_cf_pairs": sum(r["normal_cf_pair"] for r in selected),
                       "feedback_gains": sum(r["feedback_gain"] for r in selected),
                       "feedback_losses": sum(r["feedback_loss"] for r in selected)}
            for arm in ("control", "feedback"):
                summary[arm] = {
                    "draft_replays": sum(r[arm + "_draft_replay"] for r in selected),
                    "postedit_replays": sum(r[arm + "_postedit_replay"] for r in selected),
                    "retained_source_changes": sum(r[arm + "_source_category"] == "retained_executable_source_change" for r in selected),
                    "passes": sum(r[arm + "_status"] == "resolved" for r in selected)}
            summaries[scope].append(summary)
        prior = original["summary"][scope]
        assert sum(r["realizations"] for r in summaries[scope]) == prior["task_realizations"]
        for arm in ("control", "feedback"):
            for new, old in (("draft_replays", "replay_on_draft_logic"),
                             ("postedit_replays", "replay_after_source_change"), ("passes", "passes")):
                assert sum(r[arm][new] for r in summaries[scope]) == prior["responses"][arm][old]
            assert sum(r[arm]["retained_source_changes"] for r in summaries[scope]) == prior["responses"][arm]["source_categories"]["retained_executable_source_change"]
    final = summaries["final_configuration"]
    assert [(r["realizations"], r["normal_cf_pairs"], r["feedback_gains"], r["feedback_losses"])
            for r in final] == [(20, 20, 1, 0), (65, 62, 1, 1), (23, 21, 0, 2)]
    final_rows = [r for r in joined if r["batch"] in ("R03", "R04")]
    repositories = ("fastapi", "rich", "requests", "httpx")
    assert {r["task"].split("_", 1)[0] for r in final_rows} == set(repositories)
    breakdowns = {
        "by_batch": [describe_scope([r for r in final_rows if r["batch"] == batch], "batch", batch)
                     for batch in ("R03", "R04")],
        "by_repository": [describe_scope([r for r in final_rows if r["task"].split("_", 1)[0] == repo],
                                         "repository", repo) for repo in repositories]}
    totals = describe_scope(final_rows, "all", "R03/R04")
    for rows in breakdowns.values():
        for field, expected in totals.items():
            if isinstance(expected, int) and field != "distinct_tasks":
                assert sum(r[field] for r in rows) == expected, (field, rows)
    assert totals["distinct_tasks"] == 54
    assert [r["distinct_tasks"] for r in breakdowns["by_repository"]] == [26, 18, 9, 1]
    assert [r["normal_cf_pairs"] for r in breakdowns["by_batch"]] == [52, 51]
    draft_statuses = ("resolved", "scored_failed", "technical_error", "no_patch")
    assert {r["draft_status"] for r in final_rows} == set(draft_statuses)
    draft_breakdown = [describe_draft_status([r for r in final_rows if r["draft_status"] == status], status)
                       for status in draft_statuses]
    assert [r["realizations"] for r in draft_breakdown] == [40, 64, 3, 1]
    for field, expected in totals.items():
        if isinstance(expected, int) and field != "distinct_tasks":
            assert sum(r[field] for r in draft_breakdown) == expected, field
    for arm in ("control", "feedback"):
        prior = original["summary"]["final_configuration"]["responses"][arm]
        for field, original_key in (("normal_draft_pairs", "normal_draft_pairs"),
                                    ("new_passes_from_draft", "new_passes"),
                                    ("lost_passes_from_draft", "lost_passes"), ("passes", "passes")):
            assert sum(r[arm + "_" + field] for r in draft_breakdown) == prior[original_key]
    failed = draft_breakdown[1]
    assert (failed["control_draft_replays"], failed["feedback_draft_replays"]) == (46, 22)
    assert (failed["control_retained_source_changes"], failed["feedback_retained_source_changes"]) == (8, 8)
    grounded_drafts = Counter((r["semantics"], r["draft_status"])
                              for r in final_rows if r["group"] == "grounded_target")
    assert grounded_drafts == {("与所检预期一致", "resolved"): 10,
                               ("与所检预期一致", "scored_failed"): 3,
                               ("公开反证", "scored_failed"): 7}
    grounded_by_draft = [{"semantics": semantics, "draft_status": status, "realizations": count}
                         for (semantics, status), count in sorted(grounded_drafts.items())]
    counter_rows = []
    counter_packets = {}
    for r in counterevidence:
        packet = json.loads(read(resolve_input(r["packet_path"])))
        verify_original_identity(r["packet_path"], r["packet_sha256"])
        counter_packets[(r["batch"], r["task"])] = packet
        for arm in ("control", "feedback"):
            record = source[(r["batch"], r["task"], arm)]
            assert packet["stages"]["draft"]["agent_patch"]["sha256"] == record["draft_patch_sha256"]
            assert packet["stages"][arm]["agent_patch"]["sha256"] == record["returned_patch_sha256"]
        c_edit = first_source_edit(packet, "control")
        f_edit = first_source_edit(packet, "feedback")
        c_stats = branch_interface_stats(packet, "control")
        f_stats = branch_interface_stats(packet, "feedback")
        if r["F"] == "resolved":
            f_class = "landed_and_passed"
        elif f_edit and f_edit["budget_rejected"]:
            if f_edit["occurrences_in_read_window"] == 1 and f_edit["has_contextual_target"]:
                f_class = "blocked_exact_unique_fix"
            else:
                f_class = "blocked_mid_localization_partial_edit"
        else:
            f_class = "blocked_at_target_read"
        counter_rows.append({"batch": r["batch"], "task": r["task"],
                             "draft_status": r["D"], "control_status": r["C"], "feedback_status": r["F"],
                             "feedback_edit_outcome_class": f_class,
                             "control_first_source_edit": c_edit,
                             "feedback_first_source_edit": f_edit,
                             "control_interface_stats": c_stats,
                             "feedback_interface_stats": f_stats,
                             "packet_path": r["packet_path"]})
    assert len(counter_rows) == 8
    assert sum(r["feedback_first_source_edit"] is not None and r["feedback_first_source_edit"]["budget_rejected"] for r in counter_rows) == 4
    assert sum(r["control_first_source_edit"] is not None and r["control_first_source_edit"]["budget_rejected"] for r in counter_rows) == 2
    assert Counter(r["feedback_edit_outcome_class"] for r in counter_rows if r["batch"] in ("R03", "R04")) == {
        "landed_and_passed": 2,
        "blocked_exact_unique_fix": 2,
        "blocked_mid_localization_partial_edit": 2,
        "blocked_at_target_read": 1,
    }
    assert sum(
        bool(r["feedback_first_source_edit"] and r["feedback_first_source_edit"]["immediate_post_cap_event9"])
        for r in counter_rows if r["batch"] in ("R03", "R04")
    ) == 3
    assert sum(
        bool(r["control_first_source_edit"] and r["control_first_source_edit"]["immediate_post_cap_event9"])
        for r in counter_rows if r["batch"] in ("R03", "R04")
    ) == 2
    if IS_MONOREPO:
        final_packets = {(r["batch"], r["task"]): json.loads(resolve_input(r["packet_path"]).read_text(encoding="utf-8"))
                         for r in final_rows}
        tool_allocation = [
            summarize_tool_allocation(final_rows, final_packets, "all_final_108"),
            summarize_tool_allocation([r for r in final_rows if r["draft_status"] == "scored_failed"], final_packets, "failing_drafts_64"),
            summarize_tool_allocation([r for r in final_rows if r["draft_status"] == "resolved"], final_packets, "passing_drafts_40"),
            summarize_tool_allocation([r for r in final_rows if r["group"] == "grounded_target"], final_packets, "grounded_target_20"),
            summarize_tool_allocation([r for r in final_rows if r["group"] == "other_output"], final_packets, "other_output_65"),
            summarize_tool_allocation([r for r in final_rows if r["semantics"] == "公开反证"], final_packets, "counterevidence_7"),
        ]
    else:
        # The lightweight release freezes all-trace tool counts; its seven final
        # counterevidence packets still allow a complete deterministic trace check.
        tool_allocation = []
        for flat in csv_rows("supplement/tool-allocation-v04.csv"):
            item = {"scope": flat["scope"], "realizations": int(flat["realizations"])}
            for arm in ("control", "feedback"):
                item[arm] = {key.removeprefix(arm + "_"): int(value)
                             for key, value in flat.items() if key.startswith(arm + "_")}
                assert all(value >= 0 for value in item[arm].values())
            tool_allocation.append(item)
        assert [(item["scope"], item["realizations"]) for item in tool_allocation] == [
            ("all_final_108", 108), ("failing_drafts_64", 64), ("passing_drafts_40", 40),
            ("grounded_target_20", 20), ("other_output_65", 65), ("counterevidence_7", 7)]
        selected = [r for r in final_rows if r["semantics"] == "公开反证"]
        rebuilt = summarize_tool_allocation(selected, counter_packets, "counterevidence_7")
        assert rebuilt == tool_allocation[5], "Bundled counterevidence tool totals changed"
    all_alloc = tool_allocation[0]
    assert (all_alloc["control"]["missing_param_calls"], all_alloc["feedback"]["missing_param_calls"]) == (45, 48)
    assert (all_alloc["control"]["missing_param_swallowed_old_string"], all_alloc["feedback"]["missing_param_swallowed_old_string"]) == (45, 48)
    assert (all_alloc["control"]["missing_param_bogus_split_keys"], all_alloc["feedback"]["missing_param_bogus_split_keys"]) == (34, 48)
    assert (all_alloc["control"]["missing_param_branches"], all_alloc["feedback"]["missing_param_branches"]) == (6, 5)
    assert (all_alloc["control"]["malformed_read_key_calls"], all_alloc["feedback"]["malformed_read_key_calls"]) == (25, 33)
    assert (all_alloc["control"]["silent_line1_reset_reads"], all_alloc["feedback"]["silent_line1_reset_reads"]) == (24, 32)
    failed_alloc = tool_allocation[1]
    assert (failed_alloc["control"]["run_command"], failed_alloc["feedback"]["run_command"]) == (226, 197)
    assert (failed_alloc["control"]["read_file"], failed_alloc["feedback"]["read_file"]) == (239, 269)
    assert (failed_alloc["control"]["missing_param_calls"], failed_alloc["feedback"]["missing_param_calls"]) == (45, 48)
    assert (failed_alloc["control"]["malformed_read_key_calls"], failed_alloc["feedback"]["malformed_read_key_calls"]) == (10, 14)
    assert (failed_alloc["control"]["silent_line1_reset_reads"], failed_alloc["feedback"]["silent_line1_reset_reads"]) == (10, 14)
    assert (failed_alloc["control"]["budget_exceeded_branches"], failed_alloc["feedback"]["budget_exceeded_branches"]) == (53, 57)
    gt_alloc = tool_allocation[3]
    assert (gt_alloc["control"]["event0_read_file_branches"], gt_alloc["feedback"]["event0_read_file_branches"]) == (6, 16)
    assert (gt_alloc["control"]["source_edit_attempt_branches"], gt_alloc["feedback"]["source_edit_attempt_branches"]) == (4, 8)
    assert (gt_alloc["control"]["source_edit_budget_rejected_branches"], gt_alloc["feedback"]["source_edit_budget_rejected_branches"]) == (2, 4)
    ce_alloc = tool_allocation[5]
    assert (ce_alloc["control"]["source_edit_attempt_branches"], ce_alloc["feedback"]["source_edit_attempt_branches"]) == (4, 6)

    # Verify whole-program scale and follow-up prompt-mitigation ablations across frozen cycle records.
    read(resolve_input("research/cycles/2026-10-12-trigger-validity/report.md"))
    study_a_batches = [json.loads(read(resolve_input(f"research/cycles/2026-10-12-trigger-validity/analysis-{b}.json")))
                       for b in ("R01", "R02", "R03")]
    study_a_jobs = [b.get("jobs") or b["sample_accounting"]["attempts"] for b in study_a_batches]
    assert study_a_jobs == [166, 285, 285]
    assert sum(study_a_jobs) == 736

    followup_cycles = {}
    for slug in ("2026-10-25-local-recursion", "2026-10-15-strong-baseline-recovery", "2026-10-23-local-progress"):
        read(resolve_input(f"research/cycles/{slug}/report.md"))
        batches = [json.loads(read(resolve_input(f"research/cycles/{slug}/analysis-{b}.json")))
                   for b in ("R01", "R02", "R03")]
        assert [b["jobs"] for b in batches] == [285, 285, 285]
        assert [b["independent_tasks"] for b in batches] == [95, 95, 95]
        assert [b["repositories"] for b in batches] == [15, 15, 15]
        followup_cycles[slug] = batches

    rec_r03 = followup_cycles["2026-10-25-local-recursion"][2]["groups"]["official54"]["arms"]
    assert (rec_r03["history5m"]["resolved_count"],
            rec_r03["local_flat_contextual"]["resolved_count"],
            rec_r03["local_nested_contextual"]["resolved_count"]) == (25, 19, 22)
    recov_r03 = followup_cycles["2026-10-15-strong-baseline-recovery"][2]["groups"]["official54"]["arms"]
    assert (recov_r03["after_v2"]["resolved_count"],
            recov_r03["recover_schema"]["resolved_count"],
            recov_r03["recover_shell"]["resolved_count"]) == (26, 24, 27)
    prog_r03 = followup_cycles["2026-10-23-local-progress"][2]["groups"]["official54"]["arms"]
    assert (prog_r03["history5m"]["resolved_count"],
            prog_r03["local_whole"]["resolved_count"],
            prog_r03["local_selective"]["resolved_count"]) == (24, 23, 27)

    program_scale = {
        "distinct_tasks": 95,
        "repositories": 15,
        "study_a_runs": 736,
        "study_b_realizations": 216,
        "study_b_graded_endpoints": 648,
        "study_b_model_sessions": 864,
        "followup_ablation_cycles": 3,
        "followup_ablation_runs": 2565,
        "total_runs_and_realizations": 736 + 216 + 2565,
        "total_graded_endpoints": 736 + 648 + 2565,
    }
    assert program_scale["total_runs_and_realizations"] == 3517
    assert program_scale["total_graded_endpoints"] == 3949

    followup_ablations = [
        {
            "cycle": "2026-10-25-local-recursion",
            "intervention": r"Subagent caps (\texttt{AgentTool}, 855)",
            "stage_target": "Stages 2--3 pool",
            "execution_behavior": "89--96\\% overrun (med. 21--24 reqs)",
            "net_outcome": "25 vs 19/22 (--9.3/--4.5 pp)",
        },
        {
            "cycle": "2026-10-15-strong-baseline-recovery",
            "intervention": "Schema/heredoc retry (855)",
            "stage_target": r"Stage 4 \texttt{old\_string}",
            "execution_behavior": "3/33 recoveries in R03 (0 pass)",
            "net_outcome": "Tie official; --2.4/--5.1 pp ext",
        },
        {
            "cycle": "2026-10-23-local-progress",
            "intervention": r"Voluntary \texttt{keep}/\texttt{reject} (855)",
            "stage_target": "Stage 4 regression",
            "execution_behavior": r"23 \texttt{keep}, 0 \texttt{reject} in 190 runs",
            "net_outcome": "+2.0 pp official; --2.4 pp ext",
        },
    ]

    flat_alloc = []
    for item in tool_allocation:
        row = {"scope": item["scope"], "realizations": item["realizations"]}
        for arm in ("control", "feedback"):
            for k, v in item[arm].items():
                row[f"{arm}_{k}"] = v
        flat_alloc.append(row)
    write_csv("supplement/tool-allocation-v04.csv", flat_alloc)
    write_csv("supplement/result-action-outcome-v04.csv", joined)
    write_csv("supplement/final-configuration-breakdown-v04.csv",
              breakdowns["by_batch"] + breakdowns["by_repository"])
    write_csv("supplement/draft-status-breakdown-v04.csv", draft_breakdown)
    write("evidence/reviewer-analysis-v04.json", json.dumps({
        "version": "v0.4 review 5", "date": "2026-11-11",
        "analysis": "Post-hoc descriptive join of existing check labels, source-state replay, tool allocation, interface delimiter/key diagnostics, returned-source changes, normal paired scores, and follow-up prompt-mitigation ablations.",
        "unit": "Task realization; paired branches share the draft and check. Repeated tasks retain their batch identity.",
        "program_scale_summary": program_scale,
        "group_definition": {"grounded_target": "Publicly supported expectation and relevant target behavior reached.",
                             "other_output": "Execution output outside that joint category, including launch failures.",
                             "no_output": "No common execution output; F receives an unavailable-check notice."},
        "summary": summaries, "final_configuration_breakdowns": breakdowns,
        "final_configuration_draft_status_breakdown": draft_breakdown,
        "final_grounded_checks_by_draft": grounded_by_draft,
        "tool_allocation_summary": tool_allocation,
        "draft_status_analysis_scope": "Retrospective stratification by the existing official draft judgment. Drafts were generated without correctness filtering; their judgments were not supplied to C/F.",
        "counterevidence_comparison": counter_rows,
        "followup_prompt_ablations": followup_ablations,
        **({"rebuild_scope": {
            "mode": "lightweight-derived-inputs",
            "full_packet_extraction": False,
            "joined_csv_realizations": len(joined),
            "counterevidence_packets_recomputed": len(counter_packets),
            "all_trace_tool_allocation": "Frozen aggregate CSV; final seven counterevidence traces recomputed.",
            "original_provenance": provenance,
        }} if not IS_MONOREPO else {}),
        "sources": INPUTS}, ensure_ascii=False, indent=2))
    labels = {"grounded_target": "Grounded target", "other_output": "Other output", "no_output": "No output"}
    table = ["% Generated by scripts/build_v04_review_analysis.py.",
             r"\begin{tabular}{lrrrrr}", r"\toprule",
             "Common result & N & Replay C/F & Edits C/F & Pairs & F gains/losses " + chr(92) * 2,
             r"\midrule"]
    for r in final:
        c, f = r["control"], r["feedback"]
        table.append(f"{labels[r['group']]} & {r['realizations']} & {c['draft_replays']}/{f['draft_replays']} & {c['retained_source_changes']}/{f['retained_source_changes']} & {r['normal_cf_pairs']} & {r['feedback_gains']}/{r['feedback_losses']} " + chr(92) * 2)
    table += [r"\bottomrule", r"\end{tabular}"]
    write("tables/result-strata-v04.tex", "\n".join(table))

    ablation_table = [
        "% Generated by scripts/build_v04_review_analysis.py.",
        r"\begin{tabular}{llll}",
        r"\toprule",
        "Prompt mitigation (runs) & Target & Execution behavior & Net solve impact " + chr(92) * 2,
        r"\midrule",
    ]
    for row in followup_ablations:
        ablation_table.append(
            f"{row['intervention']} & {row['stage_target']} & {row['execution_behavior']} & {row['net_outcome']} " + chr(92) * 2
        )
    ablation_table += [r"\bottomrule", r"\end{tabular}"]
    write("tables/prompt-ablations-v04.tex", "\n".join(ablation_table))

    print(json.dumps({"mode": "full-packet-extraction" if IS_MONOREPO else "lightweight-derived-inputs",
                      "joined_realizations": len(joined),
                      "program_scale": program_scale,
                      "final_configuration": final,
                      "counterevidence_first_edit_rejections": {"C": 2, "F": 4}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
