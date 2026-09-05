# Trạng thái dự án

- Dự án: **XYZ Klipper Tool**
- Trạng thái kho: Phase 02 được supervisor duyệt tại candidate `ce99ca14b4df5e870a79364ef188884c0394dc65`
- Mức sẵn sàng production: **CHƯA SẴN SÀNG**
- Phase hiện tại: Phase 03 — capture camera, calibration và framework detector
- Trạng thái phase: `NEEDS_WORK` — adapter OpenCV host bounded và kiểm tra candidate pixel archive đã IMPLEMENTED; 75 frame thật mới đã kiểm tra hash nhưng vẫn `WARNING`, chưa gán nhãn, chưa calibration và bị loại
- Cổng kế tiếp: Phase 03 vẫn `NEEDS_WORK`; còn thiếu ground truth tâm đã review cùng các session calibration/development/holdout độc lập đã gán nhãn, synthetic holdout không phải evidence reliability và hành vi vật lý vẫn `REQUIRES_HIL`
- Hành động vật lý trên máy in: bị chặn; mỗi lượt mới cần operator cho phép rõ ràng lại và preflight mới về trạng thái/home

## Sổ phase

| Phase | Trạng thái | Bằng chứng |
|---|---|---|
| 00 Quy tắc, nguồn, license, bằng chứng | `IMPLEMENTED` | Artifact governance song ngữ, manifest SHA-256 23 file, nhập 21 JSON Z, kiểm tra offline đạt |
| 01 Domain model, đơn vị, dấu, thống kê | `PASS` | Commit được supervisor duyệt `9d58fecb6cc19342c1bcd9dd62eafb8bf03c1a0d`; 16/16 test pin, coverage 95%, mọi gate offline nêu trên đạt; hành vi vật lý vẫn `REQUIRES_HIL` |
| 02 Adapter và simulator | `PASS` | Candidate `ce99ca14b4df5e870a79364ef188884c0394dc65` được supervisor duyệt; 27 test và coverage 91%; directory durability vẫn OPEN và hành vi vật lý `REQUIRES_HIL` |
| 03 Camera và pipeline thị giác | `NEEDS_WORK` | Đã triển khai adapter OpenCV host bounded cùng report/overlay candidate không calibration; hai session mới có 75 frame thật đã kiểm tra hash, tất cả `WARNING`/bị loại do thiếu ground truth/calibration; contour ROI chung vẫn mơ hồ (3–28); hành vi vật lý `REQUIRES_HIL` |
| 04 Điều phối X/Y theo chu kỳ độc lập | `PLANNED` | Chưa bắt đầu |
| 05 Z provider công tắc vật lý | `PLANNED` | Chưa bắt đầu |
| 06 Z provider Cartographer Touch | `PLANNED` | Chưa bắt đầu |
| 07 Giao dịch áp dụng có duyệt và rollback | `PLANNED` | Chưa bắt đầu |
| 08 Host API và service | `PLANNED` | Chưa bắt đầu |
| 09 Klipper extension và lệnh | `PLANNED` | Chưa bắt đầu |
| 10 Cài đặt, cập nhật, gỡ cài đặt | `PLANNED` | Chưa bắt đầu |
| 11 Tài liệu, bảo mật, cổng release | `PLANNED` | Chưa bắt đầu |
| 12 HIL canary có giám sát | `REQUIRES_HIL` | Chưa được cho phép |
