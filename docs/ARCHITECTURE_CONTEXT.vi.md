# Bối cảnh kiến trúc Phase 00

```text
Klippy extension --(contract hữu hạn, không blocking)--> host service
      |                                                   |
state máy/khám phá tool                                camera/CV/evidence/report
      |                                                   |
 ports: ToolchangerAdapter, ZProvider, StationStore, EvidenceStore, Offset*
                         \--> domain model và verdict thuần
```

Domain không import framework/I/O. Camera X/Y và provider Z là adapter riêng. Station được dạy từ pose hiện tại và version kèm configuration fingerprint. Đo tạo evidence bất biến; apply là boundary giao dịch riêng. Phase 00 không có mã đo production.
