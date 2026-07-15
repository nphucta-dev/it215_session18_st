# BÁO CÁO THIẾT KẾ HỆ THỐNG QUẢN LÝ WORKSHOP

## PHẦN 1: THIẾT KẾ KIẾN TRÚC

### 1.1. Phân tích nhu cầu

**Khách hàng đang gặp vấn đề gì?**
Trung tâm đang quản lý đăng ký workshop thủ công bằng Google Form + Excel nên không kiểm soát được: đăng ký trùng, vượt số lượng tối đa, đăng ký workshop đã đóng, và tổng hợp dữ liệu (sinh viên tham gia workshop nào, workshop có những ai) đều phải làm tay, tốn thời gian và dễ sai sót.

**Người dùng chính của hệ thống**
- Nhân viên trung tâm: tạo workshop, tra cứu danh sách đăng ký.
- Sinh viên: đăng ký/hủy đăng ký workshop (thông qua hệ thống, không trực tiếp gọi API nhưng là đối tượng nghiệp vụ chính).

**Chức năng hệ thống cần giải quyết**
- Quản lý sinh viên, quản lý workshop.
- Đăng ký / hủy đăng ký workshop.
- Tra cứu hai chiều: sinh viên → danh sách workshop đã đăng ký, workshop → danh sách sinh viên đã đăng ký.
- Áp dụng đầy đủ ràng buộc nghiệp vụ ngay tại tầng service, không phụ thuộc con người kiểm tra thủ công.

**Chức năng quan trọng nhất**
API `POST /registrations` — đây là nơi tập trung toàn bộ ràng buộc nghiệp vụ (sinh viên/workshop tồn tại, trạng thái, thời gian, trùng lặp, giới hạn số lượng), vì đây chính là nguồn gốc của các lỗi khách hàng đang gặp phải.

### 1.2. Thiết kế cơ sở dữ liệu

**Các bảng**
| Bảng | Mô tả |
|---|---|
| `students` | Thông tin sinh viên |
| `workshops` | Thông tin workshop |
| `registrations` | Bảng trung gian, lưu quan hệ đăng ký giữa sinh viên và workshop |

**Khóa chính**
- `students.id`, `workshops.id`, `registrations.id` — đều là `INTEGER AUTO_INCREMENT`.

**Khóa ngoại**
- `registrations.student_id` → `students.id`
- `registrations.workshop_id` → `workshops.id`

**Loại quan hệ**
- `Student` 1—N `Registration` N—1 `Workshop`, tức quan hệ **N–N** giữa `Student` và `Workshop` thông qua bảng trung gian `Registration`.

**Ràng buộc dữ liệu**
- `students.student_code` UNIQUE, `students.email` UNIQUE.
- Không đặt `UNIQUE(student_id, workshop_id)` cứng ở tầng DB cho `registrations`, vì hệ thống cho phép sinh viên hủy rồi đăng ký lại — việc chống trùng chỉ áp dụng cho các bản ghi đang ở trạng thái `REGISTERED`, được kiểm tra ở tầng service.

### 1.3. Các quyết định thiết kế (mục 5 đề bài)

| Câu hỏi | Quyết định | Lý do |
|---|---|---|
| Trạng thái Workshop | `OPEN`, `CLOSED`, `CANCELLED` | Phân biệt rõ "đang mở đăng ký" và "đã bị hủy" để xử lý khác nhau |
| Trạng thái Student | `ACTIVE`, `INACTIVE` | Chặn sinh viên ngừng hoạt động đăng ký mới |
| Hủy đăng ký | Đổi trạng thái `CANCELLED`, không xóa | Giữ lịch sử đăng ký để tra cứu/thống kê sau này |
| Sinh viên INACTIVE có được đăng ký? | Không | Đồng bộ với quy tắc trạng thái sinh viên |
| Workshop đã bắt đầu (`start_time` đã qua) có được đăng ký? | Không | Tránh đăng ký vào sự kiện đã diễn ra |
| Workshop bị hủy thì các đăng ký xử lý sao? | Chặn đăng ký mới vào workshop `CANCELLED`; các đăng ký cũ giữ nguyên để tra cứu lịch sử, không tự động xóa | Đơn giản, minh bạch, không mất dữ liệu |
| Email hay mã sinh viên cần duy nhất? | Cả hai đều UNIQUE | Cả hai đều dùng để định danh/liên hệ sinh viên |
| Dữ liệu trả về phẳng hay lồng nhau? | Phẳng (flat), có id tham chiếu | Dễ dùng ở frontend, khớp với response format 6 trường chuẩn hóa |
| Tách service nào? | `StudentService`, `WorkshopService`, `RegistrationService` | Tách theo nghiệp vụ, `RegistrationService` chứa toàn bộ logic ràng buộc phức tạp nhất |

## PHẦN 2: SẢN PHẨM

Xem source code trong thư mục `app/`. Cấu trúc:

```
app/
  main.py                     # khởi tạo FastAPI, đăng ký router + exception handler
  database.py                 # engine, SessionLocal, get_db()
  models/                     # SQLAlchemy 2.0 (Mapped/mapped_column)
    student.py
    workshop.py
    registration.py
  schemas/                    # Pydantic v2
    student.py
    workshop.py
    registration.py
  services/                   # business logic
    student_service.py
    workshop_service.py
    registration_service.py   # toàn bộ ràng buộc đăng ký workshop
  routers/
    student_router.py
    workshop_router.py
    registration_router.py
  core/
    response.py                # build_response() - format 6 trường chuẩn
    exceptions.py               # global exception handler (HTTPException/422/500)
```

### Danh sách API đã hoàn thành

| Method | Endpoint | Mã trạng thái |
|---|---|---|
| POST | /students | 201 / 400 (trùng mã hoặc email) / 422 |
| GET | /students | 200 |
| POST | /workshops | 201 / 422 |
| GET | /workshops | 200 |
| GET | /workshops/{id} | 200 / 404 |
| POST | /registrations | 201 / 404 (sinh viên hoặc workshop không tồn tại) / 400 (vi phạm nghiệp vụ) |
| PUT | /registrations/{id} | 200 / 404 / 400 (đã hủy trước đó) |
| GET | /students/{id}/workshops | 200 / 404 |
| GET | /workshops/{id}/students | 200 / 404 |

### Cách chạy

1. Tạo database MySQL tên `workshop_db`, cập nhật `DATABASE_URL` trong `app/database.py` nếu cần (user/password/host/port khác).
2. Cài thư viện:
   ```
   pip install -r requirements.txt
   ```
3. Chạy server:
   ```
   uvicorn app.main:app --reload
   ```
4. Bảng sẽ tự tạo khi khởi động (`Base.metadata.create_all`).

Đã kiểm thử toàn bộ luồng nghiệp vụ (tạo sinh viên trùng email/mã, đăng ký trùng, đăng ký khi đủ số lượng, đăng ký sinh viên/workshop không tồn tại, hủy rồi đăng ký lại, lỗi validation 422) bằng test tự động với SQLite in-memory, tất cả đều trả đúng mã trạng thái và message.
