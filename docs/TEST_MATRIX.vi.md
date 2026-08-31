# Ma trận test Phase 00

| ID | Kiểm tra | Lệnh/cách | Kỳ vọng |
|---|---|---|---|
| TEST-001 | Cặp Markdown | `python scripts/check_markdown_pairs.py` | kiểm tra hai chiều đạt, lỗi ổn định theo path+lý do |
| TEST-009 | Fixture âm và exemption Markdown | `python scripts/test_markdown_pairs.py` | thiếu VI, thiếu EN và orphan trong artifacts đều fail; Markdown raw evidence/imported được miễn; không còn fixture trong kho |
| TEST-010 | ID requirements/traceability | `python scripts/check_requirements_traceability.py` và `python scripts/test_requirements_traceability.py` | không thiếu/thừa/trùng hoặc lệch ID song ngữ; fixture âm fail trong root tạm |
| TEST-011 | Field pin/license source ledger | `python scripts/check_source_ledger.py` và `python scripts/test_source_ledger.py` | mỗi row song ngữ có URL, access/content identity, claim, license rõ và không placeholder cấm |
| TEST-012 | License artifact chuẩn | `python scripts/check_license_artifact.py` | heading/version GPL-3.0, disclaimer bảo hành/trách nhiệm, marker cuối, ending và SHA-256 chuẩn hóa đạt |
| TEST-002 | Hash evidence | `Get-FileHash` so manifest | tất cả khớp |
| TEST-003 | Raw bất biến | so hash nguồn/đích | tất cả khớp |
| TEST-004 | Scan secret | `rg -n -i` mẫu credential | không phát hiện trong evidence |
| TEST-005 | Scan link | audit target local Markdown | không thiếu target |
| TEST-006 | License/provenance | review ledger/notices | row upstream pin hoặc follow-up rõ |
| TEST-007 | Ranh giới production code | inventory/search | không có `src/`, `klippy/`, mã đo |
| TEST-008 | Parity master prompt | `python scripts/check_master_prompt_parity.py` | đủ 18 mục, 42 heading và mọi code/command token |
