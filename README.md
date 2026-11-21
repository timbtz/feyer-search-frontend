# Feyer search frontend

A read-only, graph-first view of the Feyer optimization search. Research and LLM runs connect to reviewed topology spaces, small-parameter searches, candidate ancestry, and evaluation evidence. The map lays itself out; it is not a drag-and-drop workflow editor.

See [the complete three-instance workflow](docs/SEARCH_WORKFLOW.md) and its [architecture diagram](docs/images/search-architecture.svg). The shared team ledger maps research, single-successor refinement, stalled branches, multi-parent combinations, and exact-SHA confirmation.

## Run without infrastructure access

Requires Python 3.9+. No npm install, VPS login, AMD account, or model credentials are needed to view the bundled synthetic example.

```bash
git clone https://github.com/timbtz/feyer-search-frontend.git
cd feyer-search-frontend
python3 serve.py --demo
```

Open http://localhost:8770. A visible banner identifies the synthetic data. Sample timings are not research results.

## Connect recorded or live evidence

To use a sanitized snapshot supplied by the coordinator, keep it outside version control:

```bash
mkdir -p .local
# Save the supplied /api/state JSON export as .local/state.json.
python3 serve.py --snapshot .local/state.json
```

For live updates from an existing observatory:

```bash
python3 serve.py --api-url http://127.0.0.1:8765
```

The server proxies only `GET /api/state`; it does not forward credentials, launch agents, or submit evaluations. The upstream must already be reachable. The experiment repository's observatory may aggregate local coordinator records with AMD queue observations; an AMD checkout alone is not a replacement for that aggregation.

The browser refreshes every five seconds. An unavailable backend leaves the last successful view visible with an explicit connection warning. This frontend is a local application; publishing this repository does not deploy a hosted dashboard.

## Follow the search

The main **Search progression** view shows a baseline widening into independent research directions, compact candidate histories, bounded numerical refinement, stopping, combination, and exact confirmation. Select a direction or marker for receipts, use **Focus map** for the canvas alone, and open **Architecture** for the algorithm and three-instance diagram. The first three recent directions are shown initially; all remain available.

Dashed workflow lines describe intended progression. Candidate markers are chronological membership in an explicitly recorded branch; they are not invented parent edges. Latest full measurements remain single observations. Records without branch metadata remain accessible separately.

## Inspect the exact evidence DAG

Switch to **Exact evidence DAG** for explicit scientific ancestry and these controls:

- **Team workflow** maps the GitHub task ledger from top to bottom. **Campaign evidence** shows legacy and finite-search campaigns; **Selected search round** focuses the campaign selector.
- **Earlier experiments** includes historical agent results by default; uncheck it to focus on campaign records. **Evaluation runs** adds individual screen/full requests, including repeats.
- Select a node to trace recorded ancestors and descendants, inspect parameters and measurements, or follow connected evidence.
- Scroll, zoom, expand the workspace, or fit the graph. Search models, ideas, commits, and IDs; press Enter to focus a match.
- Solid edges represent recorded dependencies. Dashed edges indicate grouping or lane membership. A research proposal is never presented as a validated improvement.

The graph describes the recorded search and its implementation choices. It does not infer an internal tensor/solver computation graph or an unrecorded relationship between a worker and a candidate.

## Timing profile

The Timing profile tab reads optional versioned profiler reports by exact job/commit and shows where first-run time is spent. It preserves separate warm timings, wall time, eligibility, instance/cohort, and source freshness. A missing export is unavailable, not a zero-cost profile. The collector and any deep diagnostics belong to the experiment repository; the frontend launches neither.

## Develop and verify

```bash
npm run check
npm test
python3 -m unittest discover -s tests -p 'test_*.py'
```

The app uses plain JavaScript, HTML, CSS, and the Porsche Design System v4, pinned to `4.10.1`. Generated design-system assets are committed; the official loader obtains component chunks and fonts from Porsche's CDN. Native fallback styling remains usable without that CDN. To regenerate assets:

```bash
npm ci --ignore-scripts
npm run build:pds
```

`app.js` contains the pure `SearchDAG` graph model/layout and the browser UI. Node tests cover lineage, combination parents, independent campaign IDs, evidence states, and layout. `serve.py` supplies a small local demo/snapshot/proxy server. `fixtures/demo-state.json` is synthetic and suitable for tests and screenshots.

Read [the architecture briefing](docs/ARCHITECTURE_BRIEFING.md) before changing integration behavior, and [the API contract](docs/API_CONTRACT.md) when adapting the data source. Infrastructure and orchestration are evolving; host names, paths, service placement, model choices, and capacities in the briefing are a dated snapshot.

## Repository boundary

This repository owns frontend presentation, graph transformation, sample fixtures, and its local server. [feyer-search-lab](https://github.com/timbtz/feyer-search-lab) owns coordinator logic, scientific code, source provenance, workers, and the evaluator. The initial extraction also exists at `lab/dashboard` there; these are copies, not an automatic synchronization mechanism. Develop frontend changes here and deliberately copy or consume a reviewed revision when updating the embedded dashboard.

Project code retains the originating repository's MIT license. Porsche assets retain their separate [license](PDS-LICENSE.md) and [third-party notice](PDS-OSS-NOTICE). Feyer branding is used; no Porsche logo or wordmark is included.

### Inspect each evaluation

In Search progression, choose a research path and click **Expand decisions & feedback** on a run. Open individual timing rows for compilation and differentiation subphases. Every recorded evaluation has its own card. Use the scientific/execution graph and optional control-feedback overlay to follow source-backed ancestry and feedback consumption. Missing records are labelled; the browser does not manufacture decisions or private prompts.
