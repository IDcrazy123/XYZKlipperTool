# Prompt xây dựng chính — XYZ Klipper Tool

## 1. Vai trò

Bạn là agent triển khai **XYZ Klipper Tool**, làm việc trong `D:\Desktop\XYZKlipperTool` và phát hành tại <https://github.com/IDcrazy123/XYZKlipperTool>. Dùng model `gpt-5.6-luna` với reasoning `medium` cho mỗi phase hữu hạn.

Hành xử như kỹ sư cấp staff cẩn trọng với tích hợp Klipper nhạy cảm an toàn. Hoàn tất phần offline được phép, xác minh, ghi tài liệu, commit và push nhánh phase. Không tuyên bố phase hoàn tất chỉ vì có kế hoạch.

## 2. Danh tính dự án bất biến

- Tên hiển thị: **XYZ Klipper Tool**.
- Python package/service slug quyết định ở Phase 00, dùng một định danh viết thường nhất quán và ghi trong ADR.
- Kho: `D:\Desktop\XYZKlipperTool`.
- Remote: `git@github.com:IDcrazy123/XYZKlipperTool.git`.
- Nhánh mặc định: `main`.
- Đây là kho greenfield; ToolVision chỉ là bằng chứng và tài liệu đối chiếu.
- Không đổi tên, fork, vendor, sao chép hoặc vá dần ToolVision vào kho này.
- Code upstream cần quyết định license/provenance rõ và attribution theo file; không che lịch sử sao chép bằng đổi tên.

## 3. Mục tiêu sản phẩm

Xây hệ thống hiệu chuẩn mở rộng được cho toolchanger Klipper:

1. Tự động đo offset X/Y tương đối bằng camera cố định.
2. Đo offset Z tương đối bằng một provider được chọn rõ: công tắc tiếp xúc vật lý hoặc Cartographer Touch.
3. Cho operator dạy trạm camera và từng trạm Z-provider từ pose hiện tại bằng G-Code, xác thực pose và lưu atomic.
4. Không giả định tọa độ camera, probe, switch, dock hoặc safe-Z cố định.
5. Khám phá tool qua adapter; không giả định đúng năm tool hoặc tên T0–T4.
6. Chạy pickup cycle độc lập lặp lại và giữ raw evidence.
7. Mặc định báo cáo candidate; apply là giao dịch riêng có preview, xác nhận và hoàn nguyên.
8. Hỗ trợ thuật toán camera, Z provider, toolchanger, storage và UI tương lai mà không đổi domain logic.

## 4. Ngoài mục tiêu của v1

- Không điều khiển ESP32-C3, WS2812B hay đèn phụ.
- Không cloud image upload/dependency.
- Không tự chuyển động vật lý nếu chưa có HIL được operator phê duyệt.
- Không làm bed-mesh, QGL, PID, input-shaper hay tuning chất lượng in tổng quát.
- Không thay Cartographer firmware calibration.
- Không tự động `SAVE_CONFIG`, restart Klipper, sửa production config hoặc apply offset.
- Không hard-code KTC và không mô phỏng mọi framework toolchanger trong v1.
- Không khẳng định camera detection đáng tin trước khi corpus gán nhãn và HIL đạt.

## 5. Quy tắc bắt buộc về bằng chứng và nguồn

Đọc `AGENTS.md`, `docs/EVIDENCE_BASELINE.md`, `docs/SOURCE_MAP.md` và `docs/STATUS.md` trước. Coi kTAMV/Z runs là bằng chứng yêu cầu, không phải source tái sử dụng.

Trước behavior phụ thuộc Klipper, Moonraker, Cartographer, OpenCV, KTC hoặc toolchanger khác:

1. Mở nguồn sơ cấp hiện tại.
2. Ghi URL, ngày truy cập, version/commit, claim, mơ hồ và license vào source ledger.
3. Thêm traceability từ requirement → source/evidence → design → test.
4. Dừng và đánh dấu `BLOCKED_BY_SOURCE` nếu chưa xác lập semantics safety-critical như dấu offset, hệ tọa độ, active-tool state hoặc probe result.

Không suy diễn default từ pose camera X170/Y20/Z40, switch X68/Y-10, scale, offset, số tool, nhiệt độ hoặc dung sai lịch sử.

## 6. Thuật ngữ và state model bắt buộc

- `OBSERVED`: có trong external evidence được bảo toàn.
- `IMPLEMENTED`: code tồn tại và test offline phù hợp đạt.
- `PLANNED`: design được duyệt hoặc việc tương lai chưa hoàn tất.
- `REQUIRES_HIL`: cần hardware execution được phê duyệt.
- `INVALID`: run lỗi/vi phạm invariant; không aggregate.
- `WARNING`: run xong nhưng thiếu/vượt acceptance check.
- `PASS`: mọi check bắt buộc của protocol đạt.

Tách các identity: `run_id` (calibration job), `outer_cycle_id` (reacquisition độc lập), `tool_visit_id` (tool visit), `frame_sample_id` (image/detection sample), `station_revision` (revision station bất biến), `configuration_fingerprint` (identity chuẩn hóa dùng freshness) và `calibration_id` (identity camera transform).

## 7. Hợp đồng lệnh bắt buộc

Phase 00 chỉ đổi tên qua ADR; bề mặt lệnh v1 giữ semantics sau.

### Lệnh station

- `XYZ_TOOL_TEACH_CAMERA_POSITION [SAFE_Z=<mm>] [NAME=<id>]`: lấy X/Y/Z hiện tại từ printer; nếu thiếu `SAFE_Z` phải ghi rõ current Z là clearance hay từ chối, không bịa; kiểm tra homing, limits, active/reference semantics và số hữu hạn.
- `XYZ_TOOL_TEACH_Z_POSITION METHOD=SWITCH|CARTOGRAPHER_TOUCH [SAFE_Z=<mm>] [NAME=<id>]`: station tách theo provider, lưu identity, pose, safe approach, frame, fingerprint, timestamp và revision.
- `XYZ_TOOL_SHOW_POSITIONS [NAME=<id>]`
- `XYZ_TOOL_CLEAR_POSITION TYPE=CAMERA|Z METHOD=<provider> NAME=<id> CONFIRM=<token>`: xóa cần preview chính xác và xác nhận.

### Lệnh đo

- `XYZ_TOOL_MEASURE_XY [CYCLES=3] [TOOLS=<selector>] [REFERENCE=<tool>] [STATION=<id>]`
- `XYZ_TOOL_MEASURE_Z METHOD=SWITCH|CARTOGRAPHER_TOUCH [CYCLES=3] [TOOLS=<selector>] [REFERENCE=<tool>] [STATION=<id>]`
- `XYZ_TOOL_MEASURE_XYZ METHOD=SWITCH|CARTOGRAPHER_TOUCH [CYCLES=3] ...`
- `XYZ_TOOL_STATUS [RUN=<id>]`
- `XYZ_TOOL_CANCEL [RUN=<id>]`
- `XYZ_TOOL_REPORT [RUN=<id>] [FORMAT=TEXT|JSON]`

Mặc định đo report-only. `CYCLES` là outer reacquisition độc lập, không phải đọc lặp khi chưa redock.

### Lệnh apply

- `XYZ_TOOL_APPLY_PREVIEW RUN=<id>`
- `XYZ_TOOL_APPLY RUN=<id> CONFIRM=<token>`
- `XYZ_TOOL_ROLLBACK APPLY=<id> CONFIRM=<token>`

Apply từ chối evidence stale/invalid/warning thiếu override, sai provider/tool-set/reference hoặc config đổi; tạo backup và rollback manifest trước mutation đầu; không che partial failure.

## 8. Kiến trúc bắt buộc

Dùng hexagonal/ports-and-adapters, dependency hướng domain.

### Domain package

Python thuần, không import Klipper, Moonraker, OpenCV, Flask/FastAPI, systemd hay filesystem-specific code. Sở hữu typed vectors/units/frames/signs, station và fingerprint objects, cycle/run state machine, validity/reason codes, robust statistics/uncertainty, apply/freshness/rollback plans và provider-neutral interfaces.

### Host service

Sở hữu camera capture có timeout/frame bound, OpenCV transform/detector, calibration/corpus evaluation, evidence/history retention, loopback HTTP/Unix API, job không chặn reactor và health/status có cấu trúc.

### Klippy extension

Sở hữu G-Code registration, đọc printer/tool/axis/heater/probe/endstop, thao tác printer bounded qua API/macro, phối hợp host không blocking, `get_status()`, abort/timeout/recovery. Không import OpenCV, không filesystem/network dài trên reactor, không dùng undocumented internals nếu thiếu shim pin và test.

### Ports và adapters

Tối thiểu có `CameraProvider`, `VisionDetector`, `ToolchangerAdapter`, `ZProvider`, `StationStore`, `EvidenceStore`, `OffsetReader`, `OffsetWriter`, `Clock`, `RunLock`. Có fake trước hardware; adapter thật đầu tiên bao phủ môi trường KTC/klipper-toolchanger và macro/status generic theo evidence Phase 00.

## 9. Invariant chuyển động và an toàn

Mã hóa từng invariant bằng reason code và fault-injection test:

1. Không chuyển động trước khi axis cần home và printer ready.
2. Không chạy khi printing, unsafe pause, shutdown hoặc có calibration lock khác.
3. Active/detected tool phải khớp nếu adapter cung cấp cả hai.
4. Station phải tồn tại, đúng provider, trong limits và khớp fingerprint hoặc migration rõ.
5. Nâng Z tại X/Y hiện tại tới clearance xác thực trước XY travel.
6. Không hạ dưới provider bounded approach envelope.
7. Switch state hợp lý và chuyển trong travel/time tối đa.
8. Cartographer Touch báo firmware/model/readiness tương thích trước approach.
9. Camera timeout, loại frame cũ và ambiguity.
10. Protocol khai báo reference return phải kiểm drift; thiếu return không pass.
11. Invalid sample/cleanup failure lưu nhưng loại estimator.
12. Cleanup best-effort theo thứ tự, không ghi đè lỗi chính.
13. Heater bị đổi phải restore/tắt an toàn; không chiếm heater chưa đụng.
14. Chỉ restore tool khi state đã biết; không đoán sau lỗi.
15. Mọi physical action idempotent hoặc có compensation/rollback được ghi.

## 10. Yêu cầu thống kê và thị giác

### Phân cấp sampling

Inner frame ước lượng detector repeatability; outer cycle ước lượng pickup/dock/reacquisition. Không coi inner frame là pickup cycle. Protocol X/Y v1 mặc định là ba outer cycle với tool động; chuỗi mục tiêu là acquire reference, đo tool bằng pickup độc lập, reacquire reference và đo return drift. Thứ tự khác cần ADR và evidence drift tương đương.

### Thống kê

Mỗi axis/tool/provider và hierarchy phải báo count total/valid/invalid/warning, raw có thứ tự, mean, median, sample standard deviation chỉ khi `n >= 2`, `INSUFFICIENT_SAMPLES` thay vì lỗi `stdev requires at least two data points`, MAD, min/max/range, reference drift, confidence/uncertainty cùng giả định, limits và reason-code verdict. Outlier policy khai báo trước, giữ raw và tạo unfiltered/filtered; mặc định không tự loại/apply.

### Thị giác

Corpus thật làm sạch phải gồm reflection, nhiều blob tròn, thiếu nozzle, blur, exposure đổi, nozzle lệch tâm; chia theo session để tránh leakage; benchmark nhiều phương pháp, không mặc định Hough circles; xuất candidate shapes, confidence, center residual, calibration identity, frame age, exposure metadata và rejection reason; định nghĩa image/decode/retry/frame/window/uncertainty bounds. Calibration và station origin tách khái niệm, tách version.

## 11. Persistence và evidence schema

Dùng atomic write-to-temp, fsync phù hợp, rename, schema version, backup rotation; không sửa raw file hoàn tất. Run manifest có schema/project version, run/cycle/visit/sample IDs, UTC/local timestamps, claim status/reason codes, command params/tool list, reference/toolchanger, station/fingerprint, camera/calibration/detector, Z provider metadata, units/frame/signs, raw/derived results, environment không secret, lỗi chính/cleanup/cancel/timeout, `applied=false` và checksum/provenance links. Migration và round-trip test phải có trước schema change; unknown fields không làm hỏng reader cũ, major version lạ fail closed.

## 12. Yêu cầu bảo mật và vận hành

- Bind `127.0.0.1` và/hoặc Unix socket mặc định.
- Remote về sau cần threat model, authentication/authorization, TLS/reverse-proxy và rate limits.
- Chỉ allowlisted camera scheme/host hoặc device cục bộ; chống SSRF/path traversal.
- Giới hạn body/image/history/concurrency/retry/queue/tool selector/string/numeric range.
- Redact credential/token trong URL, log, evidence, exception, support bundle.
- Không shell interpolation input.
- Pin dependency bằng hash sau license/vulnerability review.
- Install/update/rollback/uninstall phải idempotent, dry-run, scope-checked, test sandbox.
- Uninstall không xóa config/evidence nếu chưa có purge flag preview target.

## 13. Cấu trúc kho bắt buộc

Phase 00 có thể đổi tên qua ADR nhưng giữ phân tách:

```text
XYZKlipperTool/
  AGENTS.md / AGENTS.vi.md
  README.md / README.vi.md
  PROJECT_BUILD_PROMPT.md / PROJECT_BUILD_PROMPT.vi.md
  pyproject.toml
  src/<package>/
    domain/ protocol/ vision/ z/ toolchanger/ persistence/ service/ klipper/
  klippy/extras/ config/ scripts/ schemas/
  tests/ unit/ component/ contract/ integration/ fault_injection/ installer/ fixtures/
  evidence/ imported/ manifests/ corpus/
  docs/ adr/ phases/ progress/ operator/ developer/ api/
```

Mọi Markdown first-party có cặp `.vi.md`.

## 14. Kế hoạch phase và cổng chấp nhận

### Phase 00 — Governance, source audit, license, evidence import

Deliver ADR identity, requirements ID `REQ-...`, source ledger pin/license, clean-room policy, license/third-party plan, import X/Y và toàn bộ Z kể cả invalid, SHA-256/evidence index, architecture/threat, risk/decision/traceability/test/roadmap/parity checker và không production measurement code.

Gate: mọi behavior có source hoặc evidence/assumption; hash import khớp hoặc giải thích; secret scan, license và Markdown parity đạt; branch push và supervisor review yêu cầu.

### Phase 01 — Domain model, units, signs, statistics

Deliver pure typed domain, state/reason model, robust/provider-separated results, apply plan, schemas và property/metamorphic tests. Gate: không I/O/framework; `n=0`/`n=1` typed insufficient; sign/coordinate table tests; invalid loại; deterministic/schema round-trip đạt.

### Phase 02 — Ports, fake adapters, simulator, station persistence

Deliver ports, fake deterministic printer/toolchanger/camera/Z, dynamic discovery, teach/show/clear, atomic persistence, fingerprints, locks và crash/fault fixtures. Gate: không hard-code T0–T4; tọa độ chỉ từ current-position; stale/corrupt/partial fail closed; concurrency đúng; power-loss giữ state cuối.

### Phase 03 — Camera capture, calibration, detector framework

Deliver bounded camera, calibration store, detector plugins, hai pipeline benchmark khi evidence hỗ trợ, diagnostics, corpus tooling và session-separated evaluation. Gate: holdout/failure metrics; frame lỗi bị reject bằng reason; uncertainty truyền vào result; không physical-accuracy claim trước HIL.

### Phase 04 — X/Y independent-cycle orchestrator

Deliver report-only orchestration với fake adapter, nested sampling, tool/reference động, station lookup, return drift, cancel/timeout/recovery/report. Gate: outer cycle reacquire; inner không giả outer; fixture kTAMV tái hiện T3 mean/median; thiếu terminal return không `PASS`; không gọi writer.

### Phase 05 — Physical-switch Z provider

Deliver switch readiness/query, station riêng, bounded approach, trigger/release, multiple-probe, thermal metadata, abort/recovery và fixture. Gate: stuck-open/closed, no/early trigger, bounce, timeout, shutdown, unknown-tool, cleanup failure; sign mapping có source/fixture; TMC `INVALID` vẫn bị loại; physical `REQUIRES_HIL`.

### Phase 06 — Cartographer Touch Z provider

Deliver readiness/version/model, station/pose semantics, Touch parser, thermal/readiness, recovery và fixture. Gate: firmware/model/output lạ fail closed; parser dùng real/synthetic fixtures; provider tách switch; physical `REQUIRES_HIL`.

### Phase 07 — Apply transaction, backup, rollback

Deliver reader/writer, exact preview, token, freshness, backup, per-tool transaction, readback, partial failure, rollback và immutable manifest. Gate: measurement không gọi apply; stale/non-`PASS` reject trừ override hẹp; mọi mutation failure restore/báo divergence; không `SAVE_CONFIG`/restart; write semantics pin/test.

### Phase 08 — Host API và service

Deliver API versioned, lifecycle, health/status, bounded evidence, Unix/loopback, auth decision, structured errors, cancel, templates/resource limits. Gate SSRF/traversal/oversize/concurrency/timeout/redaction/crash/backcompat đạt; không listener ngoài mặc định; schema hai ngôn ngữ.

### Phase 09 — Klipper extension và G-Code commands

Deliver loader, command Section 7, non-blocking client, status, adapter selection, state guards, motion bridge, simulated integration. Gate reactor không block; help/error actionable; fake tests startup/restart/disconnect/shutdown/cancel/missing provider; parse error nêu option/remediation.

### Phase 10 — Installer, updater, uninstaller

Deliver prerequisites, dry-run, symlink/service/config exact, backup, versioned update/rollback, safe uninstall, purge preview, sandbox matrix. Gate idempotent; scope checks; không overwrite config; network không chạy code unpinned; rollback test.

### Phase 11 — Documentation, security, release candidate

Deliver paired guides/reference/troubleshooting/safety-HIL, architecture/ADR index, security/contribution/changelog/release checklist, redaction, SBOM/dependency/license report và release tag. Gate toàn bộ offline/lint/type/security/link/example/build/install/upgrade/uninstall đạt; không option thiếu docs; traceability đầy đủ; chưa production-ready.

### Phase 12 — Supervised HIL canary

Chỉ bắt đầu sau run sheet bằng văn bản được operator duyệt và xác nhận máy sẵn sàng. Run sheet có command teach, limits, clearance, tool/reference/provider, nhiệt độ, stop criteria, E-stop, thời lượng, capture và rollback. Bắt đầu report-only single-tool/single-cycle, không nhảy all-tools/apply. Gate: raw evidence traceable cho X/Y, switch Z, Cartographer Z; ba outer cycle đạt limits; failure/recovery drill an toàn; apply vẫn là quyết định riêng; chỉ review xong mới cân nhắc release.

## 15. Chính sách test và chất lượng

Dùng test deterministic và fixture rõ: unit domain/statistics; property/metamorphic transform/sign/aggregation/invariant; component capture/detection/persistence/provider/API; contract upstream/version; fake-Klipper/Moonraker; fault injection physical/persistence; installer sandbox; schema compatibility/migration; docs link/example và bilingual pair; secret/dependency/license/static-security/type/lint; performance/resource image/job/history/API. Mục tiêu tối thiểu 90% line/branch production first-party và 95% safety state machine/domain invariant, nhưng coverage không thay fault cases/traceability.

## 16. Tiến độ, Git và giám sát

- Mỗi phase một branch: `phase/00-governance`, `phase/01-domain`, v.v.
- Giữ `main` có thể phát hành; không tự merge trước supervisor gate.
- Commit tiếng Anh theo Conventional Commits, ví dụ `docs: establish phase 00 source ledger`.
- Không force-push branch dùng chung hay rewrite history publish.
- Push sau mỗi checkpoint nhất quán.
- Tạo progress pair `docs/progress/YYYY-MM-DD-phase-NN.md` và `.vi.md`.
- Record phải có objective, inputs, source updates, files, commands/tests exact, evidence, decisions, risks, status, commit, remote branch, next gate.
- Test artifacts máy đọc được ở `artifacts/test-runs/<run-id>/` cùng manifest; không commit secret/binary lớn không kiểm soát.
- Chỉ tag `checkpoint-phase-NN` sau supervisor approval; stable semantic release cần Phase 12 review.

## 17. Báo cáo cuối task bắt buộc

Mỗi Luna task báo cáo: (1) kết quả trước: hoàn tất/một phần/bị chặn; (2) phase và acceptance criteria; (3) file/kiến trúc đổi; (4) source/evidence thêm đổi; (5) command validation và pass/fail; (6) claim-state (`PLANNED` → `IMPLEMENTED` hoặc còn `REQUIRES_HIL`); (7) rủi ro và mơ hồ; (8) commit SHA/branch push; (9) phase/gate kế tiếp, không âm thầm bắt đầu.

Nếu bị chặn, tiếp tục offline độc lập trước. Blocker thật phải nêu fact/authority thiếu, hành động đã thử, evidence giữ lại và quyết định nhỏ nhất cần user.

## 18. Task đầu tiên phải thực hiện

Thực hiện **chỉ Phase 00**.

Không viết production measurement code. Xây governance, source, license, requirements, evidence-import, risk, traceability, test-matrix, architecture-context, threat-model, progress và bilingual-parity foundation. Nhập/checksum toàn bộ evidence liên quan mà không sửa raw. Xác minh mọi Markdown first-party có cặp Anh/Việt. Commit và push `phase/00-governance`, rồi dừng để supervisor review.
