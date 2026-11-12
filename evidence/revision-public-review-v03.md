# v0.3 public evidence review

Codex-assisted post-hoc review; no independent human review recorded. The selection was fixed before these judgments. Manuscript results and grading outcomes were already known to the reviewer.

All original semantic labels and grading outcomes are retained. The scope was fixed before these new judgments: all 32 source-edited branches, all 26 supported-and-target-reaching checks, and four additional output-producing negatives per batch (seed 2026110903). No model, execution, or grading was added.

## Source retained at delivery

| Post-hoc source category | C | F | Total |
|---|---:|---:|---:|
| retained_code_revision | 14 | 10 | 24 |
| removed_requested_draft_logic | 1 | 3 | 4 |
| quote_syntax_repair | 1 | 0 | 1 |
| docstring_only | 1 | 1 | 2 |
| temporary_edit_restored | 0 | 1 | 1 |

The 24 retained code revisions include incomplete, untested, and apparently invalid changes. They are not 24 new functional repairs. Four branches remove logic directly required in the public issue; two only add docstrings; one returns exactly to D after a temporary corrupting edit. Quote repair is recorded separately. Whole-patch identity and business-source validation are different: deleting a reproduction or adding a docstring can change the former without changing the checked executable logic.

| Batch / task / branch | Final difference from D | Public validation scope |
|---|---|---|
| R01 / requests_7433 / feedback | Deletes D's hasattr(data, '__iter__') stream fallback; retains only a parenthesized isinstance condition. | The final source is exercised by repro.py and raises TypeError. Two restoration edits are rejected at the eight-tool cap. |
| R01 / fastapi_9555 / feedback | Replaces inspect.unwrap(self.call) with self.call in coroutine classification; D's other unwrapping changes remain. | The preceding reproduction passes; after deleting coroutine unwrapping, both rerun and restoration are rejected. |
| R01 / fastapi_14794 / control | Gates special request/response type handling on depends is None and removes the assertion forbidding Depends. | The final source is present during the attempted reproduction, but FastAPI initialization fails on Router's on_startup argument before the annotated dependency is exercised. |
| R01 / rich_3052 / control | Adds a case_sensitive docstring and removes strip() from both choice-matching branches. | The check passes on D before the edits; the final rerun is rejected. |
| R01 / rich_3052 / feedback | Adds only a case_sensitive line to the class docstring. An attempted strip() removal is rejected. | Two Prompt.ask calls accept lower/upper-case input before the docstring edit. The full source text changes, but the executable logic does not. |
| R01 / rich_3930 / control | Extends D's grapheme grouping so a character following a zero-width joiner stays in the current group. | The final version still fails the branch's chop_cells assertion; its particular expected split is not treated as a reference oracle. |
| R02 / requests_7433 / control | Adds the hasattr(data, '__iter__') stream fallback absent from D. | After the edit, repro.py prints the proxy body and chunked transfer encoding without an exception; it does not assert network behavior. |
| R02 / fastapi_9555 / control | Removes inspect.unwrap from generator, async-generator, and coroutine classification. | Two requests return 200 before the removal. A rerun and attempted restoration are rejected, so that success does not cover delivery. |
| R02 / rich_3930 / control | Replaces literal escaped quotes in D's split_graphemes definition with valid quoted source, including its joiner literal. | The subsequent import still raises SyntaxError because D inserted code before a future import. |
| R02 / fastapi_13786 / feedback | Adds not_authenticated_status_code to APIKeyHeader's constructor and stores it on the instance. | The edit is the final ordinary tool operation; no subsequent request exercises the new constructor or missing-credential behavior. |
| R02 / fastapi_13537 / feedback | Tracks processed field aliases in _extract_form_body and uses them to prevent reinsertion of discarded empty values. | The original target test node passes after the edit; the whole-file common output also contains unrelated async-test failures. |
| R03 / requests_7433 / feedback | Deletes D's hasattr(data, '__iter__') fallback while constructing a negative reproduction and never restores it. | The final version raises TypeError in the same reproduction after an earlier pass on D. A later exploratory command is rejected. |
| R03 / rich_3469 / control | Rewrites set_cell_size's binary search and removes padding for a cut through a wide character; deletes D's reproduction file. | The edited function prints 'abc' with width 3 instead of D's 'abc ' with width 4. Only the auxiliary reproduction is deleted after this observation; business source remains the tested version. |
| R03 / rich_3067 / feedback | Adds ~ to ReprHighlighter's URL character set after two malformed edit calls. | The original full-URL span assertions pass after the edit and the business source is retained. |
| R03 / httpx_3672 / control | Adds request.stream.read() in the server path and replaces the unused parser.complete reference with parser.reset(). D's parser API changes remain. | No behavioral check follows the two server edits. Source is under src/httpx/, which the preliminary path-based reading aid omitted; the full returned patch was directly reviewed. |
| R03 / requests_6592 / control | Adds too_early to the existing 425 alias tuple while retaining both old aliases. | The original lower/upper-case attribute assertions pass after the edit. |
| R03 / requests_6592 / feedback | Adds too_early to the existing 425 alias tuple while retaining both old aliases. | The original lower/upper-case attribute assertions pass after the edit. |
| R03 / rich_3535 / feedback | Excludes U+00AD from D's fast-path character range. | The post-edit command compiles a copied regex string, without importing the final repository predicate. It is not a final-source behavioral rerun. |
| R03 / fastapi_14482 / control | Changes jsonable_encoder's model dump mode from json to python. | The original arbitrary-type reproduction passes its dict/foo assertions after the edit. |
| R03 / fastapi_14482 / feedback | Changes jsonable_encoder's model dump mode from json to python, delivering the same patch as C. | The original dict/foo assertions and a second object-field assertion pass on the final business source. |
| R03 / fastapi_13786 / control | Changes check_api_key to an instance method using self.not_authenticated_status_code and adds a WWW-Authenticate formatter. | No request executes the edited method. The apparent attribute-completeness defect is a source observation, not a newly executed failure. |
| R04 / rich_3067 / control | Adds ~ to ReprHighlighter's URL character set after malformed edit calls. | The unchanged reproduction now prints a full URL span and exits zero after the edit. |
| R04 / rich_3067 / feedback | A sed command corrupts highlighter.py after repeated malformed edits; git checkout restores the business file. The returned patch equals D exactly. | The final patch is byte-identical to the earlier failed D reproduction. There is no fresh behavioral rerun after restoration. |
| R04 / rich_3278 / control | Changes the ANSI single-character escape class from [(@-Z\-_] to [0-Z\-_]. | Post-edit decoding assertions pass for ESC7/ESC8 and ESC0/ESC?. No complete ANSI compatibility claim follows. |
| R04 / rich_3278 / feedback | Changes the ANSI escape class to [0-?@-Z\-_] and rewrites the auxiliary reproduction. | The last executed decoder reproduction fails before the successful final edit. The delivered business revision is not rerun. |
| R04 / rich_3506 / control | Revises Segment._split_cells boundary handling and proportional padding around a split character. | A finite branch reproduction passes after editing. Deleting only its auxiliary script later changes the whole patch identity without changing the checked business source. |
| R04 / fastapi_15763 / feedback | Removes the prefixless empty-path guard but duplicates the start of the include_context assignment. Failed and budget-rejected repairs leave that duplicate in delivery. | The empty-path inclusion raises FastAPIError before editing. No final syntax or behavioral execution occurs; the technical-unknown grading endpoint is preserved. |
| R04 / fastapi_14986 / control | Changes Swagger URL/config JSON formatting and replaces </script> with </\script> in two expressions. | Swagger escaping fails before editing; a separate root_path subset passes before the docs.py changes. No Swagger or final-source rerun occurs. |
| R04 / rich_3718 / control | Applies the panel style to title_text and subtitle_text before the border style. | Final title rendering prints red-background ANSI styling. The subtitle run is rejected, so that new branch is unexercised. |
| R04 / fastapi_14361 / feedback | Guards an additional remapper access using schema.get('$ref') and skips non-string references. | A branch reproduction observes KeyError before editing. Its try/except deliberately exits zero on the error; the attempted post-edit rerun is rejected. |
| R04 / fastapi_13920 / feedback | Adds TypeAliasType dispatch through get_args(annotation)[0] to five annotation predicates. A sixth addition is rejected. | The common check exercises only D's helper, not the five subsequently changed predicates; no branch execution validates the delivered additions. |
| R04 / rich_3052 / control | Adds only a case_sensitive line to the class docstring. | After the docstring addition, the input-stream reproduction passes both case-sensitive and case-insensitive ASCII cases. |

## Bounded checking review

All 26 positive joint labels, including eight counterevidence records, and all 16 sampled negative labels were retained within their stated scopes. Joint-label disagreements: 0; category disagreements: 0. This is agreement with an outcome-informed AI review, not a validation rate, reliability coefficient, or independent annotation study.

| Batch / task | Selection | Public interpretation and limit |
|---|---|---|
| R01 / requests_6592 | positive_joint_label | The issue requires too_early=425; three repository attribute/dictionary assertions complete. Existing aliases and other status names are outside the check. |
| R01 / rich_3052 | positive_joint_label | The six real Prompt.check_choice assertions cover default sensitivity and ASCII insensitive matches. Prompt.ask interaction, whitespace, and Unicode are untested. |
| R01 / fastapi_14953 | positive_joint_label | UploadFile's real schema has the requested contentMediaType replacement. Whole-dictionary equality is stronger than the issue's field requirement and cannot certify raw bytes or all routes. |
| R01 / fastapi_14371 | negative_output_sample | The string alias direction is supported, but an inline decorator causes SyntaxError before any request. |
| R01 / fastapi_14246 | negative_output_sample | Three schema-name presence checks do not specify input/output separation. The single-line class definition causes SyntaxError before OpenAPI generation. |
| R01 / requests_6644 | negative_output_sample | Single-leading-slash path_url expectations follow the public issue, but the inline class statement prevents all assertions. |
| R01 / fastapi_13537 | negative_output_sample | Empty Optional[int] form values should use None, but the inline decorator is a checking-program syntax failure. |
| R02 / requests_6592 | positive_joint_label | Both requested lower/upper-case aliases equal 425 after importing the workspace Requests source. Old aliases are not checked. |
| R02 / fastapi_14303 | positive_joint_label | The public Form-model multi-value reproduction reaches TestClient and completes the 200/list assertions. Single-value and other parameter types are outside scope. |
| R02 / fastapi_13537 | positive_joint_label | The independent target node receives 422 for an empty Optional[int] form field, contradicting the required 200/None behavior. Two unrelated async collection failures do not erase this target failure; the JSON assertion is not reached. |
| R02 / fastapi_14372 | negative_output_sample | Hashability is required, but equality and set deduplication of separately constructed instances are additional assumptions. The missing here-document prevents Python execution. |
| R02 / fastapi_9425 | negative_output_sample | The issue concerns typed return annotations and bodiless routes; a generic helper identity assertion expands that contract. Python treats PY as a missing file, so no helper call runs. |
| R02 / rich_4075 | negative_output_sample | Console.print(None, end='!') prints None! and continues to Done. The public title does not establish None as an empty call or no-crash as the full requirement. |
| R02 / fastapi_14794 | negative_output_sample | The Response/Depends annotation is supported, but app construction fails on on_startup before the dependency endpoint is registered. |
| R03 / rich_3067 | positive_joint_label | The requested tilde URL reaches ReprHighlighter. The single span starts at zero but ends before the full URL; failure occurs at the endpoint assertion, not span count or style. |
| R03 / fastapi_9753 | positive_joint_label | Three self-contained partial dependencies resolve via a real request and return foo. Async callable instances and generator combinations are not covered. |
| R03 / requests_7309 | positive_joint_label | The real parser excludes the parameter lacking '=', while preserving charset=utf-8. The assertion does not cover all Content-Type grammar. |
| R03 / fastapi_9555 | positive_joint_label | Two real requests exercise a cache/reawaitable wrapped async dependency and obtain bar. The simplified Settings class and modified cached generator do not validate every wrapper or generator case. |
| R03 / requests_6592 | positive_joint_label | The real codes object lacks the explicitly requested too_early attribute. This fails before the upper-case alias assertion. |
| R03 / rich_3535 | positive_joint_label | The real fast-path predicate matches four ordinary single-width examples. Public source supports the limited predicate interpretation; full Unicode range and performance claims do not follow. |
| R03 / fastapi_14986 | positive_joint_label | The OpenAPI response includes /root in servers, contradicting the visible requirement. The first failure prevents the Swagger escaping check from running. |
| R03 / rich_3052 | positive_joint_label | The real Prompt.ask path accepts insensitive input and rejects it under explicit/default sensitivity. Return-case expectations are consistent with the visible process_response implementation, not a new issue-wide contract. |
| R03 / fastapi_14463 | positive_joint_label | The public three-route/two-model reproduction generates anyOf length two. Reference identity and all route entries are not independently asserted. |
| R03 / fastapi_15763 | negative_output_sample | Empty-path inclusion completes. GET '/' fails the inferred 200 requirement, but the public title only explicitly requires allowing the empty route; this does not provide a strict grounded contradiction. |
| R03 / requests_6644 | negative_output_sample | The issue requires request-uri normalization, not necessarily rewriting PreparedRequest.url. The missing here-document fails first; the intended Request call also misplaces the URL in the method argument. |
| R03 / rich_3278 | negative_output_sample | The explicit ESC0..ESC? range is supported. Python is invoked on a nonexistent PY file, so the tokenizer and preservation checks never run. |
| R03 / fastapi_14360 | negative_output_sample | The Query model alias and extra-name checks correspond to the two public defects. Missing shell-to-Python wrapping prevents both tests; Header/Cookie are untested. |
| R04 / fastapi_15800 | positive_joint_label | The FastAPI object lacks the explicitly requested frontend API. File-serving and router assertions are later and unexecuted; the observed API failure alone establishes the contradiction. |
| R04 / httpx_3672 | positive_joint_label | All three explicitly requested parser API-name assertions complete. hasattr neither verifies a property value nor executes reset, keep-alive, request reading, or shutdown. |
| R04 / requests_7309 | positive_joint_label | The real parser excludes a malformed parameter with no '=' and retains the valid charset. The returned content type and other grammar cases are not asserted. |
| R04 / fastapi_9555 | positive_joint_label | One real request awaits the issue's cache/reawaitable dependency and returns bar. Repeat awaiting and generator classification remain outside this check. |
| R04 / requests_6592 | positive_joint_label | The explicitly requested alias resolves to 425 via real attribute and dictionary access. Upper-case and old aliases are untested. |
| R04 / rich_3535 | positive_joint_label | The real single-width fast-path predicate matches p and ~. This neither validates every character in the extended range nor measures performance. |
| R04 / requests_6629 | positive_joint_label | The requested pickle roundtrip completes and preserves JSONDecodeError type. The check does not assert msg/doc/pos values or execute a process pool. |
| R04 / rich_3518 | positive_joint_label | Table(highlight=True).add_row creates columns that fail the directly requested highlight inheritance assertion. Other table/highlighter settings are outside scope. |
| R04 / fastapi_13786 | positive_joint_label | The missing-key request passes the 401 status assertion but fails the visible ApiKey query header-format requirement. The issue warns that parts are outdated; the later 403 compatibility scenario is not executed. |
| R04 / fastapi_13537 | positive_joint_label | The real scalar int=Form(None) route returns 200 and q=None for q=''. This does not certify models, aliases, file fields, or all regressions. |
| R04 / fastapi_15589 | positive_joint_label | The model Header path accepts an underscored name under the default conversion setting, directly contradicting the issue. Four scalar assertions and the model hyphen case pass first; the final model-disabled scenarios are not reached. |
| R04 / fastapi_14873 | negative_output_sample | The callback-execution direction is public, but the shell wrapping fails before app construction. The app.lifespan trigger itself is not independently validated. |
| R04 / fastapi_15763 | negative_output_sample | Route inclusion is public; resolving the empty string to a 200 root request is an additional assumption. Missing here-document wrapping prevents either stage. |
| R04 / fastapi_14583 | negative_output_sample | Importing an internal compatibility module emits the expected message substring. The issue concerns using pydantic.v1; exact wording, warning category, user trigger, and silence without v1 use are not established. |
| R04 / requests_7505 | negative_output_sample | The reader-preservation direction matches the public source, but this class directly defines read instead of proxying it. An unterminated f-string prevents parsing, so no protocol fallback is exercised. |

## Traceable companion files

- [Complete machine-readable review](revision-public-review-v03.json) binds every selected packet, source patch, grading status, frozen label, new judgment, and event pointer.
- [Source rows](../supplement/source-branch-retention-v03.csv) and [check rows](../supplement/check-semantic-review-v03.csv) are curated summaries; public packet payloads remain in the original local research paths.
- [All ten C/F discordances](../supplement/feedback-discordances-v03.csv), [constructor delivery](../supplement/checker-delivery-v03.csv), and [all four budget-denied edit slots](../supplement/budget-denied-edits-v03.csv) preserve negative and positive evidence.
- Original selection: [fixed scope](revision-review-scope-v03.json). New labels: [curated judgments](review-judgments-v03.json). Neither replaces frozen experimental annotations.

Human review, annotation-model provenance where absent, redistribution rights, and an externally accessible release remain author responsibilities. No additional human supervision or publication status is asserted.
