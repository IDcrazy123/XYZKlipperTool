# Mốc bằng chứng

Tài liệu này lập chỉ mục các bằng chứng máy thật đã thúc đẩy XYZ Klipper Tool. Đây là dữ liệu đối chiếu, không phải mặc định sản phẩm. Phase 00 phải nhập bản sao đã loại dữ liệu nhạy cảm và bất biến vào kho này, tạo manifest SHA-256 và giữ nguyên các trường trạng thái gốc.

## Bằng chứng camera X/Y (`OBSERVED`)

Nguồn:

- `D:\Desktop\All-Config-Voron-main\Voron 5 Tool\extras\experiments\ktamv-xy-independent-cycles-20260831.csv`
- SHA-256: `f27715158d7a238509a6a2b20bead4b727723cfb59ef213a2a90615689130a6f`
- SHA-256 báo cáo đi kèm: `0cadc499af50ee21d6aa477447ced05d689622fcf4b882da16b30c60559b19e3`

Quy trình và bối cảnh đã quan sát:

- Ba chu kỳ pickup độc lập, mỗi chu kỳ chạy T0, T1, T2, T3, T4.
- Fixture không có lần đo T0 trả về ở cuối từng chu kỳ; kiểm tra drift mạnh hơn đó là `PLANNED` và `REQUIRES_HIL`.
- Tỷ lệ camera quan sát: `0.0570 mm/pixel`; RSD hiệu chuẩn: `6.3%`.
- Origin camera quan sát: `[168.716, 18.451]` và Z an toàn quan sát: `40 mm`; cả hai chỉ là dữ liệu lịch sử của một máy và bị cấm làm mặc định.
- Ánh sáng là nguồn sáng thông thường của camera do người dùng cung cấp. Vòng ESP32-C3/WS2812B ngoài là giải pháp tình thế và nằm ngoài phạm vi.
- Không candidate X/Y nào được tự động áp dụng.

Giá trị X/Y thô theo milimét, tương đối với tool tham chiếu:

| Chu kỳ | T0 | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| 1 | `(0.000, 0.000)` | `(+0.004, -0.078)` | `(+0.006, -0.130)` | `(+0.029, -0.073)` | `(+0.004, -0.078)` |
| 2 | `(+0.001, -0.026)` | `(+0.004, -0.078)` | `(+0.004, -0.078)` | `(+0.005, -0.104)` | `(+0.004, -0.078)` |
| 3 | `(+0.001, -0.026)` | `(+0.004, -0.078)` | `(+0.005, -0.104)` | `(+0.004, -0.078)` | `(+0.003, -0.052)` |

Các giá trị X của T3 cho thấy mean là chưa đủ: mean `+0.012667 mm`, median `+0.005 mm`. Hệ thống mới phải giữ mọi quan sát thô và báo thống kê robust, không âm thầm xóa giá trị cao.

## Bằng chứng Z (`OBSERVED`)

Thư mục nguồn:

`D:\Desktop\All-Config-Voron-main\Voron 5 Tool\extras\backups\pre-toolvision-ux-hil-20260826-161315\Generated-Data-ToolVision\tool-vision-history`

Thư mục lịch sử có 20 file lượt đo Z: 4 lượt công tắc vật lý và 16 lượt Cartographer Touch. Một lượt switch `INVALID` liên quan nằm trong backup pre-resume riêng được liệt kê bên dưới, nên bộ nhập đầy đủ có 21 file: 5 switch và 16 Cartographer Touch. Phải giữ lỗi; không được chỉ chọn giá trị trông có vẻ thành công.

Quan sát đại diện ở chế độ chỉ báo cáo:

- Lượt switch `20260825-094715-333-z-switch-01.json`, SHA-256 `e398dd88599aa05bc6143e2b37b8f199b3dab16ae2860974a0ef0c159df9243a`: T0 `0`, T1 `+0.114`, T2 `-0.384`, T3 `-0.186`, T4 `+0.090 mm`; reference return drift `+0.034 mm`; trạng thái `WARNING` vì chưa cấu hình giới hạn; `applied=false`.
- Lượt Cartographer `20260825-133944-202-z-cartographer_touch-01.json`, SHA-256 `570ff8de65a327f656e4656c24cf742db80d03e7d166930ed706eb1a49d3200c`: T0 `0`, T1 `+0.260`, T2 `-0.254`, T3 `-0.184`, T4 `+0.100 mm`; reference return drift `+0.020 mm`; trạng thái `WARNING`; `applied=false`.
- Lượt switch lỗi `20260826-114524-081-z-switch-01.json` ghi `TMC 'stepper_x' ... ShortToSupply_A`, offsets rỗng, cleanup lỗi và `INVALID`. Đây là bằng chứng sự cố và phục hồi phải là dữ liệu hạng nhất, tuyệt đối không được đưa vào trung bình candidate.

Giá trị production lịch sử và kết quả switch trước đây khác nhau do lực công tắc, vị trí đo, nhiệt độ và xác nhận bằng bản in. Vì vậy v1 phải giữ baseline riêng theo provider, không trộn mẫu switch và Cartographer vào cùng estimator.

## Quy trình bằng chứng bắt buộc cho XYZ Klipper Tool

1. Tách chu kỳ pickup độc lập bên ngoài khỏi các frame camera bên trong.
2. Quy trình X/Y mặc định là ba chu kỳ ngoài; mỗi chu kỳ pickup lại từng tool. Chuỗi nâng cao mục tiêu là reference → toàn bộ tool được chọn → reference trả về.
3. Khám phá tool động; T0–T4 chỉ là fixture đã quan sát.
4. Lấy pose an toàn và vị trí provider hiện tại qua lệnh/cấu hình khi chạy. Không cố định tọa độ camera, dock, probe, switch hay safe Z.
5. Ghi giá trị thô, timestamp, trạng thái tool, revision vị trí, fingerprint cấu hình, phiên bản phần mềm, nhiệt độ, định danh ảnh/calibration, lỗi và sự kiện cleanup.
6. Báo mean, median, sample SD chỉ khi có ít nhất hai điểm hợp lệ, MAD, range, reference drift, uncertainty và reason code kết luận rõ.
7. Giữ riêng phép đo switch và Cartographer. Ghi quy ước dấu và chỉ so với cùng semantics cấu hình sau khi test chứng minh mapping.
8. Kết quả chỉ để báo cáo đến khi giao dịch áp dụng riêng vượt qua kiểm tra freshness và an toàn.

## Giới hạn trạng thái

- Quan sát hiện có xác nhận yêu cầu và fixture; không xác nhận implementation mới.
- Camera X/Y và hai Z provider vẫn là `PLANNED` trong XYZ Klipper Tool.
- Mọi tuyên bố tương thích máy thật vẫn là `REQUIRES_HIL` cho đến khi canary có giám sát hoàn tất.
