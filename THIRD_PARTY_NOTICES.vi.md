# Thông báo bên thứ ba

Phase 00 không sao chép source upstream. Nếu phase sau phân phối hoặc dẫn xuất từ component, phải giữ notice và attribution theo license đã ghi.

| Component | Identity đã pin | License | Cách dùng/provenance |
|---|---|---|---|
| Klipper và docs Klipper | `f0892d82b0f1c1228454f09eb508eddde2250f4b` | GPL-3.0 | tham chiếu lệnh/kiến trúc; không sao chép code |
| Moonraker và API docs | `985c1d0bbeb90bc057d34a232c9dc3b05e0c6c8d` | GPL-3.0 | tham chiếu API; không sao chép code |
| Cartographer docs | `b0519c0f35ee3d77d7c4b7c16f414ad2e68f559a` | GPL-3.0 | tham chiếu Touch; không sao chép code |
| OpenCV docs/source identity | tag `4.12.0`, deref `49486f61fb25722cbcf586b7f4320921d46fb38e` | Apache-2.0 | tham chiếu CV ứng viên; không sao chép code |
| kTAMV | `72421f2d54da0de8701c4f84449c6e6b7d060301` | GPL-3.0 | đối chiếu hành vi/provenance evidence |
| KTC | `b880e37a960c4746a370b7f6ac76a6a829430387` | GPL-3.0 | đối chiếu adapter ứng viên |
| klipper-toolchanger | `94756dfde9b729fd69f9b8780067821c5c99a528` | GPL-3.0 | đối chiếu adapter ứng viên |

Trước release phải thêm copyright holder, URL chính xác, thay đổi, toàn văn license và notice dependency cho material thực sự phân phối. Tương thích phần cứng vẫn `REQUIRES_HIL`.
## opencv-python-headless 4.14.0.94

Chỉ dùng bởi `vision/jpeg_adapter.py` phía host để decode JPEG bounded và phân tích ảnh. Python wrapper có license MIT; OpenCV có Apache-2.0. Các notice third-party đi kèm vẫn áp dụng. Không sao chép implementation upstream.
