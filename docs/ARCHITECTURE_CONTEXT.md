# Phase 00 architecture context

```text
Klippy extension --(bounded non-blocking contract)--> host service
      |                                                   |
printer state/tool discovery                         camera/CV/evidence/report
      |                                                   |
  ports: ToolchangerAdapter, ZProvider, StationStore, EvidenceStore, Offset*
                         \--> pure domain models and verdicts
```

The domain has no framework/I/O imports. Camera X/Y and Z providers are separate adapters. Stations are taught from current pose and versioned with configuration fingerprints. Measurement produces immutable evidence; apply is a separate transaction boundary. No production measurement code is introduced in Phase 00.
