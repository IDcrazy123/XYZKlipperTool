# Báo cáo dừng HIL một phần Phase 03

Trạng thái: `ABORTED_FAIL_CLOSED`; đây là hồ sơ bằng chứng, không phải supervisor PASS và không phải kết quả độ tin cậy.

## Các hành động đã hoàn tất

- Giữ nguyên một JPEG nguồn 8086 cũ dưới trạng thái `INVALID`, lý do `WRONG_CAMERA_SOURCE`; loại khỏi mọi corpus.
- Giữ nguyên đúng ba JPEG VoronBed của T1 dưới trạng thái `OBSERVED_LED_ON`; cả ba bị loại khỏi corpus LED-off và corpus thuật toán.
- Lượt tiếp tục T2 LED-off đã dừng trước khi chấp nhận di chuyển XY hoặc capture. Không có JPEG T2 và không tuyên bố kết quả T2.
- Lần `SET_LED` malformed đầu tiên, các lệnh LED runtime hợp lệ sau đó và lần dừng do tool ambiguous vẫn được giữ trong log operator/session bên ngoài artifact này.
- Không ghi lại source sản phẩm, thuật toán, JPEG raw hoặc byte metadata trong lượt phục hồi này.

## Điều kiện dừng

Truy vấn LED-off T2 ban đầu cho thấy mọi kênh `color_data` của T0–T4 đều đúng bằng zero, nhưng `toolchanger.tool_number=-1` mâu thuẫn với `detected_tool_number=2`; vì vậy capture bị từ chối fail-closed. Lượt tiếp tục sau đó cũng dừng bởi usage-limit gate. Truy vấn supervisor sau đó ngày 2026-09-05 ghi nhận máy đứng yên tại X170 Y20 Z40 hiển thị, T0 declared/detected và heater target bằng 0, nhưng `homed_axes` rỗng. Báo cáo này không cho phép lệnh home, chuyển động, camera, LED hoặc Moonraker nào.

## Xác minh

Manifest partial-run bất biến ghi nhận bốn JPEG raw: một `INVALID`, ba `OBSERVED_LED_ON`, zero frame LED-off được chấp nhận và zero frame T2. Byte size và SHA-256 của mọi raw đều khớp metadata kề bên. Tương thích camera vật lý và mọi việc dùng cho thuật toán vẫn là `REQUIRES_HIL`; Phase 03 vẫn `NEEDS_WORK`.

Điều kiện kế tiếp: cần operator cho phép rõ ràng mới, sau đó home thành công `xyz` và re-preflight đầy đủ trước mọi tiếp tục vật lý.
