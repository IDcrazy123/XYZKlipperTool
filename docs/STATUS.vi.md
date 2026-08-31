# Trạng thái dự án

- Dự án: **XYZ Klipper Tool**
- Trạng thái kho: hoàn tất correction pass miền Phase 01 offline; chờ supervisor re-review
- Mức sẵn sàng production: **CHƯA SẴN SÀNG**
- Phase hiện tại: Phase 01 — mô hình miền, đơn vị, dấu và thống kê
- Cổng kế tiếp: supervisor review Phase 01 trước khi merge
- Hành động vật lý trên máy in: trạng thái kho hiện tại không cho phép

## Sổ phase

| Phase | Trạng thái | Bằng chứng |
|---|---|---|
| 00 Quy tắc, nguồn, license, bằng chứng | `IMPLEMENTED` | Artifact governance song ngữ, manifest SHA-256 23 file, nhập 21 JSON Z, kiểm tra offline đạt |
| 01 Domain model, đơn vị, dấu, thống kê | `NEEDS_WORK` | Test correction đạt; host chưa có mypy/pyright đã pin; hành vi vật lý vẫn `REQUIRES_HIL` |
| 02 Adapter và simulator | `PLANNED` | Chưa bắt đầu |
| 03 Camera và pipeline thị giác | `PLANNED` | Chưa bắt đầu |
| 04 Điều phối X/Y theo chu kỳ độc lập | `PLANNED` | Chưa bắt đầu |
| 05 Z provider công tắc vật lý | `PLANNED` | Chưa bắt đầu |
| 06 Z provider Cartographer Touch | `PLANNED` | Chưa bắt đầu |
| 07 Giao dịch áp dụng có duyệt và rollback | `PLANNED` | Chưa bắt đầu |
| 08 Host API và service | `PLANNED` | Chưa bắt đầu |
| 09 Klipper extension và lệnh | `PLANNED` | Chưa bắt đầu |
| 10 Cài đặt, cập nhật, gỡ cài đặt | `PLANNED` | Chưa bắt đầu |
| 11 Tài liệu, bảo mật, cổng release | `PLANNED` | Chưa bắt đầu |
| 12 HIL canary có giám sát | `REQUIRES_HIL` | Chưa được cho phép |
