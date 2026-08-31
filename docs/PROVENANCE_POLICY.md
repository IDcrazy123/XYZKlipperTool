# Clean-room and provenance policy

The project may read legacy ToolVision/All-Config material as requirements evidence and behavioral comparison. Raw imports are byte-preserving, sanitized only for secrets, immutable after import, and recorded in `evidence/manifests/`. No legacy source code, history, configuration default, or machine coordinate may be copied into product code. Any future upstream-derived code requires file-level attribution, pinned source, license approval, and a review record before merge.

Evidence summaries must cite source hash, formula, units, coordinate frame, sign convention, software version and timestamp. Secrets are excluded from public artifacts; exclusions and hashes are recorded. A source mismatch blocks dependent behavior until explained.
