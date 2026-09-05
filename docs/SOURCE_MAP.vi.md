# Bản đồ nguồn sơ cấp

Trạng thái: `OBSERVED` khi bootstrap kho ngày 2026-08-31. Phase 00 phải mở lại từng nguồn, pin phiên bản/commit phù hợp và ghi mọi hành vi đã thay đổi trước khi triển khai.

| Lĩnh vực | Nguồn sơ cấp | Phạm vi được hỗ trợ | Việc bắt buộc tiếp theo |
|---|---|---|---|
| Klipper G-Code và probing | <https://www.klipper3d.org/G-Codes.html> | Tên lệnh và hành vi probe/query chính thức | Pin phiên bản Klipper hỗ trợ bởi v1 và kiểm tra lệnh tồn tại |
| Kiến trúc Klipper host extension | <https://www.klipper3d.org/Code_Overview.html> | `klippy/extras`, object lookup, event handler, ràng buộc reactor, status contract | Kiểm tra commit Klipper được hỗ trợ; cấm xử lý camera blocking trong reactor |
| Mã nguồn Klipper | <https://github.com/Klipper3d/klipper> | Hành vi API chưa được tài liệu public mô tả đủ | Gắn mỗi compatibility shim với commit và fixture kiểm thử |
| Moonraker external API | <https://moonraker.readthedocs.io/en/latest/external_api/introduction/> | HTTP, JSON-RPC, sự kiện/phản hồi WebSocket, Unix socket cục bộ | Định nghĩa client contract theo phiên bản, timeout, xác thực và reconnect |
| kTAMV upstream | <https://github.com/TypQxQ/kTAMV> | Đối chiếu hành vi tách camera/server và workflow người vận hành | Ghi commit chính xác; không sao chép implementation trước khi kiểm tra license/nguồn gốc |
| KTC v2 | <https://github.com/TypQxQ/KTC> | Một adapter toolchanger ứng viên và hành vi lưu trạng thái | Ghi phiên bản hỗ trợ chính xác và tạo contract test bằng trạng thái giả |
| Klipper Toolchanger | <https://github.com/viesturz/klipper-toolchanger> | Adapter khác; semantics tool/status/offset động | Pin commit docs/source và kiểm tra quy ước dấu bằng fixture |
| Hiệu chuẩn Cartographer Touch | <https://docs.cartographer3d.com/cartographer-probe/installation-and-setup/software-configuration/touch-calibration> | Luồng lệnh provider và cảnh báo an toàn vật lý | Chụp snapshot tài liệu, kiểm tra firmware và output lệnh trước HIL |
| OpenCV Hough circles | <https://docs.opencv.org/4.12.0/d4/d70/tutorial_hough_circle.html> | Một kỹ thuật phát hiện đường tròn ứng viên | Chỉ coi là ứng viên, benchmark với corpus nozzle đã gán nhãn, loại nếu bằng chứng không đạt |
| OpenCV camera calibration | <https://docs.opencv.org/4.12.0/d4/d94/tutorial_camera_calibration.html> | Khái niệm hiệu chuẩn và cảnh báo suy biến | Định nghĩa model hiệu chuẩn thực tế và metric chấp nhận từ frame đại diện |
| GPT-5.6 Luna | <https://developers.openai.com/api/docs/models/gpt-5.6-luna> | Agent theo phase tiết kiệm chi phí theo yêu cầu và reasoning hỗ trợ | Dùng `gpt-5.6-luna`, reasoning `medium`, trừ khi ADR ghi lý do đo được để đổi |

## Chính sách nguồn

1. Ưu tiên tài liệu chính thức hoặc kho upstream của chủ sở hữu.
2. Issue chỉ dùng để hình thành giả thuyết; không coi comment trong issue là đặc tả.
3. Ghi URL, thời điểm truy cập, phiên bản/commit, kết luận nguồn hỗ trợ, điểm xung đột và license.
4. Nếu tài liệu khác hành vi quan sát, giữ cả hai, tái hiện bằng simulator hoặc HIL đã duyệt, và chặn triển khai đến khi giải quyết contract.
5. Không nguồn nào được dùng để hợp thức hóa tọa độ mặc định theo một máy. Vị trí phải được dạy bằng lệnh.

## Provenance bằng chứng HIL

Báo cáo và manifest partial-run Phase 03 là hồ sơ operator first-party, không phải nguồn upstream. Chúng giữ endpoint camera, timestamp, trạng thái printer/tool và hash file raw đã quan sát; chúng không chứng minh tương thích camera hay an toàn vật lý. Lượt chạy đã dừng fail-closed và cần cho phép mới cùng home thành công `xyz` trước khi tiếp tục. Inventory `picture/` do user tạo là `USER_PROVIDED_UNLABELED`, read-only, đã ghi hash và bị loại cho tới supervisor review.
