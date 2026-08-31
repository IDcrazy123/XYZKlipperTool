# XYZ Klipper Tool — Quy tắc AI Agent

Đây là điểm vào bắt buộc cho mọi đóng góp của người hoặc AI. Phải đọc toàn bộ trước khi hành động. Bản tiếng Anh là [AGENTS.md](AGENTS.md).

## Mục tiêu và phạm vi

Xây dựng một dự án hiệu chuẩn Klipper độc lập, dễ mở rộng: đo offset X/Y của tool bằng camera và đo Z bằng công tắc vật lý hoặc Cartographer Touch. Vị trí đo phải được dạy từ vị trí hiện tại của máy bằng lệnh rõ ràng và lưu kèm nguồn gốc; không tọa độ máy nào được nhúng thành mặc định sản phẩm.

Kho mã hiện chưa sẵn sàng cho production. Không được coi kiểm thử offline là bằng chứng an toàn vật lý.

## Thứ tự đọc bắt buộc

1. `README.vi.md`
2. `PROJECT_BUILD_PROMPT.vi.md`
3. `docs/STATUS.vi.md`
4. `docs/EVIDENCE_BASELINE.vi.md`
5. `docs/SOURCE_MAP.vi.md`
6. Kế hoạch theo phase và các bản ghi quyết định được tạo về sau

## Ngôn ngữ và tính đồng bộ tài liệu

- Tiếng Anh là bản chuẩn cho mã, định danh, comment, docstring, schema, commit message và file `.md` không có hậu tố ngôn ngữ.
- Mỗi file Markdown do dự án viết phải có file tiếng Việt cùng tên với hậu tố `.vi.md`: `GUIDE.md` và `GUIDE.vi.md`.
- Phải cập nhật hai ngôn ngữ trong cùng commit. Ý nghĩa, cảnh báo an toàn, lệnh, đơn vị, nhãn trạng thái và liên kết phải tương đương.
- Thông báo bên thứ ba được sinh tự động và bằng chứng upstream chỉ được miễn khi đã ghi nguồn gốc và không bị chỉnh sửa.
- CI về sau phải kiểm tra cặp tài liệu song ngữ và từ chối file Markdown do dự án viết bị thiếu bản đối ứng.

## Kỷ luật bằng chứng

- Phân loại phát biểu thành `OBSERVED`, `IMPLEMENTED`, `PLANNED` hoặc `REQUIRES_HIL`.
- Không biến tọa độ, offset, ngưỡng, nhiệt độ, nguồn sáng hoặc dung sai của một máy trong lịch sử thành mặc định chung.
- Giữ nguyên dữ liệu thô bất biến. Báo cáo dẫn xuất phải chỉ rõ hash nguồn, công thức, đơn vị, hệ tọa độ, quy ước dấu, phiên bản phần mềm và timestamp.
- Không âm thầm loại outlier. Phải báo dữ liệu thô, mean, median, sample standard deviation khi đủ mẫu, MAD, range, lý do loại và trạng thái chấp nhận/từ chối.
- Nghiên cứu nguồn sơ cấp trước khi triển khai. Ghi URL chính xác, ngày truy cập, phiên bản/commit, kết luận được nguồn hỗ trợ và điểm chưa chắc chắn.
- Muốn sao chép mã upstream phải có kiểm tra license và nguồn gốc riêng. Đối chiếu hành vi không đồng nghĩa được phép sao chép mã.

## An toàn và quyền hạn

- Với tác vụ build/fix, được phép đọc, lập kế hoạch, sửa file trong phạm vi và chạy kiểm thử offline không phá hủy.
- Mọi chuyển động máy in, gia nhiệt, probe, đổi tool, restart firmware, áp dụng cấu hình, triển khai service hoặc HIL đều cần người vận hành phê duyệt rõ cho lượt đó.
- Vị trí đã lưu chỉ là dữ liệu, không chứng minh đường đi an toàn. Trước mỗi lượt vật lý phải kiểm tra homing, giới hạn, tool đang active, vị trí hiện tại, khoảng hở Z, heater, endstop/probe và đường abort.
- Thứ tự di chuyển an toàn thuộc provider và phải được kiểm chứng: nâng Z tại X/Y hiện tại, chỉ di chuyển X/Y sau khi đủ khoảng hở, sau đó tiếp cận trạm trong giới hạn hữu hạn.
- Dừng khi fingerprint cấu hình cũ, thiếu vị trí, trạng thái tool mơ hồ, camera lỗi, detector thiếu chắc chắn, probe/endstop không nhất quán, reference drift, timeout hoặc printer shutdown.
- Không tự chạy `SAVE_CONFIG`, không tự sửa offset production và không tự restart Klipper. Áp dụng kết quả là giao dịch riêng có preview, backup, validation, dữ liệu rollback và xác nhận người vận hành.
- Ánh sáng camera mặc định do người dùng cung cấp được xem là đủ. Đèn ESP32-C3/WS2812B là thiết bị tạm bên ngoài, không phải dependency hay đối tượng điều khiển của dự án.

## Ràng buộc kiến trúc

- Logic domain thuần không phụ thuộc Klipper, Moonraker, OpenCV, filesystem hay network I/O.
- Host service sở hữu camera capture, computer vision, lưu trữ hữu hạn và báo cáo.
- Klippy extension sở hữu tích hợp trạng thái máy và chỉ lập lịch công việc không blocking; không import OpenCV hoặc chặn reactor của Klipper.
- Phụ thuộc qua port/adapter: `CameraProvider`, `ToolchangerAdapter`, `ZProvider`, `StationStore`, `EvidenceStore` và `OffsetWriter`.
- Khám phá tool động và cho phép chọn reference tool. Không hard-code T0–T4 thành mô hình sản phẩm.
- Switch và Cartographer là hai Z provider riêng, có hợp đồng dấu/hệ tọa độ và validation theo provider.
- Tách hoàn toàn đo và áp dụng. Mặc định chỉ báo cáo.
- Service chỉ bind loopback mặc định, giới hạn mọi input/output, che thông tin xác thực và tắt cloud upload mặc định.

## Quy ước code và comment

- Dùng định danh tiếng Anh và type annotation. API public phải có docstring ghi đơn vị, hệ tọa độ, quy ước dấu, side effect, khả năng blocking, lỗi và điều kiện an toàn.
- Comment giải thích *tại sao*, invariant, bằng chứng, tương thích hoặc nguy cơ; không diễn giải lại cú pháp hiển nhiên.
- Cho phép các tiền tố kiểm soát: `SAFETY:`, `INVARIANT:`, `EVIDENCE:`, `COMPAT:` và `TODO(issue-id):`.
- Mọi đại lượng đi qua boundary phải có đơn vị rõ trong tên hoặc type. Tránh trường chung chung `offset`, `position`, `distance`, `timeout`.
- Ưu tiên module nhỏ có type, dependency injection, hàm thuần xác định, reason code rõ và schema máy đọc được.
- Không thêm TODO chưa giải quyết nếu không có issue/phase và điều kiện hoàn thành.

## Quy trình từng phase

Với mỗi phase:

1. Fetch và kiểm tra kho mã; xác nhận base sạch.
2. Đọc file bắt buộc và hợp đồng của phase.
3. Kiểm tra nguồn sơ cấp và bằng chứng trước khi thiết kế hành vi.
4. Tạo `phase/NN-short-name` từ base đã duyệt.
5. Viết kế hoạch hữu hạn và acceptance test.
6. Chỉ triển khai phase đó; không làm trước phase sau.
7. Chạy unit, component, static, security, documentation và fault-injection test phù hợp.
8. Cập nhật cả hai ngôn ngữ của status, decisions, risks, traceability, test matrix và nhật ký phase.
9. Commit tiếng Anh theo Conventional Commits và push nhánh phase. Không force-push nhánh dùng chung.
10. Báo cáo lệnh, kết quả, rủi ro còn lại, yêu cầu HIL, commit và nhánh remote. Không merge vào `main` trước khi qua cổng giám sát.

Dùng GPT-5.6 Luna với reasoning medium cho công việc từng phase, trừ khi có quyết định bằng văn bản thay đổi. Chia tác vụ tập trung thay vì bù cho prompt quá lớn bằng model đắt hơn.

## Tiêu chuẩn hoàn thành

Một phase chỉ hoàn thành khi đủ deliverable, acceptance test đạt, bằng chứng và tài liệu có cặp song ngữ, trạng thái trung thực, commit đã push. `PLANNED` không phải hoàn thành. Tính năng vật lý có thể còn `REQUIRES_HIL`, nhưng toàn bộ việc offline và quy trình vận hành an toàn phải hoàn tất trước.

