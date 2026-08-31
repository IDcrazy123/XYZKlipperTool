# ADR-0001: Repository identity and package slug

- Status: `IMPLEMENTED` (Phase 00 decision)
- Date: 2026-08-31

## Decision

The project remains the independent repository **XYZ Klipper Tool**. The Python package/service slug is `xyz_klipper_tool` (distribution name `xyz-klipper-tool`). The implementation starts from contracts and sanitized evidence; no ToolVision source or history is copied.

## Rationale and consequences

The slug is lowercase, stable, and distinct from the legacy project. Historical machine values remain evidence only. Future code must preserve domain isolation and the Phase 00 safety boundaries. This ADR does not authorize printer motion, configuration writes, deployment, or HIL.

## Evidence

Repository bootstrap files and the master prompt, inspected 2026-08-31. No prior commit existed; `main` was the clean reviewed base except for uncommitted bootstrap files.
