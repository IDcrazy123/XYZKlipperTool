# Chỉ mục bằng chứng đã nhập

Nhập vào `evidence/imported/` ngày 2026-08-31. Bản sao được so SHA-256 trước commit; scan Phase 00 không thấy secret. Raw là bằng chứng `OBSERVED`, bất biến, chỉ báo cáo.

| ID | Nội dung | Số lượng/trạng thái | Nguồn |
|---|---|---|---|
| EVID-XY-001 | CSV kTAMV và báo cáo; 3 cycle độc lập, T0–T4 | 2 file; observed | thư mục experiments All-Config |
| EVID-Z-001 | JSON Z lịch sử, switch và Cartographer Touch | 21 file: 5 switch + 16 Cartographer; có `WARNING` và `INVALID` | hai thư mục backup All-Config |
| EVID-Z-INVALID-001 | `20260826-114524-081-z-switch-01.json` | `INVALID`, offset rỗng, TMC ShortToSupply_A và cleanup lỗi | backup pre-resume |

Baseline trước nói 20 file Z trong một thư mục; bộ bằng chứng liên quan đầy đủ là 21 sau khi nhập lượt invalid ở vị trí riêng. Tọa độ, nhiệt độ, scale, tên tool và dung sai lịch sử không phải default sản phẩm.

## Lượt HIL một phần Phase 03

`evidence/hil/phase-03/partial-run-manifest.json` ghi nhận bốn JPEG raw từ hồ sơ canary bị gián đoạn: một frame T0 `INVALID/WRONG_CAMERA_SOURCE` và ba frame T1 `OBSERVED_LED_ON`, tất cả bị loại khỏi thuật toán/corpus. Không capture hoặc tuyên bố frame T2 nào. Lượt chạy dừng fail-closed vì nhận dạng tool ambiguous (`tool_number=-1`, `detected_tool_number=2`); kiểm tra supervisor sau đó cũng thấy `homed_axes` rỗng. Byte size và SHA-256 raw khớp metadata. Muốn tiếp tục cần operator cho phép rõ ràng mới và home thành công `xyz`.

Thư mục `picture/` do user tạo được inventory read-only trong `evidence/hil/phase-03/user-provided-picture-inventory.json` với provenance `USER_PROVIDED_UNLABELED`. 17 file gốc bị loại khỏi mọi corpus đã kiểm định cho tới khi supervisor review; còn thiếu session, ground-truth, tool, illumination, camera identity và capture timestamp.
