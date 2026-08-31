# Kế hoạch Phase 00 — Governance, audit nguồn, license và nhập evidence

## Phạm vi

Thiết lập nền governance và evidence cho XYZ Klipper Tool: parity tài liệu song ngữ, provenance nguồn/license, traceability requirements, nhập evidence bất biến đã làm sạch, bối cảnh threat/risk và kiểm tra offline tái lập được.

## Ngoài phạm vi

Không viết mã đo production, không chuyển động máy, gia nhiệt, probe, đổi tool, restart firmware, apply cấu hình, triển khai service hay chạy HIL. Tọa độ, offset, nhiệt độ, camera scale, số tool và dung sai lịch sử chỉ là evidence.

## Deliverable

- Danh tính kho, quyết định GPL-3.0-or-later cho first-party và license artifact đầy đủ.
- 24 requirements ổn định và traceability matrix song ngữ một-một.
- Source ledger pin, third-party notices và clean-room/provenance policy.
- 2 file evidence X/Y và 21 JSON Z, gồm `WARNING` và `INVALID`, có manifest SHA-256.
- Architecture context, threat model, risk register, decision log, roadmap và parity checker.
- Checker source-ledger, requirements-traceability, master-prompt-parity, license và Markdown-pair cùng fixture âm.
- Test artifact máy đọc được tại `artifacts/test-runs/phase-00-closure/`.

## Nguồn và input

Nguồn sơ cấp ghi trong [SOURCE_LEDGER.md](../SOURCE_LEDGER.md), gồm identity đã pin của Klipper, Moonraker, Cartographer docs, OpenCV, kTAMV, KTC và klipper-toolchanger. Input gồm bootstrap đã review, report/CSV X/Y và Z history liên quan từ All-Config. Không sao chép source upstream.

## Giả định và quyết định

- License first-party: SPDX `GPL-3.0-or-later`.
- Package slug: `xyz_klipper_tool`.
- Raw import giữ byte và bất biến sau commit.
- `evidence/imported` là raw có provenance; Markdown khác là first-party trừ exemption rõ kèm provenance.
- Kiểm tra offline không chứng minh an toàn vật lý hay tương thích hardware.

## Acceptance test

1. Mọi Markdown first-party có cặp hai chiều; thiếu EN, thiếu VI và orphan trong `artifacts/` đều fail trong fixture tạm.
2. Master prompt có 18 mục/42 heading và mọi code/command token hiện diện trong bản Việt.
3. Requirements và traceability có cùng 24 ID duy nhất ở hai ngôn ngữ, mỗi ID một hàng; fixture thiếu/thừa/trùng fail.
4. Source ledger có 11 row song ngữ với URL, identity access/content, claim, license rõ và không placeholder cấm; fixture placeholder fail.
5. License artifact khớp SHA-256 chuẩn hóa và marker GPL bắt buộc.
6. Evidence parse được, hash khớp manifest, giữ `WARNING`/`INVALID`, không phát hiện secret.
7. Link, diff và boundary production đạt.

## Ranh giới HIL và cổng

Mọi claim khả năng vật lý vẫn `REQUIRES_HIL`. Phase chỉ hoàn tất cho deliverable governance/evidence offline và dừng tại supervisor review. Kế hoạch này không cấp quyền cho production behavior.
