# Phase 03 — Capture camera, hiệu chuẩn và framework detector

## Phạm vi và cổng

Triển khai contract dữ liệu capture camera phía host có giới hạn, persistence calibration, plugin detector, diagnostics xác định và công cụ chia corpus. Phase này không tích hợp Klipper/Moonraker, I/O máy in, chuyển động, camera network, triển khai hay HIL.

## Deliverable

- Capture request/frame typed có giới hạn và validation URL/device local-only.
- Model/store calibration versioned với transform, residual, uncertainty, provenance và persistence atomic có checksum.
- Protocol detector và hai pipeline ứng viên xác định: blob connected-component và chấm điểm candidate dạng circle. Chỉ là ứng viên; không tuyên bố reliability.
- Inventory, label, source hash bất biến và split calibration/development/holdout tách theo session.
- Diagnostics xác định có calibration identity, frame age, residual, uncertainty và reason code typed.
- Schema song ngữ, test round-trip/fault/resource/security và artifact closure máy đọc được.

## Quyết định và giả định

Adapter JPEG host và kiểm tra pixel archive cần runtime OpenCV đã pin; pure domain vẫn độc lập OpenCV. Phase này không sao chép code upstream. 21 frame thật đều WARNING/unhomed và thiếu calibration/ground truth, nên chỉ là diagnostic phát triển, không chứng minh reliability detection hay độ chính xác vật lý.

Mọi dimension, encoded byte, retry, timeout, frame age, số candidate và chuỗi diagnostic đều hữu hạn. URL camera chỉ nhận scheme/host local được allowlist rõ; credential và path traversal bị từ chối. Origin calibration tách khỏi origin station và không có scale/origin/tolerance lịch sử làm default.

## Acceptance test

Test bound capture/decode, calibration malformed/non-finite, checksum/version/fault persistence, detector success/zero/multi-candidate/diagnostic, calibration mismatch/stale, chống leakage corpus, schema Draft 2020-12, type/lint/parity/secret/hash/link và import-boundary phải đạt. Đánh giá corpus thật đã sanitize còn thiếu và có trạng thái `NEEDS_WORK`; tương thích camera vật lý riêng biệt là `REQUIRES_HIL`.

## Kết thúc

Dừng ở `SUPERVISOR_REVIEW_PENDING`; báo lệnh, coverage, hash artifact, giới hạn evidence, rủi ro OPEN và HIL chính xác. Không bắt đầu Phase 04.
Phạm vi correction: adapter OpenCV JPEG chỉ phía host dùng identity ROI/calibration explicit, decode bounded, diagnostic chất lượng, plugin gradient/radial và contour/ellipse độc lập, cùng consensus fail-closed. Ảnh user vẫn bị loại khỏi claim reliability.

Kiểm tra candidate pixel từ archive là đường host-only tách riêng. Nó nhận source root/manifest explicit và output directory mới, kiểm tra hash nguồn và containment, xuất mọi hình học candidate cùng shape score hình học có bound và residual, đồng thời ghi overlay full-frame và development-ROI. Calibration không có, frame time là unknown khi thiếu, candidate không bao giờ được chấp nhận là nozzle, và collision output bị từ chối.
