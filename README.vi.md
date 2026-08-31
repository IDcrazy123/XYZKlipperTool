# XYZ Klipper Tool

XYZ Klipper Tool là dự án mới, xây dựng theo bằng chứng thực tế để hiệu chuẩn các đầu công cụ hoán đổi trên Klipper:

- tự động đo offset X/Y bằng camera;
- đo Z tùy chọn bằng công tắc vật lý hoặc Cartographer Touch;
- vị trí đo được nhập bằng lệnh và lưu lại, không cố định tọa độ theo một máy;
- mặc định chỉ báo cáo kết quả, thao tác áp dụng là một giao dịch riêng có duyệt;
- có adapter cho nhiều hệ toolchanger và phần cứng mở rộng về sau.

Kho này chủ ý khởi tạo quy tắc, bằng chứng và prompt triển khai trước khi viết mã production. Hiện tại **chưa an toàn để cài lên máy in**.

## Bắt đầu tại đây

1. Đọc [AGENTS.vi.md](AGENTS.vi.md).
2. Đọc [PROJECT_BUILD_PROMPT.vi.md](PROJECT_BUILD_PROMPT.vi.md).
3. Kiểm tra [docs/EVIDENCE_BASELINE.vi.md](docs/EVIDENCE_BASELINE.vi.md) và [docs/SOURCE_MAP.vi.md](docs/SOURCE_MAP.vi.md).
4. Tiếp tục từ [docs/STATUS.vi.md](docs/STATUS.vi.md).

Tài liệu tiếng Anh: [README.md](README.md).

## Định danh kho mã

- Tên hiển thị: **XYZ Klipper Tool**
- Đường dẫn cục bộ: `D:\Desktop\XYZKlipperTool`
- GitHub: <https://github.com/IDcrazy123/XYZKlipperTool>
- Nhánh mặc định: `main`

Kho ToolVision cũ chỉ là nguồn bằng chứng và tài liệu đối chiếu. Không được triển khai XYZ Klipper Tool bằng cách đổi tên, tiếp tục nhánh, hoặc chắp vá mã nguồn ToolVision.
