# Imported evidence index

Imported under `evidence/imported/` on 2026-08-31. Source copies were compared by SHA-256 before commit; no secrets were found by the Phase 00 scan. Raw files are `OBSERVED`, immutable, report-only evidence.

| ID | Content | Count/status | Source |
|---|---|---|---|
| EVID-XY-001 | kTAMV CSV and companion report; 3 independent cycles, T0–T4 | 2 files; observed | All-Config experiments directory |
| EVID-Z-001 | Historical Z JSON, switch and Cartographer Touch | 21 files: 5 switch + 16 Cartographer; includes `WARNING` and `INVALID` | Two recorded All-Config backup locations |
| EVID-Z-INVALID-001 | `20260826-114524-081-z-switch-01.json` | `INVALID`, empty offsets, TMC ShortToSupply_A and cleanup failures | pre-resume backup |

The prior baseline said 20 Z files in one directory; the complete related evidence set is 21 after importing the separately located invalid run. Historical coordinates, temperatures, scale, tool names and tolerances are not product defaults.
