# Initial threat model

| Asset/boundary | Threat | Control/status |
|---|---|---|
| Printer motion/heaters | unsafe or stale command | fail-closed guards; `PLANNED`; HIL required |
| Configuration/evidence | accidental overwrite, tamper, loss | atomic writes, immutable raw, hashes; `PLANNED` |
| Local API | SSRF, traversal, oversized input, unauthorized apply | loopback, allowlists, bounds, confirmation; `PLANNED` |
| Logs/support bundles | credential leakage | redaction scan; `PLANNED` |
| Upstream supply chain | unreviewed copied code/dependency | source ledger, license/provenance review, pinning; Phase 00 policy |

Out of scope: remote exposure, cloud upload, ESP32 lighting control. Any remote enablement requires a new threat-model decision.
