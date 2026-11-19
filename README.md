# VN101 AI Office

Nền tảng điều hành nhiều AI Agent theo mô hình văn phòng số: có vai trò, nhiệm vụ, nhật ký hoạt động, báo cáo và cơ chế phê duyệt của chủ sở hữu.

## Mục tiêu giai đoạn đầu

- Xây dựng backend API làm lõi điều phối.
- Tách AI Gateway khỏi logic nghiệp vụ để có thể thay đổi nhà cung cấp mô hình.
- Quản lý người dùng, vai trò và quyền hạn theo nguyên tắc least privilege.
- Ghi nhận task, trạng thái, hoạt động và lịch sử phê duyệt.
- Không cho AI tự ý triển khai production, thay đổi hạ tầng hoặc truy cập bí mật nếu chưa được cấp quyền.

## Kiến trúc dự kiến

- **Backend:** Python + FastAPI.
- **Database:** MongoDB Atlas, database riêng `vn101_ai_office`.
- **AI Gateway:** lớp adapter độc lập với nhà cung cấp AI.
- **Frontend:** dashboard điều hành (xây dựng ở giai đoạn tiếp theo).
- **Authentication:** xác thực người dùng và phân quyền phía server.
- **Integrations:** GitHub, Render và các dịch vụ khác qua adapter có quyền tối thiểu.

## Cấu trúc hiện tại

```text
backend/
  app/
    core/
    main.py
  tests/
.env.example
.gitignore
requirements.txt
```

## Chạy backend local

Yêu cầu Python 3.11 trở lên.

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

API kiểm tra sức khỏe: `GET /healthz`  
Tài liệu OpenAPI local: `/docs`

## Nguyên tắc bảo mật

- Không commit file `.env`, token, private key, service-account JSON hoặc thông tin kết nối thật.
- Chỉ dùng biến môi trường cho cấu hình nhạy cảm.
- AI Agent mặc định không có quyền ghi; mọi hành động có tác động bên ngoài phải đi qua policy và approval.
- Không kết nối hoặc dùng chung database, Firebase credentials hay secrets của dự án Dautu.
- Mọi thay đổi nền tảng được thực hiện qua branch và Pull Request; không tự động merge vào `main`.

## Trạng thái

Đây là bộ khung khởi tạo ban đầu. Authentication, MongoDB repository, AI Gateway, orchestration và dashboard chưa được triển khai.
