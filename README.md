# VN101 AI Office

Nền tảng điều hành nhiều AI Agent theo mô hình văn phòng số: có vai trò, nhiệm vụ, nhật ký hoạt động, báo cáo và cơ chế phê duyệt của chủ sở hữu.

## Mục tiêu giai đoạn đầu

- Xây dựng backend API làm lõi điều phối.
- Tách AI Gateway khỏi logic nghiệp vụ để có thể thay đổi nhà cung cấp mô hình.
- Quản lý người dùng, vai trò và quyền hạn theo nguyên tắc least privilege.
- Ghi nhận task, trạng thái, hoạt động và lịch sử phê duyệt.
- Không cho AI tự ý triển khai production, thay đổi hạ tầng hoặc truy cập bí mật nếu chưa được cấp quyền.

## Kiến trúc hiện tại

- **Backend:** Python 3.11+ và FastAPI.
- **Database:** MongoDB Atlas, database riêng `vn101_ai_office`.
- **Authentication:** Firebase Authentication (Email/Password) và Firebase Admin SDK để xác minh ID token.
- **User profile:** lưu trong MongoDB collection `users`; UID được cấu hình làm chủ sở hữu nhận role `owner`, người dùng mới khác nhận role `user`.
- **Frontend:** dashboard điều hành (xây dựng ở giai đoạn tiếp theo).
- **Integrations:** GitHub, Render và các dịch vụ khác qua adapter có quyền tối thiểu.

## Cấu trúc chính

```text
backend/
  app/
    api/routes/users.py
    core/
    main.py
  tests/
scripts/
  configure_local_env.py
.env.example
.gitignore
requirements.txt
```

## Thiết lập môi trường local (Windows/macOS/Linux)

Yêu cầu Python 3.11 trở lên. Trước khi chạy, cần có:
- File Firebase Service Account JSON tải từ đúng dự án Firebase `vn101-ai-office`.
- MongoDB Atlas connection string với mật khẩu thật đã thay vào; nếu mật khẩu có ký tự đặc biệt, hãy URL-encode theo hướng dẫn của MongoDB.

### 1. Tạo môi trường ảo và cài thư viện

Tại thư mục gốc repository:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Tạo file cấu hình bí mật local

Đặt file JSON ở thư mục gốc repository với tên `service-account.json`, hoặc nhập đường dẫn đầy đủ khi script hỏi. Chạy:

```bash
python scripts/configure_local_env.py
```

Script sẽ:
- Kiểm tra đây là service-account JSON của đúng Firebase project.
- Đọc file JSON trực tiếp trên máy, không in private key ra màn hình.
- Yêu cầu nhập MongoDB URI bằng chế độ ẩn ký tự.
- Tạo `backend/.env` với các giá trị cần thiết.
- Không ghi bất kỳ secret nào vào GitHub.

Nếu `backend/.env` đã tồn tại, script yêu cầu xác nhận rõ ràng trước khi ghi đè.

### 3. Chạy API và kiểm tra

```bash
cd backend
uvicorn app.main:app --reload
```

- Liveness: `GET http://127.0.0.1:8000/healthz`
- Readiness (MongoDB): `GET http://127.0.0.1:8000/readyz`
- OpenAPI: `http://127.0.0.1:8000/docs`
- Hồ sơ người dùng đã đăng nhập: `GET /api/v1/users/me` với Firebase ID token trong Bearer header. Email phải được xác minh.

## Nguyên tắc bảo mật

- Không commit `.env`, token, private key, service-account JSON hoặc thông tin kết nối thật.
- `.env` được Git ignore; chỉ dùng biến môi trường cho cấu hình nhạy cảm.
- Không chia sẻ Firebase credentials, MongoDB URI hoặc database với dự án Dautu.
- Không gửi service-account JSON, private key hoặc mật khẩu qua chat.
- AI Agent mặc định không có quyền ghi; mọi hành động có tác động bên ngoài phải đi qua policy và approval.
- Mọi thay đổi nền tảng được thực hiện qua branch và Pull Request; không tự động merge vào `main`.

## Trạng thái

Đã có nền tảng FastAPI, MongoDB readiness check và lớp xác thực Firebase/user role cơ bản. AI Gateway, orchestration và dashboard sẽ được triển khai ở các giai đoạn tiếp theo.
