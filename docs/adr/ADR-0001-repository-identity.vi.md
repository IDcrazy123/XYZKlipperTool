# ADR-0001: Danh tính kho mã và package slug

- Trạng thái: `IMPLEMENTED` (quyết định Phase 00)
- Ngày: 2026-08-31

## Quyết định

Kho vẫn là dự án độc lập **XYZ Klipper Tool**. Slug Python/service là `xyz_klipper_tool` (tên phân phối `xyz-klipper-tool`). Implementation bắt đầu từ contract và bằng chứng đã làm sạch; không sao chép mã hay lịch sử ToolVision.

## Lý do và hệ quả

Slug viết thường, ổn định và khác dự án cũ. Giá trị máy lịch sử chỉ là bằng chứng. Mã tương lai phải giữ domain isolation và ranh giới an toàn Phase 00. ADR này không cho phép chuyển động máy, ghi cấu hình, triển khai hay HIL.

## Bằng chứng

Các file bootstrap và master prompt được kiểm tra ngày 2026-08-31. Trước đó chưa có commit; `main` là base được xem xét, ngoài các file bootstrap chưa commit.
