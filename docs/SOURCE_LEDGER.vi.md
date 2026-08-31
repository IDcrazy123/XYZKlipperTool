# Sổ nguồn

Ngày truy cập mọi dòng: 2026-08-31. Không sao chép implementation upstream.

| ID | URL | Phiên bản pin | Claim được hỗ trợ | License | Mơ hồ/theo dõi |
|---|---|---|---|---|---|
| SRC-001 | https://www.klipper3d.org/G-Codes.html | tài liệu hiện tại; commit TBD | bề mặt lệnh/query/probe | dự án Klipper GPL-3.0; điều khoản docs cần kiểm tra | Pin release trước Phase 09 |
| SRC-002 | https://www.klipper3d.org/Code_Overview.html | tài liệu hiện tại; commit TBD | reactor, extras, object/event | dự án Klipper GPL-3.0 | Đối chiếu commit pin |
| SRC-003 | https://github.com/Klipper3d/klipper | `f0892d82b0f1c1228454f09eb508eddde2250f4b` | hành vi source | GPL-3.0 | Cần fixture tương thích |
| SRC-004 | https://moonraker.readthedocs.io/en/latest/external_api/introduction/ | tài liệu hiện tại | HTTP/JSON-RPC/WebSocket cục bộ | cần kiểm tra license Moonraker trước reuse | Pin version |
| SRC-005 | https://github.com/TypQxQ/kTAMV | `72421f2d54da0de8701c4f84449c6e6b7d060301` | chỉ đối chiếu hành vi | GPL-3.0 | Không sao chép code |
| SRC-006 | https://github.com/TypQxQ/KTC | `b880e37a960c4746a370b7f6ac76a6a829430387` | hành vi adapter ứng viên | GPL-3.0 | Contract test trước adapter |
| SRC-007 | https://github.com/viesturz/klipper-toolchanger | `94756dfde9b729fd69f9b8780067821c5c99a528` | semantics adapter khác | GPL-3.0 | Kiểm tra quy ước dấu |
| SRC-008 | https://docs.cartographer3d.com/cartographer-probe/installation-and-setup/software-configuration/touch-calibration | trang hiện tại | luồng Touch và cảnh báo | chưa pin license/điều khoản docs | Snapshot trước HIL |
| SRC-009 | https://docs.opencv.org/4.12.0/d4/d70/tutorial_hough_circle.html | docs 4.12.0 | detector đường tròn ứng viên | dự án Apache-2.0; không sao chép code | Benchmark corpus |
| SRC-010 | https://docs.opencv.org/4.12.0/d4/d94/tutorial_camera_calibration.html | docs 4.12.0 | khái niệm calibration | dự án Apache-2.0; không sao chép code | Chốt model/metric |
| SRC-011 | https://developers.openai.com/api/docs/models/gpt-5.6-luna | trang hiện tại | cấu hình agent phase | điều khoản OpenAI | chỉ là hướng dẫn vận hành |

Việc mở nguồn là `OBSERVED`, không chứng minh tương thích phần cứng. Phải cập nhật URL, version và điểm chưa giải quyết trước implementation phụ thuộc.
