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
| TEST-013 | unit/property/fault miền Phase 01 | `set PYTHONPATH=src; python -m unittest discover -s tests -v` | toàn bộ test miền, statistics, provider, schema, evidence-fixture đạt |
| TEST-014 | boundary import Phase 01 | scan import tĩnh của `src/xyz_klipper_tool/domain` | không import framework, filesystem, network hoặc service |
| TEST-015 | artifact schema Phase 01 | parse JSON schema và test codec schema | artifact version 1 và round-trip/tương thích ngược đạt |
| TEST-016 | contract schema Phase 01 | `set PYTHONPATH=src; python -m unittest tests.test_schema -v` | schema cả hai provider kiểm tra required/const/enum/finite và fault codec đạt |
| TEST-017 | coverage Phase 01 | `python -m coverage run -m unittest discover -s tests; python -m coverage report -m` | 16 test đạt; tổng coverage 95% |
| TEST-018 | type-check Phase 01 đã pin | venv cô lập; `python -m mypy`; `pyright` theo requirements đã pin | PASS: mypy và pyright không lỗi |
| TEST-019 | contract port/fake/station Phase 02 | `PYTHONPATH=src; python -m unittest discover -s tests -v` | port, fake xác định, tool động, workflow station và cô lập writer đạt |
| TEST-020 | ma trận fault persistence Phase 02 | `PYTHONPATH=src; python -m unittest tests.test_phase02 -v` | fault temp/flush/replace, corrupt, checksum, version và backup fail closed |
| TEST-021 | schema và fingerprint Phase 02 | jsonschema Draft 2020-12 đã pin cùng test fingerprint | contract envelope station, ordering canonical, redaction và phát hiện đổi đạt |
