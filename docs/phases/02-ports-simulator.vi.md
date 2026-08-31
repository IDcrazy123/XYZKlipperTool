# Phase 02 — Port, fake adapter, simulator và persistence station

## Base và phạm vi

Phase này bắt đầu từ checkpoint `checkpoint-phase-01` đã supervisor duyệt tại commit `9417f69efbd57be0ca35241e65745f19c16ed15a`. Chỉ triển khai port có kiểu, fake xác định, workflow dữ liệu teach/show/clear station, fingerprint cấu hình, run lock và persistence hữu hạn trong thư mục tạm.

## Ngoài phạm vi

Không Klipper, Moonraker, OpenCV, network, service, installer, adapter phần cứng thật, config máy in, chuyển động, gia nhiệt, probing, đổi tool, restart, deploy, apply offset hay HIL thật. Fake không bao giờ hành động vật lý. Không biến tọa độ, dung sai, scale hay safe-Z lịch sử thành default.

## Kiến trúc

- `src/xyz_klipper_tool/ports/` sở hữu protocol interface và contract thuần.
- `src/xyz_klipper_tool/adapters/` sở hữu fake xác định và fault script.
- `src/xyz_klipper_tool/stations/` sở hữu value model station và use case teach/show/clear thuần.
- `src/xyz_klipper_tool/persistence/` sở hữu adapter filesystem; test chỉ dùng thư mục tạm.
- Domain vẫn độc lập với adapter và không import filesystem hay framework.

Các contract bắt buộc là `CameraProvider`, `VisionDetector`, `ToolchangerAdapter`, `ZProvider`, `StationStore`, `EvidenceStore`, `OffsetReader`, `OffsetWriter`, `Clock`, `RunLock`, cùng contract có kiểu cho printer-state/current-pose.

## Quyết định SAFE_Z

`SAFE_Z` là tùy chọn trong từ vựng lệnh nhưng nếu bỏ qua thì use case teach Phase 02 từ chối bằng reason có kiểu. Hệ thống chưa có clearance envelope được xác thực hay default lịch sử; không âm thầm coi Z hiện tại là clearance. Đây chỉ là quyết định data-contract và không cấp quyền di chuyển.

## Deliverable

- Port có kiểu, runtime-checking, docstring rõ unit, frame/sign, side effect, blocking, lỗi và điều kiện an toàn.
- Fake script xác định cho printer state/pose, tool, camera, detector, hai Z provider, store, clock và lock; có call recording và fault injection.
- Khám phá/chọn reference động với kiểm tra empty/duplicate/missing/ambiguous, mismatch active/detected, thứ tự xác định và giới hạn.
- Model station camera và từng Z provider tách namespace, có provenance pose hiện tại, revision, timestamp, fingerprint, safe approach và không có coordinate default.
- Use case show/teach/clear; clear cần preview và confirmation chính xác, không use case nào gọi `OffsetWriter`.
- Fingerprint cấu hình canonical có version, ổn định theo thứ tự, che secret và phát hiện thay đổi.
- Envelope/schema station có version, atomic persistence trong thư mục tạm, backup hữu hạn, checksum, recovery, migration và fixture power-loss.
- Lock run/teach/apply có ownership typed, cleanup xác định và giữ lỗi chính.
- Tài liệu song ngữ, kết quả test máy đọc được, manifest hash, cập nhật traceability/risk/status.

## Ma trận fault và test chấp nhận

1. Port từ chối value sai kiểu/provider, non-finite và ghi nhận không có hành động vật lý.
2. Tool discovery từ chối empty/duplicate/ambiguous/mismatch và trả thứ tự xác định có bound.
3. Camera và mỗi Z provider dùng namespace station riêng; tọa độ chỉ nhận từ input current-pose tường minh.
4. Bỏ SAFE_Z thì fail-closed bằng reason có kiểu; SAFE_Z hữu hạn được cung cấp thì giữ unit và provenance.
5. Show chỉ đọc; teach chỉ ghi qua `StationStore`; clear cần exact preview confirmation; nơi phù hợp đều từ chối fingerprint cũ.
6. Fingerprint ổn định khi đổi thứ tự mapping và không chứa secret; config đổi tạo mismatch.
7. Test persistence tiêm lỗi trước temp write, sau temp write, sau flush/fsync, trước replace, sau replace, khi backup rotation và với state corrupt/truncated/unsupported/checksum sai. State hợp lệ trước đó vẫn đọc được và temp/partial không thành current.
8. Test RunLock gồm double acquire, wrong release, release sau fault và conflict run/teach/apply với ownership có kiểu.
9. Import-boundary domain, schema Draft 2020-12, round-trip/migration, unit/property/metamorphic/fault, security/bounds, link/parity/secret/license, lint/format/type, coverage và diff đều đạt.

## Nguồn/bằng chứng và biên HIL

Không cần claim nguồn upstream mới cho các contract thuần này; ledger Phase 00, evidence baseline và master prompt chi phối. Atomic filesystem là assumption của adapter cục bộ được test, không phải bằng chứng an toàn máy in. Tương thích vật lý và travel an toàn vẫn `REQUIRES_HIL`; không được phép hành động vật lý.

## Gate và báo cáo

Phase dừng tại supervisor review trên `phase/02-ports-simulator`. Progress phải ghi lệnh, exit code, count, coverage, hash artifact, risk và `REQUIRES_HIL` còn lại một cách chính xác. Không tạo checkpoint tag trước supervisor PASS.
