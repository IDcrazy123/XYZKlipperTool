# Phase 03 — Camera capture, calibration, and detector framework

## Scope and gate

Implement bounded host-side camera data contracts, calibration persistence, detector plugins, deterministic diagnostics, and corpus split tooling. This phase has no Klipper/Moonraker integration, printer I/O, motion, network camera, deployment, or HIL.

## Deliverables

- Typed bounded capture request/frame and local-only URL/device validation.
- Versioned calibration model/store with transform, residual, uncertainty, provenance, and checksummed atomic persistence.
- Detector protocol and two deterministic candidate pipelines: connected-component blob and circle-like candidate scoring. They are candidates only; no reliability claim is made.
- Immutable corpus inventory, labels, source hashes, and session-separated calibration/development/holdout split.
- Bounded deterministic diagnostics carrying calibration identity, frame age, residual, uncertainty, and typed reason codes.
- Paired schemas, round-trip/fault/resource/security tests, and machine-readable closure artifact.

## Decisions and assumptions

The host JPEG adapter and archived pixel inspection require the pinned OpenCV runtime; the pure domain remains OpenCV-independent. This phase does not copy upstream code. The 21 real frames are WARNING/unhomed and lack calibration/ground truth, so they are development diagnostics only and cannot establish detection reliability or physical accuracy.

All dimensions, encoded bytes, retries, timeouts, frame age, candidate count, and diagnostic strings are bounded. Camera URLs accept only explicitly allowlisted local schemes/hosts; credentials and path traversal are rejected. Calibration origin is separate from station origin and no historical scale/origin/tolerance is a default.

## Acceptance tests

Capture/decode bounds, malformed/non-finite calibration, persistence checksum/version/fault recovery, detector success/zero/multi-candidate/diagnostic paths, calibration mismatch/staleness, corpus leakage prevention, schema Draft 2020-12 validation, type/lint/parity/secret/hash/link checks, and import-boundary checks pass. The missing sanitized real-corpus evaluation is `NEEDS_WORK`; physical camera compatibility is separately `REQUIRES_HIL`.

## Exit

Stop at `SUPERVISOR_REVIEW_PENDING`; report exact commands, coverage, artifact hashes, evidence limitations, OPEN risks, and HIL boundary. Do not begin Phase 04.
Correction scope: the host-only OpenCV JPEG adapter now uses explicit ROI/calibration identity, bounded decode, quality diagnostics, independent gradient/radial and contour/ellipse plugins, and fail-closed consensus. User-provided images remain excluded from reliability claims.

The archived pixel candidate inspection is a separate host-only path. It accepts explicit source roots/manifests and a new output directory, validates source hashes and containment, emits all candidate geometry with bounded geometric shape scores and residuals, and writes full-frame plus development-ROI overlays. Calibration is unavailable, frame time is unknown when absent, candidates are never accepted as nozzles, and output collisions are rejected.
