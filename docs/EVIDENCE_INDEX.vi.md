# Chỉ mục bằng chứng đã nhập

Nhập vào `evidence/imported/` ngày 2026-08-31. Bản sao được so SHA-256 trước commit; scan Phase 00 không thấy secret. Raw là bằng chứng `OBSERVED`, bất biến, chỉ báo cáo.

| ID | Nội dung | Số lượng/trạng thái | Nguồn |
|---|---|---|---|
| EVID-XY-001 | CSV kTAMV và báo cáo; 3 cycle độc lập, T0–T4 | 2 file; observed | thư mục experiments All-Config |
| EVID-Z-001 | JSON Z lịch sử, switch và Cartographer Touch | 21 file: 5 switch + 16 Cartographer; có `WARNING` và `INVALID` | hai thư mục backup All-Config |
| EVID-Z-INVALID-001 | `20260826-114524-081-z-switch-01.json` | `INVALID`, offset rỗng, TMC ShortToSupply_A và cleanup lỗi | backup pre-resume |

Baseline trước nói 20 file Z trong một thư mục; bộ bằng chứng liên quan đầy đủ là 21 sau khi nhập lượt invalid ở vị trí riêng. Tọa độ, nhiệt độ, scale, tên tool và dung sai lịch sử không phải default sản phẩm.
