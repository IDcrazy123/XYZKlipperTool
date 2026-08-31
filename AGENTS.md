# XYZ Klipper Tool — AI Agent Rules

This file is the mandatory entry point for every human or AI contribution. Read it completely before taking action. The Vietnamese counterpart is [AGENTS.vi.md](AGENTS.vi.md).

## Mission and boundaries

Build an independent, extensible Klipper calibration project that measures tool X/Y offsets with a camera and tool Z offsets with either a physical switch or Cartographer Touch. Measurement stations are taught from the current machine position by explicit commands and persisted with provenance; no machine coordinate may be embedded as a product default.

The current repository is not production-ready. Never imply that offline tests prove physical safety.

## Mandatory reading order

1. `README.md`
2. `PROJECT_BUILD_PROMPT.md`
3. `docs/STATUS.md`
4. `docs/EVIDENCE_BASELINE.md`
5. `docs/SOURCE_MAP.md`
6. The phase-specific plan and decision records created later

## Language and documentation parity

- English is canonical for code, identifiers, comments, docstrings, schemas, commit messages, and the unqualified `.md` document.
- Every first-party Markdown file must have a Vietnamese sibling using `.vi.md` before the extension: `GUIDE.md` and `GUIDE.vi.md`.
- Update both language versions in the same commit. Meaning, safety warnings, commands, units, status labels, and links must stay equivalent.
- Generated third-party notices and upstream evidence are exempt only when their provenance is recorded and they are not edited.
- CI must eventually enforce bilingual Markdown parity and reject orphaned first-party documents.

## Evidence discipline

- Classify claims as `OBSERVED`, `IMPLEMENTED`, `PLANNED`, or `REQUIRES_HIL`.
- Never convert a historical machine coordinate, offset, threshold, temperature, light source, or tolerance into a general default.
- Preserve raw evidence immutably. Derived summaries must identify source hashes, formulas, units, coordinate frames, sign conventions, software versions, and timestamps.
- Do not silently delete outliers. Report raw values, mean, median, sample standard deviation where defined, MAD, range, rejection reason, and accepted/rejected status.
- Research primary sources before implementation. Record the exact URL, access date, version/commit, supported claim, and any unresolved ambiguity.
- Copying upstream code requires an explicit license and provenance review. Behavioral comparison is not permission to copy implementation.

## Safety and authority

- Offline reading, planning, editing, and non-destructive tests are authorized for a build/fix task.
- Physical printer motion, heating, probing, tool changes, firmware restart, configuration apply, service deployment, or HIL require explicit operator approval for that run.
- A saved station is data, not proof that travel is safe. Validate homing, limits, active tool, current position, Z clearance, heater state, endstop/probe readiness, and abort path before every physical run.
- Safe travel order is provider-owned and validated: raise Z at the current X/Y, move in X/Y only after clearance, then approach the station under a bounded envelope.
- Stop on stale configuration fingerprint, missing station, ambiguous tool state, camera failure, detector uncertainty, probe/endstop inconsistency, reference drift, timeout, or printer shutdown.
- Never issue `SAVE_CONFIG`, edit production offsets, or restart Klipper implicitly. Applying results is a separate previewed transaction with backup, validation, rollback data, and operator confirmation.
- The camera's normal illumination is assumed to be supplied by the user. ESP32-C3/WS2812B lighting is external temporary equipment and is not a required dependency or control target.

## Architecture constraints

- Keep pure domain logic independent from Klipper, Moonraker, OpenCV, filesystems, and network I/O.
- The host service owns camera capture, computer vision, bounded storage, and reporting.
- The Klippy extension owns printer state integration and schedules non-blocking work; it must not import OpenCV or block the Klipper reactor.
- Depend on ports/adapters: `CameraProvider`, `ToolchangerAdapter`, `ZProvider`, `StationStore`, `EvidenceStore`, and `OffsetWriter`.
- Support dynamic tool discovery and configurable reference tools. Never hard-code T0–T4 as the product model.
- Implement switch and Cartographer as separate Z providers with explicit sign/coordinate contracts and provider-specific validation.
- Keep measurement and application separate. Report-only is the default.
- Bind local services to loopback by default, bound all inputs and outputs, redact credentials, and disable cloud upload by default.

## Code and comment conventions

- Use English identifiers and type annotations. Public APIs require docstrings describing units, coordinate frame, sign, side effects, blocking behavior, failure modes, and safety preconditions.
- Comments explain *why*, invariants, evidence, compatibility, or hazards; do not narrate obvious syntax.
- Controlled prefixes are allowed: `SAFETY:`, `INVARIANT:`, `EVIDENCE:`, `COMPAT:`, and `TODO(issue-id):`.
- Every quantity crossing a boundary must have an explicit unit in its name or type. Avoid unqualified `offset`, `position`, `distance`, and `timeout` fields.
- Prefer small typed modules, dependency injection, deterministic pure functions, explicit reason codes, and machine-readable schemas.
- Do not add an unresolved TODO without an issue or phase reference and an acceptance condition.

## Phase workflow

For each phase:

1. Fetch and inspect the repository; verify a clean base.
2. Read the mandatory files and the phase contract.
3. Audit primary sources and evidence before designing behavior.
4. Create `phase/NN-short-name` from the reviewed base.
5. Write a bounded implementation plan and acceptance tests.
6. Implement only that phase; do not pre-build later phases.
7. Run unit, component, static, security, documentation, and fault-injection checks applicable to the phase.
8. Update both language versions of status, decisions, risks, traceability, test matrix, and the phase progress record.
9. Commit in English using Conventional Commits and push the phase branch. Never force-push shared branches.
10. Report exact commands, results, remaining risks, HIL requirements, commit, and remote branch. Do not merge to `main` until the supervisor gate passes.

Use GPT-5.6 Luna with medium reasoning for phase work unless a written decision changes the setting. Break work into focused tasks rather than compensating for an oversized prompt with a higher-cost model.

## Completion standard

A phase is complete only when its deliverables exist, acceptance tests pass, evidence and documentation are paired, status is truthful, and the commit is pushed. `PLANNED` is not completion. Physical capabilities may remain `REQUIRES_HIL`, but all offline work and a safe operator protocol must be complete first.
