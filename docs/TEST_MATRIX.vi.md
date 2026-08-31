# Ma trận test Phase 00

| ID | Kiểm tra | Lệnh/cách | Kỳ vọng |
|---|---|---|---|
| TEST-001 | Cặp Markdown | `python scripts/check_markdown_pairs.py` | kiểm tra hai chiều đạt, lỗi ổn định theo path+lý do |
| TEST-009 | Fixture âm Markdown | `python scripts/test_markdown_pairs.py` | thiếu VI và thiếu EN đều fail trong root tạm; không còn fixture trong kho |
| TEST-010 | ID requirements/traceability | `python scripts/check_requirements_traceability.py` và `python scripts/test_requirements_traceability.py` | không thiếu/thừa/trùng hoặc lệch ID song ngữ; fixture âm fail trong root tạm |
| TEST-002 | Hash evidence | `Get-FileHash` so manifest | tất cả khớp |
| TEST-003 | Raw bất biến | so hash nguồn/đích | tất cả khớp |
| TEST-004 | Scan secret | `rg -n -i` mẫu credential | không phát hiện trong evidence |
| TEST-005 | Scan link | audit target local Markdown | không thiếu target |
| TEST-006 | License/provenance | review ledger/notices | row upstream pin hoặc follow-up rõ |
| TEST-007 | Ranh giới production code | inventory/search | không có `src/`, `klippy/`, mã đo |
| TEST-008 | Parity master prompt | `python scripts/check_master_prompt_parity.py` | đủ 18 mục, 42 heading và mọi code/command token |
