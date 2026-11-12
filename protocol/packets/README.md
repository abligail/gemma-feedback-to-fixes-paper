# Core public case traces

All event indices and parameter keys are preserved, including malformed `start_line"` keys and swallowed `old_string:` arguments. Packet source hashes in the paper's CSV/JSON identify the original exports. Use the [release manifest](../public-release-manifest.json) to locate their public projections and verify the public-byte hashes.

| Study / batch | Case | Evidence covered |
|---|---|---|
| B / R02 | [FastAPI13537](study-b/R02/fastapi_13537.json) | F lands the alias-handling repair; C returns D |
| B / R03 | [Rich3067](study-b/R03/rich_3067.json) | F regex repair; C's 17 missing-parameter retries |
| B / R03 | [Requests6592](study-b/R03/requests_6592.json) | Both branches land and pass |
| B / R03 | [FastAPI14986](study-b/R03/fastapi_14986.json) | Localization ends at the cap; incomplete edit follows |
| B / R04 | [FastAPI15800](study-b/R04/fastapi_15800.json) | C/F event-9 edits follow event-8 budget rejection |
| B / R04 | [Rich3518](study-b/R04/rich_3518.json) | Unique matching C/F edits blocked by the cap |
| B / R04 | [FastAPI13786](study-b/R04/fastapi_13786.json) | Unique matching F edit blocked by the cap |
| B / R04 | [FastAPI15589](study-b/R04/fastapi_15589.json) | First target-file read rejected |
| B / R03 | [Requests7433](study-b/R03/requests_7433.json) | F deletes working draft logic |
| B / R04 | [Rich3067](study-b/R04/rich_3067.json) | Separate D; F corrupts and restores the source |
| B / R04 | [Rich3718](study-b/R04/rich_3718.json) | F's 24 malformed edit requests |
| A / R03 | [Requests7427](study-a/R03/requests_7427-2026101213-trigger_probe_v1.json) | Narrow checks pass on a partial fix |
| A / R03 | [pytest7205](study-a/R03/pytest-dev__pytest-7205-2026101213-trigger_probe_v1.json) | Unverified deletion of `saferepr` |
| A / R03 | [SymPy23950](study-a/R03/sympy__sympy-23950-2026101213-trigger_probe_v1.json) | Eleven calls before the first edit hits the cap |

Task statements/hints and model conversations are excluded. Recorded commands are evidence for inspection; the build scripts parse the records without executing these commands. Official outcome statuses and returned-patch fingerprints are in the [endpoint table](../../supplement/feedback-task-outcomes.csv) and [Study A outcomes](../../supplement/checking-task-outcomes.csv).
