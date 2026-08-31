# Phase 01 — Mô hình miền, đơn vị, dấu và thống kê

## Phạm vi

Chỉ triển khai logic miền thuần túy, xác định được cho các đại lượng có kiểu, hợp đồng hệ tọa độ/dấu, định danh, kết quả đo riêng theo provider, verdict/mã lý do, chuyển trạng thái lượt chạy, thống kê bền vững, quyết định ngoại lệ, dữ liệu kế hoạch apply/freshness/rollback và schema trong bộ nhớ có phiên bản.

## Ngoài phạm vi

Không camera, Klipper, Moonraker, filesystem, network, service, installer, hardware adapter, I/O production, chuyển động máy, gia nhiệt, probing, đổi tool, restart, triển khai, apply cấu hình hoặc thực thi HIL. Bằng chứng lịch sử chỉ là fixture kiểm thử; không được trở thành giá trị mặc định của sản phẩm.

## Sản phẩm bàn giao

- Đại lượng kiểu millimetre, pixel, second và Celsius; vector, hệ tọa độ, quy ước dấu và chuyển đổi hai chiều.
- Định danh độc lập cho run, outer-cycle, tool-visit và frame-sample; các mô hình kết quả switch/Cartographer Touch tách biệt.
- Trạng thái claim/verdict, mã lý do tường minh và state machine lượt chạy xác định, fail-closed.
- Summary bền vững giữ raw, có số lượng valid/invalid/warning, mean, median, sample standard deviation, MAD, cận, range, uncertainty, drift và chính sách outlier đã khai báo; n=0 và n=1 là kết quả có kiểu.
- Kế hoạch apply, freshness và rollback không có side effect.
- Schema máy đọc được có phiên bản, kèm test round-trip và tương thích với field chưa biết.
- Test unit, table-driven, property/metamorphic và fault-case, gồm fixture bằng chứng kTAMV T3 đã làm sạch.

## Nguồn và giả định

Source ledger, evidence baseline, requirements và traceability của Phase 00 là đầu vào chi phối. Phase này không đưa ra claim bên ngoài mới. Các giá trị evidence hiện có vẫn gắn provenance và bất biến. Uncertainty bền vững được gắn nhãn rõ là output của estimator, không phải bảo đảm an toàn vật lý; thiếu mẫu tạo kết quả có kiểu. Semantics dấu/tọa độ của provider vẫn là hợp đồng tường minh và tương thích vật lý chưa xác định vẫn là `REQUIRES_HIL`.

## Test nghiệm thu

- Module miền chỉ import standard library Python, không phụ thuộc framework hay I/O.
- Mọi quantity qua boundary đều nêu unit; hợp đồng frame và sign có docstring cùng test chuyển đổi hai chiều.
- Kết quả switch và Cartographer Touch tách về cấu trúc; sample invalid không bao giờ vào estimator.
- Có coverage cho n=0, n=1, `INVALID`, `WARNING`, uncertainty, drift, loại outlier, transition bất hợp lệ, fingerprint cũ và rollback.
- Có coverage cho version schema, serialize round-trip, field lạ tương thích ngược và lỗi version không hỗ trợ.
- Parity Markdown song ngữ, link, secret, license, format, type/lint, unit/property/fault, coverage và artifact máy đọc được đều đạt.

## Ranh giới HIL và cổng

Phase này không thực hiện hành động vật lý và không thể xác lập an toàn vật lý. HIL vẫn bắt buộc cho dạy station theo máy, tương thích provider, envelope di chuyển, probing, trạng thái tool và xác nhận abort của operator. Hoàn tất dừng ở supervisor review trên nhánh đã push `phase/01-domain`; không merge vào `main` và không release.

## Chiến lược test

Chạy `python -m unittest discover -s tests -v`, kiểm tra import-boundary và schema, các kiểm tra lint/type/coverage khả dụng, toàn bộ checker governance Phase 00 và `git diff --check`. Ghi command, exit code, số lượng và hash artifact chính xác trong progress record và JSON test-run Phase 01.

## Tiêu chí đóng correction pass

Correction pass phải giữ cổng `NEEDS_WORK` trừ khi dependency mypy/pyright đã pin được cài đặt và chạy thành công. Contract test phải chạy cả hai Z provider, hierarchy và cô lập provider, validation finite/non-empty, rejection record tường minh, reference drift, required/type/enum/finite của schema, invariant freshness/apply/rollback và mọi negative path đã nêu.
