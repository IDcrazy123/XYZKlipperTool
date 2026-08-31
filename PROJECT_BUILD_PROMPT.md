# Master Build Prompt — XYZ Klipper Tool

## 1. Role

You are the implementation agent for **XYZ Klipper Tool**, working in `D:\Desktop\XYZKlipperTool` and publishing to <https://github.com/IDcrazy123/XYZKlipperTool>. Use model `gpt-5.6-luna` with reasoning effort `medium` for each bounded phase.

Act as a careful staff-level software engineer for a safety-sensitive Klipper integration. Finish all authorized offline work in the current phase, verify it, document it, commit it, and push the phase branch. Do not declare a phase complete because a plan exists.

## 2. Immutable project identity

- Display name: **XYZ Klipper Tool**.
- Python package and service slug: decide in Phase 00, but use one consistent lowercase identifier; record the decision in an ADR.
- Local repository: `D:\Desktop\XYZKlipperTool`.
- Remote: `git@github.com:IDcrazy123/XYZKlipperTool.git`.
- Default branch: `main`.
- This is a greenfield repository. ToolVision is evidence and comparison material only.
- Do not rename, fork, vendor, copy, or progressively patch ToolVision into this repository.
- Do not hide copied history by changing names. Any upstream-derived code requires an explicit license/provenance decision and file-level attribution.

## 3. Product objective

Build an extensible calibration system for Klipper toolchangers that:

1. Automatically measures relative X/Y tool offsets with a fixed camera.
2. Measures relative Z tool offsets through one explicitly selected provider:
   - physical contact switch; or
   - Cartographer Touch.
3. Lets the operator teach the camera station and each Z-provider station from the current machine pose using G-Code commands, validates the pose, and persists it atomically.
4. Never assumes fixed camera, probe, switch, dock, or safe-Z coordinates.
5. Discovers tools through an adapter; the product must not assume exactly five tools or names T0–T4.
6. Runs repeated, independent pickup cycles and retains raw evidence.
7. Reports candidates by default; applying offsets is a separate, previewed, confirmed, reversible transaction.
8. Supports future camera algorithms, Z providers, toolchanger frameworks, storage backends, and user interfaces without changing domain logic.

## 4. Non-goals for v1

- No control of an ESP32-C3, WS2812B ring, or other auxiliary lighting.
- No cloud image upload and no cloud dependency.
- No autonomous physical movement without an operator-approved HIL run.
- No general bed-mesh, QGL, PID, input-shaper, or print-quality tuning.
- No replacement for Cartographer's own firmware calibration.
- No implicit `SAVE_CONFIG`, Klipper restart, production config edit, or offset apply.
- No hard-coded KTC-only implementation and no emulation of every toolchanger framework in v1.
- No claim that camera detection is reliable until the labeled corpus and HIL gates pass.

## 5. Mandatory evidence and source behavior

Read `AGENTS.md`, `docs/EVIDENCE_BASELINE.md`, `docs/SOURCE_MAP.md`, and `docs/STATUS.md` before work. Treat the recorded kTAMV and Z runs as requirements evidence, not reusable source code.

Before writing behavior that depends on Klipper, Moonraker, Cartographer, OpenCV, KTC, or another toolchanger:

1. Open the current primary source.
2. Record URL, access date, version/commit, supported claim, ambiguity, and license in the source ledger.
3. Add a traceability row from requirement → source/evidence → design → test.
4. Stop and mark the item `BLOCKED_BY_SOURCE` if a safety-critical semantic such as offset sign, coordinate frame, active-tool state, or probe result cannot be established.

Never infer product defaults from the observed machine's camera pose near X170/Y20/Z40, switch near X68/Y-10, camera scale, offsets, tool count, temperatures, or tolerances.

## 6. Required terminology and state model

Use these claim states consistently:

- `OBSERVED`: present in preserved external evidence.
- `IMPLEMENTED`: code exists and applicable offline tests pass.
- `PLANNED`: approved design or future work without completed implementation.
- `REQUIRES_HIL`: cannot be established without approved hardware execution.
- `INVALID`: the run failed or violated an invariant; never aggregate it.
- `WARNING`: run completed but one or more configured acceptance checks were absent or exceeded.
- `PASS`: all required checks for the declared protocol passed.

Separate these identities:

- `run_id`: one requested calibration job.
- `outer_cycle_id`: one independent physical reacquisition cycle.
- `tool_visit_id`: one selected tool visit inside a cycle.
- `frame_sample_id`: one image/detection sample inside a visit.
- `station_revision`: immutable revision of a taught station.
- `configuration_fingerprint`: normalized machine/plugin/config identity used for freshness checks.
- `calibration_id`: camera calibration/transform identity.

## 7. Required command contract

Phase 00 may refine names only through an ADR. The v1 command surface must preserve the following capabilities and unambiguous semantics:

### Station commands

- `XYZ_TOOL_TEACH_CAMERA_POSITION [SAFE_Z=<mm>] [NAME=<id>]`
  - Capture current X/Y/Z from the printer, not from user-entered defaults.
  - If `SAFE_Z` is omitted, define and document whether current Z becomes clearance or the command refuses; never invent a value.
  - Validate homed axes, machine limits, active tool/reference semantics, and finite numbers.
- `XYZ_TOOL_TEACH_Z_POSITION METHOD=SWITCH|CARTOGRAPHER_TOUCH [SAFE_Z=<mm>] [NAME=<id>]`
  - Keep separate stations per provider.
  - Persist provider identity, current pose, safe approach data, coordinate frame, configuration fingerprint, timestamp, and revision.
- `XYZ_TOOL_SHOW_POSITIONS [NAME=<id>]`
- `XYZ_TOOL_CLEAR_POSITION TYPE=CAMERA|Z METHOD=<provider> NAME=<id> CONFIRM=<token>`
  - Destructive station removal requires exact preview and confirmation.

### Measurement commands

- `XYZ_TOOL_MEASURE_XY [CYCLES=3] [TOOLS=<selector>] [REFERENCE=<tool>] [STATION=<id>]`
- `XYZ_TOOL_MEASURE_Z METHOD=SWITCH|CARTOGRAPHER_TOUCH [CYCLES=3] [TOOLS=<selector>] [REFERENCE=<tool>] [STATION=<id>]`
- `XYZ_TOOL_MEASURE_XYZ METHOD=SWITCH|CARTOGRAPHER_TOUCH [CYCLES=3] ...`
- `XYZ_TOOL_STATUS [RUN=<id>]`
- `XYZ_TOOL_CANCEL [RUN=<id>]`
- `XYZ_TOOL_REPORT [RUN=<id>] [FORMAT=TEXT|JSON]`

Measurement defaults must remain report-only. `CYCLES` means independent outer reacquisition cycles, not repeated reads without redocking.

### Apply commands

- `XYZ_TOOL_APPLY_PREVIEW RUN=<id>`
- `XYZ_TOOL_APPLY RUN=<id> CONFIRM=<token>`
- `XYZ_TOOL_ROLLBACK APPLY=<id> CONFIRM=<token>`

Apply must reject stale, invalid, warning-without-override, mismatched-provider, mismatched-tool-set, mismatched-reference, or changed-configuration evidence. It must create a backup and rollback manifest before the first mutation. It must never conceal partial failure.

## 8. Required architecture

Use a hexagonal/ports-and-adapters design with dependency direction toward the domain.

### Domain package

Pure Python with no imports from Klipper, Moonraker, OpenCV, Flask/FastAPI, systemd, or filesystem-specific code. It owns:

- typed vectors, units, coordinate frames, and sign conventions;
- station and configuration-fingerprint value objects;
- cycle/run state machine;
- validity and reason-code model;
- robust statistics and uncertainty summaries;
- apply plan, freshness validation, and rollback plan;
- provider-neutral interfaces.

### Host service

Owns:

- camera URL/device capture with strict timeouts and frame-size limits;
- OpenCV transforms and detector plugins;
- calibration artifacts and labeled corpus evaluation;
- evidence/history persistence and retention;
- loopback HTTP/Unix-socket API;
- job execution that does not block Klipper's reactor;
- structured health/status endpoints.

### Klippy extension

Owns:

- G-Code registration;
- reading current printer/tool/axis/heater/probe/endstop state;
- invoking bounded printer operations through supported APIs/macros;
- non-blocking coordination with the host service;
- status exposure through `get_status()`;
- abort, timeout, and recovery hooks.

It must not import OpenCV, perform long filesystem/network operations on the reactor, or use undocumented internals without a pinned compatibility shim and tests.

### Ports and adapters

At minimum define contracts for:

- `CameraProvider`
- `VisionDetector`
- `ToolchangerAdapter`
- `ZProvider`
- `StationStore`
- `EvidenceStore`
- `OffsetReader`
- `OffsetWriter`
- `Clock`
- `RunLock`

Provide fake adapters before real hardware adapters. The first real toolchanger adapters should cover the observed KTC/klipper-toolchanger environment and a generic macro/status contract, but implementation order must follow Phase 00 evidence.

## 9. Motion and safety invariants

Encode each invariant as a named reason code and test it with fault injection.

1. No motion before required axes are homed and the printer is ready.
2. No run while printing, paused in an unsafe state, shutdown, or another calibration lock is held.
3. Active and detected tool states must agree when the adapter exposes both.
4. A selected station must exist, match provider, pass machine limits, and match the current configuration fingerprint or an explicit migration.
5. Raise Z at the current X/Y to a validated clearance before XY travel.
6. Never lower below the provider's bounded approach envelope.
7. Switch state must be plausible before approach and must transition within maximum travel/time.
8. Cartographer Touch must report compatible firmware/model/readiness before approach.
9. Camera capture and detection must time out, reject stale frames, and reject ambiguity.
10. Reference return drift must be checked in protocols that declare it; missing reference return is not a pass.
11. Invalid samples and cleanup failures are stored but excluded from estimators.
12. Cleanup is best-effort and ordered, but the primary error must never be overwritten by cleanup errors.
13. Heaters changed by the run are restored or safely turned off according to the approved protocol; untouched heaters are not commandeered.
14. Tool restoration is attempted only when state is known; never guess the mounted tool after an error.
15. Every physical action is idempotent or has a recorded compensation/rollback step.

## 10. Statistical and vision requirements

### Sampling hierarchy

- Inner frame samples estimate detector repeatability while one tool remains physically acquired.
- Outer cycles estimate pickup/dock/reacquisition variation.
- Do not inflate sample count by treating inner frames as independent pickup cycles.
- Default v1 X/Y protocol: three outer cycles with dynamic selected tools.
- Target sequence per cycle: acquire reference, measure selected tools with independent pickups, reacquire reference and measure return drift. If the toolchanger makes a different safe ordering necessary, record an ADR and retain equivalent drift evidence.

### Statistics

For each axis/tool/provider and at each declared hierarchy:

- count total, valid, invalid, and warning samples;
- retain ordered raw values;
- mean;
- median;
- sample standard deviation only for `n >= 2`; return an explicit `INSUFFICIENT_SAMPLES`, never throw an unhandled `stdev requires at least two data points` error;
- MAD;
- min, max, and range;
- reference-start/return drift;
- confidence/uncertainty metric whose assumptions are documented;
- configured acceptance limits and reason-coded verdict.

Outlier policies must be declared before evaluation, preserve original values, and produce both unfiltered and filtered summaries. Default behavior is no automatic removal and no automatic apply.

### Vision

- Build a labeled corpus from sanitized real frames, including reflections, multiple circular blobs, missing nozzle, blur, exposure changes, and off-center nozzle.
- Split calibration, development, and holdout data by capture session to avoid leakage.
- Benchmark candidate methods rather than assuming Hough circles is sufficient.
- Emit diagnostics: candidate shapes, confidence, center residual, calibration identity, frame age, exposure metadata when available, and rejection reason.
- Define maximum image size, decode time, capture retries, frame age, allowed center window, transform uncertainty, and measurement uncertainty.
- Camera calibration and station origin are separate concepts and separately versioned.

## 11. Persistence and evidence schema

Use atomic write-to-temp, fsync where applicable, rename, schema version, and backup rotation. Never mutate a completed raw evidence file.

Every run manifest must include:

- schema and project version;
- run/cycle/visit/sample IDs;
- UTC and local timestamps;
- claim status and reason codes;
- requested command parameters and resolved dynamic tool list;
- reference tool and toolchanger adapter/version;
- station identity/revision and configuration fingerprint;
- camera/calibration/detector identities;
- Z provider identity and provider-specific metadata;
- units, coordinate frame, and sign semantics;
- raw samples and derived summaries;
- temperature/environment observations without embedding secrets;
- primary error, cleanup errors, cancellation/timeout state;
- `applied=false` by default;
- checksum/provenance links for artifacts.

Define schema migrations and round-trip tests before changing a persisted schema. Unknown future fields must not corrupt older readers; unsupported major versions fail closed.

## 12. Security and operational requirements

- Bind to `127.0.0.1` and/or a local Unix socket by default.
- If remote access is later enabled, require an explicit threat model, authentication, authorization, TLS/reverse-proxy guidance, and rate limits.
- Accept only allowlisted camera schemes/hosts or local devices; prevent SSRF and path traversal.
- Bound body size, image size, history count, concurrent jobs, retries, queue depth, tool selectors, string lengths, and numeric ranges.
- Redact credentials and tokens from URLs, logs, evidence, exceptions, and support bundles.
- No shell interpolation of user input.
- Pin dependencies with hashes after license and vulnerability review.
- Provide install, update, rollback, and uninstall scripts that are idempotent, dry-run capable, scope-checked, and tested in sandbox fixtures.
- Never delete user configuration or evidence during uninstall unless an explicit purge flag previews exact targets.

## 13. Required repository structure

Phase 00 may adjust names through an ADR, but preserve the separation:

```text
XYZKlipperTool/
  AGENTS.md / AGENTS.vi.md
  README.md / README.vi.md
  PROJECT_BUILD_PROMPT.md / PROJECT_BUILD_PROMPT.vi.md
  pyproject.toml
  src/<package>/
    domain/
    protocol/
    vision/
    z/
    toolchanger/
    persistence/
    service/
    klipper/
  klippy/extras/
  config/
  scripts/
  schemas/
  tests/
    unit/
    component/
    contract/
    integration/
    fault_injection/
    installer/
    fixtures/
  evidence/
    imported/
    manifests/
    corpus/
  docs/
    adr/
    phases/
    progress/
    operator/
    developer/
    api/
```

Every first-party Markdown file has a paired `.vi.md` version.

## 14. Phase plan and acceptance gates

### Phase 00 — Governance, source audit, license, evidence import

Deliver:

- repository identity ADR;
- v1 requirements with stable IDs (`REQ-...`);
- source ledger with pinned commits/versions and licenses;
- clean-room/provenance policy;
- license decision and third-party notices plan;
- sanitized immutable import of X/Y CSV/report and all relevant Z JSON, including invalid runs;
- SHA-256 manifest and evidence index;
- architecture context diagram and initial threat model;
- risk register, decision log, traceability matrix, test matrix, roadmap, and bilingual parity checker;
- no production measurement implementation.

Gate:

- every v1 behavior has a source or explicit evidence/assumption label;
- all imported files match recorded hashes or differences are explained;
- secrets scan passes;
- licenses allow the planned use;
- all Markdown pairs pass parity checks;
- branch pushed and supervisor review requested.

### Phase 01 — Domain model, units, signs, statistics

Deliver typed pure domain models, state machine, reason codes, robust statistics, provider-separated results, apply-plan model, schemas, and property/metamorphic tests.

Gate:

- no I/O or framework imports in domain;
- `n=0` and `n=1` statistics return typed insufficient-data results;
- sign/coordinate conversions have table-driven tests;
- invalid samples never enter estimators;
- deterministic tests and schema round trips pass.

### Phase 02 — Ports, fake adapters, simulator, station persistence

Deliver all port interfaces, deterministic fake printer/toolchanger/camera/Z providers, dynamic tool discovery, teach/show/clear station use cases, atomic persistence, configuration fingerprints, locks, and crash/fault fixtures.

Gate:

- no hard-coded T0–T4 logic;
- station coordinates come only from current-position input in command use cases;
- stale/corrupt/partial state fails closed;
- concurrent run/teach/apply operations are rejected correctly;
- power-loss write simulations preserve the last valid state.

### Phase 03 — Camera capture, calibration, detector framework

Deliver bounded camera adapters, calibration store, detector plugin interface, at least two benchmarked candidate pipelines where evidence supports them, diagnostic overlays/artifacts, labeled corpus tooling, and session-separated evaluation.

Gate:

- holdout metrics and failure classes are published;
- stale/missing/oversized/corrupt/multi-candidate frames are rejected with reason codes;
- calibration identity and transform uncertainty propagate into results;
- no claim of physical accuracy without HIL.

### Phase 04 — X/Y independent-cycle orchestrator

Deliver report-only X/Y orchestration using fake adapters first, nested sampling hierarchy, dynamic tools/reference, station lookup, reference return drift, cancellation, timeout, recovery evidence, and report generation.

Gate:

- tests prove each outer cycle reacquires tools;
- inner frames cannot masquerade as outer cycles;
- historical kTAMV fixture reproduces expected summaries, including T3 mean/median difference;
- missing terminal reference return cannot produce `PASS` for the enhanced protocol;
- no offset writer is invoked.

### Phase 05 — Physical-switch Z provider

Deliver switch readiness/query contract, provider-specific taught station, bounded approach state machine, trigger/release validation, multiple-probe aggregation, thermal metadata, abort/recovery behavior, and imported switch fixture tests.

Gate:

- stuck-open, stuck-closed, no-trigger, early-trigger, bounce, timeout, shutdown, unknown-tool, and cleanup-failure tests pass;
- sign mapping to configured tool offsets is proven by source and fixtures;
- historical `INVALID` TMC run remains invalid and excluded;
- physical behavior remains `REQUIRES_HIL`.

### Phase 06 — Cartographer Touch Z provider

Deliver Cartographer readiness/version/model contract, taught station or documented provider pose semantics, Touch invocation/result parser, thermal/readiness checks, bounded recovery, and imported Cartographer fixture tests.

Gate:

- unsupported firmware/model/output fails closed;
- parser uses recorded real output fixtures plus synthetic errors;
- provider samples remain separate from switch samples;
- physical behavior remains `REQUIRES_HIL`.

### Phase 07 — Apply transaction, backup, rollback

Deliver offset-reader/writer adapters, exact preview, confirmation token, freshness checks, configuration backup, transactional per-tool apply, verification readback, partial-failure record, rollback command, and immutable apply manifest.

Gate:

- default measurement paths cannot call apply;
- stale or non-PASS evidence is rejected unless a narrowly documented override exists;
- simulated failure after every mutation point restores or reports exact divergence;
- no implicit `SAVE_CONFIG` or restart;
- actual framework-specific write semantics are source-pinned and contract-tested.

### Phase 08 — Host API and service

Deliver versioned local API, job lifecycle, health/status, bounded evidence access, Unix-socket/loopback service, authentication decision, structured errors, cancellation, service templates, and resource limits.

Gate:

- SSRF, traversal, oversized payload, concurrency, timeout, credential-redaction, crash-restart, and backwards-compatibility tests pass;
- no externally reachable listener by default;
- API schema is documented in both languages.

### Phase 09 — Klipper extension and G-Code commands

Deliver minimal loader, registered commands from Section 7, non-blocking client, status object, adapter selection, printer-state guards, motion-provider bridge, and simulated Klipper integration tests.

Gate:

- Klipper reactor is never blocked by camera/network work;
- command help and errors are actionable;
- fake Klipper tests cover startup, restart, disconnect, shutdown, cancellation, and missing optional providers;
- configuration parse failures identify exact option and remediation.

### Phase 10 — Installer, updater, uninstaller

Deliver documented prerequisites, dry-run installer, exact symlink/service/config changes, backups, versioned updates, rollback, non-destructive uninstall, purge preview, and sandbox test matrix for supported hosts.

Gate:

- repeated install/update/uninstall is idempotent;
- scope checks prevent deleting broad or unresolved paths;
- existing Klipper/Moonraker config is never overwritten silently;
- no network install runs unpinned code;
- rollback from a failed step is tested.

### Phase 11 — Documentation, security, release candidate

Deliver paired English/Vietnamese operator and developer guides, command/config/API references, troubleshooting, safety/HIL manual, architecture and ADR index, security policy, contribution guide, changelog, release checklist, support bundle redaction, SBOM/dependency/license reports, and release candidate tag.

Gate:

- all offline tests, lint, type checks, security scans, docs links, examples, package build, fresh install simulation, upgrade simulation, and uninstall simulation pass;
- no undocumented command/config option;
- every requirement has implementation and test traceability or is explicitly deferred;
- no claim of production readiness yet.

### Phase 12 — Supervised HIL canary

Do not start until the operator explicitly approves a written run sheet and confirms the machine is ready.

The run sheet must include exact station-teach commands, discovered limits, safe clearance, tool list, reference tool, provider, temperature plan, stop criteria, emergency-stop access, expected duration, data capture, and rollback. Begin with report-only single-tool/single-cycle canaries, then expand. Never jump directly to all tools or apply.

Gate:

- approved X/Y, switch Z, and Cartographer Z protocols each have traceable raw evidence;
- three independent outer cycles pass configured limits for the selected production protocol;
- failure/recovery drill is demonstrated safely;
- apply remains a separate operator decision;
- only after review may production-ready status or a stable release be considered.

## 15. Test and quality policy

Use deterministic tests and explicit fixtures. Required categories:

- unit tests for domain and statistics;
- property/metamorphic tests for transforms, sign, aggregation, and invariants;
- component tests for capture, detection, persistence, providers, and API;
- contract tests for each upstream/version adapter;
- fake-Klipper and fake-Moonraker integration tests;
- fault injection at every physical-operation and persistence boundary;
- installer sandbox tests;
- schema compatibility and migration tests;
- documentation link/example tests and bilingual-pair checks;
- secret, dependency, license, static-security, type, and lint checks;
- performance/resource tests for image, job, history, and API bounds.

Aim for at least 90% line/branch coverage of first-party production code and 95% for safety state machines/domain invariants, but never use coverage percentage as a substitute for fault cases and requirements traceability.

## 16. Progress, Git, and supervision

- Work one phase per branch: `phase/00-governance`, `phase/01-domain`, and so on.
- Keep `main` releasable and do not merge your own phase without a supervisor gate.
- Commit messages are English Conventional Commits, for example `docs: establish phase 00 source ledger`.
- Do not force-push shared branches and do not rewrite published history.
- Push after each coherent checkpoint, not only at the end of a long phase.
- Create paired progress records: `docs/progress/YYYY-MM-DD-phase-NN.md` and `.vi.md`.
- Each progress record includes objective, inputs, source updates, files changed, commands/tests with exact results, evidence produced, decisions, risks, status, commit, remote branch, and next gate.
- Store machine-readable test artifacts under `artifacts/test-runs/<run-id>/` with a manifest; do not commit secrets or uncontrolled large binaries.
- Tag accepted checkpoints as `checkpoint-phase-NN` only after supervisor approval. Stable semantic release tags require Phase 12 review.

## 17. Required end-of-task report

For each Luna task, report:

1. Outcome first: completed, partially completed, or blocked.
2. Phase and acceptance criteria addressed.
3. Files and architecture changed.
4. Sources/evidence added or changed.
5. Exact validation commands and pass/fail counts.
6. Claim-state changes (`PLANNED` → `IMPLEMENTED`, or still `REQUIRES_HIL`).
7. Safety risks and unresolved ambiguities.
8. Commit SHA and pushed branch.
9. Exact next phase/gate; do not silently start it.

If blocked, continue all independent offline work first. A genuine blocker report names the missing fact/authority, actions already attempted, preserved evidence, and the smallest user decision needed.

## 18. First task to execute

Execute **Phase 00 only**.

Do not write measurement production code. Build the governance, source, license, requirements, evidence-import, risk, traceability, test-matrix, architecture-context, threat-model, progress, and bilingual-parity foundations. Import and checksum the complete relevant evidence set without modifying raw files. Verify that all first-party Markdown has an English/Vietnamese pair. Commit and push `phase/00-governance`, then stop for supervisor review.
