# Baseline yêu cầu Phase 00

Mỗi ID ổn định xuất hiện một lần và có ít nhất một tham chiếu `SRC-*`, `EVID-*` hoặc `ASSUMPTION`.

| ID | Yêu cầu | Trạng thái | Nguồn/bằng chứng |
|---|---|---|---|
| REQ-IDENT-001 | Giữ danh tính kho độc lập và package slug | `IMPLEMENTED` | ADR-0001 |
| REQ-CMD-001 | Giữ khả năng lệnh station, đo, báo cáo, apply và rollback của v1 | `PLANNED` | Master prompt; SRC-001 |
| REQ-STATION-001 | Dạy/lưu station camera/Z từ pose hiện tại; không dùng tọa độ lịch sử làm default | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-STATE-001 | Dùng claim state, run/cycle/visit/sample ID, station revision, fingerprint và calibration identity rõ ràng | `PLANNED` | Master prompt; ASSUMPTION: ID bất biến |
| REQ-TOOL-001 | Khám phá tool động và chọn reference | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-PROVIDER-001 | Tách switch và Cartographer Touch Z với contract rõ | `PLANNED` | Master prompt; EVID-Z-001; SRC-008 |
| REQ-MOTION-001 | Ép invariant homing, limits, active-tool, clearance, approach bounded, abort và recovery | `PLANNED` | AGENTS; SRC-001; ASSUMPTION: provider sở hữu envelope |
| REQ-SAMPLE-001 | Dùng ba outer pickup cycle độc lập và giữ phân cấp inner frame | `PLANNED` | EVID-XY-001 |
| REQ-STAT-001 | Báo mean, median, sample SD khi `n >= 2`, MAD, range, drift, uncertainty và reason verdict | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-OUTLIER-001 | Khai báo outlier policy trước đánh giá; giữ raw và tạo summary unfiltered/filtered | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-VISION-001 | Giới hạn camera/detection và loại frame cũ, mơ hồ, hỏng hoặc không hỗ trợ | `PLANNED` | Master prompt; SRC-009 |
| REQ-CORPUS-001 | Xây corpus gán nhãn tách session và benchmark phương pháp vision ứng viên | `PLANNED` | Master prompt; SRC-009; SRC-010 |
| REQ-PERSIST-001 | Ghi atomic có backup rotation và không sửa raw evidence hoàn tất | `PLANNED` | Master prompt; ASSUMPTION: filesystem hỗ trợ rename |
| REQ-SCHEMA-001 | Version schema, hỗ trợ migration/round-trip và fail closed với major không hỗ trợ | `PLANNED` | Master prompt; ASSUMPTION: schema version tăng đơn điệu |
| REQ-EVID-001 | Giữ raw evidence bất biến, hash, status, provenance, lỗi và cleanup event | `IMPLEMENTED` | Import Phase 00; EVID-Z-INVALID-001 |
| REQ-APPLY-001 | Mặc định report-only; apply riêng có preview, backup, xác nhận và rollback | `PLANNED` | Master prompt; EVID-Z-001 |
| REQ-FRESH-001 | Từ chối evidence stale, mismatch, invalid, warning hoặc config đổi khi apply | `PLANNED` | Master prompt; ASSUMPTION: fingerprint là authority freshness |
| REQ-SEC-001 | Bind loopback/Unix, che secret, chống SSRF/path traversal và tắt cloud mặc định | `PLANNED` | Master prompt; ASSUMPTION: mặc định local-only |
| REQ-RESOURCE-001 | Giới hạn body/image/history/job/retry/queue/selector/string/number và pin dependency | `PLANNED` | Master prompt; ASSUMPTION: limit cấu hình là hữu hạn |
| REQ-PORT-001 | Domain độc lập và có port/adapter yêu cầu, fake trước hardware | `PLANNED` | Master prompt; SRC-002 |
| REQ-PORT-002 | Định nghĩa boundary có kiểu cho printer-state/current-pose, clock, lock, store, reader và writer với contract side effect rõ | `IMPLEMENTED` | Master prompt; ASSUMPTION: port là boundary đảo chiều phụ thuộc |
| REQ-SIM-001 | Có fake xác định, scripted, dynamic tool selection và fault injection nhưng không hành động vật lý | `IMPLEMENTED` | Master prompt; EVID-XY-001 |
| REQ-STATION-002 | Teach/show/clear station tách provider từ current pose tường minh; bỏ SAFE_Z thì fail closed | `IMPLEMENTED` | Master prompt; ASSUMPTION: không có clearance default được xác thực |
| REQ-PERSIST-002 | Lưu state station có version, atomic, checksum, backup hữu hạn, recovery và fail closed khi corrupt | `IMPLEMENTED` | Master prompt; ASSUMPTION: contract rename/fsync của filesystem |
| REQ-LOCK-001 | Từ chối conflict ownership run/teach/apply và cleanup lock xác định | `IMPLEMENTED` | Master prompt; ASSUMPTION: một owner cục bộ hoạt động |
| REQ-NONBLOCK-001 | Giữ camera/network/filesystem ngoài Klipper reactor và phối hợp bounded | `PLANNED` | SRC-002; SRC-003 |
| REQ-INSTALL-001 | Install/update/rollback/uninstall idempotent, dry-run, scope-checked, không phá hủy mặc định | `PLANNED` | Master prompt; ASSUMPTION: không purge ngầm |
| REQ-OPS-001 | Có evidence, diagnostic, support redaction, tài liệu và progress/reporting record chính xác | `PLANNED` | Master prompt; ASSUMPTION: vận hành report-only |
| REQ-HIL-001 | Giữ tương thích vật lý và production readiness `REQUIRES_HIL` tới khi canary giám sát đạt | `REQUIRES_HIL` | Master prompt; EVID-Z-INVALID-001 |
