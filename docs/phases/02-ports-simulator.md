# Phase 02 — Ports, fake adapters, simulator, and station persistence

## Base and scope

This phase starts from supervisor-approved checkpoint `checkpoint-phase-01` at commit `9417f69efbd57be0ca35241e65745f19c16ed15a`. It delivers only typed ports, deterministic fakes, station teaching/show/clear data workflows, configuration fingerprints, run locks, and bounded temporary-directory persistence.

## Non-goals

No real Klipper, Moonraker, OpenCV, network, service, installer, hardware adapter, printer configuration, motion, heating, probing, tool change, restart, deployment, offset apply, or HIL. Fakes never perform physical actions. No historical coordinate, tolerance, scale, or safe-Z value becomes a default.

## Architecture

- `src/xyz_klipper_tool/ports/` owns protocol interfaces and pure contracts.
- `src/xyz_klipper_tool/adapters/` owns deterministic fake implementations and fault scripts.
- `src/xyz_klipper_tool/stations/` owns station value models and pure teach/show/clear use cases.
- `src/xyz_klipper_tool/persistence/` owns a filesystem adapter; tests use only temporary directories.
- Domain code remains independent of these adapters and imports no filesystem or framework code.

Required contracts are `CameraProvider`, `VisionDetector`, `ToolchangerAdapter`, `ZProvider`, `StationStore`, `EvidenceStore`, `OffsetReader`, `OffsetWriter`, `Clock`, and `RunLock`, plus typed printer-state/current-pose contracts.

## SAFE_Z decision

`SAFE_Z` is optional in the command vocabulary but omitted SAFE_Z is rejected by the Phase 02 teach use cases with a typed reason. The system has no validated clearance envelope or historical default; current Z is not silently promoted to clearance. This is a data-contract decision only and does not authorize movement.

## Deliverables

- Typed, runtime-checking ports with explicit units, frame/sign, side effects, blocking, failure, and safety-precondition documentation.
- Deterministic scripted fakes for printer state/pose, tools, camera, detector, both Z providers, stores, clock, and lock with call recording and fault injection.
- Dynamic tool discovery/reference selection with duplicate, empty, missing, ambiguous, active/detected mismatch, deterministic-order, and bound checks.
- Provider-separated camera and Z station models with current-pose provenance, revision, timestamp, fingerprint, safe approach data, and no coordinate defaults.
- Show/teach/clear use cases; clear requires preview plus exact confirmation and none call `OffsetWriter`.
- Canonical versioned configuration fingerprint with secret redaction and change detection.
- Versioned station envelope/schema, atomic temporary-directory persistence, bounded backups, checksum validation, recovery, migration policy, and power-loss fixtures.
- Typed run/teach/apply lock ownership with deterministic cleanup and primary-error preservation.
- Bilingual docs, machine-readable test results, hash manifest, traceability/risk/status updates.

## Fault matrix and acceptance tests

1. Port contracts reject malformed/non-finite/wrong-provider values and record no physical action.
2. Tool discovery rejects empty/duplicate/ambiguous/mismatched state and returns deterministic bounded order.
3. Camera and each Z provider use separate station namespaces; station coordinates are accepted only from an explicit current-pose input.
4. Omitted SAFE_Z fails closed with a typed reason; supplied finite SAFE_Z is preserved with units and provenance.
5. Show is read-only; teach writes only through `StationStore`; clear requires exact preview confirmation; all three reject stale fingerprint where applicable.
6. Fingerprints are deterministic under mapping order and do not contain secrets; changed configuration produces a mismatch.
7. Persistence tests inject failure before temp write, after temp write, after flush/fsync, before replace, after replace, during backup rotation, and on corrupt/truncated/unsupported/checksum-invalid state. The prior valid state remains readable and temp/partial state is never current.
8. RunLock tests cover double acquire, wrong release, release after fault, and run/teach/apply conflict with typed ownership.
9. Domain import-boundary, schema Draft 2020-12 contract, round-trip/migration, unit/property/metamorphic/fault, security/bounds, link/parity/secret/license, lint/format/type, coverage, and diff checks pass.

## Source/evidence and HIL boundary

No new upstream source claim is needed for these pure contracts; the Phase 00 ledger, evidence baseline, and master prompt govern behavior. Filesystem atomicity is an explicitly tested local adapter assumption, not printer safety evidence. All physical compatibility and safe travel remain `REQUIRES_HIL`; no physical action is authorized.

## Gate and reporting

The phase stops at supervisor review on `phase/02-ports-simulator`. Progress records must contain exact commands, exit codes, counts, coverage, artifact hashes, risks, and remaining `REQUIRES_HIL`. No checkpoint tag is created before supervisor PASS.
