# Baseline yêu cầu Phase 00

| ID | Yêu cầu | Trạng thái | Nguồn/bằng chứng |
|---|---|---|---|
| REQ-IDENT-001 | Giữ danh tính độc lập và quyết định slug | `IMPLEMENTED` | ADR-0001 |
| REQ-STATION-001 | Dạy/lưu trạm camera/Z từ pose hiện tại; không dùng tọa độ lịch sử làm mặc định | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-PROVIDER-001 | Tách provider Z switch và Cartographer Touch | `PLANNED` | Master prompt; EVID-Z-001 |
| REQ-TOOL-001 | Khám phá tool động và chọn reference | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-SAMPLE-001 | Baseline ba outer pickup cycle độc lập và giữ phân cấp frame | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-EVID-001 | Giữ raw bất biến, hash, trạng thái và provenance | `IMPLEMENTED` | Import và manifest Phase 00 |
| REQ-STAT-001 | Báo thống kê robust và verdict invalid/warning rõ | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-APPLY-001 | Mặc định report-only; apply riêng có preview, backup, rollback | `PLANNED` | Master prompt; EVID-Z-001 |
| REQ-SAFE-001 | Fail closed khi state không an toàn/cũ; không hành động vật lý ngầm | `PLANNED` | AGENTS; tài liệu Klipper |
| REQ-SEC-001 | Mặc định loopback, giới hạn input, che secret, tắt cloud | `PLANNED` | Master prompt |
