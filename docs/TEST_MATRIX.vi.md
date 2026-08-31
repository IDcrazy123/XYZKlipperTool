# Ma trận test Phase 00

| ID | Kiểm tra | Lệnh/cách | Kỳ vọng |
|---|---|---|---|
| TEST-001 | Cặp Markdown | `python scripts/check_markdown_pairs.py` | pass, không orphan |
| TEST-002 | Hash evidence | `Get-FileHash` so manifest | tất cả khớp |
| TEST-003 | Raw bất biến | so hash nguồn/đích | tất cả khớp |
| TEST-004 | Scan secret | `rg -n -i` mẫu credential | không phát hiện trong evidence |
| TEST-005 | Scan link | audit target local Markdown | không thiếu target |
| TEST-006 | License/provenance | review ledger/notices | row upstream pin hoặc follow-up rõ |
| TEST-007 | Ranh giới production code | inventory/search | không có `src/`, `klippy/`, mã đo |
