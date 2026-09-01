# Sổ nguồn

Ngày truy cập mọi dòng: 2026-08-31. Mọi web page không có version được pin bằng content identity của repository sở hữu bên dưới. Không sao chép implementation upstream.

| ID | URL | Version/content identity đã pin | Claim được hỗ trợ | License | Mơ hồ/theo dõi |
|---|---|---|---|---|---|
| SRC-001 | https://www.klipper3d.org/G-Codes.html | repo sở hữu `Klipper3d/klipper`, commit `f0892d82b0f1c1228454f09eb508eddde2250f4b`; mở page 2026-08-31 | bề mặt lệnh G-Code/query/probe | GPL-3.0 (repo sở hữu) | Render docs không phải claim tương thích máy; pin v1 trước Phase 09 |
| SRC-002 | https://www.klipper3d.org/Code_Overview.html | repo sở hữu `Klipper3d/klipper`, commit `f0892d82b0f1c1228454f09eb508eddde2250f4b`; mở page 2026-08-31 | kiến trúc reactor, extras, object/event | GPL-3.0 (repo sở hữu) | Đối chiếu API với commit này trước adapter |
| SRC-003 | https://github.com/Klipper3d/klipper | commit `f0892d82b0f1c1228454f09eb508eddde2250f4b` (HEAD) | hành vi source | GPL-3.0 | Cần compatibility fixture; không suy ra HIL |
| SRC-004 | https://moonraker.readthedocs.io/en/latest/external_api/introduction/ | repo sở hữu `Arksine/moonraker`, commit `985c1d0bbeb90bc057d34a232c9dc3b05e0c6c8d` (HEAD); mở page 2026-08-31 | khái niệm HTTP/JSON-RPC/WebSocket cục bộ | GPL-3.0 (repo sở hữu) | Đã pin content; version client hỗ trợ là contract về sau |
| SRC-005 | https://github.com/TypQxQ/kTAMV | commit `72421f2d54da0de8701c4f84449c6e6b7d060301` (HEAD) | chỉ đối chiếu hành vi | GPL-3.0 | Không sao chép code; evidence nhập riêng |
| SRC-006 | https://github.com/TypQxQ/KTC | commit `b880e37a960c4746a370b7f6ac76a6a829430387` (HEAD) | hành vi adapter ứng viên | GPL-3.0 | Cần contract test trước adapter; không claim HIL |
| SRC-007 | https://github.com/viesturz/klipper-toolchanger | commit `94756dfde9b729fd69f9b8780067821c5c99a528` (HEAD) | semantics adapter khác | GPL-3.0 | Kiểm tra semantics dấu bằng fixture |
| SRC-008 | https://docs.cartographer3d.com/cartographer-probe/installation-and-setup/software-configuration/touch-calibration | repo sở hữu `Cartographer3D/docs`, commit `b0519c0f35ee3d77d7c4b7c16f414ad2e68f559a` (HEAD); mở page 2026-08-31 | luồng Touch và cảnh báo an toàn | GPL-3.0 (repo sở hữu) | Đã pin docs; firmware/model/output và HIL cần xác thực sau |
| SRC-009 | https://docs.opencv.org/4.12.0/d4/d70/tutorial_hough_circle.html | tag OpenCV `4.12.0`, commit deref `49486f61fb25722cbcf586b7f4320921d46fb38e`; mở page 2026-08-31 | detector đường tròn ứng viên | Apache-2.0 | Chỉ ứng viên; benchmark corpus |
| SRC-010 | https://docs.opencv.org/4.12.0/d4/d94/tutorial_camera_calibration.html | tag OpenCV `4.12.0`, commit deref `49486f61fb25722cbcf586b7f4320921d46fb38e`; mở page 2026-08-31 | khái niệm calibration | Apache-2.0 | Chốt model/metric; không claim chính xác vật lý |
| SRC-011 | https://developers.openai.com/api/docs/models/gpt-5.6-luna | mở page 2026-08-31; content identity là trang docs model hiện tại | cấu hình agent phase | OpenAI terms (điều khoản OpenAI) | Chỉ là hướng dẫn vận hành, không phải dependency |
| SRC-012 | https://netpbm.sourceforge.net/doc/pgm.html | trang đặc tả PGM Netpbm mở 2026-09-01; content identity là URL đặc tả đã nêu | header P5, kích thước, max-value và diễn giải raster | điều khoản tài liệu Netpbm; implementation first-party GPL-3.0-or-later | Chỉ tham chiếu format; không sao chép implementation |
| SRC-013 | https://github.com/IDcrazy123/XYZKlipperTool | commit project `ccd561aff55b0ed646de241d2665adf57fa4b183`; mở 2026-09-01 | heuristic connected-component/circularity và shape metrics do project viết | GPL-3.0-or-later | Không phải OpenCV Hough; chỉ synthetic đến khi có holdout thật có nhãn |

Nguồn sơ cấp đã được mở và đọc ngày 2026-08-31. Record chỉ xác lập provenance và claim được hỗ trợ; không xác lập tương thích phần cứng hay cho phép chạy vật lý.
