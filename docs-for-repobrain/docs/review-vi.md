# Review Tiếng Việt

File này ghi lại review kỹ thuật hiện tại của RepoBrain theo góc nhìn code review/product review. Mục tiêu là ưu tiên lỗi, rủi ro, regression và khoảng trống test trước khi tiếp tục thêm feature mới.

Trạng thái hiện tại: 4 finding trong file này đã được xử lý trong vòng fix review.

## Tóm Tắt

RepoBrain đang có nền khá tốt:

- Kiến trúc tách lớp rõ: config, scanner, store, engine, CLI, MCP.
- Product direction rõ: local-first, evidence-first, không tự động sửa code ở v1.
- Docs và release direction đã khá đầy đủ.
- Test suite hiện pass với `14 passed`.
- Tree-sitter optional đã chạy được và có heuristic fallback.

Điểm cần xử lý trước khi mở rộng sâu hơn là độ ổn định retrieval, độ chính xác edge tracing, launcher Windows và kiểm tra trạng thái index.

## Finding 1: Vector Persisted Dùng Python `hash()` Không Ổn Định

Mức độ: `P1`

Trạng thái: đã fix.

File liên quan:

- `src/repobrain/engine/providers.py`

Vấn đề:

`LocalHashEmbeddingProvider` đang dùng built-in `hash(token)` để map token vào vector slot. Python randomize hash seed theo process, nên vector được tạo lúc `repobrain index` có thể không cùng không gian với vector query lúc `repobrain query` nếu chạy ở process khác.

Tác động:

- Semantic retrieval có thể lệch giữa các lần chạy CLI.
- Kết quả vector search không ổn định.
- Debug ranking sẽ khó vì score thay đổi theo process.

Hướng sửa:

- Đã thay `hash(token)` bằng stable hash từ `hashlib.blake2b`.
- Đã thêm test đảm bảo cùng token luôn map về cùng vector qua nhiều provider instance.

## Finding 2: Import Call Edges Bỏ Lỡ Named Imports

Mức độ: `P1`

Trạng thái: đã fix.

File liên quan:

- `src/repobrain/engine/scanner.py`

Vấn đề:

Scanner đang lưu import dạng module path như `app.services.auth_service` hoặc `./oauth`, rồi khi tạo edge lại so called function với `item.split(".")[-1]`. Cách này không bắt được named imports như `login_with_google`, `handleGoogleCallback`, hoặc alias import.

Tác động:

- Trace route -> service thiếu edge quan trọng.
- Impact analysis yếu hơn vì graph support không đủ.
- `build_change_context` có thể vẫn tìm đúng file nhờ retrieval, nhưng structural rationale chưa đủ mạnh.

Hướng sửa:

- Đã extract thêm imported binding/alias cho Python và TS/JS.
- Khi function call trùng imported binding, scanner tạo `imports_call` edge.
- Đã thêm test cho Python alias import và TS named alias import.

## Finding 3: `chat.cmd` Chưa Ưu Tiên Venv Của Project

Mức độ: `P2`

Trạng thái: đã fix.

File liên quan:

- `chat.cmd`

Vấn đề:

Launcher đang gọi plain `python`, nên khi double-click có thể dùng global Python thay vì `venv\Scripts\python.exe`.

Tác động:

- Có thể mất dependency đã cài trong venv, ví dụ `tree-sitter`.
- Có thể chạy sai Python version.
- Trải nghiệm "bấm là chat" thiếu ổn định trên máy người dùng khác.

Hướng sửa:

- `chat.cmd` đã ưu tiên `venv\Scripts\python.exe`.
- Nếu không có `venv`, launcher thử `.venv\Scripts\python.exe`.
- Nếu không có virtualenv, launcher mới fallback sang global `python`.

## Finding 4: `indexed()` Chỉ Check DB File Tồn Tại

Mức độ: `P2`

Trạng thái: đã fix.

File liên quan:

- `src/repobrain/engine/store.py`

Vấn đề:

`indexed()` hiện chỉ trả true nếu `.repobrain/metadata.db` tồn tại. Nếu indexing crash sau khi tạo DB, hoặc DB thiếu table/chunk, query vẫn có thể chạy vào index hỏng.

Tác động:

- Query error khó hiểu.
- `doctor.indexed` có thể báo sai.
- MCP/CLI downstream có thể tin nhầm repo đã indexed đầy đủ.

Hướng sửa:

- Đã check DB tồn tại.
- Đã check các table bắt buộc: `files`, `chunks`, `chunk_fts`, `symbols`, `edges`.
- Đã check có ít nhất một file và một chunk.
- Nếu DB hỏng hoặc thiếu table, `indexed()` trả false thay vì để exception lan ra query path.

## Thứ Tự Sửa Đề Xuất

1. Đã sửa stable hash cho local embedding.
2. Đã sửa import binding extraction và `imports_call` edges.
3. Đã sửa `chat.cmd` để dùng đúng venv.
4. Đã sửa `indexed()` health check.
5. Việc tiếp theo nên làm: thêm confidence calibration tests sau khi graph và vector đã ổn định hơn.

## Ghi Chú Product

RepoBrain đang đi đúng hướng cho một OSS local-first AI coding tool. Điểm mạnh hiện tại không phải là "nhiều feature", mà là có trust model rõ: evidence, warning, confidence, local storage và optional parser fallback.

Nếu tiếp tục giữ nhịp này, release tiếp theo nên tập trung vào chất lượng retrieval và trace graph thay vì thêm dashboard hoặc autonomous mutation quá sớm.
