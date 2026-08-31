# Threat model ban đầu

| Tài sản/biên | Nguy cơ | Kiểm soát/trạng thái |
|---|---|---|
| Chuyển động/gia nhiệt máy | lệnh cũ hoặc không an toàn | guard fail-closed; `PLANNED`; cần HIL |
| Cấu hình/evidence | ghi đè, sửa, mất | atomic write, raw bất biến, hash; `PLANNED` |
| API cục bộ | SSRF, traversal, input lớn, apply trái phép | loopback, allowlist, bound, xác nhận; `PLANNED` |
| Log/support bundle | lộ credential | redaction scan; `PLANNED` |
| Chuỗi cung ứng | code/dependency chưa review | source ledger, review license/provenance, pin; policy Phase 00 |

Ngoài phạm vi: mở remote, cloud upload, điều khiển đèn ESP32. Bật remote cần quyết định threat model mới.
