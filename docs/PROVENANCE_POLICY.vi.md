# Chính sách clean-room và provenance

Có thể đọc tài liệu ToolVision/All-Config cũ làm bằng chứng yêu cầu và đối chiếu hành vi. Raw import giữ nguyên byte, chỉ làm sạch secret, bất biến sau import và ghi trong `evidence/manifests/`. Không sao chép source, history, default cấu hình hay tọa độ máy cũ vào product code. Code upstream tương lai cần attribution từng file, source pin, duyệt license và record review trước merge.

Tóm tắt bằng chứng phải ghi hash nguồn, công thức, đơn vị, hệ tọa độ, quy ước dấu, phiên bản phần mềm và timestamp. Secret loại khỏi artifact công khai; việc loại và hash phải được ghi. Mismatch nguồn sẽ chặn behavior phụ thuộc cho tới khi giải thích được.
