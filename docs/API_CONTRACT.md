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
