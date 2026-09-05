# Bằng chứng HIL Phase 03 — 2026-09-05

## Kết quả

`WARNING` / dừng fail-closed tại biên an toàn sau khi gắn T1 và căn chỉnh tới station. Operator xác nhận `T0_LED`–`T4_LED` là LED nozzle hướng từ trên xuống theo từng tool, không phải nguồn sáng camera. Sau xác nhận này không phát lệnh đổi tool, chuyển động hay capture nào nữa. Thiết bị ESP32-C3/WS2812B không bị điều khiển.

## Hành động được cho phép và đã thực hiện

Quyền cho phép bao gồm `G28`, đổi tool qua provider trong giới hạn, chuyển động trong giới hạn và station theo lượt X=170 mm, Y=20 mm, Z=40 mm. Các lệnh đã thực hiện là `GET_POSITION`, `STATUS`, `G28`, `G91`, `G1 Z30 F900`, `G90`, `G1 X170 Y20 F1800`, `G1 Z40 F600`, `T0`, các lệnh `SET_LED` runtime, `T1` qua provider, `G1 X170 Y20 F1800` và `G1 Z40 F600`. Bộ đầu tiên của T0 tạo 9 snapshot VoronBed raw: 3 LED tắt, 3 yêu cầu LOW và 3 yêu cầu MEDIUM. Bộ LOW/MEDIUM nay được phân loại `OBSERVED_TOOL_LED_TOP_DOWN`; cả 9 lần thử T0 là `WARNING/METADATA_INCOMPLETE` và bị loại khỏi corpus chấp nhận cho ánh sáng camera. Không capture frame T1–T4.

Endpoint camera dùng đúng là `http://192.168.1.43/webcam/?action=snapshot`. UID VoronBed là `48efbfd8-83c8-488a-9fb8-b409905e808b`; fingerprint định danh nguồn được ghi trong `run-manifest.json`. File raw và metadata từng frame nằm trong thư mục này; byte JPEG raw không bị sửa sau capture.

## Trạng thái quan sát cuối

Ở truy vấn cuối, Klipper/Moonraker ready và connected, `homed_axes=xyz`, toolchanger ready với tool khai báo và phát hiện đều là `tool T1` / số 1, vị trí gcode là [170, 20, 40] mm, vị trí toolhead là [169.841, 19.805, 40.236] mm. Target mọi heater đều 0 °C. Mọi kênh `color_data` của T0–T4 đều chính xác [0, 0, 0, 0]. Không chạy `SAVE_CONFIG`, apply offset, probing, gia nhiệt, restart, sửa production config hay deployment.

## Số lượng và hash bằng chứng

- 9 JPEG sample raw; 9 metadata từng frame; 0 frame được chấp nhận vào camera corpus.
- T0: 3 warning LED tắt, 3 warning yêu cầu LOW được phân loại lại là LED tool hướng từ trên xuống, 3 warning yêu cầu MEDIUM được phân loại lại tương tự.
- T1/T2/T3/T4: 0 frame.
- Snapshot preflight: 238.425 byte, SHA-256 `f5e50ff5fad44a266fd9931e40c6f202a6cbfe5bc3d6952216fc810e98da8898`.
- Tổng byte sample raw: 2.385.626. Manifest đầy đủ là `run-manifest.json`.

Lượt này không xác lập tương thích nguồn sáng camera, độ tin cậy detector hay an toàn vật lý ngoài các hành động supervised đã quan sát. Lượt sau cần operator cho phép rõ ràng mới và phải xác định nguồn sáng camera thực trước khi capture.
