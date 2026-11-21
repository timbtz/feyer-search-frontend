# Read only search snapshot contract

The browser requests `GET /api/state` every five seconds while visible. The response is one JSON object, based on `lab.live_dashboard.Observatory.state()` in `feyer-search-lab`. This is a documented consumer contract, not a separately versioned public API. Unknown fields may be retained in node details; absent optional fields render as unknown, not as a success.

The smallest loadable response is `{"campaigns":[]}`. A complete, synthetic example is [demo-state.json](../fixtures/demo-state.json).

| Field | Shape and use |
| --- | --- |
| `generated_at` | Unix seconds for snapshot creation; source timestamps remain separate. |
| `demo` | `true` only for explicitly synthetic examples; displays a prominent banner. |
| `snapshot` | `true` for a saved observation; displays a static-snapshot banner. |
| `campaigns` | Required array. Each entry has `id`, `selector`, `status`, and arrays below. |
| `campaigns[].campaign.spec` | Frozen objective, validation cohort, and campaign configuration. |
| `rounds` | `round_id`, `closed`, `spec.dimensions`, `spec.lanes`, `spec.materializer_version`, optional `spec.selector`. Explicit `guidance_id` or `guidance_ids`, if supplied by a future producer, creates an admission edge; the current UI does not infer it. |
| `candidates` | `candidate_id`, `commit_sha`, `kind`, `parents` (scientific candidate IDs), `round_id`, `lane_id`, `parameters`, `status`, `valid`, `metrics`, `full_run_count`, `metric_ranges`, `cohort_digest`, `progress`, `provenance`. |
| `model_calls` | `call_id`, `actor`, `metadata.model` (string or object with `model`), `at`. A candidate links via exact `provenance.model_call_id`. A reserved invocation is not proof of completion. |
| `model_outcomes` | `call_id`, `actor`, `metadata`. An outcome record does not automatically mean success. |
| `guidance` | `guidance_id`, `actor`, `payload.parents`, `payload.actual_model`, `payload.session_id`, `payload.hypothesis`, `payload.proposed_operator`. A guidance node is a proposal, not a benchmark. |
| `evaluations` | `request_id`, `candidate_id`, `profile`, `attempt`, `job_id`, `evidence_id`, `status`. Repeats retain distinct request identities. |
| `evidence` | Payloads keyed by `evidence_id`, with recorded check verdicts, measurement/profile and provenance. |
| `workers` | Top-level array of `id`, `model`, `provider`, `status`, `stale`, `observed_at`, `session_id`, `branch`, `direction`, and `host`. No secrets. |
| `historical.candidates` | Earlier records keyed by `run_key` or `job_id`; optional `parent_run_key`, `sha`, `branch`, `validated`, check states and metrics. |
| `queue` | `enabled`, `observed_at`, `stale`, `error`, and `jobs`. Separate from local campaign state. |
| `alerts`, `storage`, `infrastructure`, `jobs` | Supporting operational observations; not sources of scientific ancestry. |

Metrics are finite numbers in seconds except `peak_rss_bytes`. Missing metrics remain absent or null; do not send `NaN`/infinity. `valid` must reflect eligibility from the producer; `completed` execution alone does not qualify. Full-pass labels, screen-pass labels, failed checks and unknown states must remain distinct.

Scientific parent references are scoped to the campaign. Multiple parents form a combination. Git SHA equality, display order, the same lane, or the same model name does not establish ancestry. The renderer rejects cyclic edges with a visible notice rather than looping or silently accepting an invalid DAG.

The frontend uses text nodes for evidence strings, not HTML. The API producer must sanitize sensitive keys and bounded logs before returning JSON. The local proxy does not independently redact a live upstream response; supply only the existing sanitized observatory API or a reviewed export. Never commit production snapshots, session transcripts, API keys, or SSH material to this repository.

No POST, submission, cancellation, assignment, or credential-management endpoints are part of this frontend contract.

## Shared task ledger

`team_search` is either null (unavailable) or an original sanitized `feyer-team-search-v1` object with `coordinator`, `tasks` keyed by task ID, `observations` keyed by instance/job identity, and `events`. Tasks retain `kind`, `status`, `parents`, `candidates`, `depends_on`, `owner`, `instance`, `deadline_unix`, frozen budget and thresholds. Kinds are explore/refine/combine/confirm/diagnose. A refine task admits one successor to its frozen incumbent. `done`, `stalled`, and `blocked` are routing outcomes, not a numerical verdict.

Each observation includes `instance` and normalized `evidence` (`candidate_sha`, `job_id`, `profile`, `eligible_full`, `category`, `cohort_digest`, `metrics`, and recorded checks). The UI keeps observations separated by instance/cohort; it never pools their totals or infers a final champion. Multiple combination inputs remain explicit.

`team_search_source` contains `available`, `mode` (github/local_snapshot), `source`, `sync_enabled`, `observed_at`, `source_updated_at`, `stale`, and `error`. A successful fetch time differs from the last source event. The observatory's explicit `--sync-team` option performs GitHub GET polling every 30 seconds; an error or observation older than 90 seconds is stale. Last-good records remain visible. No write credentials are sent to the browser.

The standalone server's `--team-snapshot` mode wraps a reviewed local ledger export in this shape and labels it static. The backend remains responsible for sanitizing sensitive content before export.

## Optional profiling export

`profiler_reports` is an array of `feyer-profiler-v1` records: `status` (ok/invalid_report/conflicting_artifacts), exact `candidate_sha` and `job_id`, `instance`, `cohort_digest`, `profile`, `eligible_full`, validation details, first-run/phase-sum/unattributed/job-wall seconds, separate `warm_timing`, ranked `phases` and `groups` with `key`/`name`, seconds and shares, plus issues/limits. The Timing profile tab shows measured phase cost before any conclusions about optimization. Hypothetical halving estimates in raw records are not realized gains.

The observatory can consume `.lab/profiler/report.json`, an optional `feyer-profiler-collection-v1` envelope with `profiler_reports`. `profiler_source` exposes availability, file-observation freshness, and errors. Collection is owned by the profiler producer; reading the dashboard does not run profiling, benchmarks or models. Last-good reports remain visible when refresh fails.

## Search progression presentation

The primary view groups `workers`, `jobs`, and historical receipts by their explicit `branch`. It joins ledger eligibility only on both exact job ID and SHA. Jobs already represented by a numerical campaign are excluded from research grouping unless an observed research worker explicitly owns that branch. Repeated jobs remain inspectable while candidate markers deduplicate exact SHA within a branch. The latest full observation is displayed without averaging or declaring a branch winner. Observations lacking branch metadata stay in a separate unlinked-evidence drawer. Only explicit `explore` task ownership supplies additional research groups.

Dashed workflow guides describe the intended algorithm, including prospective combination/confirmation. They are not scientific parent links. The Exact evidence DAG remains the view for recorded ancestry. Active/complete worker observations, source staleness, scientific pass/fail and task routing remain separate concepts.

Optional `team_search.comparison_regime` describes the currently observed mode/epoch/receipt; each observation's `comparison_context` describes that measurement separately. `concurrent` and `unverified_timing` are exploratory timing. `serial` still requires confirmation. Missing context remains unknown and is never filled from the current regime. Correctness eligibility is unchanged. Candidate summaries separate timing groups by instance, cohort, mode and epoch; source context survives the API redaction boundary.

## Expandable evaluations and control feedback

Each exact job keeps a separate card, including repeated SHA evaluations and screen runs. The five totals are first-run, setup, compilation, forward execution, and differentiation execution. Nested rows expose the 14 recorded phases; compilation includes lowering and compilation for forward, sensitivity, and gradients. Missing measurements are unknown. Warm and job-wall timings remain separate.

Green/red deltas require explicit scientific parents and matching instance, eligible full evidence, cohort, timing mode and epoch; repeated parent measurements use medians. Combination cards compare with the faster eligible parent and require evidence for every declared parent. Changes within the noise guard stay neutral. These are observed differences, not causal or confirmed-winner claims. Legacy producer-qualified baseline comparisons are marked exploratory and excluded from new timing regimes.

`recorded_feedback` joins exact job, SHA and profile. Cards expose the recorded hypothesis, change summary, declared phase targets, scientific inputs, downstream candidates, selection parameters, validation errors and checkpoint artifacts. Missing decisions or input receipts stay explicitly unavailable. Current-turn private input digests do not imply a captured next prompt or provide public downloads.

Optional `search_lineage` (`feyer-search-lineage-v1`) supplies nodes, scientific `edges`, separate `control_edges`, records, issues and limits. The scientific/execution view lays out scientific edges; the control-feedback toggle overlays separately styled links without making feedback cycles scientific ancestry. Producer research records are the authority for target phases, stopping reasons, combinations and consumed-feedback receipts. Exhausted menus are not local-optimum claims.

## Compact topology map

The default map groups exact candidate revisions by explicit topology metadata, admitted campaign `space_version`, or declared phase focus. Phase focus is labelled separately from a topology. Unknown topology remains unclassified; worker names and free-text hypotheses never create phase or ancestry edges. Explicit campaign candidate IDs resolve inside their campaign. Proposed research with no candidate remains an unmeasured assignment. Repeat job receipts are expandable within the candidate node; the compact metric is the latest recorded job, not a pooled winner.
